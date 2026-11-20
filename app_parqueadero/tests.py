"""Pruebas de verificación para los criterios 1.1 a 2.4 sin alterar la BD ni los triggers."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.db.models.functions import Now
from django.test import SimpleTestCase

from .models import (
    Bitacora,
    BitacoraMovimientos,
    Estacionamiento,
    Estacionamientos,
    Pago,
    Pagos,
    Vehiculo,
    Vehiculos,
)
from .services import ParqueaderoService

BASE_DIR = Path(__file__).resolve().parent.parent


class TestRubricaEtapas1Y2(SimpleTestCase):
    # ------------------------------------------------------------------
    # Criterio 1.1: Diagrama de clases UML
    # ------------------------------------------------------------------
    def test_1_1_diagramas_uml_y_cardinalidad_corregida(self):
        self.assertTrue((BASE_DIR / 'docs' / 'diagramas' / 'clases.png').is_file())
        mmd = (BASE_DIR / 'docs' / 'diagramas' / 'diagrama_clases.mmd').read_text(encoding='utf-8')
        md = (BASE_DIR / 'docs' / 'diagramas' / 'diagrama_clases.md').read_text(encoding='utf-8')

        for entidad in ('class Vehiculos', 'class Estacionamientos', 'class Pagos', 'class BitacoraMovimientos'):
            self.assertIn(entidad, mmd)
        self.assertIn('Vehiculos "1" --> "0..*" Estacionamientos', mmd)
        self.assertIn('Estacionamientos "1" --> "0..1" Pagos', mmd)
        self.assertIn('trg_validar_doble_ingreso', mmd)
        self.assertIn('```mermaid', md)

    # ------------------------------------------------------------------
    # Criterio 1.2: Esquema SQL y triggers intactos
    # ------------------------------------------------------------------
    def test_1_2_sql_tablas_y_triggers_intactos(self):
        sql = (BASE_DIR / 'database' / '01_esquema_y_triggers.sql').read_text(encoding='utf-8')
        sql_upper = sql.upper()
        for tabla in ('VEHICULOS', 'ESTACIONAMIENTOS', 'PAGOS', 'BITACORA_MOVIMIENTOS'):
            self.assertIn(f'CREATE TABLE IF NOT EXISTS {tabla}', sql_upper)
        for trigger in (
            'TRG_VALIDAR_DOBLE_INGRESO',
            'TRG_REGISTRAR_BITACORA_ENTRADA',
            'TRG_REGISTRAR_BITACORA_SALIDA_ESTADO',
        ):
            self.assertIn(trigger, sql_upper)

    # ------------------------------------------------------------------
    # Criterio 2.1: Clases del dominio POO y configuración ORM segura
    # ------------------------------------------------------------------
    def test_2_1_modelos_oop_y_defaults_compatibles_con_mysql(self):
        self.assertIs(Vehiculo, Vehiculos)
        self.assertIs(Estacionamiento, Estacionamientos)
        self.assertIs(Pago, Pagos)
        self.assertIs(Bitacora, BitacoraMovimientos)

        # managed = False garantiza que Django nunca altere tablas ni triggers MySQL
        for modelo in (Vehiculos, Estacionamientos, Pagos, BitacoraMovimientos):
            self.assertFalse(modelo._meta.managed)

        # hora_entrada delegada a MySQL y estado_parqueo por defecto ACTIVO
        campo_hora = Estacionamientos._meta.get_field('hora_entrada')
        campo_estado = Estacionamientos._meta.get_field('estado_parqueo')
        self.assertIsInstance(campo_hora.db_default, Now)
        self.assertEqual(campo_estado.default, 'ACTIVO')

        pago = Pagos(id_estacionamiento_id=1, valor_total=Decimal('4000.00'))
        pago.clean()
        self.assertFalse(pago.esta_pagado())

        pago_negativo = Pagos(id_estacionamiento_id=1, valor_total=Decimal('-100.00'))
        with self.assertRaises(ValidationError):
            pago_negativo.clean()

    # ------------------------------------------------------------------
    # Criterio 2.2: Validación de placas y campos obligatorios
    # ------------------------------------------------------------------
    def test_2_2_validacion_vehiculos(self):
        for placa_valida, esperado in (
            ('abc-123', 'ABC123'),
            ('xyz 45d', 'XYZ45D'),
            ('abc123d', 'ABC123D'),
        ):
            v = Vehiculos(placa=placa_valida, tipo_vehiculo='Moto', marca='Yamaha')
            v.clean()
            self.assertEqual(v.placa, esperado)

        for placa_invalida in ('', '   ', '123', '123ABC', 'AB!@#1'):
            v = Vehiculos(placa=placa_invalida, tipo_vehiculo='Carro', marca='Mazda')
            with self.assertRaises(ValidationError):
                v.clean()

        with self.assertRaises(ValidationError):
            Vehiculos(placa='ABC123', tipo_vehiculo='   ', marca='Mazda').clean()

        with self.assertRaises(ValidationError):
            Vehiculos(placa='ABC123', tipo_vehiculo='Carro', marca='   ').clean()

    # ------------------------------------------------------------------
    # Criterio 2.3: Registro de entrada automático con hora MySQL + triggers
    # ------------------------------------------------------------------
    @patch('app_parqueadero.models.Estacionamientos.objects')
    @patch('app_parqueadero.models.Vehiculos.objects')
    @patch('app_parqueadero.models.connection')
    def test_2_3_entrada_automatica_omite_hora_en_python(
        self, mock_conn, mock_veh_mgr, mock_est_mgr
    ):
        mock_veh_mgr.filter.return_value.exists.return_value = True
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 42
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        hora_mysql = datetime(2026, 11, 20, 10, 45, 0)
        esperado = Estacionamientos(
            id_estacionamiento=42,
            placa_vehiculo_id='ABC123',
            hora_entrada=hora_mysql,
            estado_parqueo='ACTIVO',
        )
        mock_est_mgr.select_related.return_value.get.return_value = esperado

        resultado = ParqueaderoService.registrar_entrada_automatica('abc-123')

        self.assertEqual(resultado.hora_entrada, hora_mysql)
        self.assertEqual(resultado.estado_parqueo, 'ACTIVO')
        sql_ejecutado, params = mock_cursor.execute.call_args[0]
        self.assertEqual(sql_ejecutado, 'INSERT INTO estacionamientos (placa_vehiculo) VALUES (%s)')
        self.assertEqual(params, ['ABC123'])

    @patch('app_parqueadero.models.Vehiculos.objects')
    @patch('app_parqueadero.models.connection')
    def test_2_3_propaga_bloqueo_de_trigger_doble_entrada(self, mock_conn, mock_veh_mgr):
        mock_veh_mgr.filter.return_value.exists.return_value = True
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = DatabaseError(
            "Error: El vehículo ya cuenta con un registro de entrada ACTIVO."
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        with self.assertRaises(ValidationError) as ctx:
            ParqueaderoService.registrar_entrada_automatica('ABC123')
        self.assertIn('Trigger', str(ctx.exception))

    # ------------------------------------------------------------------
    # Criterio 2.4: Consulta directa de hora, estado actual e historial
    # ------------------------------------------------------------------
    @patch('app_parqueadero.services.BitacoraMovimientos.consultar_por_placa')
    @patch('app_parqueadero.services.Estacionamientos.objects')
    @patch('app_parqueadero.services.Vehiculos.objects')
    @patch('app_parqueadero.services.connection')
    def test_2_4_consulta_hora_estado_e_historial(
        self, mock_conn, mock_veh_mgr, mock_est_mgr, mock_bitacora
    ):
        ahora_mysql = datetime(2026, 11, 20, 11, 15, 0)
        entrada_mysql = datetime(2026, 11, 20, 10, 45, 0)

        mock_veh_mgr.filter.return_value.first.return_value = Vehiculos(
            placa='ABC123', tipo_vehiculo='Carro', marca='Renault'
        )
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (ahora_mysql,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        est = Estacionamientos(
            id_estacionamiento=42,
            placa_vehiculo_id='ABC123',
            hora_entrada=entrada_mysql,
            estado_parqueo='ACTIVO',
        )
        mock_est_mgr.filter.return_value.order_by.return_value = [est]
        mock_bitacora.return_value = [
            BitacoraMovimientos(
                id_bitacora=1,
                placa_referencia='ABC123',
                evento='Ingreso registrado. Estado: ACTIVO',
                fecha_evento=entrada_mysql,
            )
        ]

        reporte = ParqueaderoService.consultar_estado_y_historial('abc-123')
        self.assertEqual(reporte['hora_actual_mysql'], ahora_mysql)
        self.assertEqual(reporte['estacionamiento_actual'].estado_parqueo, 'ACTIVO')
        self.assertEqual(reporte['estacionamiento_actual'].hora_entrada, entrada_mysql)
        self.assertEqual(len(reporte['historial_movimientos']), 1)
