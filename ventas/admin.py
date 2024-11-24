from django.contrib import admin
from .models import Producto, Venta, DetalleVenta, ConfiguracionTicket

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo_barra', 'nombre', 'precio')
    search_fields = ('codigo_barra', 'nombre')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'total')
    search_fields = ('id',)

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'subtotal')

@admin.register(ConfiguracionTicket)
class ConfiguracionTicketAdmin(admin.ModelAdmin):
    list_display = ('nombre_negocio', 'mensaje_final')
