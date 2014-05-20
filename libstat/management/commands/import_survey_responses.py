from django.core.management.base import BaseCommand, CommandError
from libstat.models import SurveyResponse, SurveyObservation, Variable
from xlrd import open_workbook

class Command(BaseCommand):
    args = "</path/to/spreadsheet.xls>"
    help = "Imports survey responses from a spreadsheet"

    def handle(self, *args, **options):
        if(len(args) != 1):
            self.stdout.write("Usage: python manage.py import_survey_responses /path/to/spreadsheet.xlsx")
            return

        self.stdout.write("Importing survey responses from: {}".format(args[0]))

        book = open_workbook(args[0])
        work_sheet = book.sheet_by_index(0)
        self.stdout.write(work_sheet.name)
        print work_sheet.ncols

        sampleYear = int(work_sheet.name)
        print sampleYear


        variable_keys = []
        for i in range(0, work_sheet.ncols):
            key = work_sheet.cell_value(0, i)
            variable_keys.append((i, key, Variable.objects.get(key=key)))

        print variable_keys


        print work_sheet.nrows
        for i in range(1, work_sheet.nrows):
            row = work_sheet.row_values(i)
            sr = SurveyResponse(respondent=row[0], refArea=row[0], sampleYear=sampleYear, observations=[])
            for n, key, variable in variable_keys:
                sr.observations.append(SurveyObservation(variable=variable, value=row[n], _variable_key=key, _is_public=variable.is_public, _metadata=variable.metadata))
            sr.save()
