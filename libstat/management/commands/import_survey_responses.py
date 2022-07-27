import re
import logging
import traceback

from django.core.management.base import BaseCommand, CommandError
from xlrd import open_workbook
from xlrd.biffh import XLRDError
from data.municipalities import (
    municipality_code_from,
    municipality_code_from_county_code,
)

from libstat.utils import TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG
from libstat.models import Survey, SurveyObservation, Variable, Library


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = (
        "--file=<file> --target_group=<folkbib|specbib|sjukbib|skolbib> --year=<YYYY>"
    )
    help = "Imports surveys from a spreadsheet"
    help_text = (
        "Usage: python manage.py import_survey_responses --file=</path/to/file> "
        "--target_group=<folkbib|specbib|sjukbib|skolbib> --year=<YYYY>\n\n"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--target_group",
            dest="target_group",
            choices=["folkbib", "specbib", "sjukbib", "skolbib"],
            help="Target group; public, research, hospital, school",
        )
        parser.add_argument(
            "--file",
            dest="file",
            help="File; Absolute path to source spreadsheet. I.e. /home/MyUser/documents/sourcefile.xlsx",
        )
        parser.add_argument(
            "--year", dest="year", type=int, help="Measurement year, format YYYY"
        )

    def _import_from_work_sheet(self, work_sheet, year, target_group):
        def _parse_value(value):
            if isinstance(value, (int, float)):
                if value == 0:
                    value = None
                elif variable.type == TYPE_BOOLEAN[0]:
                    value = True if value == 1 else False
                elif variable.type == TYPE_INTEGER[0]:
                    value = int(value)
                elif variable.type == TYPE_LONG[0]:
                    value = int(value)

            if isinstance(value, str) and value.strip() == "":
                value = None
            return value

        variable_keys = []
        library_name_column = -1

        for i in range(0, work_sheet.ncols):
            key = work_sheet.cell_value(0, i)
            variables = Variable.objects.filter(key=key)
            if len(variables) > 0:
                variable = variables[0]
                if variable.sub_category in ["Biblioteksnamn"]:
                    library_name_column = i
                variable_keys.append((i, variable))

        if library_name_column == -1:
            raise CommandError("Library identifier variable not found, aborting!")

        if not variable_keys:
            raise CommandError("Failed to find any variables, aborting!")

        municipality_code_column = -1
        county_code_column = -1
        for i in range(0, work_sheet.ncols):
            if work_sheet.cell_value(1, i) == "Kommunkod":
                municipality_code_column = i
                break
            elif work_sheet.cell_value(1, i) == "Länskod":
                county_code_column = i
                break

        if county_code_column == -1 and municipality_code_column == -1:
            raise CommandError("Could not find municipality or county code, aborting!")

        num_imported_surveys = 0
        for i in range(2, work_sheet.nrows):
            row = work_sheet.row_values(i)

            lib_col_value = row[library_name_column]
            # Research libraries file and hospital libraries file has summary rows mixed with library response rows
            if (
                lib_col_value
                and isinstance(lib_col_value, str)
                and not lib_col_value.startswith(
                    (
                        "Summa",
                        "summa",
                        "Riket",
                    )
                )
            ):
                library_name = lib_col_value.strip()
            else:
                continue

            if Survey.objects.filter(library__name=library_name, sample_year=year):
                continue

            if municipality_code_column != -1:
                municipality_code = municipality_code_from(
                    row[municipality_code_column]
                )
            elif county_code_column != -1:
                municipality_code = municipality_code_from_county_code(
                    row[county_code_column]
                )

            if target_group == "specbib":
                library_type = {
                    "Nationalbibliotek": "natbib",
                    "Högskolebibliotek": "univbib",
                    "Specialbibliotek": "specbib",
                }[row[2]]
            else:
                library_type = target_group

            library = Library(name=library_name, library_type=library_type)
            if municipality_code is not None:
                library.municipality_code = municipality_code
            survey = Survey(
                sample_year=year, library=library, selected_libraries=[library.sigel]
            )
            for col, variable in variable_keys:
                survey.observations.append(
                    SurveyObservation(
                        variable=variable,
                        value=_parse_value(row[col]),
                        _is_public=variable.is_public,
                    )
                )

            survey.save().publish()

            num_imported_surveys += 1

        logger.info("...{} surveys imported".format(num_imported_surveys))

    def handle(self, *args, **options):
        def _get_work_sheet(file_name, year):
            try:
                book = open_workbook(file_name, verbosity=0)
                return book.sheet_by_name(str(year))
            except XLRDError as xld_e:
                raise CommandError(
                    "No data for year {} in workbook: {}".format(year, xld_e)
                )

        def _valid_year(year):
            return re.compile("^\d{4}$").match(str(year))

        file_name = options.get("file")
        year = options.get("year")
        target_group = options.get("target_group")

        if not file_name or not target_group or not year:
            logger.info(self.help_text)
            return

        if not _valid_year(year):
            raise CommandError("Invalid Year '{}', aborting".format(year))

        work_sheet = _get_work_sheet(file_name, year)

        try:
            self._import_from_work_sheet(work_sheet, year, target_group)
        except Exception as e:
            print((traceback.format_exc()))
