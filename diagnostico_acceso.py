
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
from html.parser import HTMLParser

URL = "https://educamosclm.castillalamancha.es/s/messages"


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
    print("Diagnostico EducamosCLM")
    print("Sin credenciales ni acceso a mensajes privados.")

    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with opener.open(request, timeout=20) as response:
            html = response.read(500_000).decode(
                "utf-8", errors="replace"
            )
            final_url = response.geturl()
            parsed_url = urllib.parse.urlsplit(final_url)

            print("HTTP:", response.status)
            print("Dominio final:", parsed_url.hostname)
            print("Ruta final:", parsed_url.path)
            print(
                "Content-Type:",
                response.headers.get("Content-Type", "").split(";")[0]
            )

            parser = FormParser()
            parser.feed(html)

            print("Formularios:", len(parser.forms))

            for index, form in enumerate(parser.forms, 1):
                print("Formulario:", index)
                print("Metodo:", form["method"])
                print("Tipos de campos:", form["fields"])

            print("Cookies recibidas:", len(cookies))

    except urllib.error.HTTPError as error:
        print("HTTP:", error.code)
    except urllib.error.URLError as error:
        print("Error de conexion:", type(error.reason).__name__)
    except Exception as error:
        print("Error:", type(error).__name__)


if __name__ == "__main__":
    main()
