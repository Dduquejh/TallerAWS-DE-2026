
CREATE TABLE IF NOT EXISTS clientes (
    cliente_id INTEGER NOT NULL,
    nombre VARCHAR(100),
    ciudad VARCHAR(100),
    PRIMARY KEY (cliente_id)
);

CREATE TABLE IF NOT EXISTS ventas (
    venta_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    producto VARCHAR(100),
    importe DECIMAL(12, 2),
    fecha DATE,
    PRIMARY KEY (venta_id)
);
