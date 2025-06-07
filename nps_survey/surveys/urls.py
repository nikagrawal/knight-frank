# surveys/urls.py
from django.urls import path
from .views import (
    RegisterView, UserProfileView, SurveyLinkCreateView,
    SurveyLinkListView, SurveyResponseCreateView, SurveyMetricsView,
    SurveyResponseCheckView, SurveyResponseCheckMultipleView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('survey-links/', SurveyLinkCreateView.as_view(), name='survey_link_create'),
    path('survey-links/list/', SurveyLinkListView.as_view(), name='survey_link_list'),
    path('survey-response/', SurveyResponseCreateView.as_view(), name='survey_response_create'),
    path('survey-response/check/<str:signed_token>/', SurveyResponseCheckView.as_view(), name='survey_response_check'),
    path('survey-response/check-bulk/', SurveyResponseCheckMultipleView.as_view(), name='survey_response_check_bulk'),
    path('metrics/', SurveyMetricsView.as_view(), name='survey_metrics'),
]