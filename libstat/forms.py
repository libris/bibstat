# -*- coding: UTF-8 -*-
from mongodbforms import DocumentForm, EmbeddedDocumentForm
from libstat.fieldgenerator import FormFieldGenerator

import math
from collections import OrderedDict
from django import forms
from django.utils.safestring import mark_safe


from libstat.models import Variable, variable_types, SurveyResponse, SurveyObservation, SURVEY_TARGET_GROUPS, SurveyResponseMetadata
from libstat.models import TYPE_STRING , TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG, TYPE_DECIMAL, TYPE_PERCENT 
from django.core.exceptions import ValidationError

#TODO: Define a LoginForm class with extra css-class 'form-control' ?

class VariableForm(DocumentForm):
    question = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    question_part = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sub_category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Since this is a checkbox, a value will only be returned in form if the checkbox is checked. Hence the required=False.
    is_public = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'value':'1'}))
    
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    
    class Meta:
        model = Variable
        fields = ["question", "question_part", "category", "sub_category", "type", "is_public", "target_groups", "description", "comment"]
        formfield_generator = FormFieldGenerator(widget_overrides={'stringfield_choices': forms.RadioSelect})

class SurveyResponseForm(forms.Form):
    """
        Custom form for creating/editing a SurveyResponse with all embedded documents.
    """
    sample_year = forms.CharField(required=True, max_length=4, widget=forms.HiddenInput) #TODO: Remove or make hidden
    target_group = forms.CharField(required=True, widget=forms.HiddenInput) # TODO: Remove or make hidden
    
    library_name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    municipality_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    municipality_code = forms.CharField(required=False, max_length=6, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '6'}))
    
    respondent_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    respondent_email = forms.EmailField(required=False, max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    respondent_phone = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '20'}))
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        
        sample_year = kwargs.pop('sample_year', None)
        target_group = kwargs.pop('target_group', None)
        library_name = kwargs.pop('library_name', None)
        
        super(SurveyResponseForm, self).__init__(*args, **kwargs)
        
        self.fields['target_group'].choices = [target_group for target_group in SURVEY_TARGET_GROUPS]
        
        if self.instance:
            self.fields['sample_year'].initial = self.instance.sample_year
            self.fields['target_group'].initial = self.instance.target_group
            self.fields['library_name'].initial = self.instance.library_name
            self.fields['municipality_name'].initial = self.instance.metadata.municipality_name if self.instance.metadata else None
            self.fields['municipality_code'].initial = self.instance.metadata.municipality_code if self.instance.metadata else None
            self.fields['respondent_name'].initial = self.instance.metadata.respondent_name if self.instance.metadata else None
            self.fields['respondent_email'].initial = self.instance.metadata.respondent_email if self.instance.metadata else None
            self.fields['respondent_phone'].initial = self.instance.metadata.respondent_phone if self.instance.metadata else None
        else:
            self.fields['sample_year'] = sample_year
            self.fields['target_group'] = target_group
            self.fields['library_name'] = library_name
            
            
    def save(self, commit=True, user=None):
      surveyResponse = self.instance if self.instance else SurveyResponse()
      surveyResponse.library_name = self.cleaned_data['library_name']
      surveyResponse.sample_year = self.instance.sample_year if self.instance else self.cleaned_data['sample_year']
      surveyResponse.target_group = self.instance.target_group if self.instance else self.cleaned_data['target_group']
      
      surveyResponse.metadata = self.instance.metadata if self.instance.metadata and (self.cleaned_data['municipality_name'] or self.cleaned_data['municipality_code']) else SurveyResponseMetadata()
      surveyResponse.metadata.municipality_name = self.cleaned_data['municipality_name']
      surveyResponse.metadata.municipality_code = self.cleaned_data['municipality_code']
      surveyResponse.metadata.respondent_name = self.cleaned_data['respondent_name']
      surveyResponse.metadata.respondent_email = self.cleaned_data['respondent_email']
      surveyResponse.metadata.respondent_phone = self.cleaned_data['respondent_phone']
      
      surveyResponse.modified_by = user
      
      if commit:
          surveyResponse.save()

      return surveyResponse

class SurveyObservationsForm(forms.Form):
    """
        Custom form to edit all SurveyObservations for a SurveyResponse with one form
    """
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(SurveyObservationsForm, self).__init__(*args, **kwargs)
        self.fields = OrderedDict()
        
        if self.instance:
            for index, observation in enumerate(self.instance.observations):
                if isinstance(observation.variable.label, list):
                    label = mark_safe(u"<div class='survey-question-order'><span class='survey-index'>{}.</span> <span class='term-key'>{}</span></div><div class='survey-question'>{}</div><div class='survey-question-part'>{}</div>".format(
                                      index+1, observation.variable.key, observation.variable.label[0], observation.variable.label[1]))
                else:    
                    label = mark_safe(u"<div class='survey-question-order'><span class='survey-index'>{}.</span> <span class='term-key'>{}</span></div><div class='survey-question'>{}</div>".format(
                                      index+1, observation.variable.key, observation.variable.label))
                    
                if observation.variable.type == TYPE_BOOLEAN[0]:
                    self.fields[observation._source_key] = forms.ChoiceField(required = False,
                                                                             widget = forms.RadioSelect(),
                                                                             choices = [(True, u"Ja"), (False, u"Nej")],
                                                                             label = label,
                                                                             initial = observation.value)
                elif observation.variable.type == TYPE_INTEGER[0]:
                    self.fields[observation._source_key] = forms.IntegerField(required = False, 
                                                                              widget = forms.NumberInput(attrs={'class': 'form-control width-auto'}),
                                                                              min_value = 0,
                                                                              label = label, 
                                                                              initial = int(round(observation.value)) if observation.value and isinstance(observation.value, (int, long, float)) else None)
                elif observation.variable.type == TYPE_LONG[0]:
                    self.fields[observation._source_key] = forms.IntegerField(required = False, 
                                                                              widget = forms.NumberInput(attrs={'class': 'form-control width-auto'}),
                                                                              label = label,
                                                                              min_value = 0, 
                                                                              initial = long(round(observation.value)) if observation.value and isinstance(observation.value, (int, long, float)) else None)
                elif observation.variable.type == TYPE_DECIMAL[0]:
                    self.fields[observation._source_key] = forms.DecimalField(required = False, 
                                                                              widget = forms.NumberInput(attrs={'class': 'form-control width-auto'}),
                                                                              label = label, 
                                                                              decimal_places = 2,
                                                                              initial = round(observation.value, 2) if observation.value and isinstance(observation.value, (int, long, float)) else None)
                elif observation.variable.type == TYPE_PERCENT[0]:
                    self.fields[observation._source_key] = forms.IntegerField(required = False, 
                                                                              widget = forms.NumberInput(attrs={'class': 'form-control width-auto'}),
                                                                              label = label, 
                                                                              initial = int(round(observation.value*100)) if observation.value and isinstance(observation.value, (int, long, float)) else None)
                else:
                    self.fields[observation._source_key] = forms.CharField(required = False, 
                                                                           widget = forms.TextInput(attrs={'class': 'form-control'}), 
                                                                           label = label, 
                                                                           initial = observation.value)
    def save(self, commit=True, user=None):
        if not self.instance:
            raise ValidationError(_(u"Enkätsvar finns inte, kan inte uppdatera"), code=u"missing_instance")
        
        surveyResponse = self.instance
        for observation in surveyResponse.observations:
            value = self.cleaned_data[observation._source_key]
            
            if observation.variable.type == TYPE_BOOLEAN[0]:
                if value and value == "True" or value == True:
                    observation.value = True
                elif value and value == "False" or value == False:
                    observation.value = False
                else:
                    observation.value = None
            elif observation.variable.type == TYPE_LONG[0]:
                observation.value = long(value) if value else None
            elif observation.variable.type == TYPE_DECIMAL[0]:
                observation.value = float(value) if value else None
            elif observation.variable.type == TYPE_PERCENT[0]:
                observation.value = float(value)/100 if value else None
            else:
                observation.value = value
        
        surveyResponse.modified_by = user
        
        if commit:
            surveyResponse.save()

        return surveyResponse