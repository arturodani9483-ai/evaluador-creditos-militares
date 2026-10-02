import streamlit as st
import pandas as pd
import os
import io
import re
import calendar
import json
import urllib.parse
from datetime import datetime, timedelta
from fpdf import FPDF

# Intentar ajustar la zona horaria a Paraguay (America/Asuncion)
try:
    import pytz
    PY_TZ = pytz.timezone('America/Asuncion')
    def obtener_fecha_hora_local():
        return datetime.now(PY_TZ)
except ImportError:
    def obtener_fecha_hora_local():
        return datetime.utcnow() - timedelta(hours=3)

def obtener_ultimo_dia_mes_siguiente(fecha_base):
    next_m = fecha_base.month + 1
    next_y = fecha_base.year
    if next_m > 12:
        next_m = 1
        next_y += 1
    max_d = calendar.monthrange(next_y, next_m)[1]
    return datetime(next_y, next_m, max_d).date()

st.set_page_config(
    page_title="SICOC - Sistema Integrado de Control Operativo y Crediticio", 
    layout="wide", 
    page_icon="🏛️"
)

# ==========================================
# 🎨 ESTILO VISUAL PERSONALIZADO
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc !important;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #0a2540 !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a2540 0%, #003848 60%, #00a884 100%) !important;
    }
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] div.stButton > button {
        background: linear-gradient(135deg, #00a884 0%, #008f70 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 168, 132, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="stSidebar"] div.stButton > button * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: linear-gradient(135deg, #008f70 0%, #00755b 100%) !important;
        transform: translateY(-2px);
    }
    [data-testid="stSidebar"] .stRadio label span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #0a2540 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
    }
    .stMainBlockContainer .stTextInput input, 
    .stMainBlockContainer .stNumberInput input, 
    .stMainBlockContainer .stSelectbox select, 
    .stMainBlockContainer div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    .stMainBlockContainer .stButton > button {
        background: linear-gradient(135deg, #00a884 0%, #008f70 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 22px !important;
        box-shadow: 0 4px 12px rgba(0, 168, 132, 0.25) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0a2540 0%, #003848 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 22px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 CONFIGURACIÓN DE USUARIOS
# ==========================================
USUARIOS_AUTORIZADOS = {
    "arthuro": "19942008",
    "fio": "credfio",
    "agustin": "cobragus",
    "estela": "giradurias",
    "martin": "mllamas",
    "yennifer": "280308",
    "juan": "171002",
    "milena": "080703"
}

TELEFONOS_USUARIOS = {
    "arthuro": "595983474662",
    "fio": "595981000001",
    "agustin": "595981000002",
    "estela": "595981000003",
    "martin": "595981000004",
    "yennifer": "595981000005",
    "juan": "595981000006",
    "milena": "595981000007"
}

USUARIOS_EDITORES_DICTAMEN = ["arthuro", "estela", "martin"]
USUARIOS_AUDITORIA_HACIENDA = ["arthuro", "martin"]
USUARIO_ADMIN_BASE = "arthuro"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if "num_creditos_adicionales" not in st.session_state:
    st.session_state["num_creditos_adicionales"] = 0

def pantalla_login():
    st.markdown("# 🏛️ SICOC")
    st.markdown("### Sistema Integrado de Control Operativo y Crediticio")
    st.info("Ingresá tus credenciales autorizadas para acceder a la plataforma.")
    
    with st.form("form_login"):
        col1, col2 = st.columns(2)
        with col1:
            user_input = st.text_input("Usuario:").strip().lower()
        with col2:
            pass_input = st.text_input("Contraseña:", type="password").strip()
            
        btn_login = st.form_submit_button("🔑 Iniciar Sesión", use_container_width=True)
        
        if btn_login:
            if user_input in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[user_input] == pass_input:
                st.session_state["autenticado"] = True
                st.session_state["usuario_actual"] = user_input
                st.success(f"¡Bienvenido/a {user_input.capitalize()}!")
                st.rerun()
            else:
                st.error("⚠️ Usuario o contraseña incorrectos.")

if not st.session_state["autenticado"]:
    pantalla_login()
    st.stop()

# ==========================================
# ⚙️ MENÚ LATERAL Y NAVEGACIÓN
# ==========================================
usuario_actual = st.session_state['usuario_actual'].lower()
es_editor = usuario_actual in USUARIOS_EDITORES_DICTAMEN
es_auditor_hacienda = usuario_actual in USUARIOS_AUDITORIA_HACIENDA
es_admin_base = (usuario_actual == USUARIO_ADMIN_BASE)

st.sidebar.title("🏛 SICOC")
st.sidebar.markdown(f"👤 **Usuario activo:** `{usuario_actual.capitalize()}`")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = ""
    st.rerun()

st.sidebar.markdown("---")

if usuario_actual in ["yennifer", "juan", "milena"]:
    opciones_menu = [
        "🔍 Evaluador de Liquidez (FF.AA.)",
        "📥 Derivaciones Internas",
        "🧮 Calculadora de Préstamos"
    ]
else:
    opciones_menu = [
        "🔍 Evaluador de Liquidez (FF.AA.)", 
        "📥 Derivaciones Internas",
        "📊 Gestión y Diagnóstico de Cobranzas",
        "📋 Dictamen del Girador",
        "🛡️ Auditoría y Cruce de Planillas",
        "🧮 Calculadora de Préstamos",
        "📥 Cargar Base Mensual"
    ]

opcion = st.sidebar.radio("Navegación de Módulos:", opciones_menu)

# BASES Y REPOSITORIOS
DB_LIQUIDEZ_FILE = "base_liquidez_militares.csv"
DB_HISTORIAL_LIQUIDEZ_FILE = "base_historial_liquidez.csv"
DB_GIRADURIAS_FILE = "Planilla_Descuentos_Consolidada.xlsx"
DB_HISTORIAL_GIRADURIAS_FILE = "base_historial_giradurias.csv"
DB_DICTAMENES_FILE = "dictamenes_giraduria.csv"
DB_DERIVACIONES_FILE = "base_derivaciones_internas.csv"

MAPEO_UNIDADES = {
    "1": "1RA DC", "2": "2da DC", "3": "3ra Dc", "4": "Epoe", "5": "I CE",
    "6": "Cimee", "7": "TEE", "8": "Ejercito", "9": "Edefisfa", "10": "Jubilados",
    "12": "Eceme", "13": "Academil", "14": "FFMM", "15": "CFN5", "17": "Diserinte",
    "18": "Dimabel", "20": "C. Logistico", "22": "Comisoe", "23": "CFN2", "24": "II CE",
    "25": "III CE", "26": "4ta DI", "27": "5ta DI", "28": "6ta DI", "29": "2da DI",
    "30": "3ra DI", "31": "Ingenieria", "32": "1ra DI",
    "35": "Comcome Oficiales", "36": "Comcome Sub Oficiales", "37": "Suprema corte", "39": "Comcome Empleados",
    "42": "Regimiento", "46": "Digetren", "50": "Esc. Caballeria",
    "54": "IAEE", "62": "EIME", "70": "Batallon", "73": "CECOPAZ", "82": "Armada",
    "83": "Aerea", "86": "Policia"
}

def limpiar_texto(val):
    try:
        if isinstance(val, (pd.Series, list)):
            val = val[0] if len(val) > 0 else ""
        s = str(val).strip()
        return "" if s.upper() in ["NAN", "NONE", "<NAT>"] else s
    except:
        return ""

def limpiar_texto_pdf(val):
    s = limpiar_texto(val)
    try:
        return s.encode('latin-1', 'ignore').decode('latin-1')
    except:
        return s

def limpiar_ci(val):
    try:
        if isinstance(val, (pd.Series, list)):
            val = val[0] if len(val) > 0 else ""
        s = str(val).strip()
        numeros = re.findall(r'\d+', s)
        return "".join(numeros) if numeros else ""
    except:
        return ""

def limpiar_monto(val):
    try:
        if val is None or pd.isna(val):
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        
        s = str(val).strip()
        if not s:
            return 0.0
            
        if '.' in s and ',' not in s:
            s_clean = s.replace('.', '')
        elif ',' in s and '.' in s:
            s_clean = s.replace('.', '').replace(',', '.')
        elif ',' in s:
            s_clean = s.replace(',', '.')
        else:
            s_clean = s

        numeros = re.findall(r'[-+]?\d*\.?\d+', s_clean)
        if numeros:
            return float(numeros[0])
        return 0.0
    except:
        return 0.0

def formato_guarani(val):
    try:
        m = limpiar_monto(val)
        return f"{int(round(m)):,}".replace(',', '.')
    except:
        return "0"

def estandarizar_columnas_ffaa(df):
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
        elif 'EXPOSICION' in c_clean or 'PELIGRO' in c_clean or 'BONIF' in c_clean:
            cols_map[c] = 'exposicion_peligro'
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
    if 'emp_ci' in df_renamed.columns:
        df_renamed['emp_ci_clean'] = df_renamed['emp_ci'].astype(str).apply(limpiar_ci)

    if 'exposicion_peligro' not in df_renamed.columns:
        df_renamed['exposicion_peligro'] = 0.0

    return df_renamed

def estandarizar_columnas_giradurias(df):
    cols_map = {}
    for c in df.columns:
        c_clean = str(c).strip().upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        if 'SOCIO' in c_clean:
            cols_map[c] = 'nro_socio'
        elif 'C.I' in c_clean or 'CEDULA' in c_clean or 'CI' in c_clean:
            cols_map[c] = 'emp_ci'
        elif 'APELLIDO' in c_clean or 'NOMBRE' in c_clean:
            cols_map[c] = 'emp_nomape'
        elif 'MONTO A DESCONTAR' in c_clean or 'TOTAL DESCUENTOS' in c_clean or 'ENVIADO' in c_clean:
            cols_map[c] = 'monto_enviado'
        elif 'COBRADO' in c_clean:
            cols_map[c] = 'monto_cobrado'
        elif 'RECHAZADO' in c_clean:
            cols_map[c] = 'monto_rechazado'
            
    df_ren = df.rename(columns=cols_map)
    if 'emp_ci' in df_ren.columns:
        df_ren['emp_ci_clean'] = df_ren['emp_ci'].astype(str).apply(limpiar_ci)
    return df_ren

@st.cache_data(ttl=2592000)
def cargar_historial_liquidez():
    if os.path.exists(DB_HISTORIAL_LIQUIDEZ_FILE):
        try:
            df = pd.read_csv(DB_HISTORIAL_LIQUIDEZ_FILE, dtype=str)
            if 'emp_ci' in df.columns:
                df['emp_ci_clean'] = df['emp_ci'].astype(str).apply(limpiar_ci)
            return df
        except:
            pass
    if os.path.exists(DB_LIQUIDEZ_FILE):
        try:
            df = pd.read_csv(DB_LIQUIDEZ_FILE, dtype=str)
            if 'emp_ci' in df.columns:
                df['emp_ci_clean'] = df['emp_ci'].astype(str).apply(limpiar_ci)
            df['periodo'] = "Agosto 2026"
            return df
        except:
            pass
    return pd.DataFrame()

def guardar_historial_liquidez(df_nuevo, periodo_tag):
    df_existente = cargar_historial_liquidez()
    df_nuevo['periodo'] = periodo_tag
    if not df_existente.empty and 'periodo' in df_existente.columns:
        df_existente = df_existente[df_existente['periodo'] != periodo_tag]
        df_unificado = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_unificado = df_nuevo
        
    df_unificado.to_csv(DB_HISTORIAL_LIQUIDEZ_FILE, index=False)
    df_nuevo.to_csv(DB_LIQUIDEZ_FILE, index=False)
    st.cache_data.clear()

@st.cache_data(ttl=2592000)
def cargar_historial_giradurias():
    if os.path.exists(DB_HISTORIAL_GIRADURIAS_FILE):
        try:
            df_h = pd.read_csv(DB_HISTORIAL_GIRADURIAS_FILE, dtype=str)
            if 'emp_ci' in df_h.columns:
                df_h['emp_ci_clean'] = df_h['emp_ci'].astype(str).apply(limpiar_ci)
            return df_h
        except:
            pass
    return pd.DataFrame()

def guardar_historial_giradurias(df_nuevo, periodo_tag):
    df_existente = cargar_historial_giradurias()
    df_nuevo['periodo'] = periodo_tag
    if not df_existente.empty and 'periodo' in df_existente.columns:
        df_existente = df_existente[df_existente['periodo'] != periodo_tag]
        df_unificado = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_unificado = df_nuevo
        
    df_unificado.to_csv(DB_HISTORIAL_GIRADURIAS_FILE, index=False)
    st.cache_data.clear()

def unificar_hojas_excel(file_or_path, periodo_tag=""):
    xls = pd.ExcelFile(file_or_path)
    dfs = []
    sheet_names = xls.sheet_names
    
    for sheet in sheet_names:
        if sheet.strip().lower() in ['hoja1', 'hoja 1', 'consolidado'] and len(sheet_names) > 1:
            continue

        num_m = re.findall(r'\d+', str(sheet))
        num_str = num_m[0] if num_m else ""
        nombre_unidad = MAPEO_UNIDADES.get(num_str, sheet)
        
        try:
            df_s = pd.read_excel(xls, sheet_name=sheet, dtype=str)
            df_s = estandarizar_columnas_giradurias(df_s)
            
            if 'nro_socio' in df_s.columns:
                df_s['nro_socio'] = df_s['nro_socio'].astype(str).apply(lambda x: re.sub(r'\.0$', '', str(x).strip()) if pd.notna(x) else "")

            if 'emp_ci' in df_s.columns:
                df_s['emp_ci_clean'] = df_s['emp_ci'].astype(str).apply(limpiar_ci)

            df_s['unidad_nombre_oficial'] = nombre_unidad
            df_s['hoja_origen'] = sheet
            if periodo_tag:
                df_s['periodo'] = periodo_tag
            dfs.append(df_s)
        except Exception:
            pass
            
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def cargar_dictamenes():
    if os.path.exists(DB_DICTAMENES_FILE):
        return pd.read_csv(DB_DICTAMENES_FILE, dtype=str)
    return pd.DataFrame(columns=['CEDULA', 'CUOTA_PROPUESTA', 'DICTAMEN_GIRADOR', 'FECHA'])

def guardar_dictamenes(df):
    df.to_csv(DB_DICTAMENES_FILE, index=False)

def cargar_derivaciones():
    if os.path.exists(DB_DERIVACIONES_FILE):
        try:
            return pd.read_csv(DB_DERIVACIONES_FILE, dtype=str)
        except:
            pass
    return pd.DataFrame(columns=[
        'ID_DERIVACION', 'FECHA_ENVIO', 'REMITENTE', 'DESTINATARIO', 
        'CEDULA', 'SOCIO_NOMBRE', 'DESCRIPCION_CASO', 'PERMITE_EFECTIVO', 
        'MONTO_EFECTIVO_AUTORIZADO', 'ESTADO_TRAMITE', 'VISTO', 'FECHA_VISTO', 'DATOS_ESTADO_CUENTA_JSON'
    ])

def guardar_derivaciones(df):
    df.to_csv(DB_DERIVACIONES_FILE, index=False)

def crear_derivacion(remitente, destinatario, cedula, socio_nombre, desc_caso, permite_efectivo, monto_efectivo, datos_ec_dict=None):
    df_d = cargar_derivaciones()
    fecha_ahora = obtener_fecha_hora_local().strftime('%d/%m/%Y %H:%M')
    id_new = str(len(df_d) + 1).zfill(5)
    
    monto_efec_entero = int(round(limpiar_monto(monto_efectivo)))
    json_ec = json.dumps(datos_ec_dict) if datos_ec_dict else "{}"

    nuevo_reg = pd.DataFrame([{
        'ID_DERIVACION': id_new,
        'FECHA_ENVIO': fecha_ahora,
        'REMITENTE': remitente.lower().strip(),
        'DESTINATARIO': destinatario.lower().strip(),
        'CEDULA': limpiar_ci(cedula),
        'SOCIO_NOMBRE': socio_nombre,
        'DESCRIPCION_CASO': desc_caso,
        'PERMITE_EFECTIVO': 'SI' if permite_efectivo else 'NO',
        'MONTO_EFECTIVO_AUTORIZADO': str(monto_efec_entero),
        'ESTADO_TRAMITE': '🟡 En Proceso',
        'VISTO': 'NO',
        'FECHA_VISTO': '-',
        'DATOS_ESTADO_CUENTA_JSON': json_ec
    }])
    df_d = pd.concat([df_d, nuevo_reg], ignore_index=True)
    guardar_derivaciones(df_d)
    return id_new

def generar_pdf_constancia(tipo_reporte, nombre, ci, unidad, presupuestado, jubilacion, tot_desc, liquido, limite, cuota, estado, obs=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "SICOC - EVALUADOR DE CAPACIDAD CREDITICIA", border=0, ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, f"Constancia Oficial de {limpiar_texto_pdf(tipo_reporte)}", border=0, ln=True, align="C")
    pdf.ln(5)
    pdf.line(10, 28, 200, 28)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "1. DATOS DEL MILITAR / SOCIO", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Nombre y Apellido: {limpiar_texto_pdf(nombre)}")
    pdf.cell(90, 6, f"Cedula N°: {ci}", ln=True)
    pdf.cell(100, 6, f"Unidad / Dependencia: {limpiar_texto_pdf(unidad)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "2. RESUMEN DE LIQUIDEZ Y HABERES", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Sueldo Presupuestado: Gs. {formato_guarani(presupuestado)}")
    pdf.cell(90, 6, f"Descuento Jubilacion: Gs. {formato_guarani(jubilacion)}", ln=True)
    pdf.cell(100, 6, f"Total Descuentos: Gs. {formato_guarani(tot_desc)}")
    pdf.cell(90, 6, f"Liquido Real Actual: Gs. {formato_guarani(liquido)}", ln=True)
    pdf.cell(100, 6, f"Limite Disponible (50%): Gs. {formato_guarani(limite)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "3. EVALUACION DE CREDITO Y DICTAMEN", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Cuota Solicitada: Gs. {formato_guarani(cuota)}")
    pdf.cell(90, 6, f"Estado de Factibilidad: {limpiar_texto_pdf(estado)}", ln=True)
    
    if obs:
        pdf.ln(2)
        pdf.multi_cell(0, 6, f"Observacion / Dictamen de Giraduria: {limpiar_texto_pdf(obs)}")

    pdf.ln(15)
    pdf.cell(0, 6, "_____________________________", align="C", ln=True)
    pdf.cell(0, 6, "Firma / Sello de Recepcion", align="C", ln=True)

    return bytes(pdf.output())

df_historial_liquidez = cargar_historial_liquidez()
df_historial_giradurias = cargar_historial_giradurias()
df_dictamenes = cargar_dictamenes()

# ==========================================
# 🪖 MÓDULO 1: EVALUADOR DE LIQUIDEZ
# ==========================================
if opcion == "🔍 Evaluador de Liquidez (FF.AA.)":
    st.subheader("🔍 Buscador de Liquidez y Estado del Socio")
    
    periodos_liq_disp = sorted([p for p in df_historial_liquidez['periodo'].dropna().unique() if str(p).strip() != ""], reverse=True) if not df_historial_liquidez.empty and 'periodo' in df_historial_liquidez.columns else ["Agosto 2026"]
    periodos_gir_disp = sorted([p for p in df_historial_giradurias['periodo'].dropna().unique() if str(p).strip() != ""], reverse=True) if not df_historial_giradurias.empty and 'periodo' in df_historial_giradurias.columns else ["Agosto 2026"]
    
    col_sel_periodo, _ = st.columns([2, 2])
    with col_sel_periodo:
        periodo_consultar = st.selectbox("🗓️ Seleccionar Período a Consultar:", sorted(list(set(periodos_liq_disp + periodos_gir_disp)), reverse=True))

    df_liquidez_actual = df_historial_liquidez[df_historial_liquidez['periodo'] == periodo_consultar] if not df_historial_liquidez.empty and 'periodo' in df_historial_liquidez.columns else df_historial_liquidez
    df_giradurias_actual = df_historial_giradurias[df_historial_giradurias['periodo'] == periodo_consultar] if not df_historial_giradurias.empty and 'periodo' in df_historial_giradurias.columns else df_historial_giradurias

    tipo_busqueda = st.radio("Método de búsqueda:", ["💳 Por Número de Cédula", "🏷️ Por Número de Socio", "👤 Por Nombre / Apellido"], horizontal=True)
    matches_l = pd.DataFrame()
    matches_g = pd.DataFrame()
    
    if tipo_busqueda == "💳 Por Número de Cédula":
        ci_input = st.text_input("Número de Cédula (C.I.):", placeholder="Ej: 5511820").strip()
        ci_input_clean = limpiar_ci(ci_input)
        if ci_input_clean:
            if not df_liquidez_actual.empty:
                matches_l = df_liquidez_actual[df_liquidez_actual['emp_ci_clean'] == ci_input_clean]
            if not df_giradurias_actual.empty and 'emp_ci_clean' in df_giradurias_actual.columns:
                matches_g = df_giradurias_actual[df_giradurias_actual['emp_ci_clean'] == ci_input_clean]

    elif tipo_busqueda == "🏷️ Por Número de Socio":
        socio_input = st.text_input("Número de Socio:", placeholder="Ej: 9946").strip()
        if socio_input:
            if not df_giradurias_actual.empty and 'nro_socio' in df_giradurias_actual.columns:
                matches_g = df_giradurias_actual[df_giradurias_actual['nro_socio'].astype(str).str.strip() == socio_input.strip()]
                if not matches_g.empty:
                    ci_socio_encontrada = limpiar_ci(matches_g.iloc[0].get('emp_ci', ''))
                    if ci_socio_encontrada and not df_liquidez_actual.empty:
                        matches_l = df_liquidez_actual[df_liquidez_actual['emp_ci_clean'] == ci_socio_encontrada]

    else:
        nombre_input = st.text_input("Nombre o Apellido:", placeholder="Ej: Sanabria").strip()
        if nombre_input:
            if not df_liquidez_actual.empty:
                matches_l = df_liquidez_actual[df_liquidez_actual['emp_nomape'].astype(str).str.contains(nombre_input, case=False, na=False)]
            if not df_giradurias_actual.empty:
                matches_g = df_giradurias_actual[df_giradurias_actual['emp_nomape'].astype(str).str.contains(nombre_input, case=False, na=False)]

    figura_en_liquidez = not matches_l.empty
    figura_en_giradurias = not matches_g.empty

    if figura_en_liquidez or figura_en_giradurias:
        if figura_en_liquidez:
            row_l = matches_l.iloc[0]
            nombre = row_l.get('emp_nomape', 'S/N')
            cedula_militar = limpiar_ci(row_l.get('emp_ci', '0'))
            unidad_militar = row_l.get('UNIDAD', 'Liquidez FF.AA.')
            categoria = row_l.get('cat_codigo', '-')

            presupuestado = limpiar_monto(row_l.get('presupuestado', 0))
            bonif_peligro = limpiar_monto(row_l.get('exposicion_peligro', 0))
            jubilacion = limpiar_monto(row_l.get('jubilacion', 0))
            giraduria = limpiar_monto(row_l.get('giraduria', 0))
            desc_cf2 = limpiar_monto(row_l.get('descuento_cf2', 0))
            judicial = limpiar_monto(row_l.get('judicial', 0))
            
            total_descuentos = jubilacion + giraduria + desc_cf2 + judicial
            liquido_real = presupuestado - total_descuentos
            
            limite_50_estandar = (presupuestado - jubilacion) / 2.0
            limite_50_cf2 = limite_50_estandar + (bonif_peligro / 2.0)

            total_deudas_actuales = giraduria + desc_cf2 + judicial
            margen_estandar_restante = limite_50_estandar - total_deudas_actuales
            margen_cf2_restante = limite_50_cf2 - total_deudas_actuales
        else:
            row_g_first = matches_g.iloc[0]
            nombre = row_g_first.get('emp_nomape', 'S/N')
            cedula_militar = limpiar_ci(row_g_first.get('emp_ci', '0'))
            u_g_ofic = row_g_first.get('unidad_nombre_oficial', 'Giradurías')
            unidad_militar = f"GIRADURÍA: {u_g_ofic}"
            categoria = "S/D"

            presupuestado = bonif_peligro = jubilacion = giraduria = desc_cf2 = judicial = total_descuentos = liquido_real = limite_50_estandar = limite_50_cf2 = margen_estandar_restante = margen_cf2_restante = 0.0

        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.success(f"👤 **Socio / Militar:** {nombre}\n\n**C.I.:** {cedula_militar} | **Cat:** {categoria}")
        with col_info2:
            st.info(f"🏛 **Unidad Registrada:** {unidad_militar}\n\n**Período:** {periodo_consultar}")

        if figura_en_liquidez:
            st.markdown("### 📊 Desglose de Haberes y Bonificaciones")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Sueldo Presupuestado", f"Gs. {formato_guarani(presupuestado)}")
            c2.metric("⚠️ Exposición al Peligro", f"Gs. {formato_guarani(bonif_peligro)}")
            c3.metric("Jubilación", f"Gs. {formato_guarani(jubilacion)}")
            c4.metric("Total Descuentos Actuales", f"Gs. {formato_guarani(total_descuentos)}")

            st.markdown("---")
            st.markdown("### 🎯 Comparativo de Capacidad de Pago (Giraduría Estándar vs. CF2)")
            
            col_lim1, col_lim2 = st.columns(2)
            with col_lim1:
                st.info(
                    f"🏛️ **LÍMITE GIRADURÍA ESTÁNDAR (50%):**\n\n"
                    f"• **Límite Máximo Habilitado:** Gs. {formato_guarani(limite_50_estandar)}\n"
                    f"• **Margen Disponible Restante:** Gs. {formato_guarani(margen_estandar_restante)}"
                )
            with col_lim2:
                st.success(
                    f"⭐ **LÍMITE ESPECIAL CF2 (50% Estándar + 50% Exp. Peligro):**\n\n"
                    f"• **Límite Máximo CF2 Habilitado:** Gs. {formato_guarani(limite_50_cf2)}\n"
                    f"• **Margen Disponible Restante CF2:** Gs. {formato_guarani(margen_cf2_restante)}"
                )

        if not df_historial_giradurias.empty and cedula_militar:
            match_hist_socio = df_historial_giradurias[df_historial_giradurias['emp_ci_clean'] == cedula_militar]
            if not match_hist_socio.empty:
                st.markdown("---")
                st.markdown("### 📜 Historial de Envíos y Cobros por Mes")
                
                hist_records = []
                for _, r_h in match_hist_socio.iterrows():
                    env_h = limpiar_monto(r_h.get('monto_enviado', 0))
                    cob_h = limpiar_monto(r_h.get('monto_cobrado', 0))
                    pct_cobro = (cob_h / env_h * 100) if env_h > 0 else 0.0
                    
                    hist_records.append({
                        'Período': r_h.get('periodo', 'Agosto 2026'),
                        'Giraduría Enviada': r_h.get('unidad_nombre_oficial', '-'),
                        'Monto Enviado (Gs.)': formato_guarani(env_h),
                        'Monto Cobrado (Gs.)': formato_guarani(cob_h),
                        '% Efectividad Cobro': f"{pct_cobro:.1f} %"
                    })
                
                df_hist_view = pd.DataFrame(hist_records)
                st.dataframe(df_hist_view, use_container_width=True)

        st.markdown("---")
        with st.expander("📤 Enviar este Estado / Ficha Internamente a un Compañero", expanded=False):
            usuarios_destino = [u.capitalize() for u in USUARIOS_AUTORIZADOS.keys() if u != usuario_actual]
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                destinatario_sel = st.selectbox("Seleccionar Compañero Destino:", usuarios_destino, key="der_dest_liq")
                obs_derivacion = st.text_area("Observación / Indicación para el compañero:", placeholder="Ej: Revisar refinanciación", key="der_obs_liq")
            with col_d2:
                permite_efectivo_chk = st.checkbox("🔑 Autorizar Modificación de Retiro de Efectivo", value=False, key="der_efec_liq")
                monto_efectivo_aut = 0
                if permite_efectivo_chk:
                    monto_efectivo_aut = int(round(limpiar_monto(st.text_input("Monto Sugerido en Efectivo (Gs.):", value="0", key="der_monto_efec_liq"))))
                
                if st.button("🚀 Confirmar y Enviar Derivación Interna", use_container_width=True, key="btn_enviar_der_liq"):
                    id_creado = crear_derivacion(
                        remitente=usuario_actual,
                        destinatario=destinatario_sel.lower(),
                        cedula=cedula_militar,
                        socio_nombre=nombre,
                        desc_caso=obs_derivacion,
                        permite_efectivo=permite_efectivo_chk,
                        monto_efectivo=monto_efectivo_aut
                    )
                    st.success(f"✅ ¡Derivación N° **{id_creado}** enviada con éxito a **{destinatario_sel}**!")

        pdf_bytes = generar_pdf_constancia("Evaluación de Liquidez", nombre, cedula_militar, unidad_militar, presupuestado, jubilacion, total_descuentos, liquido_real, limite_50_estandar, 0.0, "EVALUACIÓN REALIZADA")
        st.download_button(
            label="📄 Descargar Constancia de Evaluación (PDF)",
            data=pdf_bytes,
            file_name=f"Constancia_Credito_{cedula_militar}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ==========================================
# 📥 MÓDULO DERIVACIONES INTERNAS
# ==========================================
elif opcion == "📥 Derivaciones Internas":
    st.subheader("📥 Bandeja de Casos y Derivaciones Internas entre Compañeros")
    df_deriv = cargar_derivaciones()

    tab_der1, tab_der2 = st.tabs(["📥 Mis Casos Recibidos", "📤 Mis Casos Enviados"])

    with tab_der1:
        mis_recibidos = df_deriv[df_deriv['DESTINATARIO'] == usuario_actual] if not df_deriv.empty else pd.DataFrame()
        if mis_recibidos.empty:
            st.info("🟢 **Sin derivaciones pendientes:** No tenés casos asignados actualmente.")
        else:
            st.success(f"📋 Tenés **{len(mis_recibidos)}** caso(s) asignado(s).")
            for idx, r_der in mis_recibidos.iterrows():
                id_d = r_der.get('ID_DERIVACION', '')
                fec_e = r_der.get('FECHA_ENVIO', '')
                rem_e = r_der.get('REMITENTE', '').capitalize()
                ced_e = r_der.get('CEDULA', '')
                nom_e = r_der.get('SOCIO_NOMBRE', '')
                obs_e = r_der.get('DESCRIPCION_CASO', '')
                est_e = r_der.get('ESTADO_TRAMITE', '🟡 En Proceso')
                
                with st.expander(f"📌 Caso N° {id_d} | Socio: {nom_e} (C.I.: {ced_e}) - Estado: {est_e}"):
                    st.write(f"**Enviado por:** {rem_e} el {fec_e}")
                    st.info(f"📝 **Instrucción:** {obs_e}")
                    nuevo_estado = st.selectbox("Actualizar Estado:", ["🟡 En Proceso", "🟢 Atendido", "✅ Procesado"], key=f"sel_est_{id_d}")
                    if st.button("💾 Guardar Cambios", key=f"btn_save_case_{id_d}"):
                        df_deriv.loc[df_deriv['ID_DERIVACION'] == id_d, 'ESTADO_TRAMITE'] = nuevo_estado
                        guardar_derivaciones(df_deriv)
                        st.success("✅ ¡Caso actualizado!")
                        st.rerun()

    with tab_der2:
        st.markdown("### 📤 Historial de Derivaciones Enviadas")
        df_view_d = df_deriv if es_admin_base else (df_deriv[df_deriv['REMITENTE'] == usuario_actual] if not df_deriv.empty else pd.DataFrame())
        if not df_view_d.empty:
            st.dataframe(df_view_d[['ID_DERIVACION', 'FECHA_ENVIO', 'DESTINATARIO', 'SOCIO_NOMBRE', 'CEDULA', 'ESTADO_TRAMITE']], use_container_width=True)

# ==========================================
# 📊 MÓDULO GESTIÓN DE COBRANZAS
# ==========================================
elif opcion == "📊 Gestión y Diagnóstico de Cobranzas":
    st.subheader("📊 Módulo de Diagnóstico de Cobranzas y Reportes")
    if df_historial_giradurias.empty:
        st.info("Por favor cargá bases en 'Cargar Base Mensual'.")
    else:
        st.dataframe(df_historial_giradurias[['periodo', 'unidad_nombre_oficial', 'nro_socio', 'emp_nomape', 'monto_enviado', 'monto_cobrado', 'monto_rechazado']], use_container_width=True)

# ==========================================
# 📋 MÓDULO DICTAMEN DEL GIRADOR
# ==========================================
elif opcion == "📋 Dictamen del Girador":
    st.subheader("📋 Módulo de Registro de Dictamen de Giraduría")
    ci_girador = st.text_input("Ingresá la Cédula para el Dictamen:").strip()
    ci_girador_clean = limpiar_ci(ci_girador)
    
    if ci_girador_clean:
        dict_previo = df_dictamenes[df_dictamenes['CEDULA'].astype(str).apply(limpiar_ci) == ci_girador_clean]
        obs_inicial = dict_previo.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_previo.empty else "Sin dictamen registrado."
        
        obs_girador = st.text_area("Observaciones / Respuesta del Girador:", value=obs_inicial)
        if st.button("💾 Guardar Dictamen"):
            fecha_dictamen = obtener_fecha_hora_local().strftime("%d/%m/%Y %H:%M")
            df_dictamenes = df_dictamenes[df_dictamenes['CEDULA'].astype(str).apply(limpiar_ci) != ci_girador_clean]
            nuevo_dictamen = pd.DataFrame([{'CEDULA': ci_girador_clean, 'CUOTA_PROPUESTA': '0', 'DICTAMEN_GIRADOR': obs_girador, 'FECHA': fecha_dictamen}])
            df_dictamenes = pd.concat([df_dictamenes, nuevo_dictamen], ignore_index=True)
            guardar_dictamenes(df_dictamenes)
            st.success("✅ Dictamen guardado correctamente.")

# ==========================================
# 🛡️ MÓDULO AUDITORÍA Y HACIENDA
# ==========================================
elif opcion == "🛡️ Auditoría y Cruce de Planillas":
    st.subheader("🛡️ Sistema de Auditoría y Cruce de Planillas (Hacienda)")
    if not es_auditor_hacienda:
        st.error("🔒 Acceso denegado: Módulo exclusivo para auditores.")
    else:
        st.info("Subí planillas para verificar inconsistencias con el mes anterior.")

# ==========================================
# 🧮 MÓDULO CALCULADORA DE PRÉSTAMOS
# ==========================================
elif opcion == "🧮 Calculadora de Préstamos":
    st.subheader("📊 Módulo de Operaciones Financieras, Préstamos y Estado de Cuenta")
    
    sub_tab1, sub_tab2 = st.tabs(["🧮 Simulación de Préstamos", "📊 Estado de Cuenta y Refinanciación Automática"])

    with sub_tab1:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            monto_capital = limpiar_monto(st.text_input("Monto Capital (Gs.):", value="0", key="monto_p1"))
            plazo = st.number_input("Plazo (meses):", min_value=1, max_value=54, value=12, key="plazo_p1")
            tasa_interes = st.number_input("Tasa Interés Anual (%):", value=20, format="%d", key="tasa_p1")

        with col_c2:
            gastos_admin = st.number_input("Gastos Administrativos (%):", value=3.50, step=0.25, format="%.2f", key="gastos_p1")
            fondo_proteccion = st.number_input("Fondo de Protección (%):", value=1.00, step=0.25, format="%.2f", key="fondo_p1")

        if st.button("🚀 Calcular Plan de Pagos", key="btn_calc_p1"):
            if monto_capital > 0:
                capital_con_gastos = monto_capital * (1 + (gastos_admin + fondo_proteccion) / 100.0)
                tasa_mensual = (tasa_interes / 100.0) / 12.0
                cuota = capital_con_gastos * (tasa_mensual * ((1 + tasa_mensual) ** plazo)) / (((1 + tasa_mensual) ** plazo) - 1)
                st.success(f"Cuota Estimada: Gs. {formato_guarani(cuota)}")

    with sub_tab2:
        st.markdown("### 📊 Estado de Cuenta y Evaluación de Refinanciación Automática")
        
        socio_refin_input = st.text_input("🔍 Buscar Socio (Cédula, N° Socio o Nombre):", placeholder="Ej: 10487").strip()
        socio_refin_clean = limpiar_ci(socio_refin_input)

        match_ref_g = pd.DataFrame()
        match_ref_l = pd.DataFrame()

        if socio_refin_input:
            if not df_historial_giradurias.empty:
                if 'nro_socio' in df_historial_giradurias.columns:
                    match_ref_g = df_historial_giradurias[df_historial_giradurias['nro_socio'].astype(str).str.strip() == socio_refin_input]
                if match_ref_g.empty and socio_refin_clean and 'emp_ci_clean' in df_historial_giradurias.columns:
                    match_ref_g = df_historial_giradurias[df_historial_giradurias['emp_ci_clean'] == socio_refin_clean]
                if match_ref_g.empty and 'emp_nomape' in df_historial_giradurias.columns:
                    match_ref_g = df_historial_giradurias[df_historial_giradurias['emp_nomape'].astype(str).str.contains(socio_refin_input, case=False, na=False)]

            ci_socio_ref = limpiar_ci(match_ref_g.iloc[0].get('emp_ci', '')) if not match_ref_g.empty else socio_refin_clean
            
            if ci_socio_ref and not df_historial_liquidez.empty:
                match_ref_l = df_historial_liquidez[df_historial_liquidez['emp_ci_clean'] == ci_socio_ref]

        if not match_ref_g.empty or not match_ref_l.empty:
            if not match_ref_g.empty:
                r_ref_g = match_ref_g.iloc[0]
                nom_ref = r_ref_g.get('emp_nomape', 'S/N')
                ci_ref = limpiar_ci(r_ref_g.get('emp_ci', '0'))
                gir_asig = r_ref_g.get('unidad_nombre_oficial', 'Giraduría')
                ult_cobrado = limpiar_monto(r_ref_g.get('monto_cobrado', 0))
            else:
                r_ref_l = match_ref_l.iloc[0]
                nom_ref = r_ref_l.get('emp_nomape', 'S/N')
                ci_ref = limpiar_ci(r_ref_l.get('emp_ci', '0'))
                gir_asig = "Sin Registrar"
                ult_cobrado = 0.0

            if not match_ref_l.empty:
                r_ref_l = match_ref_l.iloc[0]
                unid_liq_ref = r_ref_l.get('UNIDAD', 'Liquidez FF.AA.')
                presup_ref = limpiar_monto(r_ref_l.get('presupuestado', 0))
                jub_ref = limpiar_monto(r_ref_l.get('jubilacion', 0))
                gir_ref = limpiar_monto(r_ref_l.get('giraduria', 0))
                cf2_ref = limpiar_monto(r_ref_l.get('descuento_cf2', 0))
                jud_ref = limpiar_monto(r_ref_l.get('judicial', 0))
                
                limite_50_ref = (presup_ref - jub_ref) / 2.0
                margen_disp_ref = limite_50_ref - (gir_ref + cf2_ref + jud_ref)
            else:
                unid_liq_ref = "Sin Registrar"
                margen_disp_ref = -321680.0

            st.success(f"👤 **Socio Ficha:** {nom_ref} | **C.I.:** {ci_ref}")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Último Descuento Cobrado", f"Gs. {formato_guarani(ult_cobrado)}")
            m2.metric("Giraduría Asignada", gir_asig)
            m3.metric("Unidad Liquidez (FF.AA.)", unid_liq_ref)
            m4.metric("Margen Disponible (50%)", f"Gs. {formato_guarani(margen_disp_ref)}")

            st.markdown("---")
            st.markdown("### 💳 1. Detalle de Créditos y Deudas Sociales del Socio")

            with st.expander("📌 Crédito N° 1 y Conceptos Sociales Fijos", expanded=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.text_input("N° de Crédito Principal:", value="26634", key="cred_n1")
                    cap_ad_1 = limpiar_monto(st.text_input("Capital Adeudado (Gs.):", value="14919125", key="cap_ad_1"))
                    int_venc_1 = limpiar_monto(st.text_input("Intereses Vencidos (Gs.):", value="873730", key="int_venc_1"))
                    int_mor_1 = limpiar_monto(st.text_input("Interés Moratorio (Gs.):", value="64001", key="int_mor_1"))
                    int_pun_1 = limpiar_monto(st.text_input("Interés Punitorio (Gs.):", value="19201", key="int_pun_1"))

                with col_c2:
                    st.markdown("**Conceptos Sociales (Única aplicación):**")
                    cs_aporte = limpiar_monto(st.text_input("Aporte (Gs.):", value="0", key="cs_aporte"))
                    cs_mantenimiento = limpiar_monto(st.text_input("Mantenimiento Local Social (Gs.):", value="24000", key="cs_mantenimiento"))
                    cs_solidaridad = limpiar_monto(st.text_input("Solidaridad (Gs.):", value="60000", key="cs_solidaridad"))
                    cs_sorteo = limpiar_monto(st.text_input("Sorteo (Gs.):", value="80000", key="cs_sorteo"))

            with st.expander("📌 Crédito Adicional N° 2", expanded=True):
                col_ad1, col_ad2 = st.columns(2)
                with col_ad1:
                    st.text_input("N° de Crédito #2:", value="28876", key="cred_n2")
                    cap_ad_2 = limpiar_monto(st.text_input("Capital Adeudado #2 (Gs.):", value="2017644", key="cap_ad_2"))
                with col_ad2:
                    int_venc_2 = limpiar_monto(st.text_input("Intereses Vencidos #2 (Gs.):", value="122287", key="int_venc_2"))
                    int_mor_2 = limpiar_monto(st.text_input("Interés Moratorio #2 (Gs.):", value="24459", key="int_mor_2"))
                    int_pun_2 = limpiar_monto(st.text_input("Interés Punitorio #2 (Gs.):", value="7278", key="int_pun_2"))

            st.markdown("---")
            st.markdown("### 💵 2. Retiro de Efectivo Adicional y Deuda Total")

            chk_efectivo = st.checkbox("✔ ¿Desea retirar dinero en efectivo adicional?", value=True, key="chk_efec_ref")
            monto_efec_retirar = 0.0
            if chk_efectivo:
                monto_efec_retirar = limpiar_monto(st.text_input("Monto en Efectivo a Retirar (Gs.):", value="1288275", key="inp_efec_ret"))

            total_creditos = (cap_ad_1 + int_venc_1 + int_mor_1 + int_pun_1) + (cap_ad_2 + int_venc_2 + int_mor_2 + int_pun_2)
            total_sociales = cs_aporte + cs_mantenimiento + cs_solidaridad + cs_sorteo
            total_deuda_base = total_creditos + total_sociales + monto_efec_retirar

            st.markdown(f"### **Total Deuda / Base Refinanciación:**\n## **Gs. {formato_guarani(total_deuda_base)}**")

            st.markdown("---")
            st.markdown("### 🎯 3. Análisis de Opciones de Cuota y Recomendación Automática")

            ref_cuota_objetivo = ult_cobrado if ult_cobrado > 0 else 1000000.0
            plazos_opciones = [12, 24, 36, 48]
            opciones_cuotas = []

            for p_op in plazos_opciones:
                cap_g_op = total_deuda_base * 1.045
                tasa_m_op = (0.22 / 12.0)
                cuota_calc = cap_g_op * (tasa_m_op * ((1 + tasa_m_op) ** p_op)) / (((1 + tasa_m_op) ** p_op) - 1)
                opciones_cuotas.append({'Plazo': f"{p_op} meses", 'Cuota Estimada (Gs.)': formato_guarani(cuota_calc), 'Diferencia vs Último Cobro': f"Gs. {formato_guarani(cuota_calc - ref_cuota_objetivo)}"})

            st.dataframe(pd.DataFrame(opciones_cuotas), use_container_width=True)

# ==========================================
# 📥 MÓDULO CARGAR BASE MENSUAL
# ==========================================
elif opcion == "📥 Cargar Base Mensual":
    st.subheader("📥 Repositorio y Carga de Bases Mensuales")
    if not es_admin_base:
        st.error("🔒 Reservado únicamente para el usuario Administrador (`Arthuro`).")
    else:
        tab_b1, tab_b2 = st.tabs(["🪖 Base Liquidez (FF.AA.)", "🏛️️ Base Enviado/Cobrado (Giradurías)"])

        with tab_b1:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                mes_liq_tag = st.selectbox("Mes Liquidez:", ["Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"], key="mes_l")
            with col_l2:
                anio_liq_tag = st.selectbox("Año Liquidez:", ["2026", "2025", "2027"], key="anio_l")

            periodo_liq_etiqueta = f"{mes_liq_tag} {anio_liq_tag}"
            archivo_l = st.file_uploader("Cargar planilla Liquidez (.xlsx / .csv)", type=["xlsx", "xls", "csv"], key="u_liquidez")
            
            if archivo_l and st.button(f"⚠ Importar Liquidez para {periodo_liq_etiqueta}"):
                ext = archivo_l.name.lower().split('.')[-1]
                if ext == 'csv':
                    df_cargado = pd.read_csv(archivo_l, dtype=str)
                else:
                    xls_file = pd.ExcelFile(archivo_l)
                    hoja_target = 'Hoja 4' if 'Hoja 4' in xls_file.sheet_names else 0
                    df_cargado = pd.read_excel(xls_file, sheet_name=hoja_target, dtype=str)

                df_normalizado = estandarizar_columnas_ffaa(df_cargado)
                guardar_historial_liquidez(df_normalizado, periodo_tag=periodo_liq_etiqueta)
                st.success(f"✅ ¡Importado con éxito para {periodo_liq_etiqueta}!")
                st.rerun()

        with tab_b2:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                mes_gir_tag = st.selectbox("Mes Giraduría:", ["Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"], key="mes_g")
            with col_g2:
                anio_gir_tag = st.selectbox("Año Giraduría:", ["2026", "2025", "2027"], key="anio_g")

            periodo_gir_etiqueta = f"{mes_gir_tag} {anio_gir_tag}"
            archivo_g = st.file_uploader("📥 Cargar Base Giradurías (.xlsx)", type=["xlsx", "xls"], key="u_giradurias")
            
            if archivo_g and st.button(f"⚠ Importar Giradurías para {periodo_gir_etiqueta}"):
                df_norm_g = unificar_hojas_excel(archivo_g, periodo_tag=periodo_gir_etiqueta)
                guardar_historial_giradurias(df_norm_g, periodo_tag=periodo_gir_etiqueta)
                st.success(f"✅ ¡Base de giradurías guardada para {periodo_gir_etiqueta}!")
                st.rerun()
