from libstat.models import Survey
from django.core.files import File
from bibstat import settings
from xlrd import open_workbook
from xlrd import XLRDError
import os, logging

logger = logging.getLogger(__name__)


def _get_surveys_with_no_observations(sample_year):
    survey_list = []
    surveys = Survey.objects.filter(sample_year=sample_year)
    for s in surveys:
        if not s.observations:
            survey_list.append(s)
    return survey_list


def _get_surveys_with_status_not_viewed(sample_year):
    surveys = [
        s for s in Survey.objects.filter(sample_year=sample_year, _status="not_viewed")
    ]
    return surveys


def _load_sigel_mapping_from_workbook(
    sheet="Blad1", column_old_value=1, column_new_value=0
):
    worksheet = None
    sigel_mapping = {}

    try:
        book = open_workbook(settings.SIGEL_MAPPING_FILE_PATH, verbosity=0)
        worksheet = book.sheet_by_name(str(sheet))
    except XLRDError as xld_e:
        logger.error("{}".format(xld_e))

    if worksheet:
        for i in range(1, worksheet.nrows):
            sigel_mapping[
                worksheet.cell_value(i, column_old_value)
            ] = worksheet.cell_value(i, column_new_value)

    return sigel_mapping


def _update_sigel(survey, matched_survey_sigel):
    if survey.library.sigel in survey.selected_libraries:
        survey.selected_libraries.remove(survey.library.sigel)
        survey.selected_libraries.append(matched_survey_sigel)
    survey.library.sigel = matched_survey_sigel
    survey.save()
    survey.publish()


def match_libraries_and_replace_sigel(sample_year):
    all_published_surveys = Survey.objects.filter(
        sample_year=sample_year, _status="published"
    )
    count = 0
    matched = 0

    f = open(
        os.path.join(
            settings.CLEAN_DATA_LOG_PATH, "match_libraries_log_%d" % sample_year
        ),
        "w"
    )
    logfile = File(f)

    # Match against existing surveys on library name

    for survey in all_published_surveys:
        if len(survey.library.sigel) == 10 or survey.library.sigel.startswith(
            "8", 0, 1
        ):  # Random-sigel or 8*-sigel
            count = count + 1
            # Find other surveys with same library name
            matching_surveys = Survey.objects.filter(
                library__name__iexact=survey.library.name, pk__ne=survey.pk
            )
            if matching_surveys.count() != 0:
                for index, matched_survey in enumerate(matching_surveys):
                    if (
                        matched_survey.library.sigel
                        and matched_survey.library.sigel != survey.library.sigel
                        and len(matched_survey.library.sigel) != 10
                    ):
                        # Only use 8*-sigel if no other is found
                        if (
                            matched_survey.library.sigel.startswith("8", 0, 1) == False
                            or index == len(matching_surveys) - 1
                        ):
                            logfile.write(
                                "Matched %s to %s. Changing sigel %s to %s\n"
                                % (
                                    survey.library.name,
                                    matched_survey.library.name,
                                    survey.library.sigel,
                                    matched_survey.library.sigel,
                                )
                            )
                            _update_sigel(survey, matched_survey.library.sigel)
                            matched = matched + 1
                            break

    # Try to match remaining 8*-sigels against sigel mapping file

    surveys_sigel_start_w_8 = [
        s
        for s in Survey.objects.filter(sample_year=sample_year, _status="published")
        if s.library.sigel.startswith("8", 0, 1) and len(s.library.sigel) < 10
    ]

    sigel_dict = _load_sigel_mapping_from_workbook()

    for survey_8 in surveys_sigel_start_w_8:
        sigel_from_mapping = sigel_dict.get(survey_8.library.sigel, None)
        if sigel_from_mapping:
            logfile.write(
                "Found mapping for 8*-sigel %s, (library: %s), changing to %s\n"
                % (survey_8.library.sigel, survey_8.library.name, sigel_from_mapping)
            )
            _update_sigel(survey_8, sigel_from_mapping)
            surveys_sigel_start_w_8.remove(survey_8)
            matched = matched + 1

    logfile.write("\nMatched libraries for year %d\n" % sample_year)
    logfile.write(
        "Found %d number of published surveys with random- (or 8*-)sigels\n" % count
    )
    logfile.write("Changed sigel for %d number of surveys\n" % matched)

    # Log remaining unmatched sigels

    no_surveys_sigel_start_w_8 = len(surveys_sigel_start_w_8)

    unmatched_surveys = [
        s
        for s in Survey.objects.filter(sample_year=sample_year, _status="published")
        if len(s.library.sigel) == 10
    ]
    no_of_unmatched_surveys = len(unmatched_surveys)

    logfile.write(
        "\nRemaining published surveys year %d with random-sigels: %d. Sigels: \n"
        % (sample_year, no_of_unmatched_surveys)
    )

    for unmatched_survey in unmatched_surveys:
        logfile.write(
            "%s %s\n" % (unmatched_survey.library.name, unmatched_survey.library.sigel)
        )

    logfile.write(
        "\nRemaining 8*-sigels found in published surveys: %d, year %d:\n"
        % (no_surveys_sigel_start_w_8, sample_year)
    )

    for surv in surveys_sigel_start_w_8:
        try:
            logfile.write("%s %s\n" % (surv.library.name, surv.library.sigel))
        except Exception as e:
            logger.error(e)

    logfile.close()


def remove_empty_surveys(sample_year, mode):
    if mode == "empty":
        remove_surveys = _get_surveys_with_no_observations(sample_year)
    elif mode == "not_viewed":
        remove_surveys = _get_surveys_with_status_not_viewed(sample_year)

    f = open(
        os.path.join(
            settings.CLEAN_DATA_LOG_PATH, "remove_surveys_log_%d" % sample_year
        ),
        "w"
    )
    logfile = File(f)
    logfile.write("Mode: %s\n" % mode)

    count = 0

    for survey in remove_surveys:
        count = count + 1
        logfile.write("Removing survey for sigel: %s\n" % survey.library.sigel)
        survey.delete()

    logfile.write("\nRemoved %d number of surveys year %s" % (count, sample_year))
    logfile.close()
