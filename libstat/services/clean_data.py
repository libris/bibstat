from libstat.models import Survey
from django.core.files import File

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

    f = open('match_libraries_log', 'wt')
    logfile = File(f)

    for survey in all_published_surveys:
        if len(survey.library.sigel) == 10: #fake sigel
            count = count + 1
            #find other surveys with same library name
            matching_surveys = Survey.objects.filter(library__name=survey.library.name, pk__ne=survey.pk)
            if matching_surveys.count() != 0:
                for matched_survey in matching_surveys:
                    if matched_survey.library.sigel and len(matched_survey.library.sigel) != 10:
                        logfile.write("Changing sigel %s to %s\n" % (survey.library.sigel, matched_survey.library.sigel))
                        survey.library.sigel = matched_survey.library.sigel
                        survey.save()
                        matched = matched + 1
                        break

    unmatched_surveys = [s for s in Survey.objects.filter(sample_year=sample_year, _status=u"published") if len(s.library.sigel) == 10]
    no_of_unmatched_surveys = len(unmatched_surveys)

    logfile.write("Matched libraries for year %d\n" % sample_year)
    logfile.write("Found %d number of published surveys with fake sigels\n" % count)
    logfile.write("Changed sigel for %d number of surveys\n" % matched)
    logfile.write("Remaining published surveys year %d with fake sigels: %d. Sigels: \n" % (sample_year, no_of_unmatched_surveys))

    for unmatched_survey in unmatched_surveys:
        logfile.write("%s\n" % unmatched_survey.library.sigel)

    logfile.close()


def remove_empty_surveys(sample_year, mode):
    if mode == 'empty':
        remove_surveys = _get_surveys_with_no_observations(sample_year)
    elif mode == 'not_viewed':
        remove_surveys = _get_surveys_with_status_not_viewed(sample_year)

    f = open('remove_surveys_log', 'wt')
    logfile = File(f)
    logfile.write("Mode: %s\n" % mode)

    count = 0

    for survey in remove_surveys:
        count = count + 1
        logfile.write("Removing survey for sigel: %s\n" % survey.library.sigel)
        survey.delete()

    logfile.write("Removed %d number of surveys year %s" % (count, sample_year))
    logfile.close()
