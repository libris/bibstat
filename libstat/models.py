from mongoengine import *

# Create your models here.

class Term(Document):
    key = StringField(max_length=30)