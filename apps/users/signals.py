from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, FreelancerProfile


@receiver(post_save, sender=CustomUser)
def create_freelancer_profile(sender, instance, created, **kwargs):
    if created and instance.role == CustomUser.Role.FREELANCER:
        FreelancerProfile.objects.create(user=instance)
        
        