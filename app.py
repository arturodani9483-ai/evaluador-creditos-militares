import streamlit as st
import pandas as pd
import os
import io
import re

st.set_page_config(page_title="Evaluador de Créditos - FF.AA.", layout="wide", page_icon="🪖")

DB_LIQUIDEZ_FILE = "base_liquidez_militares.csv"
DB_DICTAMENES_FILE = "dictamenes_giraduria.csv"

def estandarizar_columnas(df):
    cols_map = {}
    for c in df.columns:
        c_clean = str(c).strip().upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        
        if 'N° C.I' in c_clean or 'C.I' in c_clean or 'CEDULA' in c_clean or 'EMP_CI' in c_clean or c_clean == 'CI':
            cols_map[c] = 'emp_ci'
        elif 'NOMBRE' in c_clean or 'APELLIDO' in c_clean or 'NOMAPE' in c_clean:
            cols_map[c] = 'emp_nomape'
        elif 'CAT' in c_clean or 'CATEGORIA' in c_clean or 'GRADO' in c_clean:
            cols_map[c] = 'cat_codigo'
        elif 'PRESUPUESTADO' in c_clean or 'SUELDO' in c_clean:
            cols_map[c] = 'presupuestado'
        elif 'JUBILA' in c_clean:
            cols_map[c] = 'jubilacion'
        elif 'GIRA' in c_clean:
            cols_map[c] = 'giraduria'
        elif 'CF2' in c_clean:
            cols_map[c] = 'descuento_cf2'
        elif 'JUDICIAL' in c_clean:
            cols_map[c] = 'judicial'
        elif 'TOTAL' in c_clean and 'DESC' in c_clean:
            cols_map[c] = 'total_desc'
        elif 'LIQUIDO' in c_clean or 'NETO' in c_clean:
            cols_map[c] = 'liquido'
        elif c_clean == 'UNIDAD' or 'DEPENDENCIA' in c_clean:
            cols_map[c] = 'UNIDAD'

    df_renamed = df.rename(columns=cols_map)
    if 'emp_ci' not in df_renamed.columns and len(df_renamed.columns) > 0:
        df_renamed['emp_ci'] = df_renamed.iloc[:, 0]
    return df_renamed

def limpiar_ci(val):
    if pd.isna(val) or val is None:
        return ""
    try:
        s = str(val).split('.')[0].replace('.', '').strip()
        numeros = re.findall(r'\d+', s)
        return str(numeros[0]) if numeros else ""
    except:
        return str(val).strip()

def limpiar_monto(val):
    if pd.isna(val) or val is None:
        return 0.0
    try:
        return float(val)
    except:
        s = str(val).replace('.', '').replace(',', '.').strip()
        numeros = re.findall(r'[-+]?\d*\.\d+|\d+', s)
        return float(numeros[0]) if numeros else 0.0

def formato_guarani(val):
    try:
        return f"{int(round(val)):,}".replace(',', '.')
    except:
        return "0"

def cargar_liquidez():
    if os.path.exists(DB_LIQUIDEZ_FILE):
        try:
            df = pd.read_csv(DB_LIQUIDEZ_FILE, dtype=str)
            if 'emp_ci' in df.columns:
                return df
        except:
            pass
    return pd.DataFrame()

def guardar_liquidez(df):
    df.to_csv(DB_LIQUIDEZ_FILE, index=False)

def cargar_dictamenes():
    if os.path.exists(DB_DICTAMENES_FILE):
        return pd.read_csv(DB_DICTAMENES_FILE, dtype=str)
    return pd.DataFrame(columns=['CEDULA', 'CUOTA_PROPUESTA', 'DICTAMEN_GIRADOR', 'FECHA'])

def guardar_dictamenes(df):
    df.to_csv(DB_DICTAMENES_FILE, index=False)

df_liquidez = cargar_liquidez()
df_dictamenes = cargar_dictamenes()

st.title("🪖 Sistema Evaluador de Capacidad Crediticia (FF.AA.)")

st.sidebar.header("⚙️ Menú Principal")
opcion = st.sidebar.radio("Navegación:", [
    "🔍 Simular / Consultar Crédito", 
    "📋 Dictamen del Girador", 
    "📥 Cargar Base Mensual"
])

# --- MÓDULO 1: SIMULAR / CONSULTAR CRÉDITO ---
if opcion == "🔍 Simular / Consultar Crédito":
    st.subheader("🔍 Buscador de Liquidez por Cédula")
    
    if df_liquidez.empty:
        st.info("👈 La base de datos está vacía. Carga la planilla mensual desde 'Cargar Base Mensual'.")
    else:
        ci_input = st.text_input("Ingresá el Número de Cédula (C.I.):", placeholder="Ej: 1160650").strip().replace('.', '')
        
        if ci_input:
            match = df_liquidez[df_liquidez['emp_ci'].apply(limpiar_ci) == ci_input]
            
            if match.empty:
                st.error(f"No se encontró ningún militar registrado con la C.I. Nº '{ci_input}'.")
            else:
                row = match.iloc[0]
                nombre = row.get('emp_nomape', 'S/N')
                unidad = row.get('UNIDAD', '-')
                categoria = row.get('cat_codigo', '-')

                presupuestado = limpiar_monto(row.get('presupuestado', 0))
                jubilacion = limpiar_monto(row.get('jubilacion', 0))
                giraduria = limpiar_monto(row.get('giraduria', 0))
                desc_cf2 = limpiar_monto(row.get('descuento_cf2', 0))
                judicial = limpiar_monto(row.get('judicial', 0))
                
                total_descuentos = jubilacion + giraduria + desc_cf2 + judicial
                liquido_real = presupuestado - total_descuentos if total_descuentos > 0 else limpiar_monto(row.get('liquido', 0))
                limite_50 = liquido_real / 2.0

                st.markdown("---")
                st.success(f"👤 **Militar:** {nombre} | **C.I.:** {ci_input} | **Categoría:** {categoria}")
                st.info(f"🏛️ **Unidad Militar:** {unidad}")

                st.markdown("### 📊 Desglose de Haberes y Descuentos")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Presupuestado", f"Gs. {formato_guarani(presupuestado)}")
                c2.metric("Jubilación", f"Gs. {formato_guarani(jubilacion)}")
                c3.metric("Giraduría", f"Gs. {formato_guarani(giraduria)}")
                c4.metric("Descuento CF2", f"Gs. {formato_guarani(desc_cf2)}")

                c5, c6, c7 = st.columns(3)
                c5.metric("Judicial", f"Gs. {formato_guarani(judicial)}")
                c6.metric("Líquido Real", f"Gs. {formato_guarani(liquido_real)}")
                c7.metric("Límite Cuota (50%)", f"Gs. {formato_guarani(limite_50)}")

                st.markdown("---")
                st.subheader("💳 Evaluación del Nuevo Crédito")
                cuota_solicitada = st.number_input("Ingresá el Monto de la Cuota para el Nuevo Crédito (Gs.):", min_value=0.0, step=50000.0, format="%.0f")

                if cuota_solicitada > 0:
                    diferencia = limite_50 - cuota_solicitada
                    if cuota_solicitada <= limite_50:
                        st.success("✅ **CRÉDITO FACTIBLE (APROBADO)**")
                        st.write(f"La cuota entra dentro del límite del 50%. Margen disponible: **Gs. {formato_guarani(diferencia)}**")
                    else:
                        st.error("⚠️ **RECHAZADO POR LÍMITE DE LIQUIDEZ DEL 50% - HABLAR CON SU GIRADURÍA**")
                        st.write(f"La cuota supera el límite del 50% por **Gs. {formato_guarani(abs(diferencia))}**.")

                dict_match = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) == ci_input]
                if not dict_match.empty:
                    st.markdown("---")
                    dict_row = dict_match.iloc[-1]
                    st.warning(f"📌 **Dictamen Registrado por Giraduría ({dict_row['FECHA']}):** {dict_row['DICTAMEN_GIRADOR']}")

# --- MÓDULO 2: DICTAMEN DEL GIRADOR ---
elif opcion == "📋 Dictamen del Girador":
    st.subheader("📋 Módulo de Registro de Dictamen de Giraduría")
    
    if df_liquidez.empty:
        st.info("Carga la base de liquidez primero.")
    else:
        ci_girador = st.text_input("Ingresá la Cédula del Militar:", placeholder="Ej: 1160650").strip().replace('.', '')
        
        if ci_girador:
            match = df_liquidez[df_liquidez['emp_ci'].apply(limpiar_ci) == ci_girador]
            
            if match.empty:
                st.error(f"No se encontró la Cédula '{ci_girador}'.")
            else:
                row = match.iloc[0]
                nombre = row.get('emp_nomape', 'S/N')
                unidad = row.get('UNIDAD', '-')
                liquido_real = limpiar_monto(row.get('liquido', 0))
                limite_50 = liquido_real / 2.0

                st.markdown("---")
                st.write("### Datos de Solo Lectura:")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.text_input("Nombre y Apellido:", value=nombre, disabled=True)
                    st.text_input("Unidad Militar:", value=unidad, disabled=True)
                with col_g2:
                    st.text_input("Cédula N°:", value=ci_girador, disabled=True)
                    st.text_input("Límite de Cuota Máxima (50%):", value=f"Gs. {formato_guarani(limite_50)}", disabled=True)

                st.markdown("---")
                dict_previo = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) == ci_girador]
                obs_inicial = dict_previo.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_previo.empty else ""

                with st.form("form_dictamen"):
                    st.subheader("📝 Editar Dictamen / Observación de Giraduría")
                    cuota_evaluando = st.number_input("Monto de Cuota Solicitada (Gs.):", min_value=0.0, step=50000.0, format="%.0f")
                    obs_girador = st.text_area("Observaciones / Respuesta del Girador:", value=obs_inicial, placeholder="Ej: Compra de deuda aprobada / Rechazado definitivo")
                    
                    btn_guardar_dictamen = st.form_submit_button("💾 Guardar Dictamen")

                    if btn_guardar_dictamen:
                        if not obs_girador.strip():
                            st.error("Por favor ingresa una observación para guardar el dictamen.")
                        else:
                            df_dictamenes = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) != ci_girador]
                            nuevo_dictamen = pd.DataFrame([{
                                'CEDULA': ci_girador,
                                'CUOTA_PROPUESTA': formato_guarani(cuota_evaluando),
                                'DICTAMEN_GIRADOR': obs_girador.strip(),
                                'FECHA': pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                            }])
                            df_dictamenes = pd.concat([df_dictamenes, nuevo_dictamen], ignore_index=True)
                            guardar_dictamenes(df_dictamenes)
                            st.success("✅ ¡Dictamen guardado con éxito!")

# --- MÓDULO 3: CARGAR BASE MENSUAL ---
elif opcion == "📥 Cargar Base Mensual":
    st.subheader("📥 Cargar Base de Liquidez Mensual de Militares")
    archivo = st.file_uploader("Seleccioná la planilla en formato Excel o CSV", type=["xlsx", "xls", "csv"])
    
    if archivo:
        if st.button("⚠️ Procesar e Importar Base de Datos Mensual"):
            try:
                ext = archivo.name.lower().split('.')[-1]
                if ext == 'csv':
                    df_cargado = pd.read_csv(archivo, dtype=str)
                else:
                    xls = pd.ExcelFile(archivo)
                    df_cargado = pd.read_excel(xls, sheet_name=0, dtype=str)

                df_normalizado = estandarizar_columnas(df_cargado)

                if df_normalizado.empty:
                    st.warning("No se encontraron datos procesables en el archivo.")
                else:
                    guardar_liquidez(df_normalizado)
                    st.success(f"✅ ¡Base de datos importada correctamente! Total de militares registrados: {len(df_normalizado):,}")
                    st.rerun()
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
