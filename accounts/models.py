# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        (1, 'Admin'),
        (2, 'Manager'),
        (3, 'Waiter'),
        (4, 'Cashier'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role_id = models.IntegerField(choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_users'
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_id_display()}"
    
    class Meta:
        db_table = 'user_profile'
        ordering = ['-created_at']


# Signal to automatically create profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when User is created
    Only if profile doesn't exist
    """
    if created and not hasattr(instance, 'profile'):
        # Default role_id for new users (can be updated later)
        UserProfile.objects.create(user=instance, role_id=3)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save UserProfile whenever User is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

        