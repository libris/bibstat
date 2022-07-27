# -*- coding: UTF-8 -*-
from datetime import datetime
from mongoengine import QuerySet, Q, DoesNotExist


class VariableQuerySet(QuerySet):
    is_draft_not_set_query = Q(is_draft=None)
    is_not_draft_query = Q(is_draft=False)
    public_query = Q(is_public=True)
    is_not_replaced_query = Q(replaced_by=None)

    def public_terms(self):
        return self.filter(
            self.public_query & (self.is_draft_not_set_query | self.is_not_draft_query)
        )

    def public_term_by_key(self, key):
        if not key:
            raise DoesNotExist("No key value given")
        key_query = Q(key=key)
        return self.get(
            key_query
            & self.public_query
            & (self.is_draft_not_set_query | self.is_not_draft_query)
        )

    def replaceable(self):
        return self.filter(
            self.is_not_replaced_query
            & (self.is_draft_not_set_query | self.is_not_draft_query)
        )

    def surveyable(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_to_not_set = Q(active_to=None)
        is_not_discontinued = Q(active_to__gt=today)
        return self.filter(
            (active_to_not_set | is_not_discontinued) & self.is_not_replaced_query
        )
