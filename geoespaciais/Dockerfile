#versão python
FROM python:3.12-slim

# Dependências a nível de sistema
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Directory
WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN GDAL_VERSION=$(gdal-config --version) && \
    pip install --no-cache-dir "GDAL==$GDAL_VERSION" && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

CMD ["python", "main.py"]


