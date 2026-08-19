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
# FILTRO DE FECHA DE CORTE
# ---------------------------------------------------------

fechas_disponibles = sorted(
    df["Fecha_Corte"].dropna().unique(),
    reverse=True
)

fecha_corte = st.selectbox(
    "Selecciona la fecha de corte:",
    options=fechas_disponibles,
    format_func=lambda x: pd.to_datetime(x).strftime("%d/%m/%Y")
)

# ---------------------------------------------------------
# FILTRO DE ESTADO
# ---------------------------------------------------------

filtro_estado = st.selectbox(
    "Filtrar clientes por estado:",
    options=[
        "Todos",
        "Solo con alerta",
        "Sin alerta"
    ]
)

df_corte = df[
    df["Fecha_Corte"] == fecha_corte
].copy()

if filtro_estado == "Solo con alerta":
    df_filtrado = df_corte[
        df_corte["Prediccion_Mora"] == 1
    ].copy()

elif filtro_estado == "Sin alerta":
    df_filtrado = df_corte[
        df_corte["Prediccion_Mora"] == 0
    ].copy()

else:
    df_filtrado = df_corte.copy()
    
# ---------------------------------------------------------
# FILTRO DE CLIENTE
# ---------------------------------------------------------

clientes_disponibles = sorted(
    df_filtrado["Cliente_ID"].dropna().unique()
)

cliente_seleccionado = st.selectbox(
    "Buscar cliente:",
    options=["Todos"] + clientes_disponibles
)

if cliente_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["Cliente_ID"] == cliente_seleccionado
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
# DETALLE DEL CLIENTE SELECCIONADO
# ---------------------------------------------------------

if cliente_seleccionado != "Todos":

    detalle_cliente = df_corte[
        df_corte["Cliente_ID"] == cliente_seleccionado
    ].copy()

    if not detalle_cliente.empty:

        cliente = detalle_cliente.iloc[0]

        st.subheader(f"Detalle del cliente {cliente_seleccionado}")

        col_d1, col_d2, col_d3, col_d4, col_d5, col_d6 = st.columns(6)

        col_d1.metric(
            "Probabilidad de mora",
            f"{cliente['Probabilidad_Mora'] * 100:.2f}%"
        )

        col_d2.metric(
            "Estado",
            "🔴 Alerta" if cliente["Prediccion_Mora"] == 1 else "🟢 Sin alerta"
        )

        col_d3.metric(
            "Saldo actual",
            f"${cliente['Saldo_Actual_USD']:,.2f}"
        )

        col_d4.metric(
            "Facturas abiertas",
            f"{int(cliente['Num_Facturas_Abiertas'])}"
        )

        max_atraso = cliente["Max_Dias_Atraso"]

        if max_atraso <= 0:
            texto_atraso = "Sin atraso"
        else:
            texto_atraso = f"{max_atraso:.0f} días"
        
        col_d5.metric(
            "Máx. días de atraso",
            texto_atraso
        )

        col_d6.metric(
            "Prom. días de pago",
            f"{cliente['Prom_Dias_Pago']:.1f}"
        )
# ---------------------------------------------------------
# CLIENTES CON ALERTA
# ---------------------------------------------------------

if filtro_estado == "Solo con alerta":
    titulo_tabla = "Clientes con alerta de mora"

elif filtro_estado == "Sin alerta":
    titulo_tabla = "Clientes sin alerta de mora"

else:
    titulo_tabla = "Clientes evaluados"

st.subheader(titulo_tabla)

tabla_general = df_filtrado[
    [
        "Cliente_ID",
        "Estado_Riesgo",
        "Probabilidad_Mora",
        "Saldo_Actual_USD",
        "Num_Facturas_Abiertas",
        "Max_Dias_Atraso",
        "Prom_Dias_Pago"
    ]
].copy()

tabla_general["Estado_Riesgo"] = tabla_general["Estado_Riesgo"].replace({
    "Alerta de mora": "🔴 Alerta de mora",
    "Sin alerta": "🟢 Sin alerta"
})

tabla_general["Probabilidad_Mora"] = (
    tabla_general["Probabilidad_Mora"] * 100
)

tabla_general = tabla_general.rename(
    columns={
        "Cliente_ID": "Cliente",
        "Estado_Riesgo": "Estado",
        "Probabilidad_Mora": "Probabilidad de Mora (%)",
        "Saldo_Actual_USD": "Saldo Actual USD",
        "Num_Facturas_Abiertas": "Facturas Abiertas",
        "Max_Dias_Atraso": "Máx. Días de Atraso",
        "Prom_Dias_Pago": "Prom. Días de Pago"
    }
)

tabla_general = tabla_general.sort_values(
    "Probabilidad de Mora (%)",
    ascending=False
)

# ---------------------------------------------------------
# CLIENTES CON ALERTA PARA LOS GRÁFICOS
# ---------------------------------------------------------

# Datos exclusivos de clientes con alerta
alertas = df_corte[
    df_corte["Prediccion_Mora"] == 1
].copy()

# Convertir probabilidad a porcentaje
alertas["Probabilidad_Mora"] = (
    alertas["Probabilidad_Mora"] * 100
)

# Ordenar de mayor a menor probabilidad
alertas = alertas.sort_values(
    "Probabilidad_Mora",
    ascending=False
)

# Tabla utilizada por los gráficos
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
    tabla_general,
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
    ax.set_xlim(78, 101)

    ax.axvline(
    x=80,
    linestyle="--",
    linewidth=1.5,
    label="Umbral 80%"
    )
    
    ax.legend(
        loc="lower right",
        fontsize=8
    )

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

    ax2.set_xlabel("Saldo Actual USD (millones)")

    ax2.xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x/1_000_000:.0f}M")
    )
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
