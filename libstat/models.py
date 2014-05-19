from mongoengine import *

# Create your models here.

class Variable(Document):
    key = StringField(max_length=30)
    comment = StringField(max_length=200)

    meta = {
        'collection': 'libstat_variables'
    }
