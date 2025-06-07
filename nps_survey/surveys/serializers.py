# surveys/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SurveyLink, SurveyResponse
from django.core.signing import Signer, BadSignature
from django.utils import timezone
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class SurveyLinkSerializer(serializers.ModelSerializer):
    expiry = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = SurveyLink
        fields = ['id', 'token', 'signed_token', 'expiry', 'campaign_id', 'created_at']
        read_only_fields = ['token', 'signed_token', 'created_at']

    def validate_expiry(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Expiration date cannot be in the past.")
        return value

class SurveyResponseSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(min_value=0, max_value=10)

    class Meta:
        model = SurveyResponse
        fields = ['survey_link', 'score', 'comments', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        survey_link = data['survey_link']
        if survey_link.expiry < timezone.now():
            raise serializers.ValidationError("Survey link has expired.")
        try:
            signer = Signer()
            signer.unsign(survey_link.signed_token)
        except BadSignature:
            raise serializers.ValidationError("Invalid survey link.")
        return data