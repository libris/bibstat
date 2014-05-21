from django.core.management.base import BaseCommand, CommandError
from libstat.models import SurveyResponse, SurveyObservation, Variable
from xlrd import open_workbook

class Command(BaseCommand):
    args = "/path/to/spreadsheet.xls [LibraryType] [Year]"
    help = "Imports survey responses from a spreadsheet"
    
    def handle(self, *args, **options):
        if(len(args) != 2):
            self.stdout.write("Usage: python manage.py import_survey_responses <SourceFile> [Year]\n\n")
            self.stdout.write("\tSourceFile: Absolute path to source spreadsheet. I.e. /home/MyUser/documents/sourcefile.xlsx")
            self.stdout.write("\tYear; YYYY")
            return

        file_name = args[0]
        year = args[1]
        
        self.stdout.write("Importing {} survey responses from: {}".format(year, file_name))

        book = open_workbook(file_name)
        work_sheet = book.sheet_by_index(0)
        
        respondingLibrary_key_index = None
        variable_keys = []
        
        for i in range(0, work_sheet.ncols):
            alias = work_sheet.cell_value(0, i)
            vars = Variable.objects.filter(aliases__contains=alias)
            if len(vars) > 0:
                v = vars[0]
                variable_keys.append((i, alias, v))
                if v.key == "respondingLibrary":
                    respondingLibrary_key_index = i
                    self.stdout.write("respondingLibrary has index {}".format(i))
                    
            else:
                self.stdout.write("Unknown variable alias {}, skipping".format(alias))

        if variable_keys and respondingLibrary_key_index:
            for i in range(1, work_sheet.nrows):
                row = work_sheet.row_values(i)
                library = row[respondingLibrary_key_index].strip()
                if library:
                    sr = SurveyResponse(library=library, sampleYear=year, observations=[])
                    for n, alias, variable in variable_keys:
                        sr.observations.append(SurveyObservation(variable=variable, value=row[n], _source_key=alias, _is_public=variable.is_public))
                    sr.save()
                    self.stdout.write(u"Imported survey response for library {}".format(library))
                else:
                    self.stdout.write(u"Skipping summary row {}".format(i))
        else:
            self.stdout.write(u"No known variables in source file, aborting")

