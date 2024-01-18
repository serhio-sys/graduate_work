from django.urls import path
from .views import home, delete_account, SetLocale, ProfileEdit

urlpatterns = [
    path('', home, name='home'),
    path('profile/delete/', delete_account, name='profile_del'),
    path('profile/', ProfileEdit.as_view(), name='profile_edit'),
    path('locale/<route>/', SetLocale.as_view(), name='locale'),
]