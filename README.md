# Arbitraje de Tasas

El bot busca arbitraje de tasas implícitas entre spot y futuro usando las cotizaciones de REMARKETS. En el caso del spot de dólar, se consulta a Yahoo Finance.

## Configuración de Remarkets

En la función _init_login_ del archivo conector.py definir las credenciales de Remarkets para la conexión:

```
def init_login(user="exey865104", password="wqdnfX3&", account="REM5104"):
```
## Configuración de los instrumentos

En el archivo **run.py** se definen las siguentes variables:
```
dias_spot = 2 

spot_symbols = ["MERV - XMEV - GGAL - 48hs",
                "MERV - XMEV - PAMP - 48hs",
                "MERV - XMEV - YPFD - 48hs"]

future_symbols = ["GGAL/AGO21",
                  "PAMP/AGO21",
                  "YPFD/AGO21",
                  "DLR/AGO21",
                  "DLR/SEP21"]
```
**dias_spot:** son los dias hasta la liquidación del spot (aplica a todos los spots excepto el de dólar que se asume contado inmediato). Ejemplo 1) es lunes y los spots liquidan a 48hs, entonces dias_spot = 2 (si no hay feriados en el medio), 2) es jueves y los spots liquidan a 48hs, entonces dias_spot = 4 (sin feriados) 

**spot_symbols:** contiene el nombre de los instrumentos spots de REMARKETS que se van a analizar. El spot de dólar no hace falta especificarlo ya que se agrega automáticamente.

Los precios BID y OFFER del spot de dólar se consulta a Yahoo Finance solamente al iniciar el bot porque es muy lenta la API.

## Lanzamiento del bot

Ejecutar el script **run.py**


Cada vez que llegue una nueva market data, se printean en pantalla y se existe una posibilidad de arbitraje se detallan los instrumentos y las tasas:

```
Nueva MD
Tasas colocadoras: GGAL/AGO21: 1020.98% PAMP/AGO21: 0.00% YPFD/AGO21: 0.00% DLR/AGO21: 200.01% DLR/SEP21: 108.47% 
Tasas tomadoras: GGAL/AGO21: 1684.62% PAMP/AGO21: 561.54% YPFD/AGO21: nan% DLR/AGO21: 325.55% DLR/SEP21: 133.60% 
Hay un arbitraje colocando en ['GGAL/AGO21'] con tasa 1020.98% y tomando en ['DLR/SEP21'] con tasa 133.60%
```

## Tests unitarios

Ejecutar el script **tests.py**

