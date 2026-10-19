
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

BASE = "https://educamosclm.castillalamancha.es"
PAGE = BASE + "/s/messages"

KEYWORDS = (
    "cerbero", "openid", "oauth", "login",
    "messages", "mensajeria", "mensaje",
    "api/", "token"
)


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            src = dict(attrs).get("src")
            if src:
                self.scripts.append(src)


def download(url, limit):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(
        request, timeout=25
    ) as response:
        return response.read(limit).decode(
            "utf-8", errors="replace"
        )


def main():
    print("Analisis publico JavaScript Educamos")
    print("No se utilizan credenciales.")

    html = download(PAGE, 500_000)

    parser = ScriptParser()
    parser.feed(html)

    main_scripts = [
        urllib.parse.urljoin(PAGE, src)
        for src in parser.scripts
        if "main." in src
        and src.endswith(".js")
    ]

    if not main_scripts:
        print("No se encontro main.js")
        return

    url = main_scripts[0]
    print("Script principal localizado.")

    javascript = download(url, 8_000_000)

    print("Caracteres analizados:", len(javascript))

    for keyword in KEYWORDS:
        matches = list(re.finditer(
            re.escape(keyword),
            javascript,
            re.IGNORECASE
        ))
        print(f"{keyword}: {len(matches)} coincidencias")

    # Solo patrones de rutas, sin valores ni parametros.
    routes = set(re.findall(
        r'["\'](/(?:api|auth|oauth|s)/'
        r'[A-Za-z0-9_./{}-]{2,120})["\']',
        javascript
    ))

    print("Rutas candidatas:", len(routes))

    for route in sorted(routes)[:40]:
        print("Ruta:", route)

    print("Diagnostico terminado.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Error:", type(error).__name__)
        raise
