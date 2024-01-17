from django import forms
from allauth.account.forms import LoginForm, SignupForm

CHOICE = [
    ("en", "EN"),
    ("uk", "UK")
]


class CustomUserCreationForm(SignupForm):
    account_img = forms.ImageField(required=False)


    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].label = ''
    

    def save(self, request):
        user = super(CustomUserCreationForm, self).save(request)
        if request.FILES:
            user.img = request.FILES['account_img']
        user.save()
        return user


class CustomUserLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserLoginForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].label = ''
        field = self.fields['remember']
        field.widget = field.hidden_widget()

class ChoiceLanguageForm(forms.Form):
    locale = forms.ChoiceField(label=False, choices=CHOICE, widget=forms.Select(attrs={'class':'form-control locale'}))