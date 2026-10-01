from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import FreelancerProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    FreelancerProfileSerializer,
    ChangePasswordSerializer,
)