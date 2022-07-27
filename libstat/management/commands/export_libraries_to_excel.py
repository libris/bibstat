from django.core.management.base import BaseCommand, CommandError
import logging, re, os
from bibstat import settings
from libstat.models import Survey
from openpyxl import Workbook
from django.core.files import File
from openpyxl.writer.excel import save_virtual_workbook

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = "--year=<YYYY> --all=<y/n>"
    help = "Export libraries with published surveys to Excel file"
    help_text = ("Usage: python manage.py export_libraries_to_excel --year=<YYYY> --all=<y/n>\n\n")

    def add_arguments(self, parser):
        parser.add_argument("--year", dest="year", type=int, help="Sample year, format YYYY")
        parser.add_argument("--all", dest="all",
                            help="Y=Export all libraries with published surveys, N=Only export libraries from published surveys with missing sigel code")

    def handle(self, *args, **options):
        year = options.get("year")
        all = options.get("all")

        def _valid_year(year):
            return re.compile('^\d{4}$').match(str(year))

        if not year:
            logger.info(self.help_text)
            return

        if not _valid_year(year):
            raise CommandError(u"Invalid Year '{}', aborting".format(year))

        if all not in ["y", "Y", "n", "N"]:
            raise CommandError(u"Invalid 'all' option '{}', aborting").format(all)

        if all and (all == "Y" or all == "y"):
            libraries = [s.library for s in Survey.objects.filter(sample_year=year, _status=u"published").only("library")]
        else:
            #Find all surveys with a generated random code instead of a sigel
            libraries = [s.library for s in Survey.objects.filter(sample_year=year, _status=u"published").only("library") if
                         len(s.library.sigel) == 10]

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(["Bibliotek", "Adress", "Postnr", "Ort", "Kommunkod", "Bibliotekstyp", "Sigel"])
        for library in libraries:
            logger.debug(library.address)
            worksheet.append([library.name, library.address, library.zip_code, library.city, library.municipality_code, library.library_type, library.sigel])
        file_name_str = "libraries_export_{}.xslx".format(year)

        if settings.ENVIRONMENT == "local":
            file_path = "{}/data/excel_exports/{}".format(os.getcwd(), file_name_str)
        else:
            file_path = "/data/appl/excel_exports/{}".format(file_name_str)

        with open(file_path, "w") as f:
            File(f).write(save_virtual_workbook(workbook))
