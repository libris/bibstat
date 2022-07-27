PRINCIPALS = (
    ("musstat", "stat"),
    ("muslan", "landsting"),
    ("muskom", "kommun"),
    ("folkbib", "kommun"),
    ("folkskolbib", "kommun"),
    ("specbib", "stat"),
    ("univbib", "stat"),
    ("sjukbib", "landsting"),
    ("myndbib", "stat"),
    ("folkhogbib", "landsting"),
    ("ovrbib", "stat"),
    ("frisgym", "privat"),
    ("friskol", "privat"),
    ("skolbib", "kommun"),
    ("gymbib", "kommun"),
    ("statskol", "stat"),
    ("vuxbib", "kommun"),
    ("natbib", "stat"),
)

name_for_principal = {
    "landsting": "Landsting",
    "kommun": "Kommun",
    "stat": "Stat",
    "privat": "Privat",
}

principal_for_library_type = dict(PRINCIPALS)
library_types_with_principals = [
    "univbib",
    "muslan",
    "muskom",
    "vuxbib",
    "frisgym",
    "skolbib",
    "sjukbib",
    "myndbib",
    "statskol",
    "folkbib",
    "folkskolbib",
    "musstat",
    "specbib",
    "folkhogbib",
    "friskol",
    "ovrbib",
    "natbib",
    "gymbib",
]

library_types_for_principal = {
    "stat": [
        "univbib",
        "myndbib",
        "statskol",
        "musstat",
        "specbib",
        "ovrbib",
        "natbib",
    ],
    "landsting": ["muslan", "sjukbib", "folkhogbib"],
    "privat": ["frisgym", "friskol"],
    "kommun": ["muskom", "vuxbib", "skolbib", "folkbib", "folkskolbib", "gymbib"],
}


def get_library_types_with_same_principal(library):
    if (
        library.library_type is None
        or library.library_type not in principal_for_library_type
    ):
        return library_types_with_principals

    principal = principal_for_library_type[library.library_type]
    return library_types_for_principal[principal]
