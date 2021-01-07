from django import forms
from .models import Submit,Learn
from django.utils import timezone
class SubmitForm(forms.ModelForm):
    class Meta:
        model = Submit
        fields = [
            'comment',
        ]
class LearnForm(forms.ModelForm):
    class Meta:
        model = Learn
        fields = [
            'lcmt',
            'tag',
        ]

class SelectForm(forms.Form):
    listchoice = [('1','LSTM'),('2','BiLSTM'),('3','GRU')]
    selectlist = forms.ChoiceField(choices=listchoice)

class RadioForm(forms.Form):
    radiochoices = ["Tất cả","Dưới 2 Triệu","Từ 2 - 5 Triệu","Từ 5 - 10 Triệu","Trên 10 Triệu"]
    radiofields = forms.RadioSelect(choices=radiochoices)