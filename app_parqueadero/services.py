"""Servicios de aplicación para los criterios 2.1 a 2.4.

Interactúa directamente con MySQL respetando intactos los triggers existentes:
- `trg_validar_doble_ingreso` (BEFORE INSERT ON estacionamientos)
- `trg_registrar_bitacora_entrada` (AFTER INSERT ON estacionamientos)
- `trg_registrar_bitacora_salida_estado` (AFTER UPDATE ON estacionamientos)
"""

from __future__ import annotations

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, connection

from .models import BitacoraMovimientos, Estacionamientos, Vehiculos


class ParqueaderoService:
    """Casos de uso de las etapas 2.1 a 2.4 sobre MySQL."""

    # ------------------------------------------------------------------
    # Criterio 2.1: Verificación de conexión y reloj de MySQL
    # ------------------------------------------------------------------
    @staticmethod
    def verificar_conexion_mysql() -> dict[str, Any]:
        """Consulta directamente al motor MySQL la BD activa, versión y hora actual."""
        with connection.cursor() as cursor:
            cursor.execute('SELECT DATABASE(), VERSION(), NOW()')
            base_datos, version_mysql, hora_motor_mysql = cursor.fetchone()
        return {
            'base_datos': base_datos,
            'version_mysql': version_mysql,
            'hora_motor_mysql': hora_motor_mysql,
        }

    # ------------------------------------------------------------------
    # Criterio 2.2: Registro y listado de vehículos con validaciones
    # ------------------------------------------------------------------
    @staticmethod
    def registrar_vehiculo(placa: str, tipo_vehiculo: str, marca: str) -> Vehiculos:
        """Valida formato de placa y campos obligatorios, y guarda el vehículo en MySQL."""
        try:
            return Vehiculos.registrar_vehiculo(
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
                marca=marca,
            )
        except IntegrityError as exc:
            placa_norm = Vehiculos.normalizar_placa(placa)
            raise ValidationError(
                {'placa': [f"Ya existe un vehículo registrado con la placa '{placa_norm}'."]}
            ) from exc

    @staticmethod
    def listar_vehiculos():
        """Retorna todos los vehículos almacenados en MySQL ordenados por placa."""
        return Vehiculos.objects.all().order_by('placa')

    # ------------------------------------------------------------------
    # Criterio 2.3: Registro de entrada automático (hora generada por MySQL)
    # ------------------------------------------------------------------
    @staticmethod
    def registrar_entrada_automatica(placa: str) -> Estacionamientos:
        """Registra una entrada delegando fecha/hora y bitácora al motor MySQL.

        - No recibe ni solicita hora manual en Python.
        - Ejecuta `INSERT INTO estacionamientos (placa_vehiculo) VALUES (%s)`.
        - MySQL asigna `hora_entrada` con `DEFAULT CURRENT_TIMESTAMP` y
          `estado_parqueo` con `DEFAULT 'ACTIVO'`.
        - MySQL ejecuta `trg_validar_doble_ingreso` (bloquea doble entrada activa)
          y `trg_registrar_bitacora_entrada` (registra el evento en bitácora).
        """
        try:
            return Estacionamientos.crear_entrada(placa)
        except DatabaseError as exc:
            raise ValidationError(
                f'Bloqueo de seguridad del motor MySQL (Trigger): {exc}'
            ) from exc

    # ------------------------------------------------------------------
    # Criterio 2.4: Consulta directa a MySQL de hora, estado e historial
    # ------------------------------------------------------------------
    @staticmethod
    def consultar_estado_y_historial(placa: str) -> dict[str, Any]:
        """Consulta directamente a MySQL la hora exacta, estado actual e historial."""
        placa_norm = Vehiculos.validar_placa(placa)

        vehiculo = Vehiculos.objects.filter(placa=placa_norm).first()
        if vehiculo is None:
            raise ValidationError(
                f"No existe ningún vehículo registrado con la placa '{placa_norm}'."
            )

        with connection.cursor() as cursor:
            cursor.execute('SELECT NOW()')
            (hora_actual_mysql,) = cursor.fetchone()

        estacionamientos = list(
            Estacionamientos.objects.filter(placa_vehiculo_id=placa_norm).order_by(
                '-hora_entrada', '-id_estacionamiento'
            )
        )
        estacionamiento_actual = estacionamientos[0] if estacionamientos else None
        movimientos = list(BitacoraMovimientos.consultar_por_placa(placa_norm))

        return {
            'hora_actual_mysql': hora_actual_mysql,
            'vehiculo': vehiculo,
            'estacionamiento_actual': estacionamiento_actual,
            'historial_estacionamientos': estacionamientos,
            'historial_movimientos': movimientos,
        }

    @staticmethod
    def listar_estacionamientos(estado: Optional[str] = None) -> dict[str, Any]:
        """Consulta en MySQL los registros de estacionamiento (opcionalmente filtrados)."""
        estado_norm = estado.strip().upper() if estado else None
        estados_validos = {e[0] for e in Estacionamientos.ESTADOS_PARQUEO}
        if estado_norm and estado_norm not in estados_validos:
            raise ValidationError(
                f"Estado inválido '{estado_norm}'. Use: {', '.join(sorted(estados_validos))}."
            )

        with connection.cursor() as cursor:
            cursor.execute('SELECT NOW()')
            (hora_actual_mysql,) = cursor.fetchone()

        qs = Estacionamientos.objects.select_related('placa_vehiculo').order_by(
            '-hora_entrada', '-id_estacionamiento'
        )
        if estado_norm:
            qs = qs.filter(estado_parqueo=estado_norm)

        return {
            'hora_actual_mysql': hora_actual_mysql,
            'estacionamientos': list(qs),
        }

    @staticmethod
    def consultar_bitacora(
        placa: Optional[str] = None,
        limite: int = 30,
    ) -> dict[str, Any]:
        """Consulta el historial de movimientos generados por los triggers en MySQL."""
        if limite <= 0:
            raise ValidationError('El límite de registros debe ser mayor que cero.')

        with connection.cursor() as cursor:
            cursor.execute('SELECT NOW()')
            (hora_actual_mysql,) = cursor.fetchone()

        qs = BitacoraMovimientos.objects.all().order_by('-fecha_evento', '-id_bitacora')
        if placa:
            placa_norm = Vehiculos.normalizar_placa(placa)
            qs = qs.filter(placa_referencia=placa_norm)

        return {
            'hora_actual_mysql': hora_actual_mysql,
            'movimientos': list(qs[:limite]),
        }
