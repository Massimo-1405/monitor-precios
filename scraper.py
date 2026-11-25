import csv
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://books.toscrape.com/"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
PAUSA_SEGUNDOS = 0.5
ARCHIVO_HISTORIAL = Path("historial_precios.csv")
CAMPOS = ["fecha", "titulo", "precio", "rating", "disponible", "url"]


def descargar_soup(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    return BeautifulSoup(response.text, "html.parser")


def extraer_libros(soup, url):
    libros = []
    for item in soup.select("article.product_pod"):
        precio_texto = item.select_one("p.price_color").text
        rating_clase = item.select_one("p.star-rating")["class"][1]
        libros.append({
            "titulo": item.h3.a["title"],
            "precio": float(re.sub(r"[^\d.]", "", precio_texto)),
            "rating": RATINGS[rating_clase],
            "disponible": "In stock" in item.select_one("p.availability").text,
            "url": urljoin(url, item.h3.a["href"]),
        })
    return libros


def obtener_todos_los_libros(url_inicial):
    libros = []
    url = url_inicial
    pagina = 1
    while url:
        print(f"Página {pagina}: {url}")
        soup = descargar_soup(url)
        libros.extend(extraer_libros(soup, url))

        siguiente = soup.select_one("li.next a")
        url = urljoin(url, siguiente["href"]) if siguiente else None
        pagina += 1
        if url:
            time.sleep(PAUSA_SEGUNDOS)
    return libros


def leer_ultimos_precios(archivo):
    ultimos = {}
    if not archivo.exists():
        return ultimos
    with open(archivo, newline="", encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            ultimos[fila["url"]] = float(fila["precio"])
    return ultimos


def detectar_cambios(libros, ultimos_precios):
    cambios = []
    for libro in libros:
        anterior = ultimos_precios.get(libro["url"])
        if anterior is not None and anterior != libro["precio"]:
            cambios.append({
                "titulo": libro["titulo"],
                "anterior": anterior,
                "actual": libro["precio"],
                "diferencia": round(libro["precio"] - anterior, 2),
            })
    return cambios


def guardar_historial(libros, archivo):
    es_nuevo = not archivo.exists()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(archivo, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS)
        if es_nuevo:
            writer.writeheader()
        for libro in libros:
            writer.writerow({"fecha": fecha, **libro})


def mostrar_cambios(cambios):
    if not cambios:
        print("Sin cambios de precio desde la última corrida.")
        return
    print(f"Cambios de precio detectados: {len(cambios)}")
    for c in cambios[:10]:
        movimiento = "subió" if c["diferencia"] > 0 else "bajó"
        print(f"- {c['titulo']}: {movimiento} de {c['anterior']} a {c['actual']} ({c['diferencia']:+})")


if __name__ == "__main__":
    ultimos_precios = leer_ultimos_precios(ARCHIVO_HISTORIAL)
    libros = obtener_todos_los_libros(URL)
    cambios = detectar_cambios(libros, ultimos_precios)
    guardar_historial(libros, ARCHIVO_HISTORIAL)
    print(f"Se guardaron {len(libros)} libros en {ARCHIVO_HISTORIAL}")
    mostrar_cambios(cambios)