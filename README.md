# 🚗 Sistema Inteligente de Parqueadero

Sistema integral para la gestión, control de tiempos y facturación de un estacionamiento, diseñado con un enfoque modular y arquitectura relacional.

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
