# -*- coding: UTF-8 -*-
from mongodbforms import DocumentForm
from libstat.fieldgenerator import FormFieldGenerator
from django import forms
from libstat.models import Variable, variable_types

#TODO: Define a LoginForm class with extra css-class 'form-control' ?

class VariableForm(DocumentForm):
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sub_category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Since this is a checkbox, a value will only be returned in form if the checkbox is checked. Hence the required=False.
    is_public = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'value':'1'}))
    
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    
    class Meta:
        model = Variable
        fields = ["category", "sub_category", "type", "is_public", "target_groups", "description", "comment"]
        formfield_generator = FormFieldGenerator(widget_overrides={'stringfield_choices': forms.RadioSelect})
