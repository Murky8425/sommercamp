# Hier importieren wir die benötigten Softwarebibliotheken.
from os.path import abspath, exists
from sys import argv
from streamlit import (text_input, header, title, subheader, 
    container, markdown, link_button, divider, set_page_config,
    button, session_state)
from pyterrier import IndexFactory
from pyterrier.terrier import Retriever
from pyterrier.text import get_text


# Diese Funktion baut die App für die Suche im gegebenen Index auf.
def app(index_dir) -> None:

    # Konfiguriere den Titel der Web-App (wird im Browser-Tab angezeigt)
    set_page_config(
        page_title="Speisen & Gerichte Suchmaschie",
        layout="centered",)

    # Darkmode Button
    if "darkmode" not in session_state:
        session_state.darkmode = False

    if button("🌙 Darkmode"):
        session_state.darkmode = not session_state.darkmode

    # Darkmode Design
    if session_state.darkmode:
        markdown(
            """
            <style>
            .stApp {
                background-color: #595959;
                # color: #FFFFFF;
            }

            h1, h2, h3, p, label {
                background-color: #595959;
                color: #FFFFFF !important;
            }

            # Hintergrund Farbe
            input {
                background-color: #000000 !important;
                color: #000000 !important;
            }

            div[data-testid="stContainer"] {
                background-color: #000000;
            }

            # Darkmode Button
            button {
                background-color: #FFFFFF !important;
                color: #00FF0F !important;
            }

            div.stLinkButton a {
            background-color: #595959 ;
            }

            div.stButton button {
            background-color: #595959 ;
            }
        
            hr {
            border-color: #FFFFFF !important;
            }

            a {
            border-color: #FFFFFF !important;
            }

            div.stVerticalBlock    {
            border-color: #FFFFFF !important;
            }

            rl    {
            background-color: #FFFFFF !important;
            }


            </style>
            """,
            unsafe_allow_html=True
        )
    
    # Gib der App einen Titel und eine Kurzbeschreibung:
    title("Gerichte-Suchmaschine")
    markdown("Hier kannst du unsere Gerichts-Suchmaschine nutzen:")

    # Erstelle ein Text-Feld, mit dem die Suchanfrage (query) 
    # eingegeben werden kann.
    query = text_input(
        label="Suchanfrage",
        placeholder="Suche...",
        value="Gerichte",)

    # Wenn die Suchanfrage leer ist, dann kannst du nichts suchen.
    if query == "":
        markdown("Bitte gib eine Suchanfrage ein.")
        return

    # Öffne den Index.
    index = IndexFactory.of(abspath(index_dir))

    # Initialisiere den Such-Algorithmus. 
    searcher = Retriever(
        index,
        wmodel="BM25",
        num_results=10,)

    # Initialisiere das Modul, zum Abrufen der Texte.
    text_getter = get_text(index, metadata=["url", "title", "text"])

    # Baue die Such-Pipeline zusammen.
    pipeline = searcher >> text_getter

    # Führe die Such-Pipeline aus und suche nach der Suchanfrage.
    results = pipeline.search(query)

    # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
    divider()
    header("Suchergebnisse")

    # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
    if len(results) == 0:
        markdown("Keine Suchergebnisse.")
        return

    # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
    markdown(f"{len(results)} Suchergebnisse.")

    # Gib nun der Reihe nach, alle Suchergebnisse aus.
    for _, row in results.iterrows():

        # Pro Suchergebnis, erstelle eine Box (container).
        with container(border=True):

            # Zeige den Titel der gefundenen Webseite an.
            subheader(row["title"])

            # Speichere den Text in einer Variablen (text).
            text = row["text"]

            # Schneide den Text nach 500 Zeichen ab.
            text = text[:500]

            # Ersetze Zeilenumbrüche durch Leerzeichen.
            text = text.replace("\n", " ")

            # Zeige den Dokument-Text an.
            markdown(text)

            # Gib Nutzern eine Schaltfläche, um die Seite zu öffnen.
            link_button("🌐 Seite öffnen", url=row["url"])


# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.
def main():

    # Lade den Pfad zum Index aus dem ersten Kommandozeilen-Argument.
    index_dir = argv[1]

    # Wenn es noch keinen Index gibt, kannst du die Suchmaschine nicht starten.
    if not exists(index_dir):
        exit(1)

    # Rufe die App-Funktion von oben auf.
    app(index_dir)


if __name__ == "__main__":
    main()