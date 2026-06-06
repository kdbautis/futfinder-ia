import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Fútbol Internacional 1872-2025",
    layout="wide",
)

@st.cache_data
def load_data():
    results = pd.read_csv("clean-data/results_clean.csv", parse_dates=["date"])
    goalscorers = pd.read_csv("clean-data/goalscorers_clean.csv", parse_dates=["date"])
    return results, goalscorers

results, goalscorers = load_data()
results_viz = results[results["year"] <= 2025].copy()

st.title("Análisis histórico del fútbol internacional (1872-2025)")

# Sidebar
st.sidebar.header("Filtros globales")
year_min = int(results_viz["year"].min())
year_max = int(results_viz["year"].max())
year_range = st.sidebar.slider("Rango de años", year_min, year_max, (1930, 2025))

df = results_viz[
    (results_viz["year"] >= year_range[0]) & (results_viz["year"] <= year_range[1])
].copy()

st.sidebar.caption(f"{len(df):,} partidos en el rango seleccionado")

# Tabs
tab_doc, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Documentación",
    "Goles por año",
    "Ventaja de local",
    "Ranking selecciones",
    "Perfil de selección",
    "Top goleadores",
])

# ── Documentacion ─────────────────────────────────────────────────────────────
with tab_doc:
    st.header("Documentacion del proyecto")

    st.markdown("""
**Integrantes:** Alejandro Paz · Kevin Bautista

---

### Descripción del problema

Durante más de 150 años el fútbol internacional ha dejado un registro de decenas de miles de
partidos que refleja tanto la evolucion del deporte como los cambios geopoliticos del mundo.
Sin embargo, ese volumen de datos es dificil de explorar manualmente: ¿qué selecciones han
dominado en distintas épocas? ¿ha disminuido la ventaja de jugar como local con el tiempo?
¿cómo varian los patrones de gol segun el tipo de torneo?

Este panel interactivo permite responder esas preguntas filtrando por periodo, selección y
torneo, sin requerir conocimiento técnico.

---

### Datos

**Fuente:** [International football results from 1872 to 2025 — Kaggle](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017)

El dataset contiene resultados de partidos de fútbol masculino de selecciones nacionales
desde 1872 hasta 2025, excluyendo Juegos Olímpicos y equipos sub-23.

| Archivo | Descripción de dominio | Descripción abstracta |
|---|---|---|
| `results.csv` | Resultado de un partido internacional | Evento binario entre dos nodos (equipos), con atributos cuantitativos (goles) y categóricos (torneo, sede) |
| `goalscorers.csv` | Gol anotado en un partido | Item con atributos de jugador, equipo, tiempo y tipo (normal / autogol / penalti) |

---

### Preprocesamiento

Pasos realizados:
- Parseo de fechas y eliminación de 72 partidos futuros (Mundial 2026 sin resultado aún)
- Conversión de scores de `float` a `int`
- Columnas derivadas: `result` (home_win / draw / away_win), `total_goals`, `year`, `decade`
- Datos guardados en `clean-data/` como CSV

---

### Escenario de uso

**Contexto:** Junio de 2026, semanas antes del Mundial. Alex es periodista deportivo de un
diario ecuatoriano y necesita preparar una nota de contexto sobre el historial internacional de la
selección de Ecuador.

**Tareas que realiza Alex:**
1. Abre el panel y mueve el slider de anos a 1990-2025 para enfocarse en la era moderna.
2. En la pestana *Perfil de selección* elige "Ecuador": ve las metricas globales y observa que
   la tasa de victorias cayo desde los anos 90. Identifica a Argentina como rival más frecuente.
3. En *Ranking selecciones* sube el minimo de partidos a 100 y compara Ecuador contra Brasil y
   Argentina para dimensionar la brecha competitiva.
4. En *Top goleadores* filtra por "Ecuador" para identificar a los maximos anotadores historicos
   e incluirlos en la nota.

---

### Referencias

- Mart Jurisoo — *International football results from 1872 to 2025*, Kaggle, 2024.
    """)

    st.divider()
    st.header("Abstracción de datos y tareas (Fase 3)")

    st.subheader("Conjunto de datos")

    n_results = len(results)
    n_goals = len(goalscorers)

    st.markdown(f"""
**`results_clean.csv`** — Tipo: Tabla — Cardinalidad: {n_results:,} partidos

| Atributo | Origen | Tipo | Cardinalidad / Rango |
|---|---|---|---|
| `date` | Original | Temporal | {results["date"].min().strftime("%Y-%m-%d")} a {results["date"].max().strftime("%Y-%m-%d")} |
| `home_team` | Original | Categórico | {results["home_team"].nunique()} equipos únicos |
| `away_team` | Original | Categórico | {results["away_team"].nunique()} equipos únicos |
| `home_score` | Original | Cuantitativo | {int(results["home_score"].min())} a {int(results["home_score"].max())} goles |
| `away_score` | Original | Cuantitativo | {int(results["away_score"].min())} a {int(results["away_score"].max())} goles |
| `tournament` | Original | Categórico | {results["tournament"].nunique()} torneos únicos |
| `city` | Original | Categórico | {results["city"].nunique():,} ciudades únicas |
| `country` | Original | Categórico | {results["country"].nunique()} paises únicos |
| `neutral` | Original | Booleano | 2 valores (True / False) |
| `result` | **Derivado** | Categórico ordinal | 3 valores: home_win, draw, away_win |
| `total_goals` | **Derivado** | Cuantitativo | {int(results["total_goals"].min())} a {int(results["total_goals"].max())} goles por partido |
| `year` | **Derivado** | Cuantitativo | {int(results["year"].min())} a {int(results["year"].max())} |
| `decade` | **Derivado** | Ordinal | {results["decade"].nunique()} decadas |

**`goalscorers_clean.csv`** — Tipo: Tabla — Cardinalidad: {n_goals:,} goles

| Atributo | Origen | Tipo | Cardinalidad / Rango |
|---|---|---|---|
| `scorer` | Original | Categórico | {goalscorers["scorer"].nunique():,} jugadores únicos |
| `team` | Original | Categórico | {goalscorers["team"].nunique()} equipos |
| `minute` | Original | Cuantitativo | {int(goalscorers["minute"].min())} a {int(goalscorers["minute"].max())} minutos |
| `own_goal` | Original | Booleano | 2 valores |
| `penalty` | Original | Booleano | 2 valores |
    """)

    st.subheader("Abstracción de tareas")
    st.markdown("""
Se definen cinco tareas abstractas que cubren en conjunto más de cinco atributos distintos.

| # | Tarea abstracta | Pregunta de dominio | Atributos | Visualizacion |
|---|---|---|---|---|
| 1 | Descubrir tendencia | ¿Como evoluciono el promedio de goles por partido a lo largo del tiempo? | `year`, `total_goals` | Goles por año |
| 2 | Comparar | ¿Que selección tiene la mayor tasa de victorias historica? | `home_team`, `away_team`, `result` | Ranking selecciones |
| 3 | Caracterizar distribución | ¿Varia la ventaja de local segun el tipo de torneo? | `tournament`, `result`, `neutral` | Ventaja de local |
| 4 | Explorar | ¿Cuales son el historial y los rivales más frecuentes de una selección? | `home_team`, `away_team`, `year`, `result` | Perfil de selección |
| 5 | Ordenar | ¿Quienes son los maximos goleadores historicos de una selección? | `scorer`, `team`, `own_goal` | Top goleadores |
    """)

    st.divider()
    st.header("Marcas y canales (Fase 4)")
    st.markdown("""
### Vista 1: Goles por año — gráfico de línea

**Tarea:** descubrir tendencia en datos temporales continuos.

**Marca:** línea. **Canales principales:** posicion en x (año) y posicion en y (promedio de goles).

La posicion es el canal de mayor precision perceptual para datos cuantitativos. La línea conecta valores ordenados en el tiempo, y su pendiente codifica de forma intuitiva la direccion e intensidad del cambio. Una alternativa de barras por año produciria ~150 columnas, dificultando ver la tendencia global y ocultando la estructura temporal. La segunda traza (media movil) usa **color** como canal secundario: el rojo sobre el azul permite separar la señal suavizada del ruido anual sin ocultar los datos originales.

---

### Vista 2: Ventaja de local — barras apiladas horizontales

**Tarea:** caracterizar la distribución de tres categorias de resultado (local / empate / visitante) comparando distintos torneos.

**Marca:** barra apilada. **Canal principal:** longitud acumulada (porcentaje). **Canal secundario:** color categórico (azul = victoria local, gris = empate, rojo = victoria visitante).

Las barras apiladas permiten leer tanto la proporcion de cada categoria como el total (siempre 100 %) en una sola vista; la longitud es el canal más preciso para comparar magnitudes. El esquema de color azul/gris/rojo es semanticamente natural (local favorecido, empate neutro, visitante desfavorecido) y produce un contraste suficiente sin requerir leyenda elaborada. Barras agrupadas dificultarian leer proporciones porque requieren comparar alturas separadas; graficos de torta por torneo impediran comparar entre torneos porque los angulos son menos precisos que las longitudes.

---

### Vista 3: Ranking de selecciones — barras horizontales ordenadas

**Tarea:** comparar la tasa de victorias entre un conjunto de equipos.

**Marca:** barra. **Canal principal:** longitud (porcentaje de victorias). **Canal secundario:** color secuencial (escala de azules).

La longitud es el canal optimo para comparar una magnitud entre muchos items. La orientacion horizontal permite leer los nombres de los equipos sin rotacion, mejorando la legibilidad. El ordenamiento descendente convierte la tarea de comparacion en un lookup directo (el mejor equipo aparece arriba). El color en escala secuencial es un canal redundante que refuerza visualmente el ranking pero no agrega una nueva dimension de datos; esto sigue el principio de redundancia controlada para facilitar la percepcion.

---

### Vista 4: Perfil de selección — línea temporal + barras de rivales

**Tarea:** explorar el historial de victorias de un equipo a lo largo del tiempo e identificar sus rivales más frecuentes.

**Marcas y canales (sub-vista 1):** igual que Vista 1 — línea con posicion en x e y para tendencia temporal. Se agrega una línea de referencia horizontal (promedio historico) como marca auxiliar que da contexto sin ocupar espacio adicional.

**Marcas y canales (sub-vista 2):** barras horizontales con longitud = numero de partidos contra cada rival, igual lógica que Vista 3. Separar en dos graficos distintos evita sobrecargar una sola vista con multiples dimensiones simultaneas, lo que aumentaria la carga cognitiva sin beneficio de percepcion conjunta entre las dos variables.

---

### Vista 5: Top goleadores — barras horizontales ordenadas

**Tarea:** ordenar jugadores por cantidad de goles para identificar a los maximos anotadores.

**Marca:** barra. **Canal principal:** longitud (conteo de goles). **Canal secundario:** color secuencial (escala de naranjas).

La lógica es idéntica a Vista 3 (longitud para ordenar y comparar un único atributo cuantitativo). Se elige naranja en lugar de azul para diferenciar visualmente esta vista del ranking de equipos, estableciendo una consistencia cromatica dentro de la app: azul identifica a equipos (selecciones), naranja identifica a jugadores individuales.
    """)

# Tab 1: Goles por año
with tab1:
    st.subheader("Evolucion de goles promedio por partido")

    moving_avg = st.checkbox("Mostrar media movil (5 anos)", value=True)

    yearly = df.groupby("year")["total_goals"].mean().reset_index()
    yearly.columns = ["year", "avg_goals"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly["year"], y=yearly["avg_goals"],
        mode="lines", name="Promedio anual",
        line=dict(color="steelblue", width=1.5), opacity=0.7,
    ))
    if moving_avg:
        yearly["ma5"] = yearly["avg_goals"].rolling(5, center=True).mean()
        fig.add_trace(go.Scatter(
            x=yearly["year"], y=yearly["ma5"],
            mode="lines", name="Media movil 5 anos",
            line=dict(color="crimson", width=2.5),
        ))
    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Goles promedio por partido",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 2: Ventaja de local
with tab2:
    st.subheader("Ventaja de local por tipo de torneo")

    top_n = st.slider("Top N torneos (por partidos disputados)", 5, 15, 10)
    top_tournaments = df["tournament"].value_counts().head(top_n).index.tolist()
    selected = st.multiselect("Torneos a mostrar", top_tournaments, default=top_tournaments)

    if selected:
        df_t = df[df["tournament"].isin(selected)]
        result_map = {
            "home_win": "Victoria local",
            "draw": "Empate",
            "away_win": "Victoria visitante",
        }
        breakdown = (
            df_t.groupby(["tournament", "result"]).size().reset_index(name="count")
        )
        totals = breakdown.groupby("tournament")["count"].sum().reset_index(name="total")
        breakdown = breakdown.merge(totals, on="tournament")
        breakdown["pct"] = breakdown["count"] / breakdown["total"] * 100
        breakdown["resultado"] = breakdown["result"].map(result_map)

        order = (
            breakdown[breakdown["resultado"] == "Victoria local"]
            .sort_values("pct")["tournament"].tolist()
        )

        fig2 = px.bar(
            breakdown,
            x="pct", y="tournament", color="resultado", orientation="h",
            category_orders={"tournament": order},
            color_discrete_map={
                "Victoria local": "#2196F3",
                "Empate": "#9E9E9E",
                "Victoria visitante": "#F44336",
            },
            labels={"pct": "% partidos", "tournament": "Torneo"},
            text=breakdown["pct"].round(1).astype(str) + "%",
        )
        fig2.update_layout(
            barmode="stack",
            xaxis_range=[0, 100],
            legend=dict(orientation="h", y=1.12),
        )
        fig2.update_traces(textposition="inside", textfont_size=11)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Selecciona al menos un torneo.")

# Tab 3: Ranking selecciones
with tab3:
    st.subheader("Ranking historico de selecciones")

    col_a, col_b = st.columns(2)
    min_matches = col_a.slider("Minimo de partidos jugados", 10, 200, 50)
    top_n_teams = col_b.slider("Mostrar top N selecciones", 10, 30, 20)

    home_w = df[df["result"] == "home_win"].groupby("home_team").size()
    away_w = df[df["result"] == "away_win"].groupby("away_team").size()
    draw_h = df[df["result"] == "draw"].groupby("home_team").size()
    draw_a = df[df["result"] == "draw"].groupby("away_team").size()
    played_h = df.groupby("home_team").size()
    played_a = df.groupby("away_team").size()

    teams_idx = sorted(set(df["home_team"]).union(df["away_team"]))
    stats = pd.DataFrame(index=teams_idx)
    stats.index.name = "team"
    stats["wins"] = home_w.add(away_w, fill_value=0)
    stats["draws"] = draw_h.add(draw_a, fill_value=0)
    stats["played"] = played_h.add(played_a, fill_value=0)
    stats["losses"] = stats["played"] - stats["wins"] - stats["draws"]
    stats["win_pct"] = stats["wins"] / stats["played"] * 100
    stats = (
        stats[stats["played"] >= min_matches]
        .sort_values("win_pct", ascending=False)
        .head(top_n_teams)
        .reset_index()
    )

    fig3 = px.bar(
        stats.iloc[::-1],
        x="win_pct", y="team", orientation="h",
        color="win_pct", color_continuous_scale="Blues",
        labels={"win_pct": "% victorias", "team": "Seleccion"},
        text=stats.iloc[::-1]["win_pct"].round(1).astype(str) + "%",
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(
        stats[["team", "played", "wins", "draws", "losses", "win_pct"]]
        .rename(columns={
            "team": "Seleccion", "played": "Jugados", "wins": "Victorias",
            "draws": "Empates", "losses": "Derrotas", "win_pct": "% Victorias",
        })
        .round(1),
        use_container_width=True,
        hide_index=True,
    )

# Tab 4: Perfil de selección
with tab4:
    st.subheader("Perfil historico de una selección")

    all_teams = sorted(set(results_viz["home_team"]).union(results_viz["away_team"]))
    default_idx = all_teams.index("Brazil") if "Brazil" in all_teams else 0
    team = st.selectbox("Selecciona una selección", all_teams, index=default_idx)

    team_home = df[df["home_team"] == team].copy()
    team_away = df[df["away_team"] == team].copy()
    team_home["won"] = (team_home["result"] == "home_win").astype(int)
    team_home["drew"] = (team_home["result"] == "draw").astype(int)
    team_home["lost"] = (team_home["result"] == "away_win").astype(int)
    team_away["won"] = (team_away["result"] == "away_win").astype(int)
    team_away["drew"] = (team_away["result"] == "draw").astype(int)
    team_away["lost"] = (team_away["result"] == "home_win").astype(int)

    tm = pd.concat([
        team_home[["year", "won", "drew", "lost"]],
        team_away[["year", "won", "drew", "lost"]],
    ])

    if tm.empty:
        st.warning("Sin partidos en el rango seleccionado para esta selección.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Partidos", len(tm))
        c2.metric("Victorias", f"{tm['won'].sum()} ({tm['won'].mean()*100:.1f}%)")
        c3.metric("Empates", str(tm["drew"].sum()))
        c4.metric("Derrotas", str(tm["lost"].sum()))

        yearly_t = tm.groupby("year")["won"].mean().reset_index()
        yearly_t["win_pct"] = yearly_t["won"] * 100
        avg_line = yearly_t["win_pct"].mean()

        fig4a = px.line(
            yearly_t, x="year", y="win_pct",
            labels={"win_pct": "% victorias", "year": "Ano"},
            title=f"Tasa de victorias por año — {team}",
        )
        fig4a.add_hline(
            y=avg_line, line_dash="dash", line_color="gray",
            annotation_text=f"Promedio: {avg_line:.1f}%",
            annotation_position="bottom right",
        )
        st.plotly_chart(fig4a, use_container_width=True)

        rivals = (
            team_home["away_team"].value_counts()
            .add(team_away["home_team"].value_counts(), fill_value=0)
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        rivals.columns = ["Rival", "Partidos"]

        fig4b = px.bar(
            rivals.iloc[::-1], x="Partidos", y="Rival", orientation="h",
            title=f"Top 10 rivales más frecuentes — {team}",
            text="Partidos",
        )
        fig4b.update_traces(marker_color="steelblue", textposition="outside")
        st.plotly_chart(fig4b, use_container_width=True)

# Tab 5: Top goleadores
with tab5:
    st.subheader("Top goleadores historicos")

    team_options = ["Todos"] + sorted(goalscorers["team"].dropna().unique())
    team_gs = st.selectbox("Filtrar por selección", team_options, key="gs_team")

    gs = goalscorers[goalscorers["own_goal"] == False]
    if team_gs != "Todos":
        gs = gs[gs["team"] == team_gs]

    top_scorers = (
        gs.groupby("scorer").size()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    top_scorers.columns = ["Jugador", "Goles"]

    fig5 = px.bar(
        top_scorers.iloc[::-1],
        x="Goles", y="Jugador", orientation="h",
        color="Goles", color_continuous_scale="Oranges",
        title=f"Top 15 goleadores — {team_gs}",
        text="Goles",
    )
    fig5.update_traces(textposition="outside")
    fig5.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)
