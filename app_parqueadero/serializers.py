from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import BitacoraMovimientos, Estacionamientos, Vehiculos


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = 'admin' if user.is_staff else 'cliente'
        return token


class VehiculoSerializer(serializers.ModelSerializer):
    """Serializador para registro y listado de vehículos (Criterio 2.2)."""

    class Meta:
        model = Vehiculos
        fields = ('placa', 'tipo_vehiculo', 'marca')


class EntradaAutomaticaSerializer(serializers.Serializer):
    """Solo solicita la placa; la hora de entrada la genera MySQL (Criterio 2.3)."""

    placa = serializers.CharField(max_length=10)


class EstacionamientoSerializer(serializers.ModelSerializer):
    """Serializador de consulta de estacionamiento y hora MySQL (Criterios 2.3 y 2.4)."""

    placa_vehiculo = serializers.CharField(source='placa_vehiculo_id', read_only=True)

    class Meta:
        model = Estacionamientos
        fields = (
            'id_estacionamiento',
            'placa_vehiculo',
            'hora_entrada',
            'hora_salida',
            'estado_parqueo',
        )
        read_only_fields = fields


class BitacoraMovimientosSerializer(serializers.ModelSerializer):
    """Serializador del historial de movimientos generado por triggers (Criterio 2.4)."""

    class Meta:
        model = BitacoraMovimientos
        fields = ('id_bitacora', 'placa_referencia', 'evento', 'fecha_evento')
        read_only_fields = fields
