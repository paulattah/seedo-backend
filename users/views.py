from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import OneTimePassword
from .serializers import PasswordResetRequestSerializer,LogoutUserSerializer, UserRegisterSerializer, LoginSerializer, SetNewPasswordSerializer,UserProfileSerializer
from rest_framework import status
from .utils import send_generated_otp_to_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated
from .models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import UserRegistration
from .serializers import UserSerializer
from django.utils.timezone import now, timedelta
from django.db.models import Count
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import logging


# Create your views here.




@api_view(['GET', 'PUT'])
@parser_classes([MultiPartParser, FormParser])
def getUserProfile(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




logger = logging.getLogger('accounts')

class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()
            user_registration = UserRegistration.objects.create(user=new_user)
            logger.info(f"User registration created: {user_registration}")
            user_data = serializer.data
            #send_generated_otp_to_email(user_data['email'], request)
            # Optionally send OTP to user's email
            # send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'data': user_data,
                'message': 'Thanks for signing up! A passcode has been sent to verify your email.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_pass_obj=OneTimePassword.objects.get(otp=passcode)
            user=user_pass_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({'message':'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

'''
class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        # return Response({'message':'user with that email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
'''  
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PasswordResetRequestSerializer

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response({"detail": "Password reset link has been sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PasswordResetRequestSerializer

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response({"detail": "Password reset link has been sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirm(GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)


class TestingAuthenticatedReq(GenericAPIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):

        data={
            'msg':'its works'
        }
        return Response(data, status=status.HTTP_200_OK)

class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
@api_view(['GET'])
def user_count(request):
    if request.method == 'GET':
        user_count = User.objects.count()
        return Response({'count': user_count})
    

from .models import UserActivity, User

@api_view(['GET'])
def active_users(request):
    # Track user login activity
    UserActivity.objects.create(user=request.user)

    # Get total number of users
    total_users = User.objects.count()

    # Calculate Daily Active Users (DAU)
    today = timezone.now().date()
    daily_active_users_count = UserActivity.objects.filter(login_time__date=today).values('user_id').distinct().count()
    daily_active_users_percentage = (daily_active_users_count / total_users) * 100 if total_users != 0 else 0

    # Calculate Monthly Active Users (MAU)
    start_of_month = timezone.now().replace(day=1)
    monthly_active_users_count = UserActivity.objects.filter(login_time__gte=start_of_month).values('user_id').distinct().count()
    monthly_active_users_percentage = (monthly_active_users_count / total_users) * 100 if total_users != 0 else 0

    return Response({
        'daily_active_users_percentage': daily_active_users_percentage,
        'monthly_active_users_percentage': monthly_active_users_percentage
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

import logging

logger = logging.getLogger('accounts')

from django.core.cache import cache

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def new_users_daily_registrations(request):
    # Check if the cached result exists
    cached_data = cache.get('new_users_today')
    if cached_data:
        return Response(cached_data)

    # Calculate the count of new user registrations for today
    today = timezone.now().date()
    new_users_count_today = UserRegistration.objects.filter(registration_time__date=today).count()

    # Cache the result for future requests
    cache.set('new_users_today', {'new_users_today': new_users_count_today}, timeout=60)  # Cache for 60 seconds

    logger.info(f"New users registered today: {new_users_count_today}")
    return Response({'new_users_today': new_users_count_today}, status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Optionally make it accessible only to authenticated users
def get_user_by_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(user)
    return Response(serializer.data)


