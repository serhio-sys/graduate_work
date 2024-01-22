from django.urls import path
from .views import SelectClassView, InventoryView,OutskirtsLocation, ChurchLocation, equip_armor, equip_weapon, buy_weapon, buy_armor, MainLocationView, back_to_starter_page, CityLocation, get_start_game_page, ShopLocation

urlpatterns = [
    path('', SelectClassView.as_view(), name='select_class'),
    path('start/', get_start_game_page, name='start' ),
    path('main/', MainLocationView.as_view(), name='main_loc'),
    path('shop/', ShopLocation.as_view(), name='shop_loc'),
    path('city/', CityLocation.as_view(), name='city_loc'),
    path('outskirts/', OutskirtsLocation.as_view(), name='outskirts_loc'),
    path('inventory/<name>', InventoryView.as_view(), name='inventory'),
    path('church/', ChurchLocation.as_view(), name='church_loc'),
    path('buy_weapon/<pk>', buy_weapon, name='buy_w'),
    path('buy_armor/<pk>', buy_armor, name='buy_a'),
    path('equip_armor/', equip_armor, name='equip_a'),
    path('equip_weapon/', equip_weapon, name='equip_w'),
    path('back_to_start/<name>', back_to_starter_page, name='back_to_main')
]