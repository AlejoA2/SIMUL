# Imagen base
FROM python:3.12-slim
#evitamos que python creen archivo .pyc
ENV PYTHONDONTWRITEBYTECODE=1
#Permite visualizar los logs
ENV PYTHONBUFFERED=1
#Directorio de trabajo
WORKDIR /app
#Dependencias del sistemas
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# dependencia de python
COPY requirements.txt .
#instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt
#Codigo de la aplicacion
COPY . .
#puerto
EXPOSE 5000
#Ejecucion
CMD ["gunicorn","--bind","0.0.0.0:5000","--workers","3","run:app"]