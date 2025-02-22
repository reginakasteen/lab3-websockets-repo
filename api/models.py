from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

GENDER = {
    'Male': 'M',
    'Female': 'F'
}


class User(AbstractUser):
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gender = models.CharField(choices=GENDER, max_length=10)
    date_of_birth = models.DateField(null=True)
    bio = models.CharField(max_length=500)
    photo = models.ImageField(default="default_image.png", upload_to="user_images")
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_profile, sender=User)
post_save.connect(save_profile, sender=User)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, null=False)
    completed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:30]
    
class Message(models.Model):
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.sender} - {self.receiver} - {self.message[:20]} - {self.date}"


    @property
    def sender_profile(self):
        sender_profile = Profile.objects.get(user=self.sender)
        return sender_profile

    @property
    def receiver_profile(self):
        receiver_profile = Profile.objects.get(user=self.receiver)
        return receiver_profile 
        