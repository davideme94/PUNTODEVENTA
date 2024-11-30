from django.shortcuts import render,redirect
from .models import Venta
from .models import Producto
from .models import ConfiguracionTicket
from django.shortcuts import get_object_or_404
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from .models import Producto, Venta, DetalleVenta
from django.db.models import Prefetch
from django.http import JsonResponse
from .models import Proveedor, RetiroEfectivo
from datetime import date
from django.db.models import Sum, DateField
from django.db.models.functions import TruncDate
from datetime import date

def cajero(request):
    productos_cajero = request.session.get('productos_cajero', [])
    total = sum(item['subtotal'] for item in productos_cajero)
    producto_inexistente = None
    cambio = None

    if request.method == "POST":
        if "actualizar_id" in request.POST:
            actualizar_id = int(request.POST.get("actualizar_id"))
            nuevo_precio = float(request.POST.get("nuevo_precio"))

            for item in productos_cajero:
                if item['id'] == actualizar_id:
                    item['precio'] = nuevo_precio
                    item['subtotal'] = item['cantidad'] * nuevo_precio
                    break

            producto = Producto.objects.get(id=actualizar_id)
            producto.precio = Decimal(nuevo_precio)
            producto.save()

            request.session['productos_cajero'] = productos_cajero

        elif "codigo_barra" in request.POST:
            codigo_barra = request.POST.get("codigo_barra")
            precio = request.POST.get("precio", None)

            producto = Producto.objects.filter(codigo_barra=codigo_barra).first()

            if producto:
                for item in productos_cajero:
                    if item['id'] == producto.id:
                        item['cantidad'] += 1
                        item['subtotal'] = float(item['cantidad'] * producto.precio)
                        break
                else:
                    productos_cajero.append({
                        'id': producto.id,
                        'nombre': producto.nombre,
                        'precio': float(producto.precio),
                        'cantidad': 1,
                        'subtotal': float(producto.precio),
                    })
                request.session['productos_cajero'] = productos_cajero
            else:
                producto_inexistente = {"codigo_barra": codigo_barra}

        elif "agregar_inexistente" in request.POST:
            codigo_barra = request.POST.get("codigo_barra_inexistente")
            nombre = request.POST.get("nombre_inexistente")
            precio = float(request.POST.get("precio_inexistente"))

            producto = Producto.objects.create(
                codigo_barra=codigo_barra,
                nombre=nombre,
                precio=Decimal(precio)
            )

            productos_cajero.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': precio,
                'cantidad': 1,
                'subtotal': precio,
            })
            request.session['productos_cajero'] = productos_cajero

        elif "agregar_manual" in request.POST:
            # Lógica para agregar productos manualmente
            nombre_manual = request.POST.get("nombre_manual")
            precio_manual = float(request.POST.get("precio_manual"))

            productos_cajero.append({
                'id': len(productos_cajero) + 1,  # Generar un ID temporal único
                'nombre': nombre_manual,
                'precio': precio_manual,
                'cantidad': 1,
                'subtotal': precio_manual,
            })
            request.session['productos_cajero'] = productos_cajero

        elif "eliminar_id" in request.POST:
            eliminar_id = int(request.POST.get("eliminar_id"))
            productos_cajero = [item for item in productos_cajero if item['id'] != eliminar_id]
            request.session['productos_cajero'] = productos_cajero

        elif "monto_pago" in request.POST:
            monto_pago = float(request.POST.get("monto_pago"))
            if monto_pago >= total:
                cambio = round(monto_pago - total, 2)
            else:
                cambio = "Monto insuficiente"

    total = sum(item['subtotal'] for item in productos_cajero)

    return render(request, 'ventas/cajero.html', {
        'productos_cajero': productos_cajero,
        'total': total,
        'producto_inexistente': producto_inexistente,
        'cambio': cambio,
    })




def historial(request):
    ventas = Venta.objects.all()

    if request.method == "POST":
        venta_id = request.POST.get("venta_id")
        Venta.objects.filter(id=venta_id).delete()

    return render(request, "ventas/historial.html", {"ventas": ventas})



def repositorio(request):
    if request.method == "POST":
        producto_id = request.POST.get("producto_id")
        Producto.objects.filter(id=producto_id).delete()

    productos = Producto.objects.all()  # Trae todos los productos
    return render(request, 'ventas/repositorio.html', {'productos': productos})


def agregar_producto(request):
    if request.method == "POST":
        # Extraer los productos enviados como un diccionario
        productos_raw = request.POST.dict()
        productos = []

        # Procesar los productos enviados
        for key, value in productos_raw.items():
            if key.startswith('productos[') and '][' in key:
                try:
                    # Separar índice y campo
                    index, field = key.split('][')
                    index = index.replace('productos[', '')
                    field = field.replace(']', '')

                    # Validar que el índice sea un entero
                    if index.isdigit():
                        index = int(index)

                        # Asegurarse de que el índice exista en la lista de productos
                        while len(productos) <= index:
                            productos.append({})

                        productos[index][field] = value
                except Exception as e:
                    # Registrar errores inesperados (para depuración)
                    print(f"Error procesando clave '{key}': {e}")

        # Crear los productos en la base de datos
        for producto in productos:
            try:
                Producto.objects.create(
                    codigo_barra=producto['codigo_barra'],
                    nombre=producto['nombre'],
                    precio=Decimal(producto['precio']),
                )
            except Exception as e:
                return JsonResponse({'error': str(e)})

        return redirect("repositorio")

    return render(request, "ventas/agregar_producto.html")





def editar_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)

    if request.method == "POST":
        producto.codigo_barra = request.POST.get("codigo_barra")
        producto.nombre = request.POST.get("nombre")
        producto.precio = request.POST.get("precio")
        producto.save()
        return redirect("repositorio")

    return render(request, "ventas/editar_producto.html", {"producto": producto})




def ticket(request):
    configuracion, created = ConfiguracionTicket.objects.get_or_create(id=1)

    if request.method == "POST":
        configuracion.nombre_negocio = request.POST.get("nombre_negocio")
        configuracion.mensaje_final = request.POST.get("mensaje_final")
        configuracion.save()

    return render(request, "ventas/ticket.html", {"configuracion": configuracion})


def imprimir_ticket(request):
    productos_cajero = request.session.get('productos_cajero', [])
    total = sum(item['subtotal'] for item in productos_cajero)
    configuracion = ConfiguracionTicket.objects.first()

    return render(request, 'ventas/imprimir_ticket.html', {
        'productos_cajero': productos_cajero,
        'total': total,
        'fecha': datetime.now(),
        'configuracion': configuracion,
    })




def terminar_compra(request):
    if request.method == "POST":
        productos_cajero = request.session.get("productos_cajero", [])
        if productos_cajero:
            with transaction.atomic():
                # Crear una nueva venta
                total = sum(float(p["subtotal"]) for p in productos_cajero)
                venta = Venta.objects.create(total=total)

                # Crear detalles de la venta
                for producto in productos_cajero:
                    producto_obj = Producto.objects.get(id=producto["id"])
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto_obj,
                        cantidad=producto["cantidad"],
                        subtotal=producto["subtotal"],
                    )

            # Limpiar la lista de productos en sesión
            request.session["productos_cajero"] = []

        return redirect("cajero")




def historial(request):
    # Obtener todas las ventas y prefetch para reducir consultas a la base de datos
    ventas = Venta.objects.prefetch_related(
        Prefetch('detalles', queryset=DetalleVenta.objects.select_related('producto'))
    )

    if request.method == "POST":
        venta_id = request.POST.get("venta_id")
        # Eliminar la venta junto con los detalles relacionados
        Venta.objects.filter(id=venta_id).delete()

    return render(request, "ventas/historial.html", {"ventas": ventas})


def cargar_proveedor(request):
    if request.method == "POST":
        if "eliminar_id" in request.POST:
            proveedor_id = request.POST.get("eliminar_id")
            Proveedor.objects.filter(id=proveedor_id).delete()
        elif "editar_id" in request.POST:
            proveedor_id = request.POST.get("editar_id")
            nuevo_nombre = request.POST.get("nuevo_nombre")
            nuevo_monto = float(request.POST.get("nuevo_monto"))
            proveedor = Proveedor.objects.get(id=proveedor_id)
            proveedor.nombre = nuevo_nombre
            proveedor.monto_pagado = nuevo_monto
            proveedor.save()
        else:
            nombre = request.POST.get("nombre")
            monto_pagado = float(request.POST.get("monto_pagado"))
            Proveedor.objects.create(nombre=nombre, monto_pagado=monto_pagado)
        return redirect("cargar_proveedor")

    # Agrupar totales por fecha
    totales_por_dia = (
        Proveedor.objects.annotate(dia=TruncDate('fecha'))  # Agrupa por fecha
        .values('dia')  # Selecciona la fecha
        .annotate(total=Sum('monto_pagado'))  # Suma los montos de ese día
        .order_by('-dia')  # Ordena por fecha descendente
    )

    proveedores = Proveedor.objects.all()

    return render(request, "ventas/cargar_proveedor.html", {
        "proveedores": proveedores,
        "totales_por_dia": totales_por_dia,
    })




def registrar_retiro(request):
    if request.method == "POST":
        if "eliminar_id" in request.POST:
            retiro_id = request.POST.get("eliminar_id")
            RetiroEfectivo.objects.filter(id=retiro_id).delete()
        elif "editar_id" in request.POST:
            retiro_id = request.POST.get("editar_id")
            nuevo_cliente = request.POST.get("nuevo_cliente")
            nueva_cantidad = float(request.POST.get("nueva_cantidad"))
            retiro = RetiroEfectivo.objects.get(id=retiro_id)
            retiro.cliente = nuevo_cliente
            retiro.cantidad = nueva_cantidad
            retiro.save()
        else:
            cliente = request.POST.get("cliente")
            cantidad = float(request.POST.get("cantidad"))
            RetiroEfectivo.objects.create(cliente=cliente, cantidad=cantidad)
        return redirect("registrar_retiro")

    # Calcular totales diarios
    totales_por_dia = (
        RetiroEfectivo.objects.annotate(dia=TruncDate('fecha'))  # Agrupa por fecha
        .values('dia')  # Selecciona la fecha
        .annotate(total=Sum('cantidad'))  # Suma las cantidades de ese día
        .order_by('-dia')  # Ordena por fecha descendente
    )

    retiros = RetiroEfectivo.objects.all()

    return render(request, "ventas/registrar_retiro.html", {
        "retiros": retiros,
        "totales_por_dia": totales_por_dia,
    })
