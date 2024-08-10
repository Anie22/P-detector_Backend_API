from django.urls import path
from accounts.views import *


urlpatterns = [
    path('', AllUser.as_view()),
    path('auth', CreateUser.as_view(), name='register'),
    path('auth/verify/', VerifyUserEmail.as_view(), name='verify'),
    path('auth/resend_code/', ResendVerificationCode.as_view(), name='resend_code'),
    path('auth/login/', Login.as_view(), name='login'),
    path('reset-password', ResetPassword.as_view(), name='reset-password'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('reset-password/set-new-password/', UpdatePassword.as_view(), name='set-new-password'),
    path('user-profile', UserProfileView.as_view())
]