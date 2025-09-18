CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_total INT NOT NULL,
    edad_cliente INT NOT NULL,
    genero_cliente ENUM('masculino', 'femenino') NOT NULL,
    ubicacion ENUM('local 1', 'local 2') NOT NULL,
    dia INT NOT NULL,
    mes INT NOT NULL,
    anio INT NOT NULL,
    fecha DATE NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);
