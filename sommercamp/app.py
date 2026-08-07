# Hier importieren wir die benötigten Softwarebibliotheken.

from os.path import abspath, exists
from sys import argv

from streamlit import (
    text_input,
    header,
    title,
    subheader,
    container,
    markdown,
    link_button,
    divider,
    set_page_config,
    button,
    session_state
)

from pyterrier import IndexFactory
from pyterrier.terrier import Retriever
from pyterrier.text import get_text

import streamlit as st

# Diese Funktion baut die App für die Suche im gegebenen Index auf.


def app(index_dir) -> None:

    # Konfiguriere den Titel der Web-App (wird im Browser-Tab angezeigt)

    set_page_config(
        page_title="Speisen & Gerichte Suchmaschie",
        layout="centered",
    )

    # Darkmode Button

    if "darkmode" not in session_state:
        session_state.darkmode = False

    # Speichert die aktuelle Seite der Suchergebnisse

    if "page" not in session_state:
        session_state.page = 1

    with st.container(
        horizontal=True,
        horizontal_alignment="right",
        vertical_alignment="center"
    ):
        with st.container():

            # Gib der App einen Titel und eine Kurzbeschreibung:

            title("Gerichte-Suchmaschine")

            markdown(
                "Hier kannst du unsere Gerichts-Suchmaschine nutzen:"
            )

        if session_state.darkmode:

            button_text = "☀️ Lightmode"

        else:

            button_text = "🌙 Darkmode"

        if button(button_text):

            session_state.darkmode = not session_state.darkmode

            st.rerun()

    # Darkmode Design

    if session_state.darkmode:

        markdown(
            """
            <style>

            .stApp {
                background-color: #595959;
            }

            h1, h2, h3, p, label {
                background-color: #595959;
                color: #FFFFFF !important;
            }

            input {
                background-color: #696969 !important;
                color: #FFFFFF !important;
            }

            div[data-testid="stContainer"] {
                background-color: #11FF00;
            }

            button {
                background-color: #595959 !important;
                color: #00FF0F !important;
                border-color: #FFFFFF !important;
            }

            div.stLinkButton a {
                background-color: #595959;
            }

            div.stButton button {
                background-color: #595959;
            }

            hr {
                border-color: #FFFFFF !important;
            }

            a {
                border-color: #FFFFFF !important;
            }

            div.stVerticalBlock {
                border-color: #FFFFFF !important;
            }

            data-testid=stCode {
                background: #595959 !important;
            }

            </style>
            """,

            unsafe_allow_html=True
        )

    else:

        markdown(
            """
            <style>
            </style>
            """,

            unsafe_allow_html=True
        )

    # Erstelle ein Text-Feld, mit dem die Suchanfrage (query)
    # eingegeben werden kann.

    query = text_input(
        label="Suchanfrage",
        placeholder="Suche...",
        value="Gerichte",
    )

    # Wenn die Suchanfrage leer ist, dann kannst du nichts suchen.

    if query == "":

        markdown(
            "Bitte gib eine Suchanfrage ein."
        )

        return
        # Öffne den Index.

    index = IndexFactory.of(
        abspath(index_dir)
    )

    # Initialisiere den Such-Algorithmus.

    searcher = Retriever(
        index,
        wmodel="BM25",
        num_results=100,
    )

    # Initialisiere das Modul, zum Abrufen der Texte.

    text_getter = get_text(
        index,
        metadata=[
            "url",
            "title",
            "text"
        ]
    )

    # Baue die Such-Pipeline zusammen.

    pipeline = searcher >> text_getter

    # Führe die Such-Pipeline aus und suche nach der Suchanfrage.

    results = pipeline.search(query)

    # Anzahl der Ergebnisse pro Seite

    results_per_page = 10

    # Berechnet die Anzahl aller verfügbaren Seiten

    total_results = len(results)

    total_pages = (
        total_results + results_per_page - 1
    ) // results_per_page

    # Falls keine Ergebnisse vorhanden sind,
    # setze die Seitenanzahl auf 1

    if total_pages == 0:

        total_pages = 1

    # Falls die aktuelle Seite größer als die letzte Seite ist,
    # springe zurück zur letzten Seite

    if session_state.page > total_pages:

        session_state.page = total_pages

    # Berechnet welche Ergebnisse auf der aktuellen Seite angezeigt werden

    start_index = (
        session_state.page - 1
    ) * results_per_page

    end_index = (
        start_index + results_per_page
    )

    page_results = results.iloc[
        start_index:end_index
    ]

    # Zeige eine Unter-Überschrift vor den Suchergebnissen an.

    divider()

    header("Suchergebnisse")

    # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.

    if len(results) == 0:

        markdown(
            "Keine Suchergebnisse."
        )

        return

    # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.

    markdown(
        f"{len(results)} Suchergebnisse."
    )

    # Gib nun der Reihe nach,
    # alle Suchergebnisse der aktuellen Seite aus.

    for _, row in page_results.iterrows():

        # Pro Suchergebnis, erstelle eine Box (container).

        with container(border=True):

            # Zeige den Titel der gefundenen Webseite an.

            subheader(
                row["title"]
            )

            # Speichere den Text in einer Variablen (text).

            text = row["text"]

            # Schneide den Text nach 500 Zeichen ab.

            text = text[:500]

            # Ersetze Zeilenumbrüche durch Leerzeichen.

            text = text.replace(
                "\n",
                " "
            )

            # Zeige den Dokument-Text an.

            markdown(
                text
            )

            # Gib Nutzern eine Schaltfläche,
            # um die Seite zu öffnen.

            link_button(
                "🌐 Seite öffnen",
                url=row["url"]
            )

            # Erstellt die Seitennavigation am Ende der Suchergebnisse.

    divider()

    col1, col2, col3 = st.columns(
        [2, 1, 2]
    )
    # Linker Button für vorherige Seite.

    with col1:
        col1a, col1b = st.columns(
            [1, 1]
        )
        with col1a:
            buttonLeft = st.button(            
                "⬅ Last Page",
                disabled=session_state.page <= 1)

            if buttonLeft == True:
                session_state.page -= 1

                st.rerun()

    # Visuelles Modul für den Seitenzähler.

    with col2:

        markdown(
            f"""
            <div style="
                text-align:center;
                font-size:20px;
            ">

                Page {session_state.page} / {total_pages}

            </div>
            """,

            unsafe_allow_html=True,
        )

    # Rechter Button für nächste Seite.

    with col3:
        col2a, col2b =st.columns(
            [1.5, 1]
        )
        with col2b:
            if button(
                "Next Page ➡",
                icon_position="left",
                disabled=session_state.page >= total_pages
            ):

                session_state.page += 1

                st.rerun()

# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.


def main():

    # Lade den Pfad zum Index aus dem ersten Kommandozeilen-Argument.

    index_dir = argv[1]

    # Wenn es noch keinen Index gibt,
    # kannst du die Suchmaschine nicht starten.

    if not exists(index_dir):

        exit(1)

    # Rufe die App-Funktion von oben auf.

    app(index_dir)


if __name__ == "__main__":

    main()