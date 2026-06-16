import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        CLIENT     = 'CLIENT',     'Client'
        FREELANCER = 'FREELANCER', 'Freelancer'
        ADMIN      = 'ADMIN',      'Admin'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email        = models.EmailField(unique=True, db_index=True)
    full_name    = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15, blank=True)
    role         = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT, db_index=True)
    avatar       = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified  = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    date_joined  = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        ordering            = ['-date_joined']

    def __str__(self):
        return f'{self.full_name} ({self.email})'

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_freelancer(self):
        return self.role == self.Role.FREELANCER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN


class FreelancerProfile(models.Model):

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user           = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='freelancer_profile')
    title          = models.CharField(max_length=120, blank=True)
    bio            = models.TextField(blank=True)
    skills         = models.JSONField(default=list, blank=True)
    hourly_rate    = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    rating_avg     = models.FloatField(default=0.0)
    jobs_completed = models.IntegerField(default=0)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Freelancer profile'

    def __str__(self):
        return f'Profile — {self.user.full_name}'