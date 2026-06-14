Esta pasta é dedicada à estimação do potencial máximo para produção de energia fotovoltaica em Portugal.
Datasets Utilizados
Mapas Raster: Potencial solar em kWh/kWp, ângulo ótimo de instalação em graus do Global Solar Atlas.
Geometria de Edifícios: Dataset de pegadas de edifícios (dividido em dois ficheiros, proveniente da Overture Maps).
Limites Administrativos: Polígonos de referência do território nacional da CAOP.
Para instalar as dependências, corre pip install -r requirements.txt
OU(recomendado devido a dependência do GDAL)
docker build -t geoespaciais-app .
Como correr os ficheiros:
corre generateparq.py, depois geoespacial.py. geoespacial _w_dbsm.py não depende desta ordem.
 
