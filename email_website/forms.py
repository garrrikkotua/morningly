from django import forms


class SubscriptionForm(forms.Form):
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'placeholder': 'Ваш Email'}))
