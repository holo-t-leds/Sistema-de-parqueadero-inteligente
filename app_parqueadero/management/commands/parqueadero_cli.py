"""Comando interactivo de consola para demostrar los criterios 2.1 a 2.4."""

from __future__ import annotations

from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import OperationalError

from app_parqueadero.services import ParqueaderoService


def _fmt(valor: object) -> str:
    if isinstance(valor, datetime):
        return valor.strftime('%Y-%m-%d %H:%M:%S')
    return str(valor) if valor is not None else '-'


def _fmt_validacion(exc: ValidationError) -> str:
    if hasattr(exc, 'message_dict'):
        partes = [f'{campo}: {", ".join(msgs)}' for campo, msgs in exc.message_dict.items()]
        return ' | '.join(partes)
    return ' | '.join(exc.messages)


class Command(BaseCommand):
    help = 'Consola interactiva del Sistema de Parqueadero Inteligente (Criterios 2.1 a 2.4).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-connection',
            action='store_true',
            help='Verifica la conexión con MySQL y muestra el reloj del motor.',
        )

    def handle(self, *args, **options):
        if options['check_connection']:
            self._probar_conexion()
            return
        self._ejecutar_menu()

    def _titulo(self, texto: str) -> None:
        self.stdout.write('\n' + '=' * 72)
        self.stdout.write(f'  {texto}')
        self.stdout.write('=' * 72)

    def _probar_conexion(self) -> None:
        self._titulo('2.1 — Prueba de Conexión y Reloj del Motor MySQL')
        info = ParqueaderoService.verificar_conexion_mysql()
        self.stdout.write(f"Base de datos activa : {info['base_datos']}")
        self.stdout.write(f"Versión de MySQL     : {info['version_mysql']}")
        self.stdout.write(f"Fecha/hora MySQL     : {_fmt(info['hora_motor_mysql'])}")

    def _registrar_vehiculo(self) -> None:
        self._titulo('2.2 — Registro de Vehículo')
        placa = input('Placa (ej. ABC123, ABC12D o ABC123D): ').strip()
        tipo = input('Tipo de vehículo (ej. Carro, Moto, Camioneta): ').strip()
        marca = input('Marca (ej. Chevrolet, Yamaha): ').strip()

        vehiculo = ParqueaderoService.registrar_vehiculo(
            placa=placa,
            tipo_vehiculo=tipo,
            marca=marca,
        )
        self.stdout.write(
            self.style.SUCCESS(f'\nVehículo registrado en MySQL: {vehiculo}')
        )

    def _listar_vehiculos(self) -> None:
        self._titulo('2.2 — Vehículos Registrados')
        vehiculos = list(ParqueaderoService.listar_vehiculos())
        if not vehiculos:
            self.stdout.write('No hay vehículos registrados todavía.')
            return
        for v in vehiculos:
            self.stdout.write(f'  - {v}')

    def _registrar_entrada(self) -> None:
        self._titulo('2.3 — Registro de Entrada Automático (Hora generada por MySQL)')
        self.stdout.write(
            'Nota: No se solicita hora manual; MySQL asigna DEFAULT CURRENT_TIMESTAMP y dispara los triggers.'
        )
        placa = input('Placa del vehículo: ').strip()
        est = ParqueaderoService.registrar_entrada_automatica(placa)
        self.stdout.write(self.style.SUCCESS('\nEntrada registrada correctamente:'))
        self.stdout.write(f'  ID Estacionamiento : {est.id_estacionamiento}')
        self.stdout.write(f'  Placa              : {est.placa_vehiculo_id}')
        self.stdout.write(f'  Hora entrada MySQL : {_fmt(est.hora_entrada)}')
        self.stdout.write(f'  Estado actual      : {est.estado_parqueo}')

    def _consultar_por_placa(self) -> None:
        self._titulo('2.4 — Consulta de Hora Exacta, Estado Actual e Historial')
        placa = input('Placa a consultar: ').strip()
        reporte = ParqueaderoService.consultar_estado_y_historial(placa)

        self.stdout.write(f"\nHora actual del motor MySQL : {_fmt(reporte['hora_actual_mysql'])}")
        self.stdout.write(f"Vehículo                    : {reporte['vehiculo']}")

        actual = reporte['estacionamiento_actual']
        self.stdout.write('\n--- Estado Actual ---')
        if actual is None:
            self.stdout.write('  El vehículo aún no tiene ingresos registrados.')
        else:
            self.stdout.write(f'  ID Estacionamiento : {actual.id_estacionamiento}')
            self.stdout.write(f'  Estado             : {actual.estado_parqueo}')
            self.stdout.write(f'  Entrada (MySQL)    : {_fmt(actual.hora_entrada)}')
            self.stdout.write(f'  Salida             : {_fmt(actual.hora_salida)}')

        estacionamientos = reporte['historial_estacionamientos']
        self.stdout.write(f'\n--- Historial de Estacionamientos ({len(estacionamientos)}) ---')
        for est in estacionamientos:
            self.stdout.write(f'  {est.resumen_estado()}')

        movimientos = reporte['historial_movimientos']
        self.stdout.write(f'\n--- Historial de Movimientos en Bitácora ({len(movimientos)}) ---')
        if not movimientos:
            self.stdout.write('  Sin movimientos registrados.')
        else:
            for mov in movimientos:
                self.stdout.write(f'  {mov}')

    def _listar_estacionamientos(self) -> None:
        self._titulo('2.4 — Estacionamientos en MySQL')
        estado = input('Filtrar por estado (ACTIVO / FINALIZADO / MOROSO / Enter todos): ').strip() or None
        resultado = ParqueaderoService.listar_estacionamientos(estado=estado)
        self.stdout.write(f"Hora actual del motor MySQL: {_fmt(resultado['hora_actual_mysql'])}\n")
        if not resultado['estacionamientos']:
            self.stdout.write('No se encontraron registros.')
            return
        for est in resultado['estacionamientos']:
            self.stdout.write(f'  {est.resumen_estado()}')

    def _consultar_bitacora(self) -> None:
        self._titulo('2.4 — Historial General de Movimientos (bitacora_movimientos)')
        placa = input('Filtrar por placa (Enter para ver todos): ').strip() or None
        resultado = ParqueaderoService.consultar_bitacora(placa=placa, limite=30)
        self.stdout.write(f"Hora actual del motor MySQL: {_fmt(resultado['hora_actual_mysql'])}\n")
        if not resultado['movimientos']:
            self.stdout.write('No hay movimientos registrados.')
            return
        for mov in resultado['movimientos']:
            self.stdout.write(f'  [#{mov.id_bitacora}] {mov}')

    def _ejecutar_menu(self) -> None:
        opciones = {
            '1': self._probar_conexion,
            '2': self._registrar_vehiculo,
            '3': self._listar_vehiculos,
            '4': self._registrar_entrada,
            '5': self._consultar_por_placa,
            '6': self._listar_estacionamientos,
            '7': self._consultar_bitacora,
        }
        while True:
            self._titulo('SISTEMA DE PARQUEADERO INTELIGENTE — CLI (CRITERIOS 2.1 A 2.4)')
            self.stdout.write('  1. Probar conexión y hora del motor MySQL (2.1)')
            self.stdout.write('  2. Registrar vehículo con validaciones (2.2)')
            self.stdout.write('  3. Listar vehículos registrados (2.2)')
            self.stdout.write('  4. Registrar entrada automática — hora MySQL + triggers (2.3)')
            self.stdout.write('  5. Consultar hora exacta, estado e historial por placa (2.4)')
            self.stdout.write('  6. Listar estacionamientos por estado (2.4)')
            self.stdout.write('  7. Consultar bitácora de movimientos (2.4)')
            self.stdout.write('  0. Salir')

            seleccion = input('\nSeleccione una opción: ').strip()
            if seleccion == '0':
                self.stdout.write('Saliendo...')
                break

            accion = opciones.get(seleccion)
            if not accion:
                self.stdout.write(self.style.WARNING('Opción inválida.'))
                continue

            try:
                accion()
            except ValidationError as exc:
                self.stdout.write(self.style.ERROR(f'\n[VALIDACIÓN] {_fmt_validacion(exc)}'))
            except OperationalError as exc:
                self.stdout.write(self.style.ERROR(f'\n[CONEXIÓN MYSQL] {exc}'))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'\n[ERROR] {exc}'))
