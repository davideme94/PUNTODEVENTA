from django.urls import path
from . import views

urlpatterns = [
    path('', views.cajero, name='cajero'),  # Página principal
    path('historial/', views.historial, name='historial'),
    path('repositorio/', views.repositorio, name='repositorio'),
    path('ticket/', views.ticket, name='ticket'),
    path('repositorio/agregar/', views.agregar_producto, name='agregar_producto'),
    path('repositorio/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('imprimir-ticket/', views.imprimir_ticket, name='imprimir_ticket'),
    path('cajero/terminar_compra/', views.terminar_compra, name='terminar_compra'),
    path("cargar_proveedor/", views.cargar_proveedor, name="cargar_proveedor"),
    path("registrar_retiro/", views.registrar_retiro, name="registrar_retiro"),

]

