import random
from django.core.mail import EmailMessage
from django.conf import settings
from .models import User, OneTimeCode

def generateOtp():
    otp = ''
    for i in range(5):
        otp += str(random.randint(1,9))
    return otp

def send_code_to_user(email):
    Subject = 'Email Verification'
    otp = generateOtp()
    user = User.objects.get(email=email)
    current_site = 'P-Detector'
    email_body = f'Good day {user.userName} thanks for signing up on {current_site} use this code {otp} to verify your account'
    from_email = settings.DEFAULT_FROM_EMAIL

    OneTimeCode.objects.create(user=user, code=otp)

    d_mail = EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
    d_mail.send(fail_silently=True)

def generateRole():
    role = ''

    for i in range(3):
        role += str(random.randint(1,9))
    return role

def send_normal_mail(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email = settings.DEFAULT_FROM_EMAIL,
        to=[data['to_email']]
    )
    email.send()

def resend_code(data):
    mail = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email = settings.DEFAULT_FROM_EMAIL,
        to=[data['to_email']]
    )
    mail.send()

