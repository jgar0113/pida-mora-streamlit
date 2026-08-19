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