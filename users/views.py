from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.utils import translation
from django.http import HttpRequest, JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
from .forms import ChoiceLanguageForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class SetLocale(View):
    def post(self, request: HttpRequest, route):
        form = ChoiceLanguageForm(request.POST)
        route_name = route
        if form.is_valid():
            translation.activate(form.cleaned_data['locale'])
            request.session['lang'] = form.cleaned_data['locale']
        else:
            return JsonResponse({"errors":form.errors})
        return redirect(route_name)

def home(request: HttpRequest):
    translation.activate(request.session.get('lang'))
    lang = request.session.get('lang')
    form = ChoiceLanguageForm()
    return render(request=request, template_name="home.html", context={'locale_form': form})

@login_required
def custom_logout(request):
    logout(request)
    return redirect("home")