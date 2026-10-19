
import urllib.request
import urllib.error
from html.parser import HTMLParser

URL = "https://cerbero.jccm.es/"


class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "form":
            self.current = {
                "method": attrs.get("method", "GET"),
                "has_action": bool(attrs.get("action")),
                "fields": [],
            }

        elif tag == "input" and self.current is not None:
            self.current["fields"].append(
                attrs.get("type", "text")
            )

    def handle_endtag(self, tag):
        if tag == "form" and self.current is not None:
            self.forms.append(self.current)
            self.current = None


def main():
    print("Diagnostico publico de Cerbero")
    print("No se utilizan credenciales.")

    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            html = response.read(500_000).decode(
                "utf-8", errors="replace"
            )

            print("HTTP:", response.status)
            print("URL final:", response.url.split("?")[0])
            print(
                "Content-Type:",
                response.headers.get("Content-Type"),
            )

            parser = FormParser()
            parser.feed(html)

            print("Formularios:", len(parser.forms))

            for index, form in enumerate(parser.forms, 1):
                print("Formulario", index)
                print("Metodo:", form["method"])
                print("Tiene action:", form["has_action"])
                print("Tipos de campos:", form["fields"])

    except urllib.error.HTTPError as error:
        print("HTTP:", error.code)

    except Exception as error:
        print("Error:", type(error).__name__)


if __name__ == "__main__":
    main()
