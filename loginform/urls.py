from django.contrib import admin
from django.urls import path
from logindata import views
from logindata.views import CartView, payment, order_create

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('products/', views.ProductView.as_view(), name='products'),
    path('add_products/', views.ProductAddView.as_view(), name='add_products'),
    path('search_products/', views.ProductSearchView.as_view(), name='search_products'),
    path('products/delete/<int:pk>/', views.ProductDeleteView.as_view(), name='delete_product'),
    path('products/update/<int:pk>/', views.ProductUpdateView.as_view(), name='update_product'),
    path('cart/', CartView.as_view(), name='cart'),
    path('payment/', payment, name='payment'),
    path('order-create/', order_create, name='order-create'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.registration_view, name='register'),

]
