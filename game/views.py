from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _
from .services import get_select_classview, post_select_classview

@login_required
def back_to_starter_page(request: HttpRequest):
    if request.method == "GET":
        request.user.current_position = request.resolver_match.url_name
        request.user.save()
        return redirect("home")
    return JsonResponse("Error")


class MainLocationView(View, LoginRequiredMixin):
    template_name = "game/main.html"

    def get(self, request: HttpRequest):
        return render(request=request, template_name=self.template_name)


class SelectClassView(View, LoginRequiredMixin):
    template_name = "game/select_class.html"

    def get(self, request: HttpRequest):
        return get_select_classview(request=request, template_name=self.template_name)
    
    def post(self, request: HttpRequest):
        return post_select_classview(request=request)
