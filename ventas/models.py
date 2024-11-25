from django.db import models

class Producto(models.Model):
    codigo_barra = models.CharField(max_length=50, unique=True, verbose_name="Código de Barra")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de la Venta")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total de la Venta")

    def __str__(self):
        return f"Venta #{self.id} - ${self.total} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles", verbose_name="Venta")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    def calcular_subtotal(self):
        self.subtotal = self.cantidad * self.producto.precio
        self.save()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} (${self.subtotal})"

class ConfiguracionTicket(models.Model):
    nombre_negocio = models.CharField(max_length=100, default="Mi Negocio", verbose_name="Nombre del Negocio")
    direccion = models.CharField(max_length=200, blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=15, blank=True, verbose_name="Teléfono")
    mensaje_final = models.TextField(blank=True, default="Gracias por su compra", verbose_name="Mensaje Final")

    def __str__(self):
        return self.nombre_negocio



class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class RetiroEfectivo(models.Model):
    cliente = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cliente
