"""Vistas API REST para los criterios 2.2, 2.3 y 2.4 (protegidas con JWT)."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    BitacoraMovimientosSerializer,
    EntradaAutomaticaSerializer,
    EstacionamientoSerializer,
    VehiculoSerializer,
)
from .services import ParqueaderoService


def _formatear_error_validacion(exc: ValidationError) -> dict:
    if hasattr(exc, 'message_dict'):
        return {'errores': exc.message_dict}
    return {'error': exc.messages[0] if exc.messages else str(exc)}


class VehiculoListCreateView(APIView):
    """Criterio 2.2: Listar y registrar vehículos con validaciones en MySQL."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        vehiculos = ParqueaderoService.listar_vehiculos()
        return Response(VehiculoSerializer(vehiculos, many=True).data)

    def post(self, request):
        placa = request.data.get('placa', '')
        tipo_vehiculo = request.data.get('tipo_vehiculo', '')
        marca = request.data.get('marca', '')
        try:
            vehiculo = ParqueaderoService.registrar_vehiculo(
                placa=placa,
                tipo_vehiculo=tipo_vehiculo,
                marca=marca,
            )
        except ValidationError as exc:
            return Response(
                _formatear_error_validacion(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            VehiculoSerializer(vehiculo).data,
            status=status.HTTP_201_CREATED,
        )


class EstacionamientoEntradaView(APIView):
    """Criterio 2.3: Registra entrada sin hora manual (generada por MySQL + triggers)."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = EntradaAutomaticaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            estacionamiento = ParqueaderoService.registrar_entrada_automatica(
                placa=serializer.validated_data['placa']
            )
        except ValidationError as exc:
            return Response(
                _formatear_error_validacion(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            EstacionamientoSerializer(estacionamiento).data,
            status=status.HTTP_201_CREATED,
        )


class EstacionamientoListView(APIView):
    """Criterio 2.4: Consulta directa a MySQL de estacionamientos y hora del motor."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        estado = request.query_params.get('estado')
        try:
            resultado = ParqueaderoService.listar_estacionamientos(estado=estado)
        except ValidationError as exc:
            return Response(
                _formatear_error_validacion(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                'hora_actual_mysql': resultado['hora_actual_mysql'],
                'estacionamientos': EstacionamientoSerializer(
                    resultado['estacionamientos'], many=True
                ).data,
            }
        )


class ConsultaEstadoVehiculoView(APIView):
    """Criterio 2.4: Consulta hora exacta de MySQL, estado actual e historial por placa."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, placa: str):
        try:
            reporte = ParqueaderoService.consultar_estado_y_historial(placa)
        except ValidationError as exc:
            return Response(
                _formatear_error_validacion(exc),
                status=status.HTTP_404_NOT_FOUND,
            )

        actual = reporte['estacionamiento_actual']
        return Response(
            {
                'hora_actual_mysql': reporte['hora_actual_mysql'],
                'vehiculo': VehiculoSerializer(reporte['vehiculo']).data,
                'estacionamiento_actual': (
                    EstacionamientoSerializer(actual).data if actual else None
                ),
                'historial_estacionamientos': EstacionamientoSerializer(
                    reporte['historial_estacionamientos'], many=True
                ).data,
                'historial_movimientos': BitacoraMovimientosSerializer(
                    reporte['historial_movimientos'], many=True
                ).data,
            }
        )


class BitacoraListView(APIView):
    """Criterio 2.4: Consulta directa del historial de movimientos en `bitacora_movimientos`."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        placa = request.query_params.get('placa')
        try:
            limite = int(request.query_params.get('limite', '30'))
            resultado = ParqueaderoService.consultar_bitacora(placa=placa, limite=limite)
        except (ValueError, ValidationError) as exc:
            msg = (
                _formatear_error_validacion(exc)
                if isinstance(exc, ValidationError)
                else {'error': 'El parámetro limite debe ser un número entero positivo.'}
            )
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'hora_actual_mysql': resultado['hora_actual_mysql'],
                'movimientos': BitacoraMovimientosSerializer(
                    resultado['movimientos'], many=True
                ).data,
            }
        )
