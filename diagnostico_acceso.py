
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
from html.parser import HTMLParser

URL = "https://educamosclm.castillalamancha.es/s/messages"


class AnalizadorHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.forms = []
        self.current_form = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])

        if tag == "form":
            self.current_form = {
                "method": attrs.get("method", "GET"),
                "fields": [],
            }

        if tag == "input" and self.current_form is not None:
            self.current_form["fields"].append(
                attrs.get("type", "text")
            )

    def handle_endtag(self, tag):
        if tag == "form" and self.current_form is not None:
            self.forms.append(self.current_form)
            self.current_form = None


def main():
    print("Diagnostico HTML y JavaScript de Educamos")
    print("Sin credenciales ni datos personales.")

    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    try:
        request = urllib.request.Request(
            URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with opener.open(request, timeout=20) as response:
            html = response.read(500_000).decode(
                "utf-8", errors="replace"
            )

            print("HTTP:", response.status)
            print("Tipo:", response.headers.get("Content-Type", "").split(";")[0])

        parser = AnalizadorHTML()
        parser.feed(html)

        print("Formularios:", len(parser.forms))
        print("Archivos JavaScript:", len(parser.scripts))
        print("Cookies:", len(cookies))

        for index, script in enumerate(parser.scripts[:30], 1):
            url = urllib.parse.urljoin(URL, script)
            parsed = urllib.parse.urlsplit(url)

            # Solo mostramos rutas, nunca parámetros ni tokens.
            print(
                f"Script {index}:",
                parsed.hostname,
                parsed.path[:180]
            )

        if not parser.scripts:
            print("No aparecen scripts externos en el HTML inicial.")

    except urllib.error.HTTPError as error:
        print("HTTP:", error.code)
    except Exception as error:
        print("Error:", type(error).__name__)


if __name__ == "__main__":
    main()
