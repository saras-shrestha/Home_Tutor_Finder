from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            ('student', 'Student'),
            ('tutor', 'Tutor'),
        ],
        widget=forms.Select()
    )
    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2',
        ]

    # def __init__(self, *args, **kwargs):

    #     super().__init__(*args, **kwargs)

    #     self.fields['role'].choices = [
    #         ('student', 'Student'),
    #         ('tutor', 'Tutor'),
    #     ]

    #     self.fields['username'].widget.attrs.update({
    #         'placeholder': 'Enter username'
    #     })

    #     self.fields['email'].widget.attrs.update({
    #         'placeholder': 'Enter email address'
    #     })

    #     self.fields['password1'].widget.attrs.update({
    #         'placeholder': 'Create a password'
    #     })

    #     self.fields['password2'].widget.attrs.update({
    #         'placeholder': 'Confirm your password'
    #     })