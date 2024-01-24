from users.forms import ChoiceLanguageForm


def context_processor(request):
    return {'locale_form': ChoiceLanguageForm()}  # or whatever you want to set to variable ss
