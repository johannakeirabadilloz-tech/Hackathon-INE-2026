"""Gráficas interactivas de las tablas publicadas, sin recalcular perfiles."""
import plotly.express as px
import plotly.graph_objects as go

from dashboard.data import COLORS, NAMES, YEARS

COLOR_MAP = {NAMES[p]: color for p, color in COLORS.items()}


def finish(fig, tokens, height=410, y_percent=True):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color=tokens["text"], size=12), height=height,
        margin=dict(l=15, r=20, t=25, b=20),
        legend=dict(title=None, orientation="h", y=-.22, x=0, font=dict(size=11, color=tokens["text"])),
        hoverlabel=dict(bgcolor=tokens["surface"], font_color=tokens["text"]),
    )
    fig.update_xaxes(gridcolor=tokens["border"], zeroline=False,
                     tickfont_color=tokens["text"], title_font_color=tokens["text"])
    fig.update_yaxes(gridcolor=tokens["border"], zeroline=False,
                     tickfont_color=tokens["text"], title_font_color=tokens["text"])
    if y_percent:
        fig.update_yaxes(range=[0, 100], ticksuffix="%", title="Participación entre especificados")
    return fig


def history_chart(history, tokens, year):
    fig = px.line(history, x="anio", y="participacion_pct", color="nombre", markers=True,
                  color_discrete_map=COLOR_MAP,
                  custom_data=["tipo_eleccion"], category_orders={"nombre": list(NAMES.values())})
    fig.update_traces(line_width=3, marker_size=8,
                      hovertemplate="%{x} · %{customdata[0]}<br>Participación: %{y:.1f}%<extra>%{fullData.name}</extra>")
    fig.add_vline(x=year, line_dash="dot", line_color=tokens["muted"], opacity=.6)
    fig.update_xaxes(tickvals=YEARS, title=None)
    return finish(fig, tokens)


def age_chart(segments, tokens, year):
    fig = px.scatter(segments, x="edad", y=str(year), color="nombre", symbol="sexo",
                     color_discrete_map=COLOR_MAP, custom_data=["sexo", "nombre"],
                     category_orders={"nombre": list(NAMES.values()), "sexo": ["Hombres", "Mujeres"]})
    fig.update_traces(marker_size=8,
                      hovertemplate="%{customdata[0]} · %{x} años<br>%{customdata[1]}<br>Participación: %{y:.2f}%<extra></extra>")
    fig.update_xaxes(title="Edad cumplida", dtick=10)
    return finish(fig, tokens, height=470)


def share_chart(history, tokens):
    current = history[history.anio == 2024].copy()
    current["etiqueta"] = current.perfil.map(lambda p: f"Perfil {p}")
    fig = px.bar(current, x="pct_lista_2024", y="etiqueta", orientation="h", color="nombre",
                 color_discrete_map=COLOR_MAP, text="pct_lista_2024", custom_data=["nombre"])
    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside", cliponaxis=False,
                      hovertemplate="%{customdata[0]}<br>Lista nominal analizada en 2024: %{x:.1f}%<extra></extra>")
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="Lista nominal analizada · 2024", ticksuffix="%", range=[0, 55])
    fig.update_yaxes(title=None, autorange="reversed", categoryorder="array", categoryarray=[f"Perfil {p}" for p in NAMES])
    return finish(fig, tokens, height=330, y_percent=False)


def territorial_chart(frame, tokens):
    fig = px.bar(frame, x="grupo", y="participacion_pct", color="nombre", barmode="group",
                 color_discrete_map=COLOR_MAP, category_orders={"nombre": list(NAMES.values())})
    fig.update_traces(hovertemplate="%{x}<br>Participación 2024: %{y:.2f}%<extra>%{fullData.name}</extra>")
    fig.update_xaxes(title=None, tickangle=-20 if frame.grupo.nunique() > 3 else 0)
    return finish(fig, tokens, height=470)


def profile_matrix(segments, tokens):
    fig = go.Figure()
    ordered = segments.sort_values(["sexo", "edad"])
    for p, name in NAMES.items():
        group = ordered[ordered.perfil == p]
        fig.add_trace(go.Scatter(x=group.edad, y=group.sexo, mode="markers", name=name,
                                 marker=dict(color=COLORS[p], size=13, symbol="square"),
                                 hovertemplate="%{y} · %{x} años<br>" + name + "<extra></extra>"))
    fig.update_xaxes(title="Edad", range=[17, 100], dtick=10)
    fig.update_yaxes(title=None, categoryorder="array", categoryarray=["Mujeres", "Hombres"])
    return finish(fig, tokens, height=250, y_percent=False)
