from allauth.account import app_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation
from allauth.account.utils import user_email
from django.conf import settings
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        ctx = {
            "user": emailconfirmation.email_address.user,
        }
        if app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            print("===========================")
            ctx.update({"code": emailconfirmation.key}) 
        else:
            print("--------------------------")
            ctx.update(
                {
                    "key": emailconfirmation.key,
                    "activate_url": self.get_email_confirmation_url( 
                        request, emailconfirmation
                    ),
                }
            ) 
        if signup:
            email_template = "account/email/email_confirmation_signup" 
        else:
            email_template = "account/email/email_confirmation"
            
        print(email_template)
        print("emailconfirmation.email_address.email =====> ", emailconfirmation.email_address.email)
        print(ctx)
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)

    def get_email_confirmation_url(self, request, emailconfirmation):
        custom_domain = "http://54.221.153.85:8000/"
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        return f"{custom_domain}{url}"   
