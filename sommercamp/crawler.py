# Hier importieren wir die benötigten Softwarebibliotheken.
from resiliparse.extract.html2text import extract_plain_text
from scrapy import Spider, Request
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.http.response.html import HtmlResponse


class SchoolSpider(Spider):
    # Gib hier dem Crawler einen eindeutigen Name,
    # der beschreibt, was du crawlst.
    name = "gerichte"

    start_urls = [
        # Gib hier mindestens eine (oder mehrere) URLs an,
        # bei denen der Crawler anfangen soll,
        # Seiten zu downloaden.
        "https://reisehappen.de/rezepte/",
        "https://volkermampft.de/kategorien/blog-events/die-kulinarische-weltreise/",
        "https://www.essen-und-trinken.de/internationale-kueche",
        "https://www.rewe.de/ernaehrung/internationale-kueche/"
    ]
    link_extractor = LxmlLinkExtractor(
        # Beschränke den Crawler, nur Links zu verfolgen,
        # die auf eine der gelisteten Domains verweisen.
        allow_domains=["reisehappen.de", "volkermampft.de", "www.essen-und-trinken.de", "www.rewe.de"],
    )
    custom_settings = {
        # Identifiziere den Crawler gegenüber den gecrawlten Seiten.
        "USER_AGENT": "Sommercamp (https://uni-jena.de)",
        # Der Crawler soll nur Seiten crawlen, die das auch erlauben.
        "ROBOTSTXT_OBEY": False,
        # Frage zu jeder Zeit höchstens 4 Webseiten gleichzeitig an.
        "CONCURRENT_REQUESTS": 6,
        # Verlangsame den Crawler, wenn Webseiten angeben,
        # dass sie zu oft angefragt werden.
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1,
        # Frage nicht zwei mal die selbe Seite an.
        "HTTPCACHE_ENABLED": True,
    }

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            # Die Webseite ist keine HTML-Webseite, enthält also keinen Text.
            return        
        # Speichere die Webseite als ein Dokument in unserer Dokumenten.
        yield {
            # Eine eindeutige Identifikations-Nummer für das Dokument.
            "docno": str(hash(response.url)),
            # Die URL der Webseite.
            "url": response.url,
            # Der Titel der Webseite aus dem <title> Tag im HTML-Code.
            "title": response.css("title::text").get(),
            # Der Text der Webseite.
            # Um den Hauptinhalt zu extrahieren, benutzen wir
            # eine externe Bibliothek.
            "text": extract_plain_text(response.text, main_content=True),
        }

        # Finde alle Links auf der aktuell betrachteten Webseite.
        for link in self.link_extractor.extract_links(response):
            if link.text == "":
                # Ignoriere Links ohne Linktext, z.B. bei Bildern.
                continue
            # Für jeden gefundenen Link, stelle eine Anfrage zum Crawling.
            yield Request(link.url, callback=self.parse)