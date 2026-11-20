# Sistema-de-parqueadero-inteligente
Un parqueadero necesita registrar vehículos, entradas, salidas y pagos. Cuando ingresa un vehículo, el sistema debe registrar su hora de entrada y mantener el historial de movimientos.
# El sistema debe cumplir estas reglas:
 i. ¿Cómo impedirías registrar dos entradas activas para la misma placa?
 ii. ¿Cómo calcularías el valor del estacionamiento según el tiempo?
 iii. ¿Qué debería ocurrir cuando un vehículo sale sin pagar?
 iv. diseñar un trigger que registre en una bitácora cada salida y cambio de estado, sin permitir que el mismo vehículo tenga dos estacionamientos
activos.

# 3. Realice el Diagrama de clases y relación con la base de datos y las tablas en
MySQL.

# 4. Requisitos funcionales
El programa debe permitir:
 Crear las clases Vehículo, Estacionamiento y Pago.
 Registrar un vehículo.
 Crear un registro de entrada sin indicar la hora.
 Consultar la hora y el estado generados por MySQL.


# 5. Roles de trabajo
 Analista: identifica requisitos y construye el diagrama.
 Programador: desarrolla las clases y sus métodos.
 Tester: prepara casos de prueba y documenta errores.
 Expositor: explica las decisiones y los resultados del equipo.

# 6. Evidencias que deben entregarse
Cada estudiante o equipo debe presentar:
1. Los diagramas de clases UML elaborados.
2. Los archivos .py con el código fuente.
3. Las capturas o registros de las pruebas realizadas.
4. Un documento breve con los errores encontrados y cómo fueron corregidos.
5. Una reflexión final sobre cómo se aplicaron los modelos conductista y
constructivista durante el desarrollo.

# API protegida con JWT

La aplicación conserva el panel administrativo en `/admin/` y añade una API
autenticada con JSON Web Tokens:

- `POST /api/auth/token/`: recibe `username` y `password`; devuelve `access` y
  `refresh`.
- `POST /api/auth/token/refresh/`: recibe un token `refresh`; devuelve un nuevo
  token `access`.
- `GET /api/auth/me/`: devuelve los datos del usuario autenticado.
- `/`: muestra un login de demostración y saluda según el rol del usuario.

Para consumir un endpoint protegido se envía el token de acceso así:

```text
Authorization: Bearer <access>
```

Los usuarios se administran mediante el sistema de usuarios de Django. La
configuración de JWT está en `proyecto_principal/settings.py` y el endpoint de
verificación está en `app_parqueadero/auth_api.py`.

Para esta primera demostración, un usuario con `is_staff=True` es `admin` y
cualquier otro usuario autenticado es `cliente`. El rol se calcula en el
servidor y también se incluye en el JWT; no debe aceptarse desde el navegador.
