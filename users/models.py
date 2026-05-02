from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
import uuid
# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ANALYST_ROLE='analyst'
    ADMIN_ROLE='admin'
    
    ROLE_CHOICES = (
        (ANALYST_ROLE, 'analyst'),
        (ADMIN_ROLE, 'admin'),
    ) 

    id = models.UUIDField(default=uuid.uuid7, primary_key=True, editable=False)
    github_id = models.CharField(max_length=255, unique=True, verbose_name=_('Github ID'))
    username = models.CharField(max_length=100, unique=True, verbose_name=_("username"))
    email = models.EmailField(max_length=100, unique=True, verbose_name=_("email"))
    avatar_url = models.CharField(max_length=255, verbose_name=_("avatar url"))
    role = models.CharField(choices=ROLE_CHOICES, default=ANALYST_ROLE)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'username' ]

    def __str__(self):
        return self.username
    
    def is_analyst(self):
        return self.role == self.ANALYST_ROLE
    
    def is_admin(self):
        return self.role == self.ADMIN_ROLE