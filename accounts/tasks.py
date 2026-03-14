from celery import shared_task

from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


@shared_task
def send_otp_mail(email, otp, expiry, name, reset_url):
   subject = "Your One Time Password!"
   message = (
      f"Dear {name}, \n\n"
      f"Please use your otp to reset your password.\n" 
      f"{otp}\n"
      f"This OTP is valid until {expiry}.\n"
      f"Validate your otp through the link {reset_url}\n\n"
      f"Best Regards,\n"
      f"FutsLab"
   )
   from_email = settings.EMAIL_HOST_USER
   recipient_list = [email]

   try:
      send_mail(subject, message, from_email, recipient_list, fail_silently=False)
      return f"OTP sent to {email} successfully."
   except BadHeaderError:
      return f"Invalid header found while sending OTP to {email}."
   except Exception as e:
      return f"Failed to send OTP to {email}. Error: {str(e)}"


@shared_task
def send_manager_invitation_mail(email, name, registration_link):
   subject = "You are invited as a Manager."
   message = (
      f"Dear {name}, \n\n"
      f"FutsLab invites you to become a part of the team as a Manager.\n"
      f"As a manager, you will have the permissions to manage games, players and the respective teams.\n"
      f"Register yourself from the given link below:\n"
      f"{registration_link}\n\n"
      f"Best Regards,\n"
      f"FutsLab"
   )
   from_email = settings.EMAIL_HOST_USER
   recipient_list = [email]

   try:
      send_mail(subject, message, from_email, recipient_list, fail_silently=False)
      print("Sending Mail")
      return "Invitation Link sent successfully."
   except BadHeaderError:
      return f"Invalid header found while sending the invitation."
   except Exception as e:
      return f"Failed to send invitation to {email}."