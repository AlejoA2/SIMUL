"""
=============================================================
PAQUETE DE DATOS SIMULADOS
=============================================================

Aquí viven los catálogos de demostración que alimentan las
vistas HTML del frontend (corte 2). La API REST del backend
(corte 3) lee la misma información desde MySQL a través de
`app/repositories`.

`simul_data.py` es la única fuente de verdad del frontend:
las vistas lo importan para pintar el HTML y lo entregan al
navegador con el filtro `tojson` para que el JavaScript
pueda filtrar, buscar y modificar sin volver a pedirlo al
servidor.
=============================================================
"""
