import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from pathlib import Path

# --- SEITENKONFIGURATION & FARBPALETTE ---
st.set_page_config(
    page_title="Ladeinfrastruktur in Deutschland | NOW GmbH",
    layout="wide"
)

NOW_GRUEN = "#00B092"
NOW_DUNKELBLAU = "#003247"
NOW_GRAU = "#D3D3D3"

LEISTUNGS_COLORS = {
    'HPC-Laden (>= 150 kW)': NOW_GRUEN,
    'Schnellladen (> 22 kW)': NOW_DUNKELBLAU,
    'Normalladen (<= 22 kW)': NOW_GRAU,
}

# --- DATEN LADEN & VORBEREITEN ---
@st.cache_data
def load_data():
    try:
        df = pd.read_parquet('02_data/03_computed_data/combined_ladestation_ladepunkt.parquet')
        df['Inbetriebnahmedatum'] = pd.to_datetime(df['Inbetriebnahmedatum'], errors='coerce')
        df['Jahr'] = df['Inbetriebnahmedatum'].dt.year
        df.dropna(subset=['Inbetriebnahmedatum', 'Bundesland', 'KreisKreisfreieStadt'], inplace=True)

        def get_leistungskategorie(leistung):
            if leistung >= 150: return 'HPC-Laden (>= 150 kW)'
            elif leistung > 22: return 'Schnellladen (> 22 kW)'
            else: return 'Normalladen (<= 22 kW)'
        df['Leistungskategorie'] = df['LadeleistungInKW'].apply(get_leistungskategorie)

        return df
    except FileNotFoundError:
        st.error("FEHLER: Die Datei 'combined_ladestation_ladepunkt.parquet' wurde nicht gefunden. Bitte überprüfe den Pfad.")
        return None

@st.cache_data
def load_geodata():
    try:
        project_root = Path(__file__).parent.parent
        shapefile_path = project_root / "02_data/02_meta_data/vg250_01-01.gk3.shape.ebenen/vg250_ebenen_0101/VG250_KRS.shp"
        gdf = gpd.read_file(shapefile_path)
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=500, preserve_topology=True)
        gdf = gdf.to_crs(epsg=4326)
        for col in gdf.columns:
            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                gdf[col] = gdf[col].astype(str)
        return gdf
    except Exception:
        return None

df = load_data()
gdf_districts = load_geodata()

if df is not None:
    # --- SEITENLEISTE MIT FILTERN ---
    st.sidebar.header("Filteroptionen")

    min_jahr, max_jahr = int(df['Jahr'].min()), int(df['Jahr'].max())
    selected_jahre = st.sidebar.slider("Zeitraum (Jahr):", min_value=min_jahr, max_value=max_jahr, value=(min_jahr, max_jahr))

    bundeslaender = sorted(df['Bundesland'].unique())
    selected_bundeslaender = st.sidebar.multiselect("Bundesland:", options=bundeslaender, default=bundeslaender)

    leistungstypen = sorted(df['Leistungskategorie'].unique())
    selected_leistungstypen = st.sidebar.multiselect("Leistungstyp:", options=leistungstypen, default=leistungstypen)

    search_kreis = st.sidebar.text_input("Landkreis/Stadt (Suche):", "").lower()
    search_betreiber = st.sidebar.text_input("Betreiber (Suche):", "").lower()

    # --- DATENFILTERUNG ---
    df_filtered = df[
        (df['Bundesland'].isin(selected_bundeslaender)) &
        (df['Jahr'] >= selected_jahre[0]) &
        (df['Jahr'] <= selected_jahre[1]) &
        (df['Leistungskategorie'].isin(selected_leistungstypen))
    ]

    if search_kreis:
        df_filtered = df_filtered[df_filtered['KreisKreisfreieStadt'].str.lower().str.contains(search_kreis, na=False)]

    if search_betreiber:
        df_filtered = df_filtered[df_filtered['BetreiberBereinigt'].str.lower().str.contains(search_betreiber, na=False)]

    # --- HAUPTSEITE ---
    st.title("Ladeinfrastruktur in Deutschland")

    df_stationen_filtered = df_filtered.drop_duplicates(subset='ladestation_id')

    # KPIs
    st.header("Statistische Kennzahlen (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Anzahl Ladestationen", f"{df_stationen_filtered['ladestation_id'].nunique():,}".replace(',', '.'))
    col2.metric("Anzahl Ladepunkte", f"{len(df_filtered):,}".replace(',', '.'))
    col3.metric("Anzahl HPC-Ladepunkte", f"{len(df_filtered[df_filtered['LadeleistungInKW'] >= 150]):,}".replace(',', '.'))
    col4.metric("Gesamtleistung", f"{df_stationen_filtered['InstallierteLadeleistungNLL'].sum() / 1_000_000:.2f} GW")

    st.divider()

    # --- Zeitreihen ---
    st.header("Entwicklung über die Zeit")

    # Gemeinsame Basis für alle vier Charts (ab 2010)
    zubau_gesamt = df_filtered.groupby('Jahr').size().reset_index(name='Anzahl')
    zubau_gesamt = zubau_gesamt[zubau_gesamt['Jahr'] >= 2010]
    kat_basis = df_filtered.groupby(['Jahr', 'Leistungskategorie']).size().reset_index(name='Anzahl')
    jahre_range = pd.RangeIndex(start=max(2010, kat_basis['Jahr'].min()), stop=kat_basis['Jahr'].max() + 1)
    full_index = pd.MultiIndex.from_product([jahre_range, list(LEISTUNGS_COLORS)], names=['Jahr', 'Leistungskategorie'])
    kat_basis = kat_basis.set_index(['Jahr', 'Leistungskategorie']).reindex(full_index, fill_value=0).reset_index()

    # ERSTE REIHE: Jährlicher Zubau
    col1, col2 = st.columns(2)
    with col1:
        fig_zubau_gesamt = px.bar(
            zubau_gesamt, x='Jahr', y='Anzahl',
            title='<b>Jährlicher Zubau von Ladepunkten (Gesamt)</b>',
            color_discrete_sequence=[NOW_DUNKELBLAU],
        )
        fig_zubau_gesamt.update_layout(bargap=0.2)
        st.plotly_chart(fig_zubau_gesamt, use_container_width=True, key="fig_zubau_gesamt")

    with col2:
        fig_zubau_kat = px.bar(
            kat_basis, x='Jahr', y='Anzahl', color='Leistungskategorie',
            title='<b>Jährlicher Zubau nach Leistungstyp</b>',
            color_discrete_map=LEISTUNGS_COLORS,
        )
        fig_zubau_kat.update_layout(bargap=0.2, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig_zubau_kat, use_container_width=True, key="fig_zubau_kat")

    # ZWEITE REIHE: Kumulative Entwicklung
    col3, col4 = st.columns(2)
    with col3:
        zubau_alle_jahre = df_filtered.groupby('Jahr').size().reset_index(name='Anzahl')
        cumulative_gesamt = zubau_gesamt.copy()
        offset = zubau_alle_jahre[zubau_alle_jahre['Jahr'] < 2010]['Anzahl'].sum()
        cumulative_gesamt['Anzahl'] = cumulative_gesamt['Anzahl'].cumsum() + offset
        fig_cum_gesamt = px.bar(
            cumulative_gesamt, x='Jahr', y='Anzahl',
            title='<b>Kumulativer Bestand an Ladepunkten (Gesamt)</b>',
            color_discrete_sequence=[NOW_DUNKELBLAU],
        )
        fig_cum_gesamt.update_layout(bargap=0.2)
        st.plotly_chart(fig_cum_gesamt, use_container_width=True, key="fig_cum_gesamt")

    with col4:
        kat_alle_jahre = df_filtered.groupby(['Jahr', 'Leistungskategorie']).size().reset_index(name='Anzahl')
        kat_offsets = kat_alle_jahre[kat_alle_jahre['Jahr'] < 2010].groupby('Leistungskategorie')['Anzahl'].sum()
        kat_kumulativ = kat_basis.copy()
        kat_kumulativ['Anzahl'] = kat_kumulativ.groupby('Leistungskategorie')['Anzahl'].cumsum()
        kat_kumulativ['Anzahl'] += kat_kumulativ['Leistungskategorie'].map(kat_offsets).fillna(0).astype(int)
        fig_cum_kat = px.bar(
            kat_kumulativ, x='Jahr', y='Anzahl', color='Leistungskategorie',
            title='<b>Kumulativer Bestand nach Leistungstyp</b>',
            color_discrete_map=LEISTUNGS_COLORS,
        )
        fig_cum_kat.update_layout(bargap=0.2, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig_cum_kat, use_container_width=True, key="fig_cum_kat")

    st.divider()

    # Detaillierte Analysen
    st.header("Detaillierte Analysen")
    col_detail1, col_detail2 = st.columns(2)
    with col_detail1:
        kategorie_counts = df_filtered['Leistungskategorie'].value_counts().reset_index()
        fig_kategorien = px.pie(kategorie_counts, names='Leistungskategorie', values='count', title='<b>Anteil der Ladepunkttypen</b>', color='Leistungskategorie', color_discrete_map=LEISTUNGS_COLORS)
        st.plotly_chart(fig_kategorien, use_container_width=True, key="fig_kategorien")
    with col_detail2:
        top_10_betreiber = df_filtered['BetreiberBereinigt'].value_counts().nlargest(10).reset_index()
        fig_betreiber = px.bar(top_10_betreiber, x='count', y='BetreiberBereinigt', orientation='h', title='<b>Top 10 Betreiber</b>', labels={'count': 'Anzahl Ladepunkte', 'BetreiberBereinigt': 'Betreiber'}, color_discrete_sequence=[NOW_GRUEN])
        fig_betreiber.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_betreiber, use_container_width=True, key="fig_betreiber")

    # --- REGIONALE ANALYSE (KARTE) ---
    st.divider()
    st.header("Regionale Analyse")
    st.caption("Die Karte zeigt den gesamtdeutschen Bestand auf Kreisebene (alle Filter außer Bundesland werden angewendet).")

    if gdf_districts is not None:
        df_for_map = df[
            (df['Jahr'] >= selected_jahre[0]) &
            (df['Jahr'] <= selected_jahre[1]) &
            (df['Leistungskategorie'].isin(selected_leistungstypen))
        ]
        if search_kreis:
            df_for_map = df_for_map[df_for_map['KreisKreisfreieStadt'].str.lower().str.contains(search_kreis, na=False)]
        if search_betreiber:
            df_for_map = df_for_map[df_for_map['BetreiberBereinigt'].str.lower().str.contains(search_betreiber, na=False)]

        df_for_map = df_for_map.assign(AGS=df_for_map['ARS'].astype(str).str.zfill(5))

        agg = df_for_map.groupby(['AGS', 'Leistungskategorie']).size().unstack(fill_value=0).rename(columns={
            'HPC-Laden (>= 150 kW)': 'HPC',
            'Schnellladen (> 22 kW)': 'Schnellladen',
            'Normalladen (<= 22 kW)': 'Normalladen',
        })
        for col_name in ['HPC', 'Schnellladen', 'Normalladen']:
            if col_name not in agg.columns:
                agg[col_name] = 0
        agg['Gesamt'] = agg[['HPC', 'Schnellladen', 'Normalladen']].sum(axis=1)
        district_data = agg.reset_index()

        merged_gdf = gdf_districts.merge(district_data, on='AGS', how='left')
        for col_name in ['Gesamt', 'HPC', 'Schnellladen', 'Normalladen']:
            merged_gdf[col_name] = merged_gdf[col_name].fillna(0).astype(int)
        gdf_for_map = merged_gdf[['AGS', 'GEN', 'geometry', 'Gesamt', 'HPC', 'Schnellladen', 'Normalladen']]

        m = folium.Map(location=[51.16, 10.45], tiles="CartoDB positron", zoom_start=6, min_zoom=6, max_bounds=True)
        m.fit_bounds([[47.27, 5.87], [55.06, 15.04]])

        max_val = int(gdf_for_map['Gesamt'].max()) if len(gdf_for_map) > 0 else 0
        bins = sorted(set([0] + [b for b in [100, 500, 1000, 2500] if 0 < b < max_val] + [max_val + 1]))
        if len(bins) < 4:
            extras = [i for i in range(1, 10) if i not in bins][:4 - len(bins)]
            bins = sorted(set(bins + extras))

        folium.Choropleth(
            geo_data=gdf_for_map,
            data=gdf_for_map,
            columns=['AGS', 'Gesamt'],
            key_on='feature.properties.AGS',
            fill_color='Greens',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Anzahl Ladepunkte pro Kreis',
            highlight=True,
            bins=bins
        ).add_to(m)

        folium.GeoJson(
            gdf_for_map,
            style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent', 'weight': 0},
            highlight_function=lambda x: {'weight': 2, 'color': NOW_DUNKELBLAU, 'fillOpacity': 0.1},
            tooltip=folium.GeoJsonTooltip(
                fields=['GEN', 'Gesamt', 'HPC', 'Schnellladen', 'Normalladen'],
                aliases=['Kreis:', 'Ladepunkte gesamt:', 'HPC (>= 150 kW):', 'Schnellladen (> 22 kW):', 'Normalladen (<= 22 kW):'],
                sticky=True,
                style="""
                    background-color: white;
                    border: 2px solid #003247;
                    border-radius: 6px;
                    box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
                    font-size: 13px;
                    padding: 8px;
                """
            )
        ).add_to(m)

        st_folium(m, use_container_width=True, height=600)
    else:
        st.warning("Geodaten (Shapefile) konnten nicht geladen werden. Die Karte wird nicht angezeigt.")

    # --- ABSCHNITT LIMITATIONEN & QUELLEN ---
    st.divider()
    st.header("Limitationen")

    st.markdown("""
    Dieses Dashboard bietet einen umfassenden Überblick über den **Bestand** der öffentlichen Ladeinfrastruktur in Deutschland. Für eine vollständige Bewertung des Marktes müssen jedoch qualitative und ökonomische Faktoren berücksichtigt werden, die über eine reine Bestandszählung und historische Entwicklung hinausgehen.

    - **Auslastungsgrad:** Das Dashboard erfasst den Bestand, aber nicht die tatsächliche Nutzung der Ladeinfrastruktur. Geringe Auslastung ist für einige Standorte eine zentrale Herausforderung, die hier nicht abgebildet wird. Das kann mit Metriken wie **durchschnittliche Ladevorgänge pro Ladepunkt und Tag** oder **durchschnittlich verladene Energiemenge pro Ladepunkt und Tag** ergänzt werden.

    - **Verhältnis von Ladepunkten zu E-Fahrzeugen:** Die reine Anzahl an Ladepunkten pro Region ist nur bedingt aussagekräftig. Eine entscheidende Kennzahl ist das Verhältnis zum lokalen E-Fahrzeugbestand, um die tatsächliche Versorgungsdichte zu bewerten. Deutschlandweit teilen sich etwa zehn E-Autos einen öffentlichen Ladepunkt.

    - **Zuverlässigkeit und Nutzererfahrung:** Gezählt werden alle registrierten Ladepunkte, unabhängig von ihrem Betriebszustand. Die tatsächliche Ausfallrate aus Nutzersichtgit ist ein entscheidender Qualitätsfaktor, der hier unberücksichtigt bleibt. Diese Diskrepanz zur offiziellen "Uptime" entsteht z.B. durch Softwarefehler oder defekte QR-Codes.

    - **Ökonomischer Kontext:** Faktoren wie der komplexe Tarifstrukturen, die durch über gewerbliche 8.000 Betreiber entstehen, Preismodelle und die allgemeine Wirtschaftlichkeit der Standorte werden nicht analysiert. Diese beeinflussen jedoch die Marktdynamik und den weiteren Ausbau maßgeblich.
    """)

    st.divider()
    st.header("Quellen")

    datenstand = pd.to_datetime(df['Inbetriebnahmedatum']).max().strftime('%d.%m.%Y')

    st.markdown(f"""
    - Bundesnetzagentur ({pd.to_datetime(df['Inbetriebnahmedatum']).max().year}) *Ladesäulenregister der öffentlich zugänglichen Ladepunkte*, Datenstand {datenstand}. Bonn: Bundesnetzagentur. [↗](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/DownloadundKontakt.html)
    - Bundesamt für Kartographie und Geodäsie (2024) *Verwaltungsgebiete 1:250 000 (VG250)*. Frankfurt am Main: BKG. [↗](https://gdz.bkg.bund.de/)
    - Lobas-Funck, F., Meister, S. und Weißbach, L. (2024) *Whitepaper Lade-Use-Cases*. Berlin: Nationale Leitstelle Ladeinfrastruktur / NOW GmbH. [↗](https://nationale-leitstelle.de/wp-content/uploads/2024/07/Whitepaper_LUC_Nationale-Leitstelle-Ladeinfrastruktur_2024.pdf)
    - Reiner Lemoine Institut (2024) *Ladeinfrastruktur nach 2025/2030: Szenarien für den Markthochlauf*, im Auftrag der NOW GmbH. Berlin: NOW GmbH. [↗](https://www.now-gmbh.de/wp-content/uploads/2024/06/Studie_Ladeinfrastruktur-2025-2030_Neuauflage-2024.pdf)
    - Nationale Leitstelle Ladeinfrastruktur (2024) *ö-LIS Report: Monitoringbericht öffentliche Ladeinfrastruktur*. Berlin: NOW GmbH. [↗](https://nationale-leitstelle.de/en/downloads/)
    - Nationale Leitstelle Ladeinfrastruktur (2024) *Studie: Einfach zu Hause laden*. Berlin: NOW GmbH. [↗](https://nationale-leitstelle.de/neue-studie-gibt-wichtige-einblicke-in-das-ladeverhalten-von-privatpersonen/)
    """)
