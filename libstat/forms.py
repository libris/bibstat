from mongodbforms import DocumentForm
from django import forms
from libstat.models import Variable, variable_types

class VariableForm(DocumentForm):
    category = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    sub_category = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Skipping use of form widgets for type, is_public and target_groups
    
    
    class Meta:
        model = Variable
        fields = ["category", "sub_category", "type", "is_public", "target_groups", "description", "comment"]
