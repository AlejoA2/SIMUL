"""
=============================================================
PAQUETE DE DATOS SIMULADOS
=============================================================

Aquí viven los catálogos de demostración del Museo Digital
mientras la base de datos MySQL no esté conectada.

`simul_data.py` es la única fuente de verdad: las vistas lo
importan para pintar el HTML y lo entregan al navegador con
el filtro `tojson` para que el JavaScript pueda filtrar,
buscar y modificar sin volver a pedirlo al servidor.

Al conectar MySQL este paquete desaparece y sus datos pasan
a leerse desde `app/repositories`.
=============================================================
"""
