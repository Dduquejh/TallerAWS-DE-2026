-- 1. Ventas superiores a $900.000 COP
SELECT venta_id, producto, importe, fecha
FROM ventas
WHERE importe > 900000
ORDER BY importe DESC;

-- 2. Ventas con información del cliente
SELECT
    v.venta_id,
    c.nombre,
    c.ciudad,
    v.producto,
    v.importe
FROM ventas AS v
INNER JOIN clientes AS c
    ON v.cliente_id = c.cliente_id
ORDER BY v.venta_id;

-- 3. Total gastado por cliente
SELECT
    c.cliente_id,
    c.nombre,
    SUM(v.importe) AS total_compras,
    COUNT(v.venta_id) AS cantidad_ventas
FROM clientes AS c
LEFT JOIN ventas AS v
    ON c.cliente_id = v.cliente_id
GROUP BY c.cliente_id, c.nombre
ORDER BY total_compras DESC;

-- 4. Ingresos por ciudad
SELECT
    c.ciudad,
    SUM(v.importe) AS ingresos_totales,
    COUNT(v.venta_id) AS cantidad_ventas
FROM ventas AS v
INNER JOIN clientes AS c
    ON v.cliente_id = c.cliente_id
GROUP BY c.ciudad
ORDER BY ingresos_totales DESC;
