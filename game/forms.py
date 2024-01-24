from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class UserIncreaseStatsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agility'] = forms.IntegerField(
            required=True,
            label=_("Спритність"),
            widget=forms.NumberInput(
            attrs={"min": self.instance.agility, 
                    "class": "ag",
                    "readonly": "readonly",
                    "value": self.instance.agility,
                    "placeholder": _("Спритність")})
            )
        self.fields['strength'] = forms.IntegerField(required=True,
                    label=_("Сила"),
                    widget=forms.NumberInput(
                    attrs={"min": self.instance.strength, "class": "str", 
                        "readonly": "readonly",
                        "value": self.instance.strength, "placeholder": _("Сила")}))
        self.fields['upgrade_points'] = forms.IntegerField(
                    required=True,
                    widget=forms.HiddenInput(
                        attrs={"value": self.instance.upgrade_points}))

    class Meta:
        model = get_user_model()
        fields = ['agility', 'strength', 'upgrade_points']
        