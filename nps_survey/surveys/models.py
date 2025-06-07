# surveys/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
from django.core.signing import Signer
from django.utils import timezone

def get_default_expiry():
    return timezone.now() + timedelta(days=7)

class SurveyLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_links')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    signed_token = models.CharField(max_length=255, unique=True, blank=True)
    expiry = models.DateTimeField(default=get_default_expiry, null=True, blank=True)
    campaign_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['signed_token']),
            models.Index(fields=['user']),
        ]

    def save(self, *args, **kwargs):
        if not self.signed_token:
            signer = Signer()
            self.signed_token = signer.sign(f"{self.user.id}:{self.token}")
        super().save(*args, **kwargs)

class SurveyResponse(models.Model):
    survey_link = models.OneToOneField(SurveyLink, on_delete=models.CASCADE, related_name='response', primary_key=True)
    score = models.IntegerField(choices=[(i, i) for i in range(11)])
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['survey_link']),
        ]