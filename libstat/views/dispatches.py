from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from libstat.models import Dispatch


@permission_required('is_superuser', login_url='login')
def dispatches(request):
    if request.method == "GET":

        dispatches = []
        for dispatch in Dispatch.objects.all():
            dispatches += [{
                "description": dispatch.description,
                "title": dispatch.title,
                "message": dispatch.message.replace("\n", "<br>"),
                "library_name": dispatch.survey.library.name,
                "library_city": dispatch.survey.library.city,
                "library_email": dispatch.survey.library.email,
            }]

        return render(request, 'libstat/dispatches.html', {"dispatches": dispatches})
