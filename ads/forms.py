from django import forms
from .models import Ad, ExchangeProposal
from django.contrib.auth.models import User

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image', 'category', 'condition']


class ExchangeProposalForm(forms.ModelForm):
    ad_sender = forms.ModelChoiceField(
        queryset=Ad.objects.none(),
        label="Ваше объявление"
    )

    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Если передали user, фильтруем объявления по нему
        if user:
            self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # если у пользователя нет first_name, ставим initial=username 
        # и захардкодим value в атрибут виджета
        if self.instance and not self.instance.first_name:
            username = self.instance.username
            self.fields['first_name'].initial = username
            self.fields['first_name'].widget.attrs['value'] = username
