from django.core.mail import EmailMessage
from django.conf import settings

def send_assignment_notification(assignment):
    email = EmailMessage(
        subject=assignment['email_subject'],
        body=assignment['email_body'],
        from_email = settings.DEFAULT_FROM_EMAIL,
        to=[assignment['to_email']]
    )
    email.send()