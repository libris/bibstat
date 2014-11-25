# -*- coding: UTF-8 -*-

PRINCIPALS = (
    (u"musstat", u"stat"),
    (u"muslan", u"landsting"),
    (u"muskom", u"kommun"),
    (u"folkbib", u"kommun"),
    (u"specbib", u"stat"),
    (u"univbib", u"stat"),
    (u"sjukbib", u"landsting"),
    (u"myndbib", u"stat"),
    (u"folkhogbib", u"landsting"),
    (u"ovrbib", u"stat"),
    (u"frigym", u"privat"),
    (u"friskol", u"privat"),
    (u"skolbib", u"kommun"),
    (u"gymbib", u"kommun"),
    (u"statskol", u"stat"),
    (u"vuxbib", u"kommun"),
    (u"natbib", u"stat")
)

principal_for_library_type = dict(PRINCIPALS)

library_types_for_principal = {}
for k, v in principal_for_library_type.iteritems():
    library_types_for_principal.setdefault(v, []).append(k)

def get_library_types_with_same_principal(library):
    principal = principal_for_library_type[library.library_type]
    return library_types_for_principal[principal]
