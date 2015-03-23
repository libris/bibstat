from libstat.models import Survey
from django.core.files import File

def get_surveys_with_no_observations(sample_year):
    survey_list = []
    surveys = Survey.objects.filter(sample_year=sample_year)
    for s in surveys:
        if not s.observations:
            survey_list.append(s)
    return survey_list


def match_libraries_and_replace_sigel(sample_year):
    all_published_surveys = Survey.objects.filter(sample_year=sample_year, _status="published")
    count = 0
    matched = 0

    f = open('match_libraries_log', 'wt')
    logfile = File(f)

    for survey in all_published_surveys:
        if len(survey.library.sigel) == 10: #fake sigel
            logfile.write("Fake sigel: %s\n" % survey.library.sigel)
            count = count + 1
            #find other surveys with same library name
            matching_surveys = Survey.objects.filter(library__name=survey.library.name, pk__ne=survey.pk)
            logfile.write("Number of matching surveys: %d\n" % matching_surveys.count())
            if matching_surveys.count() != 0:
                matched_survey = matching_surveys[0]
                if matched_survey.library.sigel:
                    #copy sigel
                    survey.library.sigel = matched_survey.library.sigel
                    survey.save()
                    matched = matched + 1
                    logfile.write("Changing sigel %s" % survey.library.sigel)
                    logfile.write(" to %s" % matched_survey.library.sigel)

    logfile.write("Matched libraries for year %d\n" % sample_year)
    logfile.write("Found %d number of published surveys with fake sigels\n" % count)
    logfile.write("Changed sigel for %d number of surveys" % matched)
    logfile.close()


def remove_empty_surveys(sample_year):
    empty_surveys = get_surveys_with_no_observations(sample_year)
    count = 0

    f = open('remove_surveys_log', 'wt')
    logfile = File(f)

    for empty_survey in empty_surveys:
        count = count + 1
        logfile.write("Removing survey for sigel %s\n" % empty_survey.library.sigel)
        empty_survey.delete()

    logfile.write("Removed %d number of empty surveys year %s" % (count, sample_year))
    logfile.close()
