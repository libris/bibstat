# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from django.conf import settings
from libstat.utils import PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY, DATA_IMPORT_nonMeasurementCategories
from libstat.utils import TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG
from libstat.models import SurveyResponse, SurveyObservation, Variable, Library, SurveyResponseMetadata
from xlrd import open_workbook
from xlrd.biffh import XLRDError
import re
from requests import get

class Command(BaseCommand):
    args = "--file=<file> --target_group=<public|research|hospital|school> --year=<YYYY> [--use_bibdb=<True|False>]"
    
    help = "Imports survey responses from a spreadsheet"
    
    option_list = BaseCommand.option_list + (
        make_option(u'--target_group', dest=u"target_group", type=u'choice', choices=[PUBLIC_LIBRARY[0], RESEARCH_LIBRARY[0], HOSPITAL_LIBRARY[0], SCHOOL_LIBRARY[0]],
            help=u'Target group; public, research, hospital, school'),
        make_option('--file', dest="file", type='string', 
            help='File; Absolute path to source spreadsheet. I.e. /home/MyUser/documents/sourcefile.xlsx'),
        make_option('--year', dest="year", type='int', 
            help='Year; Measurment year, format YYYY'),
        make_option('--use_bibdb', dest="use_bibdb", type=u"choice", default=u"False", choices=[u"True", u"False"],
            help='Use bibdb; Lookup library using BIBDB'),
    )
    
    library_name_value = [u"Biblioteksnamn"]
    
    municipality_name_keys = [u"Folk1"]
    municipality_code_keys = [u"Folk2"]
    respondent_name_keys = [u"Folk5"]
    respondent_email_Keys = [u"Folk6"]
    respondent_phone_keys = [u"Folk7"]
    survey_time_hours_keys = [u"Folk198"]
    survey_time_minutes_keys = [u"Folk199"]
    population_nation_keys = [u"Folk200"]
    population_0to14y_keys = [u"Folk201"]
    
    def handle(self, *args, **options):
        if not options[u"file"] or not options[u"target_group"] or not options[u"year"]:
            self.stdout.write("Usage: python manage.py import_survey_responses --file=</path/to/file> --target_group=<public|research|hospital|school> --year=<YYYY> [--use_bibdb=<True|False>]\n\n")
            return

        file_name = options[u"file"]
        year = options[u"year"]
        target_group = options[u"target_group"]
        
        if not re.compile('^\d{4}$').match(str(year)):
            raise CommandError(u"Invalid Year '{}', aborting".format(year))

        work_sheet = None
        try: 
            book = open_workbook(file_name, verbosity=0)
            work_sheet = book.sheet_by_name(str(year))
        except XLRDError as xld_e:
            raise CommandError(u"No data for year {} in workbook: {}".format(year, xld_e))
#         except Exception as e:
#             raise CommandError(u"Unable to open workbook file {}: {}".format(file_name, e))

        self.stdout.write(u"Importing {} survey responses from: {}...".format(year, file_name))
        
        use_bibdb = options[u"use_bibdb"] == "True"
        if use_bibdb:
            # Test connection to bibdb
            self.stdout.write(u"Using BIBDB to lookup libraries")
            try:
                response = get(settings.BIBDB_BASE_URL)
            except Exception as e:
                use_bibdb = False
                self.stderr.write(u"No connection to Bibdb, importing without libraries: {}".format(e))

        variable_keys = []
        library_column_index = -1

        for i in range(0, work_sheet.ncols):
            key = work_sheet.cell_value(0, i)
            vars = Variable.objects.filter(key=key)
            if len(vars) > 0:
                v = vars[0]
                if v.sub_category in self.library_name_value:
                    library_column_index = i
                    self.stdout.write(u"Found library identifier '{}':'{}' in column: {}".format(key, v.sub_category, i))
                variable_keys.append((i, key, v))

            else:
                self.stdout.write("Unknown variable key {}, skipping".format(key))
        
        if library_column_index == -1:
            raise CommandError(u"Library identifier variable not found, aborting!")

        imported_responses = 0
        
        if variable_keys:
            for i in range(2, work_sheet.nrows):
                row = work_sheet.row_values(i)
                
                library_name = None
                library = None
                lib_col_value = row[library_column_index]
                # Research libraries file and hospital libraries file has summary rows mixed with library response rows
                if lib_col_value and isinstance(lib_col_value, basestring) \
                        and not lib_col_value.startswith("Summa") and not lib_col_value.startswith("summa") \
                        and not lib_col_value.startswith("Riket"):
                    library_name = lib_col_value.strip()
                
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
#                                     print u"Found active library match with id:{}, sigel:'{}' matching name:'{}' (of {} libraries in response)".format(
#                                         lib[u"id"], lib[u"sigel"], lib[u"name"], len(libraries))
                                    break
                          
                   
                    existing_responses = SurveyResponse.objects.filter(library_name=library_name, sample_year=year)
                    if len(existing_responses) == 0:
                        sr = SurveyResponse(library_name=library_name, sample_year=year, target_group=target_group, observations=[])
                        #sr_metadata = SurveyResponseMetadata()
                        if library:
                            sr.library = library #TODO
                        for n, key, variable in variable_keys:
                            value = row[n]
                            
                            # Default number value format seemst to be float, need to convert properly
                            if isinstance(value, (int, float, long)):
                                if value == 0:
                                    # Zero is to be interpreted as "no value given" because of bad data quality
                                    value = None
                                elif variable.type == TYPE_BOOLEAN[0]:
                                    value = (True if value == 1 else False)
                                elif variable.type == TYPE_INTEGER[0]:
                                    value = int(value)
                                elif variable.type == TYPE_LONG[0]:
                                    value = long(value)
                            
                            if (isinstance(value, str) and value.strip() == ""):
                                # Empty string is to be interpreted as "no value given" because of bad data quality
                                value = None
                                
                            sr.observations.append(SurveyObservation(variable=variable, value=value, _source_key=key, _is_public=variable.is_public))
                            #self._extract_metadata(key, value, sr_metadata)
                        
                        #sr.metadata = sr_metadata     
                        sr.save()
                        imported_responses += 1
#                         self.stdout.write(u"Imported survey response for library name {}".format(library_name))
                    
                    elif library and not existing_responses[0].library:
                        sr = existing_responses[0]
                        if library and not sr.library:
                            sr.library = library
                            sr.save()
#                             self.stdout.write(u"Updating survey response for {} {} with library {}".format(year, library_name, library.bibdb_sigel))
                    
                    else:
                        self.stdout.write(u"Survey response for {} already exists for year {}, skipping".format(library_name, year))
                        
                else:
                    self.stdout.write(u"No library name, skipping row {}".format(i))
            
            self.stdout.write(u"...{} survey responses imported".format(imported_responses))
                              
        else:
            self.stdout.write(u"No known variables in source file, aborting")


    # TODO:
    def _extract_metadata(self, key, value, sr_metadata):
        if key in self.municipality_name_keys:
            sr_metadata.municipality_name = value
        elif key in self.municipality_code_keys:
            sr_metadata.municipality_code = value
        elif key in self.respondent_name_keys:
            sr_metadata.respondent_name = value
        elif key in self.respondent_email_Keys:
            sr_metadata.respondent_email = value
        elif key in self.respondent_phone_keys:
            sr_metadata.respondent_phone = value
        elif key in self.survey_time_hours_keys:
            sr_metadata.survey_time_hours = value
        elif key in self.survey_time_minutes_keys:
            sr_metadata.survey_time_minutes = value
        elif key in self.population_nation_keys:
            sr_metadata.population_nation = value
        elif key in self.population_0to14y_keys:
            sr_metadata.population_0to14y = value
