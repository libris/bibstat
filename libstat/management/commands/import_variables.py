from django.core.management.base import BaseCommand, CommandError
from libstat.models import Variable
from xlrd import open_workbook

class Command(BaseCommand):
    args = "</path/to/spreadsheet.xls>"
    help = "Imports statistical variables from a spreadsheet"

    def handle(self, *args, **options):
        if(len(args) != 1):
            self.stdout.write("Usage: python manage.py import_spreadsheet /path/to/spreadsheet.xlsx")
            return

        self.stdout.write("Importing variables from: {}".format(args[0]))

        book = open_workbook(args[0])
        works_sheet = book.sheet_by_index(0)
        for i in range(1, works_sheet.nrows):
            row = works_sheet.row_values(i)
            object = Variable(key=row[0], description=row[1], comment=row[2])
            object.save()
            self.stdout.write("Imported Variable %s" % object.key)

