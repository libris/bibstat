from libstat.models import Survey
from django.core.files import File
from bibstat import settings
import os, logging, codecs

logger = logging.getLogger(__name__)


def _get_surveys_with_no_observations(sample_year):
    survey_list = []
    surveys = Survey.objects.filter(sample_year=sample_year)
    for s in surveys:
        if not s.observations:
            survey_list.append(s)
    return survey_list


def _get_surveys_with_status_not_viewed(sample_year):
    surveys = [s for s in Survey.objects.filter(sample_year=sample_year, _status=u"not_viewed")]
    return surveys


def match_libraries_and_replace_sigel(sample_year):
    all_published_surveys = Survey.objects.filter(sample_year=sample_year, _status=u"published")
    count = 0
    matched = 0

    f = codecs.open(os.path.join(settings.CLEAN_DATA_LOG_PATH, 'match_libraries_log'), 'wt', 'utf-8')
    logfile = File(f)

    for survey in all_published_surveys:
        if len(survey.library.sigel) == 10 or survey.library.sigel.startswith("8", 0, 1):  # fake sigel or 8*-sigel
            count = count + 1
            #find other surveys with same library name
            matching_surveys = Survey.objects.filter(library__name=survey.library.name, pk__ne=survey.pk)
            if matching_surveys.count() != 0:
                for index, matched_survey in enumerate(matching_surveys):
                    if matched_survey.library.sigel and matched_survey.library.sigel != survey.library.sigel and len(matched_survey.library.sigel) != 10:
                        #only use 8*-sigel if no other is found
                        if matched_survey.library.sigel.startswith("8", 0, 1) == False or index == len(matching_surveys) - 1:
                            logfile.write(
                                "Changing sigel %s to %s\n" % (survey.library.sigel, matched_survey.library.sigel))
                            survey.library.sigel = matched_survey.library.sigel
                            survey.save()
                            survey.publish()
                            matched = matched + 1
                            break

    unmatched_surveys = [s for s in Survey.objects.filter(sample_year=sample_year, _status=u"published") if
                         len(s.library.sigel) == 10]
    no_of_unmatched_surveys = len(unmatched_surveys)

    logfile.write("\nMatched libraries for year %d\n" % sample_year)
    logfile.write("Found %d number of published surveys with fake sigels\n" % count)
    logfile.write("Changed sigel for %d number of surveys\n" % matched)
    logfile.write(
        "Remaining published surveys year %d with fake sigels: %d. Sigels: \n" % (sample_year, no_of_unmatched_surveys))

    for unmatched_survey in unmatched_surveys:
        logfile.write("%s\n" % unmatched_survey.library.sigel)

    surveys_sigel_start_w_8 = [s for s in Survey.objects.filter(sample_year=sample_year, _status=u"published") if
                               s.library.sigel.startswith("8", 0, 1)]
    no_surveys_sigel_start_w_8 = len(surveys_sigel_start_w_8)

    logfile.write(
        "Remaining 8-sigels found in published surveys: %d, year %d:\n" % (no_surveys_sigel_start_w_8, sample_year))

    for surv in surveys_sigel_start_w_8:
        try:
            logfile.write("%s %s\n" % (surv.library.sigel, surv.library.name))
        except Exception as e:
            logger.error(e)

    logfile.close()


def remove_empty_surveys(sample_year, mode):
    if mode == 'empty':
        remove_surveys = _get_surveys_with_no_observations(sample_year)
    elif mode == 'not_viewed':
        remove_surveys = _get_surveys_with_status_not_viewed(sample_year)

    f = codecs.open(os.path.join(settings.CLEAN_DATA_LOG_PATH, 'remove_surveys_log'), 'wt', 'utf-8')
    logfile = File(f)
    logfile.write("Mode: %s\n" % mode)

    count = 0

    for survey in remove_surveys:
        count = count + 1
        logfile.write("Removing survey for sigel: %s\n" % survey.library.sigel)
        survey.delete()

    logfile.write("Removed %d number of surveys year %s" % (count, sample_year))
    logfile.close()

