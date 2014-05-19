from mongonaut.sites import MongoAdmin
from libstat.models import Term

class TermAdmin(MongoAdmin):
    def has_view_permission(self, request):
        return True

# Instantiate the PostAdmin subclass
# Then attach PostAdmin to your models
Term.mongoadmin = TermAdmin()