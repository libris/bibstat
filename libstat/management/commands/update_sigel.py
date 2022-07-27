from django.core.management.base import BaseCommand
import logging
import sys

from libstat.models import OpenData, Survey, CachedReport

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = "--from=<old sigel> --to=<new sigel>"
    help = "Updates a sigel."
    help_text = "Usage: python manage.py update_sigel --from=<old sigel> --to=<new sigel>\n\n"

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="from", help="Old sigel")
        parser.add_argument("--to", dest="to", help="New sigel")

    def handle(self, *args, **options):
        old_sigel = options.get('from')
        new_sigel = options.get('to')
        changed = False

        if not old_sigel or not new_sigel:
            print(self.help_text)
            sys.exit(1)

        logger.info("Changing sigel {} to {}".format(old_sigel, new_sigel))

        for s in Survey.objects.filter(library__sigel__iexact=old_sigel):
            logger.info("Survey {} {} {}: sigel {} to {}".format(
                s.id, s.library.name, s.sample_year, s.library.sigel, new_sigel))
            if s.library.sigel in s.selected_libraries:
                s.selected_libraries.remove(s.library.sigel)
                s.selected_libraries.append(new_sigel)

            s.library.sigel = new_sigel
            s.save()
            if s.is_published:
                logger.info("Survey {} {} {}: republishing survey".format(
                    s.id, s.library.name, s.sample_year
                ))
                s.publish()
            changed = True

        for o in OpenData.objects.filter(sigel__iexact=old_sigel):
            if o.sigel.lower() == old_sigel.lower():
                logger.info("OpenData {} {} {} {}: changing sigel {} to {}".format(
                    o.id, o.library_name, o.sample_year, o.variable_key, o.sigel,
                    new_sigel))
                o.sigel = new_sigel
                o.save()
                changed = True

        if changed:
            logger.info("Dropping cached reports collection")
            CachedReport.drop_collection()
        else:
            logger.info("Nothing to do.")
