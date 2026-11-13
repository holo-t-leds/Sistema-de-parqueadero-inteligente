# 🚗 Sistema Inteligente de Parqueadero

Sistema integral para la gestión, control de tiempos y facturación de un estacionamiento, diseñado con un enfoque modular y arquitectura relacional.

## 📋 Requisitos del Sistema

El desarrollo de este sistema se basó en el levantamiento formal de requerimientos para garantizar la integridad de las reglas de negocio y un rendimiento óptimo. 

<details>
<summary><strong>⚙️ Requisitos Funcionales (Reglas de Negocio)</strong></summary>
<br>

| ID | Módulo | Descripción del Requisito | Prioridad |
|:---|:---|:---|:---:|
| **RF-01** | Control de Acceso | Permitir registrar un nuevo vehículo capturando datos esenciales como la placa, tipo y marca. | Alta |
| **RF-02** | Control de Acceso | Crear un registro de entrada delegando a MySQL la asignación automática de la hora (`TIMESTAMP`) y el estado inicial. | Alta |
| **RF-03** | Control de Acceso | Validar en la base de datos e impedir que se registre una nueva entrada si la placa del vehículo ya cuenta con un parqueo "activo". | Alta |
| **RF-04** | Facturación | Calcular automáticamente el valor total a pagar basándose en la diferencia entre la hora de entrada y la de salida. | Alta |
| **RF-05** | Facturación | Permitir registrar formalmente el pago asociado a un estacionamiento finalizado. | Alta |
| **RF-06** | Facturación | Ejecutar una alerta o bloqueo si un vehículo registra una salida sin tener un pago validado (prevención de evasión). | Media |
| **RF-07** | Consultas | Permitir la consulta en cualquier momento de la hora exacta de ingreso y el estado actual de un vehículo. | Media |
| **RF-08** | Auditoría (BD) | Mantener un historial detallado e inmutable de todos los movimientos de los vehículos mediante Triggers (Bitácora). | Alta |

</details>

<details>
<summary><strong>📐 Requisitos No Funcionales (Arquitectura y Diseño)</strong></summary>
<br>

| ID | Categoría | Descripción del Requisito | Prioridad |
|:---|:---|:---|:---:|
| **RNF-01** | Arquitectura | El programa debe estructurarse en Python utilizando el paradigma Orientado a Objetos (Clases: `Vehiculo`, `Estacionamiento`, `Pago`). | Alta |
| **RNF-02** | Base de Datos | El sistema debe utilizar MySQL como sistema gestor de base de datos relacional. | Alta |
| **RNF-03** | Base de Datos | La automatización del historial (bitácora) y el bloqueo de dobles ingresos debe realizarse nativamente mediante *Triggers* (disparadores) SQL. | Alta |
| **RNF-04** | Interfaz UI/UX | La interfaz gráfica debe seguir un diseño web SaaS, minimalista, limpio y utilizando colores pastel (azul, verde menta, gris claro). | Media |
| **RNF-05** | Rendimiento | El cálculo de tarifas y la validación de placas activas deben realizarse con respuesta en tiempo real. | Alta |

</details>

## 📐 Arquitectura y Modelado

### 1. Diagramas de Casos de Uso
Define la interacción entre los operadores del parqueadero y los procesos automatizados del sistema.

<p align="center">
  <img src="./diagramas/caso_uso_p.png" alt="Diagrama de Casos de Uso" width="800">
</p>
<p align="center">
  <img src="./diagramas/control.png" alt="Diagrama de Casos de Uso" width="800">
</p>

### 2. Diagrama de Clases
Estructura orientada a objetos que define las entidades del sistema, sus atributos y comportamientos.

<p align="center">
  <img src="diagramas/clases.png" alt="Diagrama de Clases" width="800">
</p>

### 3. Modelo Entidad-Relación (Conceptual)
Abstracción de las reglas de negocio y cardinalidad entre vehículos, estacionamientos y pagos.

<p align="center">
  <img src="Base_de_datos/Modelo-ER.png" alt="Modelo Entidad Relación" width="700">
</p>

## 🎨 Diseño de Interfaz (Mockups)

El diseño del sistema sigue una estética SaaS limpia, minimalista y orientada a la eficiencia operativa, utilizando una paleta de colores basada en tonos azul pastel, verde menta y gris claro.

A continuación, se presentan las vistas principales del aplicativo:

<div align="center">
  
| 🏠 Landing Page & Autenticación | 📊 Dashboards & Control |
| :---: | :---: |
| **Landing Page**<br><br><img src="Mockups/landing%20page.png" width="400" alt="Landing Page"> | **Panel Principal**<br><br><img src="Mockups/Panel_principal.png" width="400" alt="Panel Principal"> |
| **Inicio de Sesión**<br><br><img src="Mockups/login.png" width="400" alt="Login"> | **Gestión de Vehículos**<br><br><img src="Mockups/Gestión.png" width="400" alt="Gestión"> |
| **Registro de Usuario**<br><br><img src="Mockups/registro.png" width="400" alt="Registro"> | **Módulo de Cobro**<br><br><img src="Mockups/cobro.png" width="400" alt="Cobro"> |

</div>

### 🛡️ Auditoría del Sistema

<div align="center">
  <img src="Mockups/Bitácora.png" width="800" alt="Bitácora de Auditoría">
  <br>
  <i>Vista del registro inmutable generado automáticamente por los triggers de MySQL.</i>
</div>

## 🛠️ Tecnologías Utilizadas
* **Base de Datos:** MySQL
* **Lógica y Triggers:** MySQL
* **Modelado:** PlantUML / Mermaid / Notación de Chen
