from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset token for {self.user.username}"
    
class Profile(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(blank=True, null=True,upload_to="images/")
    mobile = PhoneNumberField(null =False,blank=False)
    address = models.CharField(max_length = 20)
    block = models.CharField(max_length =20)
    room = models.CharField(max_length = 10)
    
    def __str__(self):
        return f'{self.customer}'
