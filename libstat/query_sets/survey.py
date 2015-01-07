# -*- coding: UTF-8 -*-
from mongoengine import QuerySet, Q
from data.municipalities import MUNICIPALITIES


class SurveyQuerySet(QuerySet):
    def by(self, sample_year=None, target_group=None, status=None, municipality_code=None, free_text=None,
           is_active=None, with_email=False, without_email=False):
        target_group_query = Q(library__library_type=target_group) if target_group else Q()
        sample_year_query = Q(sample_year=sample_year) if sample_year else Q()
        status_query = Q(_status=status) if status else Q()
        is_active_query = Q(is_active=is_active) if is_active is not None else Q()
        municipality_code_query = (Q(library__municipality_code=municipality_code)
                                   if municipality_code else Q())

        email_query = Q()
        if with_email:
            email_query = Q(library__email__exists=True) & Q(library__email__ne="")
        if without_email:
            email_query = Q(library__email__exists=False) | Q(library__email="")

        free_text_query = Q()
        if free_text:
            free_text = free_text.strip().lower()
            municipality_codes = [m[1] for m in MUNICIPALITIES if free_text in m[0].lower()]

            free_text_municipality_code_query = Q(library__municipality_code__icontains=free_text)
            free_text_municipality_name_query = Q(library__municipality_code__in=municipality_codes)
            free_text_email_query = Q(library__email__icontains=free_text)
            free_text_library_name_query = Q(library__name__icontains=free_text)
            free_text_query = (free_text_municipality_code_query | free_text_email_query | free_text_library_name_query
                               | free_text_municipality_name_query)

        return self.filter(target_group_query & sample_year_query & status_query &
                           municipality_code_query & email_query & free_text_query &
                           is_active_query).exclude("observations")