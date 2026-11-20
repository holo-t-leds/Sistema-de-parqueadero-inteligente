# Diagrama de Clases UML — Sistema de Parqueadero Inteligente

Este documento complementa y corrige el diagrama visual existente ([clases.png](clases.png)) para cumplir al 100% el **criterio 1.1**, manteniéndose alineado exactamente con `database/01_esquema_y_triggers.sql` y `app_parqueadero/models.py`.

## Correcciones aplicadas respecto a `clases.png`

1. **Cardinalidad `Vehiculos` -> `Estacionamientos`:** corregida de `1` a `1` hacia **`1` a `0..*`**, ya que un mismo vehículo puede tener múltiples ingresos históricos en el parqueadero (el trigger `trg_validar_doble_ingreso` restringe únicamente ingresos `ACTIVO` simultáneos).
2. **Cardinalidad `Estacionamientos` -> `Pagos`:** ajustada a **`1` a `0..1`**, porque un estacionamiento `ACTIVO` todavía no tiene pago generado hasta su salida.
3. **Longitud de `evento` en `BitacoraMovimientos`:** alineada con el script SQL (`VARCHAR(100)` en lugar de `VARCHAR(50)`).
4. **Triggers reflejados fielmente:** `trg_validar_doble_ingreso`, `trg_registrar_bitacora_entrada` y `trg_registrar_bitacora_salida_estado`.

## Diagrama UML (Mermaid)

```mermaid
classDiagram
    direction LR

    class Vehiculos {
        -str placa <<PK>>
        -str tipo_vehiculo
        -str marca
        +normalizar_placa(placa: str) str
        +validar_placa(placa: str) void
        +clean() void
        +registrar_vehiculo(placa: str, tipo_vehiculo: str, marca: str) Vehiculos
        +tiene_estacionamiento_activo() bool
        +consultar_historial() QuerySet
    }

    class Estacionamientos {
        -int id_estacionamiento <<PK>>
        -str placa_vehiculo <<FK>>
        -datetime hora_entrada
        -datetime hora_salida
        -str estado_parqueo
        +clean() void
        +esta_activo() bool
        +crear_entrada(placa: str) Estacionamientos
        +consultar_estado() dict
        +resumen_estado() str
    }

    class Pagos {
        -int id_pago <<PK>>
        -int id_estacionamiento <<FK>>
        -Decimal valor_total
        -str estado_pago
        +clean() void
        +esta_pagado() bool
        +asentar_pago() bool
    }

    class BitacoraMovimientos {
        -int id_bitacora <<PK>>
        -str placa_referencia
        -str evento
        -datetime fecha_evento
        +consultar_por_placa(placa: str) QuerySet
        <<trigger>> trg_validar_doble_ingreso()
        <<trigger>> trg_registrar_bitacora_entrada()
        <<trigger>> trg_registrar_bitacora_salida_estado()
    }

    Vehiculos "1" --> "0..*" Estacionamientos : registra
    Estacionamientos "1" --> "0..1" Pagos : genera
    Estacionamientos "1" ..> "0..*" BitacoraMovimientos : dispara triggers
```
