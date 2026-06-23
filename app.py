import streamlit as st
import pandas as pd

st.set_page_config(page_title="Transformación de Balances", layout="wide")

st.title("📊 Transformador de Balances (Horizontal → Vertical)")

# Cargar archivo
archivo = st.file_uploader("Sube tu archivo de Excel", type=["xlsx"])

if archivo:
    # Leer hoja completa sin encabezados
    df_raw = pd.read_excel(archivo, header=None)

    st.subheader("Vista original")
    st.dataframe(df_raw.head(15))

    try:
        # -------------------------------
        # CONFIGURACIÓN (ajustable)
        # -------------------------------
        fila_po = 1      # fila 2 (index 1)
        fila_fecha = 4   # fila 5 (index 4)
        fila_inicio_data = 5  # fila 6 (index 5)
        col_inicio_balances = 230  # HW aprox (ajusta si necesitas)

        # -------------------------------
        # DATOS FIJOS (columnas A-L)
        # -------------------------------
        df_fijo = df_raw.iloc[fila_inicio_data:, :12].copy()
        df_fijo.columns = [f"Col_{i}" for i in range(1, 13)]

        # -------------------------------
        # BALANCES
        # -------------------------------
        df_balances = df_raw.iloc[fila_inicio_data:, col_inicio_balances:].copy()

        # PO y fechas
        po_values = df_raw.iloc[fila_po, col_inicio_balances:]
        fecha_values = df_raw.iloc[fila_fecha, col_inicio_balances:]

        # Crear nombres de columnas combinando info
        nuevas_columnas = [
            f"{po}_{fecha}" for po, fecha in zip(po_values, fecha_values)
        ]

        df_balances.columns = nuevas_columnas

        # -------------------------------
        # UNPIVOT
        # -------------------------------
        df_final = df_balances.copy()
        df_final = pd.concat([df_fijo.reset_index(drop=True), df_balances.reset_index(drop=True)], axis=1)

        df_melt = df_final.melt(
            id_vars=df_fijo.columns.tolist(),
            var_name="PO_FECHA",
            value_name="BALANCE"
        )

        # Separar PO y FECHA
        df_melt[["PO", "FECHA"]] = df_melt["PO_FECHA"].str.split("_", expand=True)

        # Limpiar datos vacíos
        df_melt = df_melt[df_melt["PO"].notna()]
        df_melt = df_melt[df_melt["BALANCE"].notna()]

        # -------------------------------
        # RESULTADO
        # -------------------------------
        st.subheader("✅ Resultado Vertical")
        st.dataframe(df_melt)

        # Descargar archivo
        st.download_button(
            label="📥 Descargar resultado",
            data=df_melt.to_csv(index=False),
            file_name="balances_vertical.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
