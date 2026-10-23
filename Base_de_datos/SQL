CREATE DATABASE parqueadero_inteligente;
USE parqueadero_inteligente;

CREATE TABLE vehiculos (
    placa VARCHAR(10) PRIMARY KEY,
    tipo_vehiculo VARCHAR(20) NOT NULL,
    marca VARCHAR(30)
);

CREATE TABLE estacionamientos (
    id_estacionamiento INT AUTO_INCREMENT PRIMARY KEY,
    placa_vehiculo VARCHAR(10) NOT NULL,
    hora_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
    hora_salida DATETIME NULL,
    estado_parqueo ENUM('ACTIVO', 'FINALIZADO', 'MOROSO') DEFAULT 'ACTIVO',
    FOREIGN KEY (placa_vehiculo) REFERENCES vehiculos(placa) ON DELETE CASCADE
);

CREATE TABLE pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_estacionamiento INT NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    estado_pago ENUM('PENDIENTE', 'PAGADO') DEFAULT 'PENDIENTE',
    FOREIGN KEY (id_estacionamiento) REFERENCES estacionamientos(id_estacionamiento) ON DELETE CASCADE
);

CREATE TABLE bitacora_movimientos (
    id_bitacora INT AUTO_INCREMENT PRIMARY KEY,
    placa_referencia VARCHAR(10) NOT NULL,
    evento VARCHAR(100) NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER //

-- Trigger A: Impedir el registro de dos entradas activas simultáneas
CREATE TRIGGER trg_validar_doble_ingreso
BEFORE INSERT ON estacionamientos
FOR EACH ROW
BEGIN
    DECLARE activos INT;
    
    -- Contar cuántos estacionamientos 'ACTIVO' tiene esta placa
    SELECT COUNT(*) INTO activos 
    FROM estacionamientos 
    WHERE placa_vehiculo = NEW.placa_vehiculo AND estado_parqueo = 'ACTIVO';
    
    -- Si ya hay 1 o más, se bloquea la inserción con un error 45000 (Excepción definida por usuario)
    IF activos > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: El vehículo ya cuenta con un registro de entrada ACTIVO.';
    END IF;
END //

-- Trigger B: Registrar el ingreso en la bitácora automáticamente
CREATE TRIGGER trg_registrar_bitacora_entrada
AFTER INSERT ON estacionamientos
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_movimientos (placa_referencia, evento)
    VALUES (NEW.placa_vehiculo, CONCAT('Ingreso registrado. Estado: ', NEW.estado_parqueo));
END //

-- Trigger C: Registrar en la bitácora cada salida o cambio de estado
CREATE TRIGGER trg_registrar_bitacora_salida_estado
AFTER UPDATE ON estacionamientos
FOR EACH ROW
BEGIN
    -- Valida si el estado cambió (por ejemplo de ACTIVO a FINALIZADO o MOROSO)
    IF OLD.estado_parqueo <> NEW.estado_parqueo THEN
        INSERT INTO bitacora_movimientos (placa_referencia, evento)
        VALUES (
            NEW.placa_vehiculo, 
            CONCAT('Cambio de estado: de ', OLD.estado_parqueo, ' a ', NEW.estado_parqueo)
        );
    END IF;
END //

DELIMITER ;

INSERT INTO vehiculos (placa, tipo_vehiculo, marca) VALUES ('ABC123D', 'Moto', 'Yamaha');

INSERT INTO estacionamientos (placa_vehiculo) VALUES ('ABC123D');

INSERT INTO estacionamientos (placa_vehiculo) VALUES ('ABC123D');

SELECT * FROM bitacora_movimientos;
