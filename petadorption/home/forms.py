from django import forms
from .models import Usert

class UserUpdateForm(forms.ModelForm):
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',  # optional for Bootstrap styling
        }),
        required=False  # match your model's `null=True, blank=True`
    )
    class Meta:
        model = Usert
        fields = [ 'email', 'first_name', 'last_name','dob','phone_number','address','profile_picture']
class EmailForm(forms.Form):
    email = forms.EmailField()

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)