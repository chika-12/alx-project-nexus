def get_upgrade_email_content(user):
    return {
        "subject": "🎉 Congratulations on Your Upgrade!",
        "message": f"""
Hi {user.first_name},

Congratulations! Your account has been successfully upgraded.

You now have access to all premium features.

Best regards,
The ALXEcommerce Team
""",
        "from_email": "no-reply@alxecommerce.com",
        "recipient_list": [user.email],
        "fail_silently": False
    }
