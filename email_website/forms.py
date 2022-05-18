from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from django.core.exceptions import ValidationError
from datetime import datetime
import time


class SubscriptionForm(forms.Form):
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))


class PrepareForSendingForm(forms.Form):
    sending_date = forms.DateField(label='Date of sending', widget=AdminDateWidget(attrs={'id': 'id_sending_date'}))
    sending_time = forms.TimeField(label='Time of sending', widget=AdminTimeWidget(attrs={'id': 'id_sending_time'}))
    right_now = forms.BooleanField(label='Send right now', required=False, initial=False)

    def clean(self):
        cleaned_data = super().clean()
        t = cleaned_data.get("sending_time")
        date = cleaned_data.get("sending_date")
        right_now = cleaned_data.get("right_now")
        if not right_now:
            dt = datetime.combine(date, t)
            if dt <= datetime.now():
                raise ValidationError(
                    'Select data and time in the future'
                )

