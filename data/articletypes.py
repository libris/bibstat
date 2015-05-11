# -*- coding: UTF-8 -*-

ARTICLE_TYPES = (
    (u"correction", u"Ändringsmeddelande"),
    (u"front_intro", u"Förstasidans rubrik och introtext"),
    (u"survey_intro", u"Introtext enkät"),
    (u"statistics_intro", u"Introtext statistik"),
    (u"statistics_info", u"Informationstext statistik"),
    (u"reports_intro", u"Introtext rapporter"),
    (u"reports_info", u"Informationstext rapporter"),
    (u"open_data_intro", u"Introtext öppet data"),
    (u"open_data_info", u"Informationstext öppet data"),
    (u"read_more_intro", u"Introtext läs mer")
)

article_types_dict = dict(ARTICLE_TYPES)

article_types_to_save_as_html = [u"statistics_info", u"open_data_info"]

single_article_types = [u"front_intro", u"survey_intro", u"statistics_intro",
                        u"statistics_info", u"reports_intro", u"reports_info",
                        u"open_data_intro", u"open_data_info", u"read_more_intro"]