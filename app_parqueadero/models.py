"""Modelos de dominio ORM (Criterios 2.1, 2.2, 2.3 y 2.4).

Mantiene `managed = False` y los nombres exactos de tablas y columnas de
`database/01_esquema_y_triggers.sql` para convivir intactamente con los
triggers y reglas de negocio del motor MySQL.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import re

from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.models.functions import Now


PATRON_PLACA = re.compile(r'^[A-Z]{3}[0-9]{2,3}[A-Z]?$')


class Vehiculos(models.Model):
    """Entidad de dominio Vehículo (tabla `vehiculos`)."""

    TIPOS_SUGERIDOS = (
        ('Carro', 'Carro'),
        ('Moto', 'Moto'),
        ('Camioneta', 'Camioneta'),
        ('Bicicleta', 'Bicicleta'),
    )

    placa = models.CharField(primary_key=True, max_length=10)
    tipo_vehiculo = models.CharField(max_length=20)
    marca = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vehiculos'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    @staticmethod
    def normalizar_placa(placa: str) -> str:
        """Elimina espacios y guiones y convierte la placa a mayúsculas."""
        if not isinstance(placa, str):
            return ''
        return re.sub(r'[\s-]+', '', placa).upper()

    @classmethod
    def validar_placa(cls, placa: str) -> str:
        """Normaliza y valida el formato de placa (ej. ABC123, ABC12D, ABC123D)."""
        placa_norm = cls.normalizar_placa(placa)
        if not placa_norm:
            raise ValidationError('La placa es obligatoria y no puede estar vacía.')
        if len(placa_norm) > 10:
            raise ValidationError('La placa no puede superar los 10 caracteres.')
        if not PATRON_PLACA.match(placa_norm):
            raise ValidationError(
                f"Formato de placa inválido '{placa_norm}'. "
                'Use formatos válidos como ABC123, ABC12D o ABC123D.'
            )
        return placa_norm

    def clean(self) -> None:
        """Valida formato de placa y obligatoriedad de campos no vacíos (Criterio 2.2)."""
        errores = {}

        try:
            self.placa = self.validar_placa(self.placa)
        except ValidationError as exc:
            errores['placa'] = exc.messages

        tipo_limpio = (self.tipo_vehiculo or '').strip()
        if not tipo_limpio:
            errores['tipo_vehiculo'] = ['El tipo de vehículo es obligatorio y no puede estar vacío.']
        elif len(tipo_limpio) > 20:
            errores['tipo_vehiculo'] = ['El tipo de vehículo no puede superar 20 caracteres.']
        else:
            self.tipo_vehiculo = tipo_limpio

        marca_limpia = (self.marca or '').strip()
        if not marca_limpia:
            errores['marca'] = ['La marca del vehículo es obligatoria y no puede estar vacía.']
        elif len(marca_limpia) > 30:
            errores['marca'] = ['La marca no puede superar 30 caracteres.']
        else:
            self.marca = marca_limpia

        if errores:
            raise ValidationError(errores)

    @classmethod
    def registrar_vehiculo(cls, placa: str, tipo_vehiculo: str, marca: str) -> 'Vehiculos':
        """Valida y registra un nuevo vehículo en MySQL verificando unicidad de placa."""
        vehiculo = cls(placa=placa, tipo_vehiculo=tipo_vehiculo, marca=marca)
        vehiculo.full_clean(validate_unique=False)
        if cls.objects.filter(placa=vehiculo.placa).exists():
            raise ValidationError(
                {'placa': [f"Ya existe un vehículo registrado con la placa '{vehiculo.placa}'."]}
            )
        vehiculo.save(force_insert=True)
        return vehiculo

    def tiene_estacionamiento_activo(self) -> bool:
        """Consulta en MySQL si el vehículo tiene actualmente un estacionamiento ACTIVO."""
        return Estacionamientos.objects.filter(
            placa_vehiculo_id=self.placa,
            estado_parqueo=Estacionamientos.ESTADO_ACTIVO,
        ).exists()

    def consultar_historial(self):
        """Retorna el historial cronológico de movimientos en bitácora para esta placa."""
        return BitacoraMovimientos.consultar_por_placa(self.placa)

    def __str__(self) -> str:
        marca_txt = f' - {self.marca}' if self.marca else ''
        return f'{self.placa} ({self.tipo_vehiculo}{marca_txt})'


class Estacionamientos(models.Model):
    """Entidad de dominio Estacionamiento (tabla `estacionamientos`).

    Criterio 2.3: `hora_entrada` usa `db_default=Now()` para que Django delegue
    la generación de la marca de tiempo al motor MySQL (`CURRENT_TIMESTAMP`) en
    lugar de enviar `NULL` o la hora local de Python.
    """

    ESTADO_ACTIVO = 'ACTIVO'
    ESTADO_FINALIZADO = 'FINALIZADO'
    ESTADO_MOROSO = 'MOROSO'
    ESTADOS_PARQUEO = (
        (ESTADO_ACTIVO, 'Activo'),
        (ESTADO_FINALIZADO, 'Finalizado'),
        (ESTADO_MOROSO, 'Moroso'),
    )

    id_estacionamiento = models.AutoField(primary_key=True)
    placa_vehiculo = models.ForeignKey(
        'Vehiculos',
        models.CASCADE,
        db_column='placa_vehiculo',
    )
    hora_entrada = models.DateTimeField(
        blank=True,
        null=True,
        db_default=Now(),
        editable=False,
    )
    hora_salida = models.DateTimeField(blank=True, null=True)
    estado_parqueo = models.CharField(
        max_length=10,
        choices=ESTADOS_PARQUEO,
        default=ESTADO_ACTIVO,
        db_default=ESTADO_ACTIVO,
    )

    class Meta:
        managed = False
        db_table = 'estacionamientos'
        verbose_name = 'Estacionamiento'
        verbose_name_plural = 'Estacionamientos'

    def clean(self) -> None:
        estados_validos = {e[0] for e in self.ESTADOS_PARQUEO}
        if not self.estado_parqueo:
            self.estado_parqueo = self.ESTADO_ACTIVO
        elif self.estado_parqueo not in estados_validos:
            raise ValidationError(
                {'estado_parqueo': [f"Estado inválido '{self.estado_parqueo}'."]}
            )

    def esta_activo(self) -> bool:
        """Retorna True si el vehículo permanece dentro del parqueadero."""
        return self.estado_parqueo == self.ESTADO_ACTIVO

    @classmethod
    def crear_entrada(cls, placa: str) -> 'Estacionamientos':
        """Registra una entrada delegando hora_entrada, estado y triggers al motor MySQL.

        Al omitir `hora_entrada` y `estado_parqueo` en el INSERT:
        - MySQL aplica `DEFAULT CURRENT_TIMESTAMP` y `DEFAULT 'ACTIVO'`.
        - Se dispara `trg_validar_doble_ingreso` (BEFORE INSERT).
        - Se dispara `trg_registrar_bitacora_entrada` (AFTER INSERT).
        """
        placa_norm = Vehiculos.validar_placa(placa)
        if not Vehiculos.objects.filter(placa=placa_norm).exists():
            raise ValidationError(
                f"El vehículo con placa '{placa_norm}' no está registrado. "
                'Regístrelo primero antes de crear una entrada.'
            )

        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO estacionamientos (placa_vehiculo) VALUES (%s)',
                [placa_norm],
            )
            nuevo_id = cursor.lastrowid

        return cls.objects.select_related('placa_vehiculo').get(
            id_estacionamiento=nuevo_id
        )

    def consultar_estado(self) -> dict:
        """Retorna un resumen estructurado del estado y marca de tiempo asignada por MySQL."""
        return {
            'id_estacionamiento': self.id_estacionamiento,
            'placa_vehiculo': self.placa_vehiculo_id,
            'hora_entrada': self.hora_entrada,
            'hora_salida': self.hora_salida,
            'estado_parqueo': self.estado_parqueo,
        }

    def resumen_estado(self) -> str:
        """Devuelve una representación legible del registro de estacionamiento."""
        entrada_txt = (
            self.hora_entrada.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(self.hora_entrada, datetime)
            else 'Asignada por MySQL'
        )
        salida_txt = (
            self.hora_salida.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(self.hora_salida, datetime)
            else 'En curso'
        )
        return (
            f'[#{self.id_estacionamiento}] Placa: {self.placa_vehiculo_id} | '
            f'Estado: {self.estado_parqueo} | Entrada (MySQL): {entrada_txt} | '
            f'Salida: {salida_txt}'
        )

    def __str__(self) -> str:
        return self.resumen_estado()


class Pagos(models.Model):
    """Entidad de dominio Pago (tabla `pagos`)."""

    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_PAGADO = 'PAGADO'
    ESTADOS_PAGO = (
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_PAGADO, 'Pagado'),
    )

    id_pago = models.AutoField(primary_key=True)
    id_estacionamiento = models.ForeignKey(
        Estacionamientos,
        models.CASCADE,
        db_column='id_estacionamiento',
    )
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago = models.CharField(
        max_length=9,
        choices=ESTADOS_PAGO,
        default=ESTADO_PENDIENTE,
        db_default=ESTADO_PENDIENTE,
    )

    class Meta:
        managed = False
        db_table = 'pagos'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def clean(self) -> None:
        if self.valor_total is None or Decimal(self.valor_total) < Decimal('0.00'):
            raise ValidationError(
                {'valor_total': ['El valor total del pago no puede ser negativo.']}
            )
        estados_validos = {e[0] for e in self.ESTADOS_PAGO}
        if not self.estado_pago:
            self.estado_pago = self.ESTADO_PENDIENTE
        elif self.estado_pago not in estados_validos:
            raise ValidationError(
                {'estado_pago': [f"Estado de pago inválido '{self.estado_pago}'."]}
            )

    def esta_pagado(self) -> bool:
        """Indica si el pago fue liquidado."""
        return self.estado_pago == self.ESTADO_PAGADO

    def asentar_pago(self) -> bool:
        """Marca el pago como PAGADO y persiste el cambio en MySQL."""
        if self.esta_pagado():
            return False
        self.estado_pago = self.ESTADO_PAGADO
        self.save(update_fields=['estado_pago'])
        return True

    def __str__(self) -> str:
        return (
            f'Pago #{self.id_pago} | Estacionamiento #{self.id_estacionamiento_id} | '
            f'${self.valor_total} ({self.estado_pago})'
        )


class BitacoraMovimientos(models.Model):
    """Entidad de auditoría poblada automáticamente por los triggers de MySQL."""

    id_bitacora = models.AutoField(primary_key=True)
    placa_referencia = models.CharField(max_length=10)
    evento = models.CharField(max_length=100)
    fecha_evento = models.DateTimeField(
        blank=True,
        null=True,
        db_default=Now(),
        editable=False,
    )

    class Meta:
        managed = False
        db_table = 'bitacora_movimientos'
        verbose_name = 'Movimiento de Bitácora'
        verbose_name_plural = 'Bitácora de Movimientos'

    @classmethod
    def consultar_por_placa(cls, placa: str):
        """Retorna los movimientos de bitácora ordenados del más reciente al más antiguo."""
        placa_norm = Vehiculos.normalizar_placa(placa)
        return cls.objects.filter(placa_referencia=placa_norm).order_by(
            '-fecha_evento', '-id_bitacora'
        )

    def __str__(self) -> str:
        fecha_txt = (
            self.fecha_evento.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(self.fecha_evento, datetime)
            else str(self.fecha_evento or '-')
        )
        return f'[{fecha_txt}] {self.placa_referencia} - {self.evento}'


# Alias en singular para compatibilidad con nombres del diagrama UML
Vehiculo = Vehiculos
Estacionamiento = Estacionamientos
Pago = Pagos
Bitacora = BitacoraMovimientos
