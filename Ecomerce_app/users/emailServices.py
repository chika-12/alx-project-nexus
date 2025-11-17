from django.core.mail import send_mail
def emailService(subject, message, from_email, recipient_list, fail_silently=False):
  try:
       
    send_mail(
      subject=subject,
      message=message,
      from_email=from_email,
      recipient_list=recipient_list,
      fail_silently=fail_silently
    )
  except Exception as e:
    print("Cant send Email")
