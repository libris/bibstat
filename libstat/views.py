from django.shortcuts import render

# Create your views here.

def index():
    render("Hello world")

"""
Slice/DataSet
{
    "slice": "slice_noOfEmployees_byYear",
    "observations": [
        {

            "refArea": "Karlstad",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Male"
            "noOfEmployees": 6
        },
        {
            "refArea": "Karlstad",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Female"
            "noOfEmployees": 23
        },
        {

            "refArea": "Enköping",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Male"
            "noOfEmployees": 8
        },
        {
            "refArea": "Enköping",
            "sampleYear": 2013
            "staffType": "Librarian",
            "sex": "Female"
            "noOfEmployees": 13
        }
    ]
}
"""
