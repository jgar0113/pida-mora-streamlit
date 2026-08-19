import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------

st.set_page_config(
    page_title="Predicción de Mora de Clientes",
    page_icon="📊",
    layout="wide"
)

st.title("Predicción de Mora de Clientes")
st.caption(
    "Modelo basado en el comportamiento histórico de pago"
)

# ---------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------

@st.cache_data
def cargar_datos():
    df = pd.read_excel(
        "resultados_dashboard.xlsx",
        sheet_name="Resultados"
    )

    df["Fecha_Corte"] = pd.to_datetime(
        df["Fecha_Corte"]
    )

    return df


df = cargar_datos()

# ---------------------------------------------------------
# ÚLTIMO CORTE DISPONIBLE
# ---------------------------------------------------------

fecha_corte = df["Fecha_Corte"].max()

df_corte = df[
    df["Fecha_Corte"] == fecha_corte
].copy()

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------

clientes_evaluados = len(df_corte)

clientes_alerta = (
    df_corte["Prediccion_Mora"] == 1
).sum()

porcentaje_alerta = (
    clientes_alerta / clientes_evaluados * 100
)

probabilidad_promedio = (
    df_corte["Probabilidad_Mora"].mean() * 100
)

saldo_alerta = df_corte.loc[
    df_corte["Prediccion_Mora"] == 1,
    "Saldo_Actual_USD"
].sum()

st.subheader(
    f"Fecha de corte: {fecha_corte.strftime('%d/%m/%Y')}"
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Clientes evaluados",
    f"{clientes_evaluados:,}"
)

col2.metric(
    "Clientes con alerta",
    f"{clientes_alerta:,}"
)

col3.metric(
    "% con alerta",
    f"{porcentaje_alerta:.2f}%"
)

col4.metric(
    "Probabilidad promedio",
    f"{probabilidad_promedio:.2f}%"
)

col5.metric(
    "Saldo clientes con alerta",
    f"${saldo_alerta:,.0f}"
)

# ---------------------------------------------------------
# CLIENTES CON ALERTA
# ---------------------------------------------------------

st.subheader("Clientes con alerta de mora")

alertas = df_corte[
    df_corte["Prediccion_Mora"] == 1
].copy()

alertas["Probabilidad_Mora"] = (
    alertas["Probabilidad_Mora"] * 100
)

alertas = alertas.sort_values(
    "Probabilidad_Mora",
    ascending=False
)

tabla = alertas[
    [
        "Cliente_ID",
        "Probabilidad_Mora",
        "Saldo_Actual_USD",
        "Num_Facturas_Abiertas",
        "Max_Dias_Atraso",
        "Prom_Dias_Pago"
    ]
].copy()

tabla = tabla.rename(
    columns={
        "Cliente_ID": "Cliente",
        "Probabilidad_Mora": "Probabilidad de Mora (%)",
        "Saldo_Actual_USD": "Saldo Actual USD",
        "Num_Facturas_Abiertas": "Facturas Abiertas",
        "Max_Dias_Atraso": "Máx. Días de Atraso",
        "Prom_Dias_Pago": "Prom. Días de Pago"
    }
)

st.dataframe(
    tabla,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Probabilidad de Mora (%)": st.column_config.NumberColumn(
            "Probabilidad de Mora (%)",
            format="%.2f%%"
        ),
        "Saldo Actual USD": st.column_config.NumberColumn(
            "Saldo Actual USD",
            format="$%,.2f"
        ),
        "Facturas Abiertas": st.column_config.NumberColumn(
            "Facturas Abiertas",
            format="%d"
        ),
        "Máx. Días de Atraso": st.column_config.NumberColumn(
            "Máx. Días de Atraso",
            format="%.0f"
        ),
        "Prom. Días de Pago": st.column_config.NumberColumn(
            "Prom. Días de Pago",
            format="%.1f"
        )
    }
)

# ---------------------------------------------------------
# GRÁFICOS PRINCIPALES
# ---------------------------------------------------------

col_graf1, col_graf2 = st.columns(2)

# TOP 10 POR PROBABILIDAD
with col_graf1:

    st.subheader("Top 10 por probabilidad de mora")

    top_alertas = tabla.head(10).copy()

    fig, ax = plt.subplots(figsize=(6, 4))

    barras = ax.barh(
        top_alertas["Cliente"][::-1],
        top_alertas["Probabilidad de Mora (%)"][::-1]
    )

    ax.set_xlabel("Probabilidad (%)")
    ax.set_ylabel("Cliente")
    ax.set_xlim(80, 101)

    for barra in barras:
        valor = barra.get_width()

        ax.text(
            valor + 0.10,
            barra.get_y() + barra.get_height() / 2,
            f"{valor:.1f}%",
            va="center",
            fontsize=8
        )

    ax.tick_params(axis="both", labelsize=8)

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


# TOP 10 POR SALDO
with col_graf2:

    st.subheader("Top 10 por saldo actual")

    top_saldo = tabla.sort_values(
        "Saldo Actual USD",
        ascending=False
    ).head(10).copy()

    fig2, ax2 = plt.subplots(figsize=(6, 4))

    barras2 = ax2.barh(
        top_saldo["Cliente"][::-1],
        top_saldo["Saldo Actual USD"][::-1]
    )

    ax2.set_xlabel("Saldo Actual USD")
    ax2.set_ylabel("Cliente")

    for barra in barras2:
        valor = barra.get_width()

        ax2.text(
            valor,
            barra.get_y() + barra.get_height() / 2,
            f" ${valor/1_000_000:.1f}M",
            va="center",
            ha="left",
            fontsize=8
        )

    ax2.tick_params(axis="both", labelsize=8)

    plt.tight_layout()

    st.pyplot(
        fig2,
        use_container_width=True
    )

    plt.close(fig2)
