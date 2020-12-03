# Estrategias de Cambio de Fondos de Pensiones

El propósito de este repositorio es compartir una metodología para analizar distintas estrategias de cambios de fondos de pensiones y poder comparar así la rentabilidad de los fondos de pensiones chilenos (estrategias "pasivas") versus estrategias activas de cambio de fondos (estilo *Felices y Forrados*).

Para asegurar la comparabilidad en el tiempo, se asume que las personas hacen una única inversión en una fecha de inicio determinada y siguiendo una estrategia determinada. (*Un ejercicio más realista debería incorporar información de aportes (o retiros) mensuales y comisiones, pero quedará fuera del ámbito de este proyecto por el momento. En todo caso, las conclusiones principales no deberían ser afectadas por estos elementos.*).

Los procedimientos desarrollados aquí permiten analizar cómo la inversión inicial evoluciona en el tiempo.

Algunas referencias relacionadas que sirven de inspiración:

- Cristi, Michael (2017). *Felices y forrados : efectividad de los cambio de fondo*. Tesis de Magíster. [URL](http://repositorio.uchile.cl/handle/2250/149952)
- Cuevas, Bernhardt y Sanclemente (2018). *The Pied Piper of Pensioners* [URL](https://www.chapman.edu/research/institutes-and-centers/economic-science-institute/_files/ifree-papers-and-photos/bernhardt-piper_last-2018.pdf)
- Da, Z., B. Larrain, C. Sialm, y J. Tessada. 2018. *Destabilizing Financial Advice: Evidence from Pension Fund Reallocations*. The
Review of Financial Studies, 31(10), 3720-3755. [URL WP](http://economiayadministracion.uc.cl/personal/blarrain/papers/pension.pdf)
- Villatoro y otros (2019). *Mislearning and (Poor) Performance of Individual Investors*. LACEA-LAMES. [URL](https://sistemas.colmex.mx/Reportes/LACEALAMES/LACEA-LAMES2019_paper_526.pdf)
- Superintendencia de Pensiones (2020). *Evolución y desempeño de los cambios de fondos*. Nota Técnica. [URL](https://www.spensiones.cl/portal/institucional/594/articles-13911_recurso_1.pdf)
- Banco Central de Chile (2020). *Informe de Estabilidad Financiera - Primer Semestre".* Recuadro V.1 "Regulación de Asesores Previsionales y Estabilidad Financiera". [URL](https://www.bcentral.cl/documents/33528/2294181/IEF1_2020_rec_Regulacion_asesores.pdf)
- Blog "La Firme de la Rentabilida de Felices y Forrados" [URL](https://economistaflaite.com/2020/11/30/la-firme-de-la-rentabilida-de-felices-y-forrados/)


TO-DO al 3 dic:
- Compartir formulario mínimo (Excel) que debería construir un usuario que quiera analizar otras estrategias de inversión.

WISHLIST:
- Agregar conexión directa a base de datos de SPensiones.
- Incorporar API de feriados. Documentación aquí: https://apis.digital.gob.cl/fl/

*Errores u omisiones son de mi propia responsabilidad. Favor reportar en [ISSUES](https://github.com/calvarad/fyf/issues).*


### Parte 1. Valores Cuota SPensiones

En esta parte del proyecto, se procesa la información de valores cuota de la Superintendencia de Pensiones. 

**INSTRUCCIONES**

1. Correr archivo [1_valores_cuota/parse_valores_cuota.py](/1_valores_cuota/parse_valores_cuota.py)
2. Valores cuota procesados quedan guardados en base SQLite.


*Archivos CSV descargados de https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php*



### Parte 2. Estrategias de Inversión

En esta parte del proyecto, se procesan las estrategias de inversión disponibles (estrategias pasivas o activas), a través de una interfaz para orderar las sugerencias de cambio de fondos, según las preferencias del usuario.

Parámetros claves:
- Fecha de inicio de la inversión
- Fecha de término de la inversión
- Nombre de la estrategia a seguir (alguno de los multifondos, o "FF", o "MAX")
- Path del archivo (opcional, si es que se tiene un archivo con fechas sugeridas de cambio)

Interfaz principal es el objeto "Estrategia", que permite procesar las estrategias disponibles y adaptarlas a lo requerido por el usuario.


VER DEMOSTRACIÓN AQUÍ: [2_avisos_cambio_fondos/test_estrategias.ipynb](/2_avisos_cambio_fondos/test_estrategias.ipynb)


**INSTRUCCIONES**

1. NO es necesario correr códigos en esta parte. 



*Fuente de recomendaciones de FyF: https://www.felicesyforrados.cl/resultados/*

Snapshot al 2 de diciembre de 2020:

<img src="/data_auxiliar/snapshot_20201202.PNG"
     alt="snapshot"
     style="float: left; margin-right: 10px;" />



### Parte 3. Simulador de Valores Cuota

Usando la base de estrategias de la Parte 2, en esta parte se puede obtener una serie histórica del monto invertido inicialmente, de acuerdo a la evolución de los valores cuotas de los fondos seleccionados en una determinada estrategia.

Parámetros claves:
- estrategia: Debe ingresarse la estrategia sobre la cual se desea consultar los valores cuota.
- afp: Debe ingresarse el nombre de la AFP sobre la cual se desea consultar los valores cuota.
- monto_inicial: Debe ingresarse el monto inicial a invertir (para asegurar comparabilidad entre distintas estrategias)
- lag_solicitud: Este parámetro permite simular un retrazo de X días en el ingreso de la solicitud de cambio de fondo (default: 0 días hábiles)
- lag_venta: Este parámetro permite definir en cuántos días hábiles se verifica la "venta" de las cuotas originales (por normativa, ocurre en t+2 días hábiles)
- lag_compra: Este parámetro permite definir en cuántos días hábiles se verifica la "compra" de las cuotas nuevas (por normativa, ocurre en t+2 días hábiles)


VER DEMOSTRACIÓN AQUÍ: [3_simulador/test_valores_cuota.ipynb](/3_simulador/test_valores_cuota.ipynb)


**INSTRUCCIONES**

1. NO es necesario correr códigos en esta parte. 


### Parte 4. Agregación de Múltiples Estrategias

En esta sección se pueden comparar diferentes estrategias.

Parámetros claves:
lista_estrategias: una lista con las estrategias a comparar
afp: 
monto_inicial:
- lag_solicitud: Este parámetro permite simular un retrazo de X días en el ingreso de la solicitud de cambio de fondo (default: 0 días hábiles)


VER DEMOSTRACIÓN AQUÍ: [4_comparador_estrategias/test_comparador.ipynb](/4_comparador_estrategias/test_comparador.ipynb)


**INSTRUCCIONES**

1. NO es necesario correr códigos en esta parte. 

### Parte 5. Estadísticas Descriptivas de Estrategias Seleccionadas

PENDIENTE

Crear visualización para las estrategias analizadas. Usar función desarrollada en la Parte 4.


### Anexos. Bases de datos auxiliares

#### Base de datos de días hábiles (2008 a 2020)

[data_auxiliar/db_habiles.db](/data_auxiliar/db_habiles.db)

Contiene información de días hábiles entre 2008 a 2020


#### Creación de Archivos con estrategias "óptimas".

[data_auxiliar/crea_estrategia_optima.py](/data_auxiliar/crea_estrategia_optima.py)

**INSTRUCCIONES**

1. Al correr el archivo "crea_estrategia_optima.py", se crean automáticamente archivos Excel (en la carpeta 2), con sugerencias de cambio de fondo, asumiendo que alguien sería capaz de predecir cuál va a ser el fondo con el mejor rendimiento en el mes entrante.
2. Se puede editar la sección "main" de ese archivo para crear sugerencias "óptimas" basándose en otras AFPs. 

