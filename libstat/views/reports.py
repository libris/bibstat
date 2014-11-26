# -*- coding: utf-8 -*-

from django.shortcuts import render

def reports(request):
    if request.method == "GET":
        return render(request, 'libstat/reports.html', { "nav_reports_css": "active" })