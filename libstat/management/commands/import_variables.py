import logging

from django.core.management.base import BaseCommand, CommandError
from xlrd import open_workbook

from libstat.utils import DATA_IMPORT_nonMeasurementCategories
from libstat.utils import TYPE_STRING, TYPE_BOOLEAN, TYPE_INTEGER, TYPE_LONG, TYPE_DECIMAL, TYPE_PERCENT
from libstat.models import Variable


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    variableTypes = {
        u"Text": TYPE_STRING[0],
        u"Numerisk": TYPE_STRING[0],
        u"Boolesk": TYPE_BOOLEAN[0],
        u"Integer": TYPE_INTEGER[0],
        u"Long": TYPE_LONG[0],
        u"Decimal två": TYPE_DECIMAL[0],
        u"Decimal ett": TYPE_DECIMAL[0],
        u"Procent": TYPE_PERCENT[0]
    }

    isPublic = {
        u"Öppet": True,
        u"Inte": False
    }

    help = "Imports statistical variables from a spreadsheet"

    def add_arguments(self, parser):
        parser.add_argument("--target-group", dest="target_group", choices=["folkbib", "specbib", "sjukbib", "skolbib"],
                            help="Target group; public, research, hospital, school")
        parser.add_argument("--file", dest="file",
                            help="File; Absolute path to source spreadsheet. i.e. /home/MyUser/documents/sourcefile.xlsx")

    def handle(self, *args, **options):
        if not options["target_group"] or not options["file"]:
            logger.info(("Usage: python manage.py import_variables --file=</path/to/file>"
                         "--target_group=<folkbib|specbib|sjukbib|skolbib>\n\n"))
            return

        file = options["file"]
        target_group = options["target_group"]

        logger.info(u"Importing {} variables from: {}...".format(target_group, file))

        book = open_workbook(file)
        work_sheet = book.sheet_by_index(0)
        imported_variables = 0
        updated_variables = 0

        for i in range(1, work_sheet.nrows):
            row = work_sheet.row_values(i)

            # Columns: 0=Ordningsnummer, 1=Beskrivning, 2=Huvudgrupp, 3=Undergrupp, 4=Enhet, 5=Visas öppet/Visas inte
            key = row[0].strip()
            description = row[1].strip()
            category = row[2].strip()
            sub_category = row[3].strip()
            variable_type = row[4].strip()
            is_public = row[5].strip()

            if variable_type not in self.variableTypes.keys():
                raise CommandError(u"Invalid variable type: {} for key: {}".format(variable_type, key))
            else:
                variable_type = self.variableTypes[variable_type]

            if is_public not in self.isPublic.keys():
                raise CommandError(u"Invalid public/private column value: {} for key: {}".format(is_public, key))
            else:
                is_public = self.isPublic[is_public]

            if category in DATA_IMPORT_nonMeasurementCategories:
                is_public = False

            existing_vars = Variable.objects.filter(key=key)
            if len(existing_vars) == 0:
                object = Variable(key=key, description=description, category=category, sub_category=sub_category,
                                  type=variable_type, is_public=is_public, target_groups=[target_group], )
                object.save()
                imported_variables += 1
            else:
                object = existing_vars[0]
                object.description = description
                object.category = category
                object.sub_category = sub_category
                object.type = variable_type
                object.is_public = is_public
                object.target_groups = [target_group]
                object.save()
                updated_variables += 1

        logger.info(u"...{} {} variables imported, {} updated.".format(imported_variables,
                                                                       target_group, updated_variables))
