# -*- coding: UTF-8 -*-

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import logging, re
from libstat.models import Survey
from libstat.services.excel_export import surveys_to_excel_workbook, _cached_workbook_exists_and_is_valid, _cache_workbook, _cache_dir_path

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = "-year=<YYYY>"
    help = "Export surveys to Excel file"
    help_text = ("Usage: python manage.py export_surveys_to_excel --year=<YYYY>\n\n")

    option_list = BaseCommand.option_list + (
        make_option("--year", dest="year", type="int", help="Sample year, format YYYY"),
    )
    
    def handle(self, *args, **options):
        year = options.get("year")
        
        def _valid_year(year):
            return re.compile('^\d{4}$').match(str(year))
        
        if not year:
            logger.info(self.help_text)
            return
        
        if not _valid_year(year):
            raise CommandError(u"Invalid Year '{}', aborting".format(year))
        
        surveys = Survey.objects.filter(sample_year=year, is_active=True)
        survey_ids = [s.id for s in surveys]
        workbook = surveys_to_excel_workbook(survey_ids)
        file_name_str = "survey_export_{} {}.xslx"
        
        if not _cached_workbook_exists_and_is_valid(year, file_name_str, workbook_is_public=False):
            _cache_workbook(workbook, year, file_name_str, workbook_is_public=False)
            logger.info("Saved excel file %s" % _cache_dir_path)
            return