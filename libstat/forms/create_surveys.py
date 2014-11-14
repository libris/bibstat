# coding=utf-8
from django import forms
from libstat.models import LibrarySelection, Library
from libstat.utils import targetGroups

__author__ = 'vlovgr'


class CreateSurveysForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CreateSurveysForm, self).__init__(*args, **kwargs)

        self.fields["sample_year"] = forms.ChoiceField(
            choices=[(2014, 2014)],
            widget=forms.Select(attrs={"class": "form-control"}))

        lib_selection, _ = LibrarySelection.objects.get_or_create(name="lib_selection")

        self.libraries = []
        for library in Library.objects.all():
            checkbox_id = str(library.pk)
            attrs = {"value": checkbox_id,
                     "class": "select-one"
                     }
            if library.sigel in lib_selection.sigels:
                attrs["checked"] = ""
            self.fields[checkbox_id] = forms.BooleanField(required=False,
                                                          widget=forms.CheckboxInput(attrs=attrs))
            self.libraries.append({
                "name": library.name,
                "city": library.city,
                "address": library.address,
                "email": library.email,
                "sigel": library.sigel,
                "library_type": targetGroups[library.library_type] if library.library_type else "",
                "checkbox_id": checkbox_id
            })