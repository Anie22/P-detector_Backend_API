from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

class User(AbstractBaseUser, PermissionsMixin):
    firstName = models.CharField(verbose_name='First Name', max_length=120, unique=False)
    lastName = models.CharField(verbose_name='Last Name', max_length=120, unique=False)
    userName = models.CharField(verbose_name='User Name', max_length=120, unique=True)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    account_type = models.CharField(verbose_name='Account Type', max_length=50, unique=False, null=True, blank=True)
    roles = models.CharField(verbose_name='role', max_length=4)
    date_joined = models.DateTimeField(verbose_name='Joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='Last login', auto_now=True)
    is_lecturer = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS=['firstName', 'lastName', 'userName', 'account_type']

    NON_REQUIRED_FIELDS=['account_type', 'roles']

    objects = UserManager()

    def __str__(self):
        return f"{self.firstName} {self.lastName}"

    def get_full_name(self):
        return f'{self.firstName} {self.lastName}'

    def token(self):
        refresh=RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

class OneTimeCode(models.Model):
    code = models.CharField(max_length=5, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.firstName}.passcode'

    def is_expire(self):
        return (timezone.now() - self.created_at).total_seconds() > 200

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(upload_to='photo', blank=True, null=True, default='user.png')

    def __str__(self):
        return f'{self.user.firstName} {self.user.lastName}'

