from django.urls import path, include

from . import views
urlpatterns = [
        path('', include('djoser.urls')),
        path('', include('djoser.urls.authtoken')),
        path('categories', views.CategoryListView.as_view()),
        path('menu-items', views.MenuItemListView.as_view()),
        path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
        path('cart/menu-items', views.CartListView.as_view()),
        path('groups/manager/users', views.ManagerView.as_view()),
        path('groups/manager/users/<int:pk>', views.ManagerDestroyView.as_view()),
        path('groups/delivery-crew/users', views.DeliveryView.as_view()),
        path('groups/delivery-crew/users/<int:pk>', views.DeliveryDestroyView.as_view()),
        path('orders', views.OrderListView.as_view()),
        path('orders/<int:pk>', views.SingleOrderView.as_view()),
]