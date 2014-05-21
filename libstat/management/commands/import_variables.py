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
        work_sheet = book.sheet_by_index(0)
        target_group = work_sheet.name

        for i in range(1, work_sheet.nrows):
            row = work_sheet.row_values(i)
            
            #Columns: 0-Alias, 1-Description, 2-Comment, 3-Variable
            alias = row[0].strip()
            description = row[1].strip()
            comment = row[2].strip()
            variable = row[3].strip()
            is_public = True
            
            if not variable:
                variable = alias
                is_public=False
            
            existing_vars = Variable.objects.filter(key=variable)
            if len(existing_vars) == 0:
                object = Variable(key=variable, aliases=[alias], description=description, comment=comment, is_public=is_public, target_groups=[target_group])
                object.save()
                self.stdout.write("IMPORTED: key={}, aliases={}, is_public={}".format(object.key, object.aliases, object.is_public))
            else:
                object = existing_vars[0]
                perform_update = False
                if alias not in object.aliases:
                    object.aliases.append(alias)
                    perform_update = True
                if target_group not in object.target_groups:
                    object.target_groups.append(target_group)
                    perform_update = True
                if perform_update:
                    object.save()
                    self.stdout.write("UPDATED: key={}, aliases={}, is_public={}".format(object.key, object.aliases, object.is_public))
                else:
                    self.stdout.write("SKIPPED: key={}, aliases={}, is_public={}".format(object.key, object.aliases, object.is_public))
            

