# Monitor de precios

Scraper en Python que recorre una tienda online, guarda un historial de precios en CSV y detecta qué productos cambiaron de precio entre una corrida y la anterior.

Está probado sobre [books.toscrape.com](https://books.toscrape.com/), un sitio hecho para practicar scraping. La estructura es fácil de adaptar a otras tiendas: solo hay que cambiar la URL y los selectores de la función `extraer_libros`.

## Qué hace

- Recorre las 50 páginas del catálogo (unos 1000 productos) siguiendo el botón "siguiente".
- Extrae título, precio, rating, disponibilidad y URL de cada producto.
- Limpia los datos: el precio pasa de texto (`£51.77`) a número (`51.77`).
- Agrega cada corrida a `historial_precios.csv` con fecha y hora, sin borrar las anteriores.
- Compara con el último precio guardado y muestra los productos que subieron o bajaron.
- Espera medio segundo entre páginas para no sobrecargar el servidor.

## Cómo usarlo

Requiere Python 3. En Windows (PowerShell):

```powershell
git clone https://github.com/Massimo-1405/monitor-precios.git
cd monitor-precios
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scraper.py
```

La primera corrida crea el historial. En las siguientes, el script avisa si algún precio cambió.

## Tecnologías

- Python
- `requests` para descargar las páginas
- `beautifulsoup4` para leer el HTML
- `csv` de la librería estándar para el historial

## Ejemplo de salida

Cuando algún precio cambió respecto de la corrida anterior, el script lo informa así (cambios simulados para esta demostración):

```
Se guardaron 1000 libros en historial_precios.csv
Cambios de precio detectados: 2
- In Her Wake: bajó de 80.09 a 12.84 (-67.25)
- A Murder in Time: bajó de 109.8 a 16.64 (-93.16)
```

En [`ejemplo_historial.csv`](ejemplo_historial.csv) hay una muestra del archivo que genera.

## Próximas mejoras

- Exportar el historial a Excel
- Enviar alertas cuando cambie un precio
- Configurar la URL y los selectores desde un archivo