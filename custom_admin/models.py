# custom_admin/models.py

from django.db import models
from django.contrib.auth.models import User
import uuid

class AdminInvitation(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation for {self.email}"
