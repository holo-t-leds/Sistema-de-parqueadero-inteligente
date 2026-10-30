from django.contrib import admin, messages
from django.db import DatabaseError
from django.utils import timezone
from decimal import Decimal
from .models import Vehiculos, Estacionamientos, Pagos, BitacoraMovimientos

@admin.register(Vehiculos)
class VehiculosAdmin(admin.ModelAdmin):
    list_display = ('placa', 'tipo_vehiculo', 'marca')

@admin.register(Estacionamientos)
class EstacionamientosAdmin(admin.ModelAdmin):
    list_display = ('id_estacionamiento', 'placa_vehiculo', 'hora_entrada', 'hora_salida', 'estado_parqueo')
    exclude = ('hora_entrada', 'hora_salida')
    # Añadimos los botones de acción personalizados
    actions = ['registrar_salida_pagada', 'registrar_salida_sin_pago']

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
            obj.refresh_from_db()
        except DatabaseError as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, f"Bloqueo de seguridad (Trigger): {e}")

    @admin.action(description='1. Registrar salida PAGADA (Calcula cobro)')
    def registrar_salida_pagada(self, request, queryset):
        TARIFA_HORA = Decimal('2000.00')
        for est in queryset.filter(estado_parqueo='ACTIVO'):
            est.hora_salida = timezone.now()
            
            # Cálculo de tiempo (Regla ii)
            tiempo = est.hora_salida - est.hora_entrada
            horas = Decimal(tiempo.total_seconds() / 3600)
            horas_cobradas = Decimal(1) if horas < 1 else round(horas, 2)
            total = horas_cobradas * TARIFA_HORA
            
            # Actualizamos el estado
            est.estado_parqueo = 'FINALIZADO'
            est.save()
            
            # Generamos el comprobante en la tabla Pagos
            Pagos.objects.create(
                # Dependiendo de cómo lo nombró inspectdb, usamos _id
                id_estacionamiento_id=est.id_estacionamiento,
                valor_total=total,
                estado_pago='PAGADO'
            )
        self.message_user(request, "Salidas pagadas y liquidadas con éxito.")

    @admin.action(description='2. Registrar salida SIN PAGO (Moroso)')
    def registrar_salida_sin_pago(self, request, queryset):
        for est in queryset.filter(estado_parqueo='ACTIVO'):
            est.hora_salida = timezone.now()
            # Cambiamos estado a MOROSO (Regla iii)
            est.estado_parqueo = 'MOROSO'
            est.save()
            
            # Dejamos una deuda pendiente en la tabla Pagos
            Pagos.objects.create(
                id_estacionamiento_id=est.id_estacionamiento,
                valor_total=Decimal('0.00'),
                estado_pago='PENDIENTE'
            )
        self.message_user(request, "Vehículo registrado como MOROSO (Fuga).", level=messages.WARNING)

@admin.register(Pagos)
class PagosAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'id_estacionamiento', 'valor_total', 'estado_pago')

@admin.register(BitacoraMovimientos)
class BitacoraMovimientosAdmin(admin.ModelAdmin):
    list_display = ('id_bitacora', 'placa_referencia', 'evento', 'fecha_evento')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False