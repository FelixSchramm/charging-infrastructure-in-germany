"""Abschließende Textabschnitte: Limitationen und Quellen."""

import pandas as pd
import streamlit as st

_LIMITATIONEN = """
Dieses Dashboard bietet einen umfassenden Überblick über den **Bestand** der öffentlichen Ladeinfrastruktur in Deutschland. Für eine vollständige Bewertung des Marktes müssen jedoch qualitative und ökonomische Faktoren berücksichtigt werden, die über eine reine Bestandszählung und historische Entwicklung hinausgehen.

- **Auslastungsgrad:** Das Dashboard erfasst den Bestand, aber nicht die tatsächliche Nutzung der Ladeinfrastruktur. Geringe Auslastung ist für einige Standorte eine zentrale Herausforderung, die hier nicht abgebildet wird. Das kann mit Metriken wie **durchschnittliche Ladevorgänge pro Ladepunkt und Tag** oder **durchschnittlich verladene Energiemenge pro Ladepunkt und Tag** ergänzt werden.

- **Verhältnis von Ladepunkten zu E-Fahrzeugen:** Die Karte zeigt das Verhältnis der öffentlichen Ladepunkte zum gewichteten lokalen E-Fahrzeugbestand (BEV zählt einfach, PHEV halb). Der Fahrzeugbestand basiert auf KBA-Daten (Zulassungsbezirke, Stichtag laut Quelle). Absolute Bestandszahlen werden vom KBA nicht veröffentlicht und werden näherungsweise aus den veröffentlichten Prozentanteilen berechnet.

- **Zuverlässigkeit und Nutzererfahrung:** Gezählt werden alle registrierten Ladepunkte, unabhängig von ihrem Betriebszustand. Die tatsächliche Ausfallrate aus Nutzersichtgit ist ein entscheidender Qualitätsfaktor, der hier unberücksichtigt bleibt. Diese Diskrepanz zur offiziellen "Uptime" entsteht z.B. durch Softwarefehler oder defekte QR-Codes.

- **Ökonomischer Kontext:** Faktoren wie der komplexe Tarifstrukturen, die durch über gewerbliche 8.000 Betreiber entstehen, Preismodelle und die allgemeine Wirtschaftlichkeit der Standorte werden nicht analysiert. Diese beeinflussen jedoch die Marktdynamik und den weiteren Ausbau maßgeblich.
"""


def render_info(df: pd.DataFrame, df_kba):
    """Zeichnet die Abschnitte Limitationen und Quellen."""
    st.divider()
    st.header("Limitationen")
    st.markdown(_LIMITATIONEN)

    st.divider()
    st.header("Quellen")
    _render_quellen(df, df_kba)


def _render_quellen(df: pd.DataFrame, df_kba):
    """Rendert die Quellenliste mit dynamischem Datenstand."""
    inbetriebnahme = pd.to_datetime(df["Inbetriebnahmedatum"])
    datenstand = inbetriebnahme.max().strftime("%d.%m.%Y")
    jahr = inbetriebnahme.max().year

    kba_stand = ""
    if df_kba is not None and "Berichtszeitpunkt" in df_kba.columns:
        kba_stand = f", Berichtszeitpunkt {df_kba['Berichtszeitpunkt'].iloc[0]}"

    st.markdown(f"""
    - Bundesnetzagentur ({jahr}) *Ladesäulenregister der öffentlich zugänglichen Ladepunkte*, Datenstand {datenstand}. Bonn: Bundesnetzagentur. [↗](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/DownloadundKontakt.html)
    - Kraftfahrt-Bundesamt (KBA) *FZ Pkw mit Elektroantrieb nach Zulassungsbezirken*{kba_stand}. Flensburg: KBA. [↗](https://das-kba-statistikportal.hub.arcgis.com/datasets/fz-pkw-mit-elektroantrieb-zulassungsbezirk/about)
    - Bundesamt für Kartographie und Geodäsie (2024) *Verwaltungsgebiete 1:250 000 (VG250)*. Frankfurt am Main: BKG. [↗](https://gdz.bkg.bund.de/)
    - Lobas-Funck, F., Meister, S. und Weißbach, L. (2024) *Whitepaper Lade-Use-Cases*. Berlin: Nationale Leitstelle Ladeinfrastruktur / NOW GmbH. [↗](https://nationale-leitstelle.de/wp-content/uploads/2024/07/Whitepaper_LUC_Nationale-Leitstelle-Ladeinfrastruktur_2024.pdf)
    - Reiner Lemoine Institut (2024) *Ladeinfrastruktur nach 2025/2030: Szenarien für den Markthochlauf*, im Auftrag der NOW GmbH. Berlin: NOW GmbH. [↗](https://www.now-gmbh.de/wp-content/uploads/2024/06/Studie_Ladeinfrastruktur-2025-2030_Neuauflage-2024.pdf)
    - Nationale Leitstelle Ladeinfrastruktur (2024) *ö-LIS Report: Monitoringbericht öffentliche Ladeinfrastruktur*. Berlin: NOW GmbH. [↗](https://nationale-leitstelle.de/en/downloads/)
    - Nationale Leitstelle Ladeinfrastruktur (2024) *Studie: Einfach zu Hause laden*. Berlin: NOW GmbH. [↗](https://nationale-leitstelle.de/neue-studie-gibt-wichtige-einblicke-in-das-ladeverhalten-von-privatpersonen/)
    """)
