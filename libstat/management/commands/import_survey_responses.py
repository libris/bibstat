# -*- coding: UTF-8 -*-
from optparse import make_option
import re
import logging

from django.core.management.base import BaseCommand, CommandError
from xlrd import open_workbook
from xlrd.biffh import XLRDError

from libstat.utils import TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG
from libstat.models import Survey, SurveyObservation, Variable, Library


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = "--file=<file> --target_group=<folkbib|specbib|sjukbib|skolbib> --year=<YYYY>"
    help = "Imports surveys from a spreadsheet"
    help_text = ("Usage: python manage.py import_survey_responses --file=</path/to/file>"
                 "--target_group=<folkbib|specbib|sjukbib|skolbib> --year=<YYYY>\n\n")

    option_list = BaseCommand.option_list + (
        make_option(u'--target_group', dest=u"target_group", type=u'choice',
                    choices=["folkbib", "specbib", "sjukbib", "skolbib"],
                    help=u'Target group; public, research, hospital, school'),
        make_option('--file', dest="file", type='string',
                    help='File; Absolute path to source spreadsheet. I.e. /home/MyUser/documents/sourcefile.xlsx'),
        make_option('--year', dest="year", type='int',
                    help='Year; Measurment year, format YYYY'),
    )

    def _import_from_work_sheet(self, work_sheet, year, target_group):
        def _parse_value(value):
            if isinstance(value, (int, float, long)):
                if value == 0:
                    value = None
                elif variable.type == TYPE_BOOLEAN[0]:
                    value = (True if value == 1 else False)
                elif variable.type == TYPE_INTEGER[0]:
                    value = int(value)
                elif variable.type == TYPE_LONG[0]:
                    value = long(value)

            if (isinstance(value, str) and value.strip() == ""):
                value = None
            return value

        variable_keys = []
        library_name_column = -1

        for i in range(0, work_sheet.ncols):
            key = work_sheet.cell_value(0, i)
            variables = Variable.objects.filter(key=key)
            if len(variables) > 0:
                variable = variables[0]
                if variable.sub_category in [u"Biblioteksnamn"]:
                    library_name_column = i
                variable_keys.append((i, variable))

        if library_name_column == -1:
            raise CommandError(u"Library identifier variable not found, aborting!")

        if not variable_keys:
            raise CommandError(u"Failed to find any variables, aborting!")

        num_imported_surveys = 0
        for i in range(2, work_sheet.nrows):
            row = work_sheet.row_values(i)

            lib_col_value = row[library_name_column]
            # Research libraries file and hospital libraries file has summary rows mixed with library response rows
            if (lib_col_value and isinstance(lib_col_value, basestring)
                    and not lib_col_value.startswith(("Summa", "summa", "Riket",))):
                library_name = lib_col_value.strip()
            else:
                continue

            if Survey.objects.filter(library__name=library_name, sample_year=year):
                continue

            survey = Survey(sample_year=year, library=Library(name=library_name, library_type=target_group))
            for col, variable in variable_keys:
                survey.observations.append(
                    SurveyObservation(variable=variable, value=_parse_value(row[col]), _is_public=variable.is_public))

            survey.save().publish()

            num_imported_surveys += 1

        logger.info(u"...{} surveys imported".format(num_imported_surveys))

    def handle(self, *args, **options):
        def _get_work_sheet(file_name, year):
            try:
                book = open_workbook(file_name, verbosity=0)
                return book.sheet_by_name(str(year))
            except XLRDError as xld_e:
                raise CommandError(u"No data for year {} in workbook: {}".format(year, xld_e))

        def _valid_year(year):
            return re.compile('^\d{4}$').match(str(year))

        file_name = options.get(u"file")
        year = options.get(u"year")
        target_group = options.get(u"target_group")

        if not file_name or not target_group or not year:
            logger.info(self.help_text)
            return

        if not _valid_year(year):
            raise CommandError(u"Invalid Year '{}', aborting".format(year))

        work_sheet = _get_work_sheet(file_name, year)

        self._import_from_work_sheet(work_sheet, year, target_group)
