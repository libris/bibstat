from django import forms
from libstat.models import Variable
from libstat.utils import VARIABLE_TYPES, SURVEY_TARGET_GROUPS

__author__ = 'vlovgr'


class VariableForm(forms.Form):
    active_from = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    active_to = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    question = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    question_part = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sub_category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    type = forms.ChoiceField(required=True, widget=forms.RadioSelect())

    # Since this is a checkbox, a value will only be returned in form if the
    # checkbox is checked. Hence the required=False.
    is_public = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'value': '1'}))

    target_groups = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple())

    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))

    replaces = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(VariableForm, self).__init__(*args, **kwargs)
        if not self.instance:
            self.fields['key'] = forms.CharField(required=True,
                                                 widget=forms.TextInput(attrs={'class': 'form-control'}))

        self.fields['type'].choices = [type for type in VARIABLE_TYPES]
        self.fields['target_groups'].choices = [target_group for target_group in SURVEY_TARGET_GROUPS]

        if self.instance:
            self.fields['active_from'].initial = (self.instance.active_from.date()
                                                  if self.instance.active_from
                                                  else None)
            self.fields['active_to'].initial = self.instance.active_to.date() if self.instance.active_to else None
            self.fields['question'].initial = self.instance.question
            self.fields['question_part'].initial = self.instance.question_part
            self.fields['category'].initial = self.instance.category
            self.fields['sub_category'].initial = self.instance.sub_category
            self.fields['type'].initial = self.instance.type
            self.fields['is_public'].initial = self.instance.is_public
            self.fields['target_groups'].initial = self.instance.target_groups
            self.fields['description'].initial = self.instance.description
            self.fields['comment'].initial = self.instance.comment
            self.fields['replaces'].initial = ", ".join(
                [str(v.id) for v in self.instance.replaces]) if self.instance.replaces else ""
            self.replaces_initial_value = ", ".join(
                ["{}:{}".format(v.key, str(v.id)) for v in self.instance.replaces] if self.instance.replaces else [])

    def clean(self):
        cleaned_data = super(VariableForm, self).clean()

        replaces = cleaned_data['replaces'] if 'replaces' in cleaned_data else None
        active_from = cleaned_data['active_from'] if 'active_from' in cleaned_data else None
        if replaces and not active_from:
            self._errors['replaces'] = self.error_class(
                ["Ange när ersättning börjar gälla genom att sätta 'Giltig fr o m'"])
            self._errors['active_from'] = self.error_class(["Måste anges"])

            del cleaned_data['replaces']
            del cleaned_data['active_from']

        active_to = cleaned_data['active_to'] if 'active_to' in cleaned_data else None
        if (self.instance and self.instance.replaced_by and active_to and self.instance.active_to
                and active_to != self.instance.active_to.date()):
            self._errors['active_to'] = self.error_class(["Styrs av ersättande term"])
            del cleaned_data['active_to']
        return cleaned_data

    def save(self, commit=True, user=None, activate=False):
        variable = self.instance if self.instance else Variable(is_draft=True)
        variable.key = self.instance.key if self.instance else self.cleaned_data['key']
        variable.active_from = self.cleaned_data[
            'active_from']  # Need to convert to UTC? It's a date and not a datetime...
        variable.active_to = self.instance.active_to if self.instance and self.instance.replaced_by else \
            self.cleaned_data['active_to']
        variable.question = self.cleaned_data['question']
        variable.question_part = self.cleaned_data['question_part']
        variable.category = self.cleaned_data['category']
        variable.sub_category = self.cleaned_data['sub_category']
        variable.type = self.cleaned_data['type']
        variable.is_public = self.cleaned_data['is_public']
        variable.target_groups = self.cleaned_data['target_groups']
        variable.description = self.cleaned_data['description']
        variable.comment = self.cleaned_data['comment']
        if activate:
            variable.is_draft = False

        to_replace = self.cleaned_data['replaces'].split(", ") if self.cleaned_data['replaces'] else []
        modified_siblings = variable.replace_siblings(to_replace, switchover_date=variable.active_from)

        if commit:
            variable.save_updated_self_and_modified_replaced(modified_siblings)

        return variable
