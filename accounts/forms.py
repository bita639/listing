from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    phone_number = forms.CharField(
        label='Phone Number', widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    address = forms.CharField(
        label='Address', widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    about = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 3, 'cols': 40, 'placeholder': 'About'}), required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number',
                  'address', 'about', 'password1', 'password2', )
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'User Name'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email', 'type': 'email'}),
            # 'description': forms.Textarea(
            #     attrs={'placeholder': 'Enter description here'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

        self.fields['password1'].widget = forms.PasswordInput(
            attrs={'placeholder': "Password"})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={'placeholder': "Confirm Password"})

        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone_number'].required = True
        self.fields['address'].required = True


class UpdateProfile(ModelForm):
    phone_number = forms.CharField()
    address = forms.CharField()
    about = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 3, 'cols': 40}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'phone_number', 'address', 'about',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        user = self.request.user
        super(UpdateProfile, self).__init__(*args, **kwargs)

        self.fields['phone_number'].initial = user.user_profile.phone_number
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['about'].initial = user.user_profile.about
        self.fields['address'].initial = user.user_profile.address
