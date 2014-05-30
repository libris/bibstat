# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand, CommandError
from libstat.models import SurveyResponse, SurveyObservation, Variable, PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY
from xlrd import open_workbook
import re

class Command(BaseCommand):
    args = "<file> [Year] <libraryId column index> [LibraryType]"
    help = "Imports survey responses from a spreadsheet"
    
    libraryTypes = { "public": PUBLIC_LIBRARY, "research": RESEARCH_LIBRARY, "hospital": HOSPITAL_LIBRARY, "school": SCHOOL_LIBRARY}
    
    def handle(self, *args, **options):
        if(len(args) != 4):
            self.stdout.write("Usage: python manage.py import_survey_responses <SourceFile> [Year] <libraryId column index> [LibraryType]\n\n")
            self.stdout.write("\tfile: Absolute path to source spreadsheet. I.e. /home/MyUser/documents/sourcefile.xlsx")
            self.stdout.write("\tYear; YYYY")
            self.stdout.write("\tlibraryId column index; The column index containing a library identifier. First column = 0.")
            self.stdout.write("\tLibraryType; public, research, hospital, school")
            return

        file_name = args[0]
        year = args[1]
        library_column_index = args[2]
        
        library_type = args[3]

        if library_type not in self.libraryTypes.keys():
            self.stdout.write(u"Invalid LibraryType '{}', aborting".format(library_type))
            return
        target_group = self.libraryTypes[library_type]
        
        book = open_workbook(file_name)
        work_sheet = book.sheet_by_index(0)

        if not year.isdigit() or not re.compile('^\d{4}$').match(str(year)):
            self.stdout.write(u"Invalid Year '{}', aborting".format(year))
            return

        if not library_column_index.isdigit() or int(library_column_index) > work_sheet.ncols:
            self.stdout.write(u"Invalid libaryId column index {}, aborting".format(library_column_index))
            return
        library_column_index = int(library_column_index)
        
        self.stdout.write(u"Importing {} survey responses from: {}".format(year, file_name))

        variable_keys = []
        
        for i in range(0, work_sheet.ncols):
            alias = work_sheet.cell_value(0, i)
            vars = Variable.objects.filter(alias=alias)
            if len(vars) > 0:
                v = vars[0]
                variable_keys.append((i, alias, v))
            elif i == library_column_index:
                self.stdout.write("Library identifier variable not found, aborting!")
                return
            else:
                self.stdout.write("Unknown variable alias {}, skipping".format(alias))

        imported_responses = 0
        
        if variable_keys:
            for i in range(1, work_sheet.nrows):
                row = work_sheet.row_values(i)
                
                # TODO: Lookup library in bibdb!
                library = row[library_column_index].strip()
                
                if library:
                    existing_responses = SurveyResponse.objects.filter(library=library, sample_year=year)
                   
                    if len(existing_responses) == 0:
                        sr = SurveyResponse(library=library, sample_year=year, target_group=target_group[0], observations=[])
                        for n, alias, variable in variable_keys:
                            value = row[n]
                            if (isinstance(value, str) and value.strip() == "") or value == 0:
                              value = None
                            sr.observations.append(SurveyObservation(variable=variable, value=value, _source_key=alias, _is_public=variable.is_public))
                        sr.save()
                        imported_responses += 1
                        self.stdout.write(u"Imported survey response for library {}".format(library))
                    #else:
                        #self.stdout.write(u"Survey response for {} already exists for year {}, skipping".format(library, year))
                        
                #else:
                    #self.stdout.write(u"Skipping summary row {}".format(i))
            
            self.stdout.write(u"{} survey responses imported".format(imported_responses))
                              
        else:
            self.stdout.write(u"No known variables in source file, aborting")

