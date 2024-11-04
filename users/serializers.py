
import json
from dataclasses import field
from .models import User
from rest_framework import serializers
from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.urls import reverse
from .utils import send_mail
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.mail import EmailMessage


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    #password2= serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields = ['email', 'first_name', 'last_name', 'password']
        
  
    def create(self, validated_data):
        user= User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password')
            )
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    full_name=serializers.CharField(max_length=255, read_only=True)
    access_token=serializers.CharField(max_length=255, read_only=True)
    refresh_token=serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['id','email', 'password','is_staff', 'full_name', 'access_token', 'refresh_token']

    

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request=self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("invalid credential try again")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        tokens=user.tokens()
        return {
            'id':user.id,
            'email':user.email,
            'is_staff':user.is_staff,
            'full_name':user.get_full_name,
            "access_token":str(tokens.get('access')),
            "refresh_token":str(tokens.get('refresh'))
        }




class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            
            # Use the frontend URL
            frontend_url = settings.FRONTEND_URL
            #relative_link = reverse('reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
            abslink = f"{frontend_url}/reset-password/{uidb64}/{token}"
            
            email_body = f"Hi {user.first_name}, use the link below to reset your password:\n{abslink}"
            data = {
                'email_body': email_body,
                'email_subject': "Reset your Password",
                'to_email': user.email
            }
            self.send_mail(data)
        return super().validate(attrs)

    def send_mail(self, data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()




class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64=serializers.CharField(min_length=1, write_only=True)
    token=serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token=attrs.get('token')
            uidb64=attrs.get('uidb64')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')

            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")


    
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')
        




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',  'email', 'first_name', 'last_name', 'location', 'date_joined', 'image']


        
class UserProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'bio', 'location', 'date_joined', 'image']
        read_only_fields = ['email', 'date_joined']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)
        instance.image = validated_data.get('image', instance.image)
        #instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        
        instance.save()

        return instance