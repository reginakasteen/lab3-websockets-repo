from api.models import User, Profile, Task, Message
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'name', 'gender', 'date_of_birth', 'is_online']

class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.profile.name
        token['gender'] = user.profile.gender
        token['username'] = user.username
        token['email'] = user.email
        token['date_of_birth'] = user.profile.date_of_birth
        token['is_online'] = user.profile.is_online
        token['bio'] = user.profile.bio
        token['photo'] = str(user.profile.photo)

        return token
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']

    def validate(self, attrs):
        if attrs:
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError(
                    {"password": "Passwords do not match"}
                )
            return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            # date_of_birth=validated_data['date_of_birth'],
            # gender=validated_data['gender']
            )
        user.set_password(validated_data['password'])
        user.save()

        return user


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user', 'title', 'completed']


class MessageSerializer(serializers.ModelSerializer):
    receiver_profile = ProfileSerializer(read_only=True)
    sender_profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'sender', 'receiver', 'sender_profile', 'receiver_profile', 'message', 'date', 'is_read']    



    