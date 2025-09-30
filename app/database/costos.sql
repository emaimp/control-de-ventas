CREATE TABLE IF NOT EXISTS costos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    precio_compra DECIMAL(10, 2) NOT NULL,
    impuesto DECIMAL(4, 2) NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);
