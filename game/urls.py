from django.urls import path
from .views import SelectClassView, MainLocationView, back_to_starter_page

urlpatterns = [
    path('', SelectClassView.as_view(), name='select_class'),
    path('main/', MainLocationView.as_view(), name='main_loc'),
    path('back_to_start/', back_to_starter_page, name='back_to_main')
]