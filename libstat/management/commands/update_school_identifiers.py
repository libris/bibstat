from django.core.management.base import BaseCommand, CommandError
from xlrd import open_workbook
from libstat.models import Survey, ExternalIdentifier
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Usage: python manage.py update_school_identifiers <path-to-file>"
    args = "<path-to-file>"

    def handle(self, *args, **options):
        def identifier_exists(external_identifier, external_identifier_list):
            for ex_id in external_identifier_list:
                if (
                    ex_id.type == external_identifier.type
                    and ex_id.identifier == external_identifier.identifier
                ):
                    return True
            return False

        if len(args) < 1:
            raise CommandError(
                "Usage: python manage.py update_school_identifiers <path-to-file>"
            )
        file = args[0]

        try:
            workbook = open_workbook(file, verbosity=0)
            sheet = workbook.sheet_by_index(0)
            sigel_column = 0
            school_code_column = 1

            for i in range(0, sheet.nrows):
                row = sheet.row_values(i)
                sigel = row[sigel_column]
                school_code = row[school_code_column]
                school_code_string = repr(school_code).split(".")[0]

                logger.info("Updating school_code for sigel %s" % sigel)

                surveys = Survey.objects.filter(library__sigel=sigel)

                for survey in surveys:
                    if survey.library:
                        external_identifier = ExternalIdentifier(
                            type="school_code", identifier=school_code_string
                        )
                        if not survey.library.external_identifiers:
                            logger.info("Adding school_code")
                            survey.library.external_identifiers = [external_identifier]
                            survey.save()
                        elif (
                            survey.library.external_identifiers
                            and not identifier_exists(
                                external_identifier, survey.library.external_identifiers
                            )
                        ):
                            survey.library.external_identifiers.append(
                                external_identifier
                            )
                            survey.save()

        except Exception as e:
            print((str(e)))
