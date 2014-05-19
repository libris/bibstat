# Import the MongoAdmin base class
from mongonaut.sites import MongoAdmin

# Import your custom models
from libstat.models import Variable

# Subclass MongoAdmin and add a customization
class VariableAdmin(MongoAdmin):
     # Searches on the title field. Displayed in the DocumentListView.
    search_fields = ("comment")

    # provide following fields for view in the DocumentListView
    list_fields = ("key", "comment")

# Instantiate the MongoAdmin subclass and attach it to your model
Variable.mongoadmin = VariableAdmin()
