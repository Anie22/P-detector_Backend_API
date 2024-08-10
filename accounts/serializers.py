from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from accounts.models import *
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_mail, generateOtp, resend_code

class GetAllUserSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(max_length=120, read_only=True)
    lastName = serializers.CharField(max_length=120, read_only=True)
    userName = serializers.CharField(max_length=120, read_only=True)
    email = serializers.EmailField(max_length=60, read_only=True)
    account_type = serializers.CharField(max_length=50, read_only=True)
    roles = serializers.CharField(max_length=4, read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    is_lecturer = serializers.BooleanField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'userName', 'email', 'account_type', 'roles', 'date_joined', 'is_lecturer', 'is_verified', 'is_admin']


class UserProfileSerializer(serializers.ModelSerializer):
    pic = serializers.ImageField(read_only=True)
    user = GetAllUserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=30, min_length=8, write_only=True)
    password2 = serializers.CharField(max_length=30, min_length=8, write_only=True)
    roles = serializers.CharField(max_length=4, read_only=True)

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'userName', 'email', 'account_type', 'roles', 'password', 'password2']


    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        userName = attrs.get('userName', '')
        email = attrs.get('email', '')

        if password != password2:
            raise serializers.ValidationError('password does not match')

        if User.objects.filter(userName=userName).exists():
            raise serializers.ValidationError('This username is already taken')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already registered')

        return attrs


    def create(self, validated_data):
        user = User.objects.create_user(
            firstName = validated_data.get('firstName'),
            lastName = validated_data.get('lastName'),
            userName = validated_data.get('userName'),
            email = validated_data['email'],
            account_type = validated_data.get('account_type'),
            password = validated_data.get('password')
        )
        return user

class VerifyUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)
    code = serializers.CharField(max_length=5, min_length=5)

    class Meta:
        fields = ['email', 'code']

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist')

        try:
            otp = OneTimeCode.objects.get(user=user, code=code)
        except OneTimeCode.DoesNotExist:
            raise serializers.ValidationError('Invalid code or already use')

        if otp.is_expire():
            raise serializers.ValidationError('Code has expire')

        return attrs

    def save(self):
        validated_data = self.validated_data
        email = validated_data.get('email')
        code = validated_data.get('code')

        user = User.objects.get(email=email)
        otp = OneTimeCode.objects.get(user=user, code=code)

        otp.delete()

        user.is_verified = True
        user.save()

        return user


class ResendVerificationCode(serializers.Serializer):
    email = serializers.EmailField(max_length=50, min_length=20)
    verification_type = serializers.CharField(max_length=25, min_length=10)

    def validate(self, data):
        email = data.get('email')
        verification_type = data.get('verification_type')

        if verification_type != 'Email Verification':
            raise serializers.ValidationError('Wrong authentication type')

        user_exists = User.objects.filter(email=email).exists()

        if not user_exists:
            raise serializers.ValidationError('User does not exist')

        return data

    def save(self):
        try:
            email = self.validated_data.get('email')
            user = User.objects.get(email=email)
            otp_exists = OneTimeCode.objects.filter(user=user).exists()

            if otp_exists:
                user_otp = OneTimeCode.objects.get(user=user)
                user_otp.delete()

            otp = generateOtp()
            new_otp = OneTimeCode(user=user, code=otp)
            new_otp.save()

            email_data = {
                'email_subject': 'Email Verification',
                'email_body': f'Good day {user.userName}, use this code {otp} to verify your account',
                'to_email': user.email
            }
            resend_code(email_data)
            return email_data
        except Exception as e:
            raise serializers.ValidationError(f'Unable to send mail {str(e)}')



class LoginUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50, min_length=5)
    password = serializers.CharField(max_length=40, write_only=True)
    userName = serializers.CharField(max_length=50, read_only=True)
    roles = serializers.CharField(max_length=4, read_only=True)
    access_token = serializers.CharField(max_length=300, read_only=True)
    refresh_token = serializers.CharField(max_length=300, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'userName', 'roles', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')

        user = User.objects.filter(email=email).first()
        if not user:
            raise AuthenticationFailed('User does not exist')

        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed('wrong password')
        if not user.is_verified:
            raise AuthenticationFailed('User email is not verified')
        token=user.token()

        return {
            'email': user.email,
            'userName': user.userName,
            'roles': user.roles,
            'access_token':str(token.get('access')),
            'refresh_token':str(token.get('refresh'))
        }

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=50)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                user_name = user.userName
                id = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                request = self.context.get('request')
                site_domain = get_current_site(request).domain
                relative_link = reverse('password-reset-confirm', kwargs={'uidb64':id, 'token':token})
                abslink = f'https://{site_domain}{relative_link}'
                email_body = f'Hi {user_name} use this link below to reset your password \n {abslink}'
                data = {
                    'email_body': email_body,
                    'email_subject':'Reset your password',
                    'to_email':user.email
                }
                send_normal_mail(data)
            raise serializers.ValidationError('User not found')
        except Exception as e:
            raise serializers.ValidationError(f'Unable to send mail {str(e)}')

        return attrs

class UpdatePasswoedSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=30, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=30, min_length=8, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('reset link has expired or is invalid', 401)
            if password != confirm_password:
                raise AuthenticationFailed('password does not match')
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise AuthenticationFailed('reset link has expired or is invalid')
