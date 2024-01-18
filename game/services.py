from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

def get_select_classview(request: HttpRequest, template_name: str) -> HttpResponse:
    if request.user.role is not None:
        return redirect('main_loc')
    classes = [
        { 
            "name": "agility",
            "img": request.build_absolute_uri('/static/img/classes/agility.png'),
            "visual_name": _("Ловкач")
        },
        { 
            "name": "strength",
            "img": request.build_absolute_uri('/static/img/classes/strength.png'),
            "visual_name": _("Силач")
        },
        { 
            "name": "shooter",
            "img": request.build_absolute_uri('/static/img/classes/archer.png'),
            "visual_name": _("Стрілок")
        }
    ]
    return render(request=request, template_name=template_name, context={"classes": classes})

def post_select_classview(request: HttpRequest):
    if request.POST['role'] is not None:
        request.user.role = request.POST['role']
        request.user.save()
    else:
        return redirect('select_class')
    return redirect('main_loc')