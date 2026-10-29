"""Gráficas interactivas de las tablas publicadas, sin recalcular perfiles."""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    if year is not None:
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


def age_bars(segments, tokens, year):
    """Barras contiguas por edad y paneles por sexo, como la figura del README."""
    sexes = [s for s in ["Hombres", "Mujeres"] if s in set(segments.sexo)]
    fig = make_subplots(rows=len(sexes), cols=1, shared_xaxes=True,
                         vertical_spacing=.16 if len(sexes) > 1 else 0,
                         subplot_titles=sexes)
    seen = set()
    for row, sex in enumerate(sexes, start=1):
        for p, name in NAMES.items():
            group = segments[(segments.sexo == sex) & (segments.perfil == p)].sort_values("edad")
            if group.empty:
                continue
            fig.add_trace(go.Bar(
                x=group.edad, y=group[str(year)], width=1, name=name, legendgroup=str(p),
                showlegend=p not in seen, marker=dict(color=COLORS[p], line_width=0),
                customdata=group[["sexo", "nombre"]].to_numpy(),
                hovertemplate="%{customdata[0]} · %{x} años<br>%{customdata[1]}<br>Participación: %{y:.2f}%<extra></extra>"
            ), row=row, col=1)
            seen.add(p)
    finish(fig, tokens, height=640 if len(sexes) == 2 else 400)
    fig.update_layout(barmode="overlay", bargap=0, margin=dict(l=15, r=20, t=35, b=75),
                       legend=dict(y=-.17, traceorder="normal"))
    # Puede haber un perfil que aparezca por primera vez en el segundo panel.
    fig.data = tuple(sorted(fig.data, key=lambda trace: list(NAMES.values()).index(trace.name)))
    fig.update_xaxes(range=[segments.edad.min()-.5, segments.edad.max()+.5], dtick=10)
    fig.update_xaxes(title="Edad cumplida", row=len(sexes), col=1)
    fig.update_yaxes(title=f"Participación {year} (%)")
    for annotation in fig.layout.annotations:
        annotation.update(x=0, xanchor="left", font=dict(color=tokens["text"], size=16))
    return fig


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


def sex_gap_data(segments, year):
    """Comparar solo edades con ambos sexos presentes tras aplicar los filtros."""
    rates = segments.pivot(index="edad", columns="sexo", values=str(year))
    if not {"Hombres", "Mujeres"}.issubset(rates.columns):
        return rates.iloc[0:0].rename_axis(columns=None).reset_index()
    rates = rates.dropna(subset=["Hombres", "Mujeres"]).sort_index()
    rates["brecha_pp"] = rates.Mujeres - rates.Hombres
    return rates.rename_axis(columns=None).reset_index()


def sex_gap_chart(gaps, tokens, year):
    positive, negative = "#D65D91", "#50BFC3"
    # Barras divergentes: cada edad conserva su valor real y no se conectan
    # edades ausentes por los filtros.
    fig = go.Figure()
    for label, mask, color in [
        ("Mayor participación de mujeres", gaps.brecha_pp >= 0, positive),
        ("Mayor participación de hombres", gaps.brecha_pp < 0, negative),
    ]:
        group = gaps[mask]
        if group.empty:
            continue
        fig.add_trace(go.Bar(x=group.edad, y=group.brecha_pp, name=label,
                             marker=dict(color=color, line_width=0), width=.8,
                             customdata=group[["Mujeres", "Hombres"]].to_numpy(),
                             hovertemplate="%{x} años<br>Mujeres: %{customdata[0]:.2f}%<br>Hombres: %{customdata[1]:.2f}%<br>Brecha: %{y:+.2f} puntos<extra></extra>"))
    finish(fig, tokens, height=420, y_percent=False)
    extent = max(2, float(gaps.brecha_pp.abs().max()) * 1.2)
    fig.update_yaxes(title="Mujeres − hombres · puntos porcentuales", range=[-extent, extent],
                      ticksuffix=" pp", zeroline=True, zerolinecolor=tokens["muted"], zerolinewidth=1.5)
    fig.update_xaxes(title="Edad cumplida", range=[gaps.edad.min()-1, gaps.edad.max()+1], dtick=10)
    fig.update_layout(barmode="overlay", legend=dict(y=-.22),
                       title=dict(text=f"Brecha de participación · {year}", font=dict(size=14), x=.02))
    return fig
