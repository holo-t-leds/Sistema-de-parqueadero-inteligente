# 🚗 Sistema Inteligente de Parqueadero

Sistema integral para la gestión, control de tiempos y facturación de un estacionamiento, diseñado con un enfoque modular y arquitectura relacional.

## 📐 Arquitectura y Modelado

### 1. Diagrama de Casos de Uso
Define la interacción entre los operadores del parqueadero y los procesos automatizados del sistema.

<p align="center">
  <img src="./diagramas/caso_uso_p.png" alt="Diagrama de Casos de Uso" width="800">
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

## 🛠️ Tecnologías Utilizadas
* **Base de Datos:** MySQL
* **Lógica y Triggers:** MySQL
* **Modelado:** PlantUML / Mermaid / Notación de Chen

## 🚀 Instalación y Despliegue
1. Clonar el repositorio: `git clone <url-del-repo>`
2. Ejecutar el script `script_db.sql` en tu gestor de MySQL (ej. XAMPP o MySQL Workbench).
