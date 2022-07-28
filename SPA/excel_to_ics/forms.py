from django import forms
from .models import Upload

class UploadForm(forms.ModelForm):
    target_year = forms.IntegerField()
    target_month = forms.IntegerField()
    class Meta:
        model = Upload
        fields = ('target_year', 'target_month', 'excel')