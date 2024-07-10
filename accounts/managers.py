from typing import Any
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("please enter a valid email address"))

    def create_user(self, firstName, lastName, userName, account_type, email, password, **extra_fields):
        if not firstName:
            raise ValueError(_("first name required"))

        if not lastName:
            raise ValueError(_("last name required"))

        if not userName:
            raise ValueError(_("user name required"))

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("email address is required"))

        if not account_type and account_type != 'Lecturer' or account_type != 'lecturer':
            extra_fields.setdefault('is_lecturer', False)
        else:
            extra_fields.setdefault('is_lecturer', True)

        user = self.model(
            firstName = firstName,
            lastName = lastName,
            userName = userName,
            account_type = account_type,
            email = email,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, firstName, lastName, userName, account_type, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if not password:
            raise ValueError(_('password required'))

        user = self.create_user(
            firstName = firstName,
            lastName = lastName,
            userName = userName,
            account_type = account_type,
            email = email,
            password = password,
            **extra_fields
        )

        user.save(using=self._db)

        return user