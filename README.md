# Rentabilidad Felices y Forrados

El propósito de este repositorio es compartir código base para comparar la rentabilidad de fondos de pensiones (a.k.a. los "multifondos") versus estrategias activas de cambio de fondos.

TO-DO al 2 dic:
- Agregar conexión directa a base de datos de SPensiones
- Incorporar posibilidad de analizar fechas de cambios arbitrarias (que usuario pueda crear y evaluar sus propias estrategias)


### Parte 1. Valores Cuota SPensiones

En esta parte del proyecto, se procesa la información de valores cuota de la Superintendencia de Pensiones. 

**INSTRUCCIONES**

1. Correr archivo 1_valores_cuota/parse_valores_cuota.py

Valores cuota procesados quedan guardados en base SQLite.


*Archivos CSV descargados de https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php*



### Parte 2. Estrategias de Inversión

En esta parte del proyecto, se procesarán las estrategias de inversión disponibles (hasta ahora, fondos pasivos, y las recomendaciones de Felices y Forrados), creado una interfaz para obtener información relevante según las preferencias del usuario:

- Fecha de inicio de la inversión
- Fecha de término de la inversión
- Estrategia a seguir (alguno de los multifondos, o FyF)

Fuente de recomendaciones de FyF: https://www.felicesyforrados.cl/resultados/

Snapshot al 2 de diciembre de 2020:

<img src="/data_auxiliar/snapshot_20201202.PNG"
     alt="snapshot"
     style="float: left; margin-right: 10px;" />



### Parte 3. Simulador de Rentabilidad


### Parte 4. Análisis Comparativo Multi Fondos vs Estrategias Activas

### Anexos. Bases de datos auxiliares

- Base de datos de feriados (2008 a 2019)

data_auxiliar/feriados.db

Contiene información de feriados entre 2008 a 2019


- API de feriados (uso 2020 en adelante)

Documentación aquí: https://apis.digital.gob.cl/fl/

