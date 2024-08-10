from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from accounts.serializers import *
from django.db import IntegrityError
from accounts.models import *
from accounts.renders import AccountAPI
from .utils import send_code_to_user, generateRole
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


# Create your views here.

class AllUser(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]

    queryset = User.objects.all()
    serializer_class = GetAllUserSerializer

    def get(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileView(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request):
        user = self.request.user
        pro = UserProfile.objects.filter(user=user)
        serializer = self.get_serializer(pro, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateUser(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]
    serializer_class = UserSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                send_code_to_user(user.email)

                if user.account_type == 'Lecturer' or user.account_type == 'lecturer':
                    L = 9
                    Lec = generateRole()
                    Lecturer = f'{L}{Lec}'
                    user.roles = Lecturer
                elif user.account_type == 'Student' or user.account_type == 'student':
                    L = 7
                    Lec = generateRole()
                    Lecturer = f'{L}{Lec}'
                    user.roles = Lecturer

                user.save()

                return Response({
                    'message':f'hi thanks for signing up a passcodde have been sent to you mail to verify your account.'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'message': 'A server error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyUserEmail(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]
    serializer_class = VerifyUserSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Account verified successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationCode(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]
    serializer_class = ResendVerificationCode
    def get_queryset(self):
        return User.objects.none()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Verification code sent to'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]
    serializer_class = LoginUserSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPassword(GenericAPIView):
    # renderer_classes = [JSONRenderer, AccountAPI]
    serializer_class = ResetPasswordSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'Check your mail a link has been sent to you to help rest your password'}, status=status.HTTP_200_OK)


class PasswordResetConfirm(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]
    def get(self, request, uidb64, token):
        try:
            user_id = urlsafe_base64_encode(uidb64)
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'mesage':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'user credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            return Response({'mesage':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)


class UpdatePassword(GenericAPIView):
    renderer_classes = [JSONRenderer, AccountAPI]
    serializer_class = UpdatePasswoedSerializer
    def patcht(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception = True)
        return Response({'message':'password updated successfully'}, status=status.HTTP_200_OK)
