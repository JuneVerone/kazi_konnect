from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FreelancerProfile


class FreelancerProfileInline(admin.StackedInline):
    model              = FreelancerProfile
    can_delete         = False
    verbose_name_plural = 'Freelancer profile'
    extra              = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines         = [FreelancerProfileInline]
    list_display    = ['email', 'full_name', 'role', 'is_verified', 'is_active', 'date_joined']
    list_filter     = ['role', 'is_verified', 'is_active']
    search_fields   = ['email', 'full_name', 'phone_number']
    ordering        = ['-date_joined']
    readonly_fields = ['id', 'date_joined', 'last_login']

    fieldsets = (
        (None,            {'fields': ('id', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number', 'avatar')}),
        ('Role & status', {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Timestamps',    {'fields': ('date_joined', 'last_login')}),
        ('Permissions',   {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'title', 'hourly_rate', 'rating_avg', 'jobs_completed']
    search_fields = ['user__email', 'user__full_name', 'title']
    