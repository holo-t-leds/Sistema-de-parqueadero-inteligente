# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BitacoraMovimientos(models.Model):
    id_bitacora = models.AutoField(primary_key=True)
    placa_referencia = models.CharField(max_length=10)
    evento = models.CharField(max_length=100)
    fecha_evento = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bitacora_movimientos'


class Estacionamientos(models.Model):
    id_estacionamiento = models.AutoField(primary_key=True)
    placa_vehiculo = models.ForeignKey('Vehiculos', models.DB_CASCADE, db_column='placa_vehiculo')
    hora_entrada = models.DateTimeField(blank=True, null=True)
    hora_salida = models.DateTimeField(blank=True, null=True)
    estado_parqueo = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estacionamientos'


class Pagos(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_estacionamiento = models.ForeignKey(Estacionamientos, models.DB_CASCADE, db_column='id_estacionamiento')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pagos'


class Vehiculos(models.Model):
    placa = models.CharField(primary_key=True, max_length=10)
    tipo_vehiculo = models.CharField(max_length=20)
    marca = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vehiculos'
