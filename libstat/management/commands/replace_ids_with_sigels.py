from django.core.management.base import BaseCommand, CommandError
import logging, re
from libstat.services.clean_data import _load_sigel_mapping_from_workbook, _update_sigel
from libstat.models import Survey

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = "--year=<YYYY>"
    help = "Replace code-string with sigel based on excel mapping file"
    help_text = "Usage: python manage.py replace_ids_with_sigels --year=<YYYY>\n\n"

    def add_arguments(self, parser):
        parser.add_argument("--year", dest="year", type=int, help="Sample year, format YYYY")

    def handle(self, *args, **options):
        year = options.get("year")

        def _valid_year(year):
            return re.compile(r'^\d{4}$').match(year)

        if not year:
            logger.info(self.help_text)
            return

        if not _valid_year(year):
            raise CommandError(u"Invalid Year '{}', aborting".format(year))

        logger.info("Changing sigels for surveys... year %s" % year)

        sigel_mapping = _load_sigel_mapping_from_workbook(sheet=year, column_old_value=6, column_new_value=7)

        for code in sigel_mapping.keys():
            sigel = sigel_mapping[code]
            logger.debug("Updating %s to %s" % (code, sigel))
            survey = Survey.objects.filter(library__sigel=code, sample_year=year).first()
            if survey:
                _update_sigel(survey, sigel)
