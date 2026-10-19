
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

BASE = "https://educamosclm.castillalamancha.es"
PAGE = BASE + "/s/messages"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            src = dict(attrs).get("src")
            if src:
                self.scripts.append(src)


def descargar(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read(8_000_000).decode(
            "utf-8", errors="replace"
        )


def main():
    html = descargar(PAGE)
    parser = Parser()
    parser.feed(html)

    principales = [
        urllib.parse.urljoin(PAGE, src)
        for src in parser.scripts
        if re.search(r"(?:^|/)main\.[^/]+\.js$", src)
    ]

    if not principales:
        print("No se localizo el modulo principal.")
        return

    js = descargar(principales[0])
    print("JavaScript principal:", len(js), "caracteres")

    patrones = {
        "Carga dinamica": r"import\(",
        "Rutas lazy Angular": r"loadChildren",
        "Chunks Webpack": r"webpackChunk|__webpack_require__",
        "Referencias a archivos JS": r"[\w.-]+\.js",
    }

    for nombre, patron in patrones.items():
        encontrados = re.findall(patron, js, re.I)
        print(nombre, ":", len(encontrados))

    archivos = set(re.findall(
        r'[\w.-]+(?:\.[a-f0-9]{8,})?\.js',
        js, re.I
    ))

    print("Archivos JS candidatos:", len(archivos))
    for archivo in sorted(archivos)[:40]:
        print("Archivo:", archivo)

    print("Analisis completado sin credenciales.")


if __name__ == "__main__":
    main()
