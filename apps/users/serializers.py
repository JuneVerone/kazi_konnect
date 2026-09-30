from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, FreelancerProfile


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model  = CustomUser
        fields = [
            'id', 'email', 'full_name',
            'phone_number', 'role',
            'password', 'password2',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def validate_role(self, value):
        if value == CustomUser.Role.ADMIN:
            raise serializers.ValidationError('You cannot register as an admin.')
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been deactivated.')

        refresh = RefreshToken.for_user(user)
        return {
            'user':          user,
            'access_token':  str(refresh.access_token),
            'refresh_token': str(refresh),
        }


class FreelancerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FreelancerProfile
        fields = [
            'title', 'bio', 'skills',
            'hourly_rate', 'rating_avg',
            'jobs_completed', 'updated_at',
        ]
        read_only_fields = ['rating_avg', 'jobs_completed', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    freelancer_profile = FreelancerProfileSerializer(read_only=True)

    class Meta:
        model  = CustomUser
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'role', 'avatar', 'is_verified',
            'date_joined', 'freelancer_profile',
        ]
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user