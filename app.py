import streamlit as st
import pandas as pd
import os
import io
import re
from fpdf import FPDF

st.set_page_config(page_title="Evaluador de Créditos - FF.AA.", layout="wide", page_icon="🪖")

EXCEL_PERMANENTE = "base_liquidez.xlsx"
DB_LIQUIDEZ_FILE = "base_liquidez_militares.csv"
DB_DICTAMENES_FILE = "dictamenes_giraduria.csv"

# --- CARGA INTELIGENTE Y PERMANENTE ---
def cargar_excel_detectando_cabecera(file_or_path):
    df_raw = pd.read_excel(file_or_path, header=None, dtype=str)
    header_idx = 0
    for idx, row in df_raw.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values if pd.notna(val)])
        if 'C.I' in row_str or 'CEDULA' in row_str or 'NOMBRE' in row_str:
            header_idx = idx
            break
    return pd.read_excel(file_or_path, skiprows=header_idx, dtype=str)

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
        s = str(val).split('.')[0].replace('.', '').replace(',', '').strip()
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

@st.cache_data(ttl=2592000)
def cargar_liquidez():
    if os.path.exists(DB_LIQUIDEZ_FILE):
        try:
            return pd.read_csv(DB_LIQUIDEZ_FILE, dtype=str)
        except:
            pass
    if os.path.exists(EXCEL_PERMANENTE):
        try:
            df = cargar_excel_detectando_cabecera(EXCEL_PERMANENTE)
            return estandarizar_columnas(df)
        except:
            pass
    return pd.DataFrame()

def guardar_liquidez(df):
    df.to_csv(DB_LIQUIDEZ_FILE, index=False)
    st.cache_data.clear()

def cargar_dictamenes():
    if os.path.exists(DB_DICTAMENES_FILE):
        return pd.read_csv(DB_DICTAMENES_FILE, dtype=str)
    return pd.DataFrame(columns=['CEDULA', 'CUOTA_PROPUESTA', 'DICTAMEN_GIRADOR', 'FECHA'])

def guardar_dictamenes(df):
    df.to_csv(DB_DICTAMENES_FILE, index=False)

def generar_pdf_constancia(tipo_reporte, nombre, ci, unidad, presupuestado, jubilacion, tot_desc, liquido, limite, cuota, estado, obs=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "SISTEMA EVALUADOR DE CAPACIDAD CREDITICIA - FF.AA.", border=0, ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, f"Constancia Oficial de {tipo_reporte}", border=0, ln=True, align="C")
    pdf.ln(5)
    pdf.line(10, 28, 200, 28)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "1. DATOS DEL MILITAR / SOCIO", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Nombre y Apellido: {nombre}")
    pdf.cell(90, 6, f"Cédula N°: {ci}", ln=True)
    pdf.cell(100, 6, f"Unidad / Dependencia: {unidad}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "2. RESUMEN DE LIQUIDEZ Y HABERES", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Sueldo Presupuestado: Gs. {formato_guarani(presupuestado)}")
    pdf.cell(90, 6, f"Descuento Jubilación: Gs. {formato_guarani(jubilacion)}", ln=True)
    pdf.cell(100, 6, f"Total Descuentos: Gs. {formato_guarani(tot_desc)}")
    pdf.cell(90, 6, f"Líquido Real Actual: Gs. {formato_guarani(liquido)}", ln=True)
    pdf.cell(100, 6, f"Límite Disponible (50%): Gs. {formato_guarani(limite)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "3. EVALUACIÓN DE CRÉDITO Y DICTAMEN", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Cuota Solicitada: Gs. {formato_guarani(cuota)}")
    pdf.cell(90, 6, f"Estado de Factibilidad: {estado}", ln=True)
    
    if obs:
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Observación / Dictamen de Giraduría: {obs}")

    pdf.ln(15)
    pdf.cell(0, 6, "_____________________________", align="C", ln=True)
    pdf.cell(0, 6, "Firma / Sello de Recepción", align="C", ln=True)

    return bytes(pdf.output())

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
    st.subheader("🔍 Buscador de Liquidez de Personal")
    
    if df_liquidez.empty:
        st.info("👈 La base de datos está vacía. Carga la planilla mensual desde 'Cargar Base Mensual'.")
    else:
        tipo_busqueda = st.radio("Seleccioná el método de búsqueda:", ["💳 Por Número de Cédula", "👤 Por Nombre / Apellido"], horizontal=True)
        matches = pd.DataFrame()
        
        if tipo_busqueda == "💳 Por Número de Cédula":
            ci_input = st.text_input("Ingresá el Número de Cédula (C.I.):", placeholder="Ej: 5511820").strip().replace('.', '')
            if ci_input:
                matches = df_liquidez[df_liquidez['emp_ci'].apply(limpiar_ci) == ci_input]
        else:
            nombre_input = st.text_input("Ingresá el Nombre o Apellido:", placeholder="Ej: Sanabria").strip()
            if nombre_input:
                matches = df_liquidez[df_liquidez['emp_nomape'].astype(str).str.contains(nombre_input, case=False, na=False)]

        if not matches.empty:
            if len(matches) > 1:
                st.warning(f"Se encontraron {len(matches)} coincidencias:")
                opciones = [f"{row['emp_nomape']} (C.I.: {row['emp_ci']}) - {row.get('UNIDAD', '-')}" for idx, row in matches.iterrows()]
                seleccion = st.selectbox("Seleccionar Militar:", opciones)
                idx_sel = opciones.index(seleccion)
                row = matches.iloc[idx_sel]
            else:
                row = matches.iloc[0]

            nombre = row.get('emp_nomape', 'S/N')
            cedula_militar = limpiar_ci(row.get('emp_ci', '0'))
            unidad = row.get('UNIDAD', '-')
            categoria = row.get('cat_codigo', '-')

            presupuestado = limpiar_monto(row.get('presupuestado', 0))
            jubilacion = limpiar_monto(row.get('jubilacion', 0))
            giraduria = limpiar_monto(row.get('giraduria', 0))
            desc_cf2 = limpiar_monto(row.get('descuento_cf2', 0))
            judicial = limpiar_monto(row.get('judicial', 0))
            
            total_descuentos = jubilacion + giraduria + desc_cf2 + judicial
            liquido_real = presupuestado - total_descuentos if total_descuentos > 0 else limpiar_monto(row.get('liquido', 0))
            
            # CÁLCULO BASE REGLAMENTARIA: Presupuestado - Jubilación
            base_imponible = presupuestado - jubilacion
            limite_50 = base_imponible / 2.0
            
            # Suma de deudas financieras (Giraduría + CF2 + Judicial)
            total_deudas_actuales = giraduria + desc_cf2 + judicial
            margen_deuda_restante = limite_50 - total_deudas_actuales

            st.markdown("---")
            st.success(f"👤 **Militar:** {nombre} | **C.I.:** {cedula_militar} | **Categoría:** {categoria}")
            st.info(f"🏛️ **Unidad Militar:** {unidad}")

            st.markdown("### 📊 Desglose de Haberes y Descuentos")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Presupuestado", f"Gs. {formato_guarani(presupuestado)}")
            c2.metric("Jubilación", f"Gs. {formato_guarani(jubilacion)}")
            c3.metric("Giraduría", f"Gs. {formato_guarani(giraduria)}")
            c4.metric("Descuento CF2", f"Gs. {formato_guarani(desc_cf2)}")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Judicial", f"Gs. {formato_guarani(judicial)}")
            c6.metric("Total Descuentos", f"Gs. {formato_guarani(total_descuentos)}")
            c7.metric("Líquido Real", f"Gs. {formato_guarani(liquido_real)}")
            c8.metric("Límite Cuota (50%)", f"Gs. {formato_guarani(limite_50)}")

            # DETECCIÓN DE EXCESO DE DEUDAS ACTUALES (ENFOCADO EN CF2 / GIRADURÍA)
            st.markdown("---")
            if total_deudas_actuales > limite_50:
                exceso_actual = total_deudas_actuales - limite_50
                st.warning(
                    f"⚠️ **ATENCIÓN: Los descuentos de deudas actuales (Gs. {formato_guarani(total_deudas_actuales)}) "
                    f"ya superan el límite del 50% por Gs. {formato_guarani(exceso_actual)}.**\n\n"
                    f"📌 **RECOMENDACIÓN:** Consultar disponibilidad con **CF2** para evaluar margen o beneficios especiales."
                )
            else:
                st.info(f"💡 **Margen disponible para nuevos descuentos:** Gs. {formato_guarani(margen_deuda_restante)}")

            st.subheader("💳 Evaluación del Nuevo Crédito")
            cuota_solicitada = st.number_input("Ingresá el Monto de la Cuota para el Nuevo Crédito (Gs.):", min_value=0.0, step=50000.0, format="%.0f")

            estado_eval = "SIN EVALUAR"
            if cuota_solicitada > 0:
                if total_deudas_actuales + cuota_solicitada <= limite_50:
                    estado_eval = "APROBADO (DENTRO DEL MARGEN DEL 50%)"
                    st.success("✅ **CRÉDITO FACTIBLE (APROBADO)**")
                    st.write(f"La cuota entra dentro del límite del 50%. Margen restante: **Gs. {formato_guarani(margen_deuda_restante - cuota_solicitada)}**")
                else:
                    estado_eval = "RECHAZADO - CONSULTAR DISPONIBILIDAD CON CF2"
                    st.error("⚠️ **RECHAZADO POR LÍMITE DE LIQUIDEZ DEL 50% - CONSULTAR DISPONIBILIDAD CON CF2**")

            dict_match = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) == cedula_militar]
            obs_dictamen = dict_match.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_match.empty else "Sin observaciones previas."
            
            if not dict_match.empty:
                st.markdown("---")
                st.warning(f"📌 **Dictamen Registrado por Giraduría:** {obs_dictamen}")

            st.markdown("---")
            pdf_bytes = generar_pdf_constancia("Simulación de Crédito", nombre, cedula_militar, unidad, presupuestado, jubilacion, total_descuentos, liquido_real, limite_50, cuota_solicitada, estado_eval, obs_dictamen)
            
            st.download_button(
                label="📄 Descargar / Imprimir Constancia de Evaluación (PDF)",
                data=pdf_bytes,
                file_name=f"Constancia_Credito_{cedula_militar}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# --- MÓDULO 2: DICTAMEN DEL GIRADOR ---
elif opcion == "📋 Dictamen del Girador":
    st.subheader("📋 Módulo de Registro de Dictamen de Giraduría")
    
    if df_liquidez.empty:
        st.info("Carga la base de liquidez primero.")
    else:
        tipo_busq_g = st.radio("Buscar por:", ["💳 Cédula", "👤 Nombre / Apellido"], horizontal=True)
        matches_g = pd.DataFrame()

        if tipo_busq_g == "💳 Cédula":
            ci_girador = st.text_input("Ingresá la Cédula:", placeholder="Ej: 5511820").strip().replace('.', '')
            if ci_girador:
                matches_g = df_liquidez[df_liquidez['emp_ci'].apply(limpiar_ci) == ci_girador]
        else:
            nom_girador = st.text_input("Ingresá el Nombre o Apellido:", placeholder="Ej: Sanabria").strip()
            if nom_girador:
                matches_g = df_liquidez[df_liquidez['emp_nomape'].astype(str).str.contains(nom_girador, case=False, na=False)]

        if not matches_g.empty:
            if len(matches_g) > 1:
                st.warning(f"Se encontraron {len(matches_g)} coincidencias:")
                opciones_g = [f"{row['emp_nomape']} (C.I.: {row['emp_ci']})" for idx, row in matches_g.iterrows()]
                seleccion_g = st.selectbox("Seleccionar Registro:", opciones_g)
                idx_g = opciones_g.index(seleccion_g)
                row_g = matches_g.iloc[idx_g]
            else:
                row_g = matches_g.iloc[0]

            nombre_g = row_g.get('emp_nomape', 'S/N')
            ci_g = limpiar_ci(row_g.get('emp_ci', '0'))
            unidad_g = row_g.get('UNIDAD', '-')
            
            presupuestado_g = limpiar_monto(row_g.get('presupuestado', 0))
            jubilacion_g = limpiar_monto(row_g.get('jubilacion', 0))
            tot_desc_g = jubilacion_g + limpiar_monto(row_g.get('giraduria', 0)) + limpiar_monto(row_g.get('descuento_cf2', 0)) + limpiar_monto(row_g.get('judicial', 0))
            liquido_real_g = presupuestado_g - tot_desc_g if tot_desc_g > 0 else limpiar_monto(row_g.get('liquido', 0))
            limite_50_g = (presupuestado_g - jubilacion_g) / 2.0

            st.markdown("---")
            st.write("### Datos de Solo Lectura:")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.text_input("Nombre y Apellido:", value=nombre_g, disabled=True)
                st.text_input("Unidad Militar:", value=unidad_g, disabled=True)
            with col_g2:
                st.text_input("Cédula N°:", value=ci_g, disabled=True)
                st.text_input("Límite de Cuota Máxima (50%):", value=f"Gs. {formato_guarani(limite_50_g)}", disabled=True)

            st.markdown("---")
            dict_previo = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) == ci_g]
            obs_inicial = dict_previo.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_previo.empty else ""

            with st.form("form_dictamen"):
                st.subheader("📝 Editar Dictamen / Observación de Giraduría")
                cuota_evaluando = st.number_input("Monto de Cuota Solicitada (Gs.):", min_value=0.0, step=50000.0, format="%.0f")
                obs_girador = st.text_area("Observaciones / Respuesta del Girador:", value=obs_inicial, placeholder="Ej: Compra de deuda aprobada / Consultar disponibilidad con CF2")
                
                btn_guardar_dictamen = st.form_submit_button("💾 Guardar Dictamen")

                if btn_guardar_dictamen:
                    if not obs_girador.strip():
                        st.error("Por favor ingresa una observación para guardar el dictamen.")
                    else:
                        df_dictamenes = df_dictamenes[df_dictamenes['CEDULA'].apply(limpiar_ci) != ci_g]
                        nuevo_dictamen = pd.DataFrame([{
                            'CEDULA': ci_g,
                            'CUOTA_PROPUESTA': formato_guarani(cuota_evaluando),
                            'DICTAMEN_GIRADOR': obs_girador.strip(),
                            'FECHA': pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                        }])
                        df_dictamenes = pd.concat([df_dictamenes, nuevo_dictamen], ignore_index=True)
                        guardar_dictamenes(df_dictamenes)
                        st.success("✅ ¡Dictamen guardado con éxito!")

            st.markdown("---")
            pdf_bytes_g = generar_pdf_constancia("Dictamen de Giraduría", nombre_g, ci_g, unidad_g, presupuestado_g, jubilacion_g, tot_desc_g, liquido_real_g, limite_50_g, cuota_evaluando, "EVALUADO POR GIRADOR", obs_inicial)
            
            st.download_button(
                label="📄 Descargar / Imprimir Dictamen de Giraduría (PDF)",
                data=pdf_bytes_g,
                file_name=f"Dictamen_Giraduria_{ci_g}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

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
                    df_cargado = cargar_excel_detectando_cabecera(archivo)

                df_normalizado = estandarizar_columnas(df_cargado)

                if df_normalizado.empty:
                    st.warning("No se encontraron datos procesables en el archivo.")
                else:
                    guardar_liquidez(df_normalizado)
                    st.success(f"✅ ¡Base de datos importada correctamente! Total de militares registrados: {len(df_normalizado):,}")
                    st.rerun()
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
