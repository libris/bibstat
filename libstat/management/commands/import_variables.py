from django.core.management.base import BaseCommand, CommandError
from libstat.models import Variable, Term, Type, Measurable, VariableMetadata, EmbeddedDimension
from xlrd import open_workbook

class Command(BaseCommand):
    args = "</path/to/spreadsheet.xls>"
    help = "Imports statistical variables from a spreadsheet"

    def handle(self, *args, **options):
        if(len(args) != 1):
            self.stdout.write("Usage: python manage.py import_spreadsheet /path/to/spreadsheet.xlsx")
            return

        self.stdout.write("Importing variables from: {}".format(args[0]))

        book = open_workbook(args[0])
        works_sheet = book.sheet_by_index(0)

        for i in range(1, works_sheet.nrows):
            row = works_sheet.row_values(i)
            # Columns: 0=Key, 1=Description, 2=Comment, 3=Measurable, 4=Range, 5=Dimension, 6=DimensionValue, 7=Dimension, 8=DimensionValue
            object = Variable(key=row[0], description=row[1], comment=row[2])
            
            measurable = row[3].strip()
            is_public = bool(measurable)

            object.is_public = is_public

            if is_public:
                metadata = VariableMetadata(measurable=measurable, range=row[4])
                metadata.dimensions = []
                
                Measurable.objects.filter(measurable=measurable).update_one(upsert=True)
                
                term1 = row[5].strip()
                Term.objects.filter(term=term1).update_one(upsert=True)
                
                type1 = row[6].strip()
                Type.objects.filter(type=type1).update_one(upsert=True)
                
                metadata.dimensions.append(EmbeddedDimension(dimension=term1, value=type1))

                term2 = row[7].strip()
                has_second_dimension = bool(term2)
                
                if has_second_dimension:
                    Term.objects.filter(term=term2).update_one(upsert=True)
                    
                    type2 = row[8].strip()
                    Type.objects.filter(type=type2).update_one(upsert=True)
                    
                    metadata.dimensions.append(EmbeddedDimension(dimension=term2, value=type2))
                    
                object.metadata = metadata
                
            object.save()
            self.stdout.write("Imported Variable %s" % object.key)

