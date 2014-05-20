# Import the MongoAdmin base class
from mongonaut.sites import MongoAdmin

# Import your custom models
from libstat.models import Variable, SurveyResponse, Term, Type, Measurable

# Subclass MongoAdmin and add a customization
class VariableAdmin(MongoAdmin):
     # Searches on the title field. Displayed in the DocumentListView.
    search_fields = ("key", "description")

    # provide following fields for view in the DocumentListView
    list_fields = ("key", "description", "is_public")

class TermAdmin(MongoAdmin):
     search_fields = ("term", "description")
     list_fields = ("description",)
     
class TypeAdmin(MongoAdmin):
     search_fields = ("type", "description")
     list_fields = ("description",)

class MeasurableAdmin(MongoAdmin):
     search_fields = ("measurable", "description")
     list_fields = ("description",)

class SurveyResponseAdmin(MongoAdmin):
    list_fields = ("respondent",)


# Instantiate the MongoAdmin subclass and attach it to your model
Variable.mongoadmin = VariableAdmin()
Term.mongoadmin = TermAdmin()
Type.mongoadmin = TypeAdmin()
Measurable.mongoadmin = MeasurableAdmin()
SurveyResponse.mongoadmin = SurveyResponseAdmin()

