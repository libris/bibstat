# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from libstat.models import SurveyResponse, SurveyObservation, Variable, Library, PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY
from xlrd import open_workbook
import re
from requests import get

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
        
        # Test connection to bibdb
        use_bibdb = True
        try:
            response = get(settings.BIBDB_BASE_URL)
        except Exception as e:
            use_bibdb = False
            print u"No connection to Bibdb, importing without libraries: {}".format(e)
            

        variable_keys = []
        
        # TODO: Hantera summafält i forsk!
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
                library_name = None
                library = None
                lib_col_value = row[library_column_index]
                if lib_col_value and isinstance(lib_col_value, basestring):
                    library_name = lib_col_value.strip()
                    #print u"Library name is : {}".format(library_name)
                #TODO: Fiska fram kolumnindex via args och värden för municipality_name, municipality_code, county_code, school_id
                
                if library_name:
                    if use_bibdb:
                        response = get(u"{}/library/autocomplete?q={}".format(settings.BIBDB_BASE_URL, library_name))
                        if response and response.status_code == 200:
                            libraries = response.json()
                            for lib in libraries:
                                #print u"Got library {}".format(lib)
                                if lib[u"alive"] == True:
                                    library = Library(bibdb_name=lib[u"name"], bibdb_id=lib[u"id"], bibdb_sigel=lib[u"sigel"])
                                    #TODO: Spara municipality_name, municipality_code, county_code, school_id
                                    print u"Found active library match with id:{}, sigel:'{}' matching name:'{}' (of {} libraries in response)".format(
                                        lib[u"id"], lib[u"sigel"], lib[u"name"], len(libraries))
                                    break
                          
                   
                    existing_responses = SurveyResponse.objects.filter(library_name=library_name, sample_year=year)
                    if len(existing_responses) == 0:
                        sr = SurveyResponse(library_name=library_name, sample_year=year, target_group=target_group[0], observations=[])
                        if library:
                            sr.library = library #TODO
                        for n, alias, variable in variable_keys:
                            value = row[n]
                            if (isinstance(value, str) and value.strip() == "") or value == 0:
                              value = None
                            sr.observations.append(SurveyObservation(variable=variable, value=value, _source_key=alias, _is_public=variable.is_public))
                        sr.save()
                        imported_responses += 1
                        self.stdout.write(u"Imported survey response for library name {}".format(library_name))
                    
                    elif library and not existing_responses[0].library:
                        sr = existing_responses[0]
                        if library and not sr.library:
                            sr.library = library
                            sr.save()
                            self.stdout.write(u"Updating survey response for {} {} with library {}".format(year, library_name, library.bibdb_sigel))
                    
                    else:
                        self.stdout.write(u"Survey response for {} already exists for year {}, skipping".format(library_name, year))
                        
                else:
                    self.stdout.write(u"No library name, skipping row {}".format(i))
            
            self.stdout.write(u"{} survey responses imported".format(imported_responses))
                              
        else:
            self.stdout.write(u"No known variables in source file, aborting")

