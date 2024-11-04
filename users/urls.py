from unicodedata import name
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (TokenRefreshView,)
   

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    

    path('new-users-today/', new_users_daily_registrations, name='new_users_today'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('users/<int:user_id>/', get_user_by_id, name='get-user-by-id'),
    path('users/', list_users, name='list-users'),
    path('profile/', getUserProfile, name= 'users-profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('get-something/', TestingAuthenticatedReq.as_view(), name='just-for-testing'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('active-users/', active_users, name='active-users'),
    path('api/user-count/', user_count, name='user_count'),
    ]