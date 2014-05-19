# Import the MongoAdmin base class
from mongonaut.sites import MongoAdmin

# Import your custom models
from libstat.models import Term

# Subclass MongoAdmin and add a customization
class TermAdmin(MongoAdmin):
    pass

# Instantiate the PostAdmin subclass
# Then attach PostAdmin to your model
Term.mongoadmin = TermAdmin()