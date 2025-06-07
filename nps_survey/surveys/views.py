# surveys/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer, SurveyLinkSerializer, SurveyResponseSerializer
from .models import SurveyLink, SurveyResponse
from django.core.signing import BadSignature, Signer
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from datetime import datetime
from django.utils.dateparse import parse_date


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class SurveyLinkCreateView(generics.CreateAPIView):
    queryset = SurveyLink.objects.all()
    serializer_class = SurveyLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SurveyLinkListView(generics.ListAPIView):
    serializer_class = SurveyLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SurveyLink.objects.filter(user=self.request.user)


class SurveyResponseCreateView(APIView):
    def post(self, request):
        signed_token = request.data.get('signed_token')
        if not signed_token:
            return Response({"error": "Signed token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            signer = Signer()
            decoded = signer.unsign(signed_token)
            user_id, token = decoded.split(':')
            survey_link = SurveyLink.objects.get(token=token, user_id=user_id)

            if survey_link.expiry < timezone.now():
                return Response({"error": "Survey link has expired."}, status=status.HTTP_400_BAD_REQUEST)

            if hasattr(survey_link, 'response'):
                return Response({"error": "Response already submitted."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = SurveyResponseSerializer(data={
                'survey_link': survey_link.id,
                'score': request.data.get('score'),
                'comments': request.data.get('comments')
            })
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except SurveyLink.DoesNotExist:
            return Response({"error": "Invalid survey link."}, status=status.HTTP_404_NOT_FOUND)
        except BadSignature:
            return Response({"error": "Invalid signed token."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Malformed signed token."}, status=status.HTTP_400_BAD_REQUEST)


class SurveyResponseCheckView(APIView):
    def get(self, request, signed_token):
        try:
            signer = Signer()
            decoded = signer.unsign(signed_token)
            user_id, token = decoded.split(':')
            survey_link = SurveyLink.objects.get(token=token, user_id=user_id)

            if survey_link.expiry < timezone.now():
                return Response({"error": "Survey link has expired."}, status=status.HTTP_400_BAD_REQUEST)

            if hasattr(survey_link, 'response'):
                return Response({"error": "Response already submitted."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "No response submitted."}, status=status.HTTP_200_OK)

        except SurveyLink.DoesNotExist:
            return Response({"error": "Invalid survey link."}, status=status.HTTP_404_NOT_FOUND)
        except BadSignature:
            return Response({"error": "Invalid signed token."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Malformed signed token."}, status=status.HTTP_400_BAD_REQUEST)


class SurveyResponseCheckMultipleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        signed_tokens = request.data.get('signed_tokens', [])
        if not signed_tokens:
            return Response({"error": "No signed tokens provided."}, status=status.HTTP_400_BAD_REQUEST)

        result = {}
        signer = Signer()
        for signed_token in signed_tokens:
            try:
                decoded = signer.unsign(signed_token)
                user_id, token = decoded.split(':')
                survey_link = SurveyLink.objects.get(token=token, user_id=user_id, user=request.user)

                if survey_link.expiry < timezone.now():
                    result[signed_token] = 'expired'
                elif hasattr(survey_link, 'response'):
                    result[signed_token] = 'responded'
                else:
                    result[signed_token] = 'active'
            except (SurveyLink.DoesNotExist, BadSignature, ValueError):
                result[signed_token] = 'invalid'

        return Response(result, status=status.HTTP_200_OK)


class SurveyMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        survey_links = SurveyLink.objects.filter(user=request.user)
        responses = SurveyResponse.objects.filter(survey_link__in=survey_links)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        campaign_id = request.query_params.get('campaign_id')
        search_query = request.query_params.get('search')

        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                responses = responses.filter(created_at__date__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                responses = responses.filter(created_at__date__lte=end_date)
        if campaign_id:
            survey_links = survey_links.filter(campaign_id=campaign_id)
            responses = responses.filter(survey_link__in=survey_links)
        if search_query:
            responses = responses.filter(comments__icontains=search_query)

        promoters = responses.filter(score__gte=9).count()
        passives = responses.filter(score__in=[7, 8]).count()
        detractors = responses.filter(score__lte=6).count()
        total = responses.count()
        nps_score = ((promoters - detractors) / total * 100) if total > 0 else 0

        trend = responses.annotate(date=TruncDate('created_at')).values('date').annotate(
            promoters=Count('survey_link', filter=Q(score__gte=9)),
            detractors=Count('survey_link', filter=Q(score__lte=6)),
            total=Count('survey_link')
        ).values('date', 'promoters', 'detractors', 'total').order_by('date')
        trend_data = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'nps_score': ((item['promoters'] - item['detractors']) / item['total'] * 100) if item[
                                                                                                     'total'] > 0 else 0
            }
            for item in trend
        ]

        return Response({
            'promoters': promoters,
            'passives': passives,
            'detractors': detractors,
            'nps_score': round(nps_score, 2),
            'total_responses': total,
            'trend': trend_data,
        })