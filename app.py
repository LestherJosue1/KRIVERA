import streamlit as st
import pandas as pd

st.set_page_config(page_title="Balances Textiles", layout="wide")

st.title("📊 Transformador de Balances (Horizontal → Vertical)")
st.write("Convierte balances textiles a formato vertical (solo negativos)")

# Subir archivo
archivo = st.file_uploader("📂 Sube tu archivo de Excel", type=["xlsx"])

if archivo:
    df_raw = pd.read_excel(archivo, header=None)

    st.subheader("🔍 Vista previa")
    st.dataframe(df_raw.head(15))

    try:
        # -----------------------------------
        # CONFIGURACIÓN
        # -----------------------------------
        fila_po = 1        # fila 2
        fila_fecha = 4     # fila 5
        fila_inicio_data = 5  # fila 6

        # -----------------------------------
        # DETECTAR INICIO DE BALANCES (AUTOMÁTICO)
        # -----------------------------------
        col_inicio_balances = None

        for i, val in enumerate(df_raw.iloc[0]):
            if str(val).strip().upper() == "BAL TEXTIL":
                col_inicio_balances = i + 1
                break

        if col_inicio_balances is None:
            st.error("❌ No se encontró la columna 'BAL TEXTIL'")
            st.stop()

        st.success(f"✅ Inicio de balances detectado en columna: {col_inicio_balances}")

        # -----------------------------------
        # DATOS BASE (A-L)
        # -----------------------------------
        df_fijo = df_raw.iloc[fila_inicio_data:, :12].copy()
        df_fijo.columns = [f"Col_{i}" for i in range(1, 13)]

        # -----------------------------------
        # BALANCES
        # -----------------------------------
        df_balances = df_raw.iloc[fila_inicio_data:, col_inicio_balances:].copy()

        # PO y FECHA
        po_values = df_raw.iloc[fila_po, col_inicio_balances:]
        fecha_values = df_raw.iloc[fila_fecha, col_inicio_balances:]

        # Crear columnas combinadas
        columnas = []
        for po, fecha in zip(po_values, fecha_values):
            if pd.isna(po) or str(po).strip() == "":
                columnas.append(None)
            else:
                columnas.append(f"{po}_{fecha}")

        df_balances.columns = columnas

        # -----------------------------------
        # UNPIVOT (VERTICAL)
        # -----------------------------------
        df_total = pd.concat(
            [df_fijo.reset_index(drop=True), df_balances.reset_index(drop=True)],
            axis=1
        )

        df_melt = df_total.melt(
            id_vars=df_fijo.columns.tolist(),
            var_name="PO_FECHA",
            value_name="BALANCE"
        )

        # -----------------------------------
        # LIMPIEZA
        # -----------------------------------
        df_melt = df_melt[df_melt["PO_FECHA"].notna()]
        df_melt = df_melt[df_melt["BALANCE"].notna()]

        # Separar PO y FECHA
        df_melt[["PO", "FECHA"]] = df_melt["PO_FECHA"].str.split("_", expand=True)

        # -----------------------------------
        # SOLO BALANCES NEGATIVOS ✅
        # -----------------------------------
        df_melt["BALANCE"] = pd.to_numeric(df_melt["BALANCE"], errors="coerce")
        df_melt = df_melt[df_melt["BALANCE"] < 0]

        # -----------------------------------
        # RESULTADO FINAL
        # -----------------------------------
        st.subheader("✅ Resultado final (solo negativos)")
        st.dataframe(df_melt, use_container_width=True)

        # Descargar
        st.download_button(
            label="📥 Descargar resultado (CSV)",
            data=df_melt.to_csv(index=False),
            file_name="balances_negativos.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")
