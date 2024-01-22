from django.urls import path
from .views import home, delete_account, SetLocale, ProfileEdit, ForbesView

urlpatterns = [
    path('', home, name='home'),
    path('profile/delete/', delete_account, name='profile_del'),
    path('profile/', ProfileEdit.as_view(), name='profile_edit'),
    path('forbes/', ForbesView.as_view(), name='forbes'),
    path('locale/<route>/', SetLocale.as_view(), name='locale'),
]