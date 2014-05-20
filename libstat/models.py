# -*- coding: UTF-8 -*-
from mongoengine import *
from pip._vendor.pkg_resources import require

# Create your models here.

"""
     Enum for types
""" 
class Type(Document):
    type = StringField(max_length=100, primary_key=True)
    description = StringField(max_length=200)
    
    meta = {
        'collection': 'libstat_types'
    }
    
    def __unicode__(self):
        return self.type
    
"""
    Enum for dimensions
"""
class Term(Document):
    term = StringField(max_length=100, primary_key=True)
    description = StringField(max_length=200)
    
    meta =  {
        'collection': 'libstat_terms'
    }
    
    def __unicode__(self):
        return self.term
    
"""
    Enum for measurables
"""
class Measurable(Document):
    measurable = StringField(max_length=100, primary_key=True)
    description = StringField(max_length=200)
    
    meta =  {
        'collection': 'libstat_measurables'
    }
    
    def __unicode__(self):
        return self.measurable

"""
Variables
[
    {
        "id": "fpweijf+9u3+r9u3493+49u",
        "key": "folk18",
        "description": "Antal anställda bibliotekarier som är män",
        "is_public": True,
        "metadata": <VariableMetadata> {
            "dimensions": {                <--- dimensions as a DictField, sadly not editable in Mongonaut...
                "staffType": "Librarian",
                "gender": "Male"
            },
            "measurable": {                <--- measurable as a DictField, sadly not editable in Mongonaut...
                "name": "noOfEmployees",
                "range": "integer"
            }
        }
    },
    {
        "id": "sd0f98s0d9f80s9d8f0d9f9s",
        "key": "folk17",
        "description": "Antal anställda bibliotekarier som är kvinnor",
        "is_public": True,
        "metadata": <VariableMetadata> {
            "dimensions": [
                <EmbeddedDimension> {
                {
                    "dimension": <Term>"staffType",
                    "value": <Type>"Librarian"
                },
                <EmbeddedDimension> {
                    "dimension": <Term>"gender",
                    "value": <Type>"Female"
                }
            ],
            "measurable": noOfEmployees
            "range": "integer"
        }
    },
    {
        "id": "sd0f9s8df098sd0f9sydf86d5",
        "key": "folk15",
        "description": "Textkommentar övriga utlåningsställen",
        "is_public": False,
        "metadata": null
    },
]
"""
class EmbeddedDimension(EmbeddedDocument):
    dimension = StringField(max_length=50, required=True)
    value = StringField(max_length=50, required=True)

    def __unicode__(self):
        return "{}: {}".format(self.dimension, self.value)

class VariableMetadata(EmbeddedDocument):
    dimensions = ListField(EmbeddedDocumentField(EmbeddedDimension))
    measurable = StringField(max_length=50)
    range = StringField(max_length=50)

    def __unicode__(self):
        return "dimensions:{}, measurable:{}, range:{}".format(self.dimensions, self.measurable, self.range)

class Variable(Document):
    key = StringField(max_length=30, required=True, unique=True)
    # TODO: variable = StringField(max_length=50, primary_key=True) d v s "folk6" i s f id + key
    # TODO: aliases = ListField(StringField(max_length=50), required=True) innehåller "folk6"
    description = StringField(max_length=300)
    comment = StringField(max_length=200)
    is_public = BooleanField(required=True, default=True)

    metadata = EmbeddedDocumentField(VariableMetadata)

    meta = {
        'collection': 'libstat_variables'
    }

    def __unicode__(self):
        #return "key:{0}, description:{1}, comment:{2}".format(self.key, self.description, self.comment)
        return self.key

"""
SurveyResponse
{
    "id": "07sdf5df08sfg9s8g09sf9",
    "respondent": "Kls1",
    "refArea": "Karlstad",
    "sampleYear": 2013,
    "observations": [
        <SurveyObservation> {
            "variable": "fpweijf+9u3+r9u3493+49u",
            "value": "6",
            "_variable_key": "folk18",
            "_is_public": True,
            "_metadata": <VariableMetadata> {
                "dimensions": {
                    "staffType": "Librarian",
                    "sex": "Male"
                },
                "measurable": {
                    "name": "noOfEmployees",
                    "range": "integer"
                }
            }
        },
        <SurveyObservation> {
            "variable": "sd0f98s0d9f80s9d8f0d9f9s",
            "value": "23"
            "_variable_key": "folk17",
            "_is_public": True,
            "_metadata": <VariableMetadata> {
                "dimensions": {
                    "staffType": "Librarian",
                    "sex": "Female"
                }
                "measurable": {
                    "name": "noOfEmployees",
                    "range": "integer"
                }
            }
        },
        <SurveyObservation> {
            "variable": "sd0f9s8df098sd0f9sydf86d5",
            "value": "Boksnurror i köpcentret"
            "_variable_key": "folk15",
            "_is_public": False
            "_metadata": null
        }
    ]
}
"""
class SurveyObservation(EmbeddedDocument):
    variable = ReferenceField(Variable, required=True)
    value = DynamicField(required=True)

    _variable_key = StringField(max_length=30)
    _is_public = BooleanField(required=True, default=True)
    _metadata = EmbeddedDocumentField(VariableMetadata)

    def __unicode__(self):
        return "{0}: {1}".format(self.variable, self.value)

class SurveyResponse(Document):
    respondent = StringField(max_length=200, required=True) # TODO: Library id
    refArea = StringField(max_length=100, required=True)
    sampleYear = IntField(required=True)

    observations = ListField(EmbeddedDocumentField(SurveyObservation))

    meta = {
        'collection': 'libstat_survey_response'
    }

    def __unicode__(self):
        return "{0}: {1}".format(self.respondent, self.observations)
