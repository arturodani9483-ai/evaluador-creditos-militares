import streamlit as st
import pandas as pd
import os
import io
import re
import calendar
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
# 🔐 CONFIGURACIÓN DE USUARIOS Y PERMISOS
# ==========================================
USUARIOS_AUTORIZADOS = {
    "arthuro": "19942008",
    "fio": "credfio",
    "agustin": "cobragus",
    "estela": "giradurias",
    "martin": "mllamas",
    "yennifer": "280308"
}

USUARIOS_EDITORES_DICTAMEN = ["arthuro", "estela", "martin"]
USUARIOS_AUDITORIA_HACIENDA = ["arthuro", "martin"]
USUARIO_ADMIN_BASE = "arthuro"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = ""

if "auditoria_ejecutada_limpia" not in st.session_state:
    st.session_state["auditoria_ejecutada_limpia"] = False
if "total_monto_auditoria" not in st.session_state:
    st.session_state["total_monto_auditoria"] = 0.0
if "total_beneficiarios_auditoria" not in st.session_state:
    st.session_state["total_beneficiarios_auditoria"] = 0

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
                st.error("⚠️ Usuario o contraseña incorrectos. Verificá con el administrador.")

    st.markdown("---")
    with st.expander("🔑 ¿Olvidaste tu contraseña?"):
        st.caption("Ingresá tu usuario registrado para comunicarte directamente con el Administrador (Arturo) por WhatsApp:")
        u_recup = st.text_input("Ingresá tu Usuario para recuperar:", key="u_recup_input").strip().lower()
        
        if u_recup:
            if u_recup in USUARIOS_AUTORIZADOS:
                mensaje_wa = f"Hola Arturo, soy el usuario {u_recup.capitalize()} y me olvidé mi contraseña del SICOC. Por favor enviame mi clave."
                msg_encoded = urllib.parse.quote(mensaje_wa)
                wa_link_recup = f"https://wa.me/595983474662?text={msg_encoded}"
                st.markdown(f'[![Solicitar por WhatsApp](https://img.shields.io/badge/WhatsApp-Solicitar_Mi_Contraseña_al_Admin-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)]({wa_link_recup})')
            else:
                st.warning("⚠️ El usuario ingresado no existe en la base autorizada.")

if not st.session_state["autenticado"]:
    pantalla_login()
    st.stop()

# ==========================================
# ⚙️ MENÚ LATERAL, SOPORTE Y NAVEGACIÓN
# ==========================================
usuario_actual = st.session_state['usuario_actual'].lower()
es_editor = usuario_actual in USUARIOS_EDITORES_DICTAMEN
es_auditor_hacienda = usuario_actual in USUARIOS_AUDITORIA_HACIENDA
es_admin_base = (usuario_actual == USUARIO_ADMIN_BASE)

st.sidebar.title("🏛️ SICOC")
st.sidebar.markdown(f"👤 **Usuario activo:** `{usuario_actual.capitalize()}`")

if es_admin_base:
    st.sidebar.caption("⭐ Rol: Administrador General")
elif es_auditor_hacienda:
    st.sidebar.caption("🛡️ Rol: Auditor / Evaluador")
elif es_editor:
    st.sidebar.caption("✍️ Rol: Editor / Evaluador")
elif usuario_actual == "yennifer":
    st.sidebar.caption("🔍 Rol: Operador de Evaluaciones y Créditos")
else:
    st.sidebar.caption("🔒 Rol: Consulta general")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = ""
    st.rerun()

st.sidebar.markdown("---")

if usuario_actual == "yennifer":
    opciones_menu = [
        "🔍 Evaluador de Liquidez (FF.AA.)",
        "🧮 Calculadora de Préstamos"
    ]
else:
    opciones_menu = [
        "🔍 Evaluador de Liquidez (FF.AA.)", 
        "📱 Giradurías Teléfonos",
        "📊 Gestión y Diagnóstico de Cobranzas",
        "📋 Dictamen del Girador",
        "🛡️ Auditoría y Cruce de Planillas",
        "🧮 Calculadora de Préstamos",
        "📥 Cargar Base Mensual"
    ]

opcion = st.sidebar.radio("Navegación de Módulos:", opciones_menu)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Soporte del Sistema")
st.sidebar.caption("Desarrollado por **Arturo Arrua**")
url_whatsapp = "https://wa.me/595983474662?text=Hola%20Arturo,%20tengo%20una%20consulta%20sobre%20el%20sistema%20SICOC"
st.sidebar.markdown(f'[![WhatsApp](https://img.shields.io/badge/WhatsApp-Contactar_Desarrollador-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)]({url_whatsapp})')

DB_LIQUIDEZ_FILE = "base_liquidez_militares.csv"
DB_GIRADURIAS_FILE = "Planilla_Descuentos_Consolidada.xlsx"
DB_HISTORIAL_GIRADURIAS_FILE = "base_historial_giradurias.csv"
DB_DICTAMENES_FILE = "dictamenes_giraduria.csv"
DB_TELEFONOS_FILE = "Giraduria con numero de telefono.xlsx"
DB_HISTORIAL_CONTACTOS_FILE = "base_historial_contactos.csv"

# ==========================================
# 🗺️ DICCIONARIO DE CORRESPONDENCIA DE UNIDADES
# ==========================================
MAPEO_UNIDADES = {
    "1": "1RA DC", "2": "2da DC", "3": "3ra Dc", "4": "Epoe", "5": "I CE",
    "6": "Cimee", "7": "TEE", "8": "Ejercito", "9": "Edefisfa", "10": "Jubilados",
    "12": "Eceme", "13": "Academil", "14": "FFMM", "15": "CFN5", "17": "Diserinte",
    "18": "Dimabel", "20": "C. Logistico", "22": "Comisoe", "23": "CFN2", "24": "II CE",
    "25": "III CE", "26": "4ta DI", "27": "5ta DI", "28": "6ta DI", "29": "2da DI",
    "30": "3ra DI", "31": "Ingenieria", "32": "1ra DI",
    "35": "Comcome Oficiales",
    "36": "Comcome Sub Oficiales",
    "37": "Suprema corte",
    "39": "Comcome Empleados",
    "42": "Regimiento", "44": "Sanidad", "46": "Digetren", "50": "Esc. Caballeria",
    "54": "IAEE", "62": "EIME", "70": "Batallon", "73": "CECOPAZ", "82": "Armada",
    "83": "Aerea", "86": "Policia"
}

# ==========================================
# 🛠️ FUNCIONES AUXILIARES Y DE DATOS
# ==========================================
def limpiar_texto(val):
    try:
        if isinstance(val, (pd.Series, list)):
            val = val[0] if len(val) > 0 else ""
        s = str(val).strip()
        return "" if s.upper() in ["NAN", "NONE", "<NAT>"] else s
    except:
        return ""

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
        if isinstance(val, (pd.Series, list)):
            val = val[0] if len(val) > 0 else 0.0
        s = str(val).replace('.', '').replace(',', '.').strip()
        numeros = re.findall(r'[-+]?\d*\.\d+|\d+', s)
        return float(numeros[0]) if numeros else 0.0
    except:
        return 0.0

def formato_guarani(val):
    try:
        return f"{int(round(val)):,}".replace(',', '.')
    except:
        return "0"

def parsear_fecha(d_str):
    d_clean = limpiar_texto(d_str)
    if not d_clean:
        return None
    s = d_clean.split(' ')[0]
    for fmt in ('%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y %H:%M:%S'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def formatear_telefono_paraguay(tel_raw):
    nums = re.findall(r'\d+', str(tel_raw))
    if not nums:
        return "", ""
    cand = re.sub(r'^0+', '', nums[0])
    if cand.startswith('9') and len(cand) == 9:
        num_local = "0" + cand
        num_wa = "595" + cand
        return num_local, num_wa
    if cand.startswith('09') and len(cand) == 10:
        return cand, "595" + cand[1:]
    return str(tel_raw).strip(), cand

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
        elif 'MONTO A DESCONTAR' in c_clean or 'TOTAL DESCUENTOS' in c_clean or 'TOTAL DESCUENTO' in c_clean or 'ENVIADO' in c_clean:
            cols_map[c] = 'monto_enviado'
        elif 'COBRADO' in c_clean:
            cols_map[c] = 'monto_cobrado'
        elif 'RECHAZADO' in c_clean:
            cols_map[c] = 'monto_rechazado'
            
    df_ren = df.rename(columns=cols_map)
    if 'emp_ci' in df_ren.columns:
        df_ren['emp_ci_clean'] = df_ren['emp_ci'].astype(str).apply(limpiar_ci)
    return df_ren

def unificar_hojas_excel(file_or_path, periodo_tag=""):
    xls = pd.ExcelFile(file_or_path)
    if len(xls.sheet_names) == 1 or "TODAS LAS UNIDADES" in [s.strip().upper() for s in xls.sheet_names]:
        sheet_target = xls.sheet_names[0]
        df_raw = pd.read_excel(xls, sheet_name=sheet_target, header=None, dtype=str)
        
        records = []
        current_unidad = "Sin Asignar"

        for idx, row in df_raw.iterrows():
            c0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            c1 = str(row[1]).strip() if pd.notna(row[1]) else ""
            c2 = str(row[2]).strip() if pd.notna(row[2]) else ""
            c3 = str(row[3]).strip() if pd.notna(row[3]) else ""
            c4 = str(row[4]).strip() if pd.notna(row[4]) else ""
            c5 = str(row[5]).strip() if pd.notna(row[5]) else ""

            if 'UNIDAD:' in c0.upper():
                num_m = re.findall(r'\d+', c0)
                num_str = num_m[0] if num_m else ""
                unid_limpia = re.sub(r'^UNIDAD:\s*\d+\s*-\s*', '', c0, flags=re.IGNORECASE).strip()
                current_unidad = MAPEO_UNIDADES.get(num_str, unid_limpia)
                continue

            if c0.upper() in ['ITEM', 'N°', 'NRO', 'ORDEN'] or 'TOTAL' in c0.upper() or 'TOTAL' in c1.upper():
                continue

            if c1 != "" and c1.upper() != 'NRO. SOCIO' and c2 != "":
                records.append({
                    'nro_socio': re.sub(r'\.0$', '', c1.strip()),
                    'emp_nomape': c2.strip(),
                    'monto_enviado': c3.strip(),
                    'monto_cobrado': c4.strip(),
                    'monto_rechazado': c5.strip(),
                    'unidad_nombre_oficial': current_unidad,
                    'periodo': periodo_tag
                })

        df_concat = pd.DataFrame(records)
        if 'emp_ci' not in df_concat.columns:
            df_concat['emp_ci'] = ""
            df_concat['emp_ci_clean'] = ""
        return df_concat

    else:
        dfs = []
        for sheet in xls.sheet_names:
            if sheet.strip().lower() in ['hoja1', 'hoja 1', 'consolidado']:
                continue

            num_m = re.findall(r'\d+', str(sheet))
            num_str = num_m[0] if num_m else ""
            nombre_unidad = MAPEO_UNIDADES.get(num_str, sheet)
            
            try:
                df_s = pd.read_excel(xls, sheet_name=sheet, dtype=str)
                if 'N°' in df_s.columns:
                    df_s = df_s[~df_s['N°'].astype(str).str.upper().str.contains('TOTAL', na=False)]
                
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
            df_concat = pd.concat(dfs, ignore_index=True)
            return df_concat
        return pd.DataFrame()

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
    
    if 'emp_ci' in df_renamed.columns:
        df_renamed['emp_ci_clean'] = df_renamed['emp_ci'].astype(str).apply(limpiar_ci)

    return df_renamed

def mapear_y_desduplicar_columnas_auditoria(df):
    cols_map = {}
    for c in df.columns:
        c_clean = str(c).strip().upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        if 'CEDULA' in c_clean or 'N° DE CEDULE' in c_clean or 'CEDULA DE IDENTIDAD' in c_clean:
            cols_map[c] = 'cedula'
        elif 'NÚMERO DEL BENEFICIARIO' in c_clean or 'NUMERO DEL BENEFICIARIO' in c_clean:
            cols_map[c] = 'beneficiario'
        elif 'NOMBRES Y APELLIDOS' in c_clean or 'BENEFICIARIO' in c_clean:
            cols_map[c] = 'nombre'
        elif 'CONCEPTO' in c_clean and 'CONCEPTO DEL DESCUENTO' in c_clean:
            cols_map[c] = 'concepto'
        elif 'OPERACION' in c_clean or 'NUMERO DE LA OPERACION' in c_clean:
            cols_map[c] = 'operacion'
        elif 'FECHA DE LA DEUDA' in c_clean:
            cols_map[c] = 'fecha_deuda'
        elif 'NUMERO DE CUOTA' in c_clean:
            cols_map[c] = 'num_cuota'
        elif 'TOTAL CUOTA' in c_clean:
            cols_map[c] = 'total_cuota'
        elif 'MONTO POR DESCONTARSE' in c_clean or 'DESCONTARSE' in c_clean:
            cols_map[c] = 'monto_desconto'
        elif 'SALDO (DEUDA)' in c_clean or 'SALDO' in c_clean:
            cols_map[c] = 'saldo_deuda'
        elif 'FECHA COMPROBANTE' in c_clean or 'FACTURA CREDITO' in c_clean:
            cols_map[c] = 'fecha_comprobante'
            
    df_ren = df.rename(columns=cols_map)
    df_ren = df_ren.loc[:, ~df_ren.columns.duplicated()]
    return df_ren

def cargar_archivo_universal(file_uploader):
    ext = file_uploader.name.lower().split('.')[-1]
    file_uploader.seek(0)
    if ext in ['xlsx', 'xls']:
        df_raw = pd.read_excel(file_uploader, header=None, dtype=str)
        header_idx = 0
        for idx, row in df_raw.iterrows():
            row_str = " ".join([str(val).upper() for val in row.values if pd.notna(val)])
            if 'CEDULA' in row_str or 'C.I' in row_str or 'BENEFICIARIO' in row_str or 'OPERACION' in row_str:
                header_idx = idx
                break
        file_uploader.seek(0)
        return pd.read_excel(file_uploader, skiprows=header_idx, dtype=str)
    else:
        try:
            return pd.read_csv(file_uploader, dtype=str, sep=None, engine='python', encoding='utf-8')
        except:
            file_uploader.seek(0)
            return pd.read_csv(file_uploader, dtype=str, sep=None, engine='python', encoding='latin1')

@st.cache_data(ttl=2592000)
def cargar_liquidez():
    if os.path.exists(DB_LIQUIDEZ_FILE):
        try:
            df = pd.read_csv(DB_LIQUIDEZ_FILE, dtype=str)
            if 'emp_ci' in df.columns:
                df['emp_ci_clean'] = df['emp_ci'].astype(str).apply(limpiar_ci)
                return df
        except:
            pass
            
    archivos_carpeta = os.listdir('.')
    archivos_excel = [f for f in archivos_carpeta if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$') and f != DB_GIRADURIAS_FILE and f != DB_TELEFONOS_FILE]
    
    if archivos_excel:
        try:
            excel_encontrado = archivos_excel[0]
            df = pd.read_excel(excel_encontrado, dtype=str)
            return estandarizar_columnas_ffaa(df)
        except Exception:
            pass

    return pd.DataFrame()

def guardar_liquidez(df):
    df.to_csv(DB_LIQUIDEZ_FILE, index=False)
    st.cache_data.clear()

@st.cache_data(ttl=2592000)
def cargar_giradurias():
    if os.path.exists(DB_GIRADURIAS_FILE):
        try:
            df_u = unificar_hojas_excel(DB_GIRADURIAS_FILE)
            if not df_u.empty and 'emp_ci' in df_u.columns:
                df_u['emp_ci_clean'] = df_u['emp_ci'].astype(str).apply(limpiar_ci)
                return df_u
        except Exception:
            pass
    return pd.DataFrame()

def guardar_giradurias(df):
    df.to_excel(DB_GIRADURIAS_FILE, index=False)
    st.cache_data.clear()

@st.cache_data(ttl=2592000)
def cargar_historial_giradurias():
    if os.path.exists(DB_HISTORIAL_GIRADURIAS_FILE):
        try:
            df_h = pd.read_csv(DB_HISTORIAL_GIRADURIAS_FILE, dtype=str)
            if 'emp_ci' in df_h.columns:
                df_h['emp_ci_clean'] = df_h['emp_ci'].astype(str).apply(limpiar_ci)
            return df_h
        except Exception:
            pass
    return pd.DataFrame()

def guardar_historial_giradurias(df_nuevo, periodo_tag):
    df_existente = cargar_historial_giradurias()
    if not df_existente.empty and 'periodo' in df_existente.columns:
        df_existente = df_existente[df_existente['periodo'] != periodo_tag]
        df_unificado = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_unificado = df_nuevo
        
    df_unificado.to_csv(DB_HISTORIAL_GIRADURIAS_FILE, index=False)
    st.cache_data.clear()

# ==========================================
# 📱 FUNCIÓN CORREGIDA: LECTURA COMPLETA DE TODAS LAS PESTAÑAS DE TELÉFONOS
# ==========================================
@st.cache_data(ttl=2592000)
def cargar_telefonos():
    if os.path.exists(DB_TELEFONOS_FILE):
        try:
            xls = pd.ExcelFile(DB_TELEFONOS_FILE)
            records = []

            for sheet in xls.sheet_names:
                df_sheet = pd.read_excel(DB_TELEFONOS_FILE, sheet_name=sheet, header=None, dtype=str)
                current_unit = str(sheet).strip() # Nombre por defecto de la pestaña
                
                for idx, row in df_sheet.iterrows():
                    col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
                    col1 = str(row[1]).strip() if pd.notna(row[1]) else ""
                    col2 = str(row[2]).strip() if pd.notna(row[2]) else ""
                    col3 = str(row[3]).strip() if pd.notna(row[3]) else ""
                    col4 = str(row[4]).strip() if pd.notna(row[4]) else ""

                    # Detectar cambio de unidad dentro de la hoja si existe
                    if 'UNIDAD:' in col0.upper():
                        current_unit = f"{col0} {col1}".strip()
                        continue

                    # Omitir cabeceras o filas vacías
                    if col2 != "" and not col2.upper().startswith("NOMBRE") and not col2.upper().startswith("APELLIDO"):
                        nro_soc = col0.split('\n')[0].strip()
                        ci_clean = limpiar_ci(col3)
                        loc_tel, wa_tel = formatear_telefono_paraguay(col4)
                        
                        records.append({
                            'nro_socio': nro_soc,
                            'emp_nomape': col2,
                            'emp_ci': col3.replace('.0', '').strip(),
                            'emp_ci_clean': ci_clean,
                            'telefono': loc_tel,
                            'telefono_wa': wa_tel,
                            'unidad': current_unit,
                            'hoja_origen': sheet
                        })

            return pd.DataFrame(records)
        except Exception:
            pass
    return pd.DataFrame()

def guardar_telefonos_excel(file_uploader):
    with open(DB_TELEFONOS_FILE, "wb") as f:
        f.write(file_uploader.getbuffer())
    st.cache_data.clear()

def cargar_historial_contactos():
    if os.path.exists(DB_HISTORIAL_CONTACTOS_FILE):
        try:
            return pd.read_csv(DB_HISTORIAL_CONTACTOS_FILE, dtype=str)
        except:
            pass
    return pd.DataFrame(columns=['CEDULA', 'SOCIO', 'USUARIO', 'PLANTILLA_NRO', 'FECHA_HORA', 'MENSAJE_TEXTO'])

def registrar_contacto(cedula, socio, usuario, plantilla_nro, mensaje_texto):
    df_h = cargar_historial_contactos()
    fecha_ahora = obtener_fecha_hora_local().strftime('%d/%m/%Y %H:%M')
    nuevo = pd.DataFrame([{
        'CEDULA': limpiar_ci(cedula),
        'SOCIO': str(socio).strip(),
        'USUARIO': usuario.lower().strip(),
        'PLANTILLA_NRO': str(plantilla_nro),
        'FECHA_HORA': fecha_ahora,
        'MENSAJE_TEXTO': mensaje_texto
    }])
    df_h = pd.concat([df_h, nuevo], ignore_index=True)
    df_h.to_csv(DB_HISTORIAL_CONTACTOS_FILE, index=False)

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
    pdf.cell(0, 10, "SICOC - EVALUADOR DE CAPACIDAD CREDITICIA", border=0, ln=True, align="C")
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

class PDFSimulacionPrestamo(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')

    def header(self):
        fecha_local = obtener_fecha_hora_local().strftime('%d/%m/%Y %H:%M')
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 7, "SICOC - SIMULACIÓN OFICIAL DE PRÉSTAMO Y AMORTIZACIÓN", border=0, ln=True, align="C")
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 4, f"Fecha de emisión: {fecha_local}", border=0, ln=True, align="C")
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_pdf_simulacion_prestamo(nombre_s, ci_s, tipo_p, monto_cap, plazo_m, tasa_i, cap_gastos, plus_1, tot_pagar, df_plan_pagos):
    pdf = PDFSimulacionPrestamo()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "1. DATOS DEL SOLICITANTE Y CONDICIONES DEL CRÉDITO", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(100, 5, f"Socio: {nombre_s}")
    pdf.cell(90, 5, f"Cédula: {ci_s}", ln=True)
    pdf.cell(100, 5, f"Tipo de Crédito: {tipo_p}")
    pdf.cell(90, 5, f"Plazo: {plazo_m} meses", ln=True)
    pdf.cell(100, 5, f"Capital Solicitado: Gs. {formato_guarani(monto_cap)}")
    pdf.cell(90, 5, f"Tasa de Interés: {tasa_i}% Anual", ln=True)
    pdf.cell(100, 5, f"Capital con Gastos: Gs. {formato_guarani(cap_gastos)}")
    pdf.cell(90, 5, f"Total a Pagar: Gs. {formato_guarani(tot_pagar)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "2. PLAN DE AMORTIZACIÓN Y VENCIMIENTOS", ln=True)
    pdf.set_font("Helvetica", "B", 8)

    w_col = [12, 25, 26, 26, 26, 22, 28, 25]
    cols = ['Cuota', 'Vencimiento', 'Cuota Gs.', 'Amortiz.', 'Intereses', 'Plus Gs.', 'Saldo Gs.', 'Ahorro Gs.']
    
    for idx, c in enumerate(cols):
        pdf.cell(w_col[idx], 6, c, border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for idx, r in df_plan_pagos.iterrows():
        pdf.cell(w_col[0], 5, str(r.get('Nro. Cuota', '')), border=1, align="C")
        pdf.cell(w_col[1], 5, str(r.get('Fecha Vencimiento', '')), border=1, align="C")
        pdf.cell(w_col[2], 5, str(r.get('Cuota (Gs.)', '')), border=1, align="R")
        pdf.cell(w_col[3], 5, str(r.get('Amortización', '')), border=1, align="R")
        pdf.cell(w_col[4], 5, str(r.get('Intereses', '')), border=1, align="R")
        pdf.cell(w_col[5], 5, str(r.get('Plus (Gs.)', '')), border=1, align="R")
        pdf.cell(w_col[6], 5, str(r.get('Saldo (Gs.)', '')), border=1, align="R")
        pdf.cell(w_col[7], 5, str(r.get('Ahorro (Gs.)', '')), border=1, align="R")
        pdf.ln()

    return bytes(pdf.output())

class PDFReporteIncidencias(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')

    def header(self):
        fecha_local = obtener_fecha_hora_local().strftime('%d/%m/%Y %H:%M')
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 8, "SICOC - INFORME OFICIAL DE PAGOS PARCIALES Y RECHAZADOS", border=0, ln=True, align="C")
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 4, f"Fecha de emisión: {fecha_local}", border=0, ln=True, align="C")
        self.ln(4)

        self.set_font("Helvetica", "B", 8)
        self.cell(10, 6, "N°", border=1, align="C")
        self.cell(18, 6, "SOCIO", border=1, align="C")
        self.cell(20, 6, "CEDULA", border=1, align="C")
        self.cell(48, 6, "NOMBRE Y APELLIDO", border=1, align="C")
        self.cell(25, 6, "U. GIRADURÍA", border=1, align="C")
        self.cell(25, 6, "U. LIQUIDEZ", border=1, align="C")
        self.cell(24, 6, "ENVIADO", border=1, align="C")
        self.cell(24, 6, "COBRADO", border=1, align="C")
        self.cell(24, 6, "RECHAZADO", border=1, align="C")
        self.cell(59, 6, "DIAGNOSTICO / OBSERVACIÓN", border=1, align="C")
        self.ln()

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

class PDFCobrabilidadUnidades(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')

    def header(self):
        fecha_local = obtener_fecha_hora_local().strftime('%d/%m/%Y %H:%M')
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 8, "SICOC - RESUMEN DE COBRABILIDAD Y EFECTIVIDAD POR UNIDAD", border=0, ln=True, align="C")
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 4, f"Fecha de emisión: {fecha_local}", border=0, ln=True, align="C")
        self.ln(4)

        self.set_font("Helvetica", "B", 9)
        self.cell(15, 7, "N°", border=1, align="C")
        self.cell(90, 7, "UNIDAD / GIRADURÍA", border=1, align="C")
        self.cell(55, 7, "MONTO ENVIADO", border=1, align="C")
        self.cell(55, 7, "MONTO COBRADO", border=1, align="C")
        self.cell(50, 7, "% EFECTIVIDAD", border=1, align="C")
        self.ln()

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_pdf_reporte_incidencias(df_reporte):
    pdf = PDFReporteIncidencias()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 7)

    for idx, r in df_reporte.iterrows():
        nro_orden = idx + 1
        pdf.cell(10, 6, str(nro_orden), border=1, align="C")
        pdf.cell(18, 6, str(r.get('SOCIO', '-'))[:10], border=1, align="C")
        pdf.cell(20, 6, str(r.get('CEDULA', '-'))[:10], border=1, align="C")
        pdf.cell(48, 6, str(r.get('NOMBRE', '-'))[:28], border=1, align="L")
        pdf.cell(25, 6, str(r.get('UNIDAD GIRADURIA', '-'))[:15], border=1, align="L")
        pdf.cell(25, 6, str(r.get('UNIDAD LIQUIDEZ', '-'))[:15], border=1, align="L")
        pdf.cell(24, 6, f"Gs. {formato_guarani(r.get('ENVIADO', 0))}", border=1, align="R")
        pdf.cell(24, 6, f"Gs. {formato_guarani(r.get('COBRADO', 0))}", border=1, align="R")
        pdf.cell(24, 6, f"Gs. {formato_guarani(r.get('RECHAZADO', 0))}", border=1, align="R")
        pdf.cell(59, 6, str(r.get('DIAGNOSTICO', '-'))[:38], border=1, align="L")
        pdf.ln()

    return bytes(pdf.output())

def generar_pdf_cobrabilidad_unidades(df_metrics):
    pdf = PDFCobrabilidadUnidades()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 8)

    for idx, r in df_metrics.iterrows():
        nro_orden = idx + 1
        nombre_u = str(r.get('unidad_nombre_oficial', r.get('Unidad / Giraduría', '-')))
        pdf.cell(15, 6, str(nro_orden), border=1, align="C")
        pdf.cell(90, 6, nombre_u[:50], border=1, align="L")
        pdf.cell(55, 6, f"Gs. {formato_guarani(r.get('monto_enviado_num', 0))}", border=1, align="R")
        pdf.cell(55, 6, f"Gs. {formato_guarani(r.get('monto_cobrado_num', 0))}", border=1, align="R")
        pdf.cell(50, 6, f"{r.get('% Cobrado', 0)} %", border=1, align="C")
        pdf.ln()

    return bytes(pdf.output())

df_liquidez = cargar_liquidez()
df_giradurias = cargar_giradurias()
df_historial_giradurias = cargar_historial_giradurias()
df_telefonos = cargar_telefonos()
df_dictamenes = cargar_dictamenes()

# ==========================================
# 🪖 MÓDULO 1: EVALUADOR DE LIQUIDEZ Y DIAGNÓSTICO INTEGRAL DE SOCIO
# ==========================================
if opcion == "🔍 Evaluador de Liquidez (FF.AA.)":
    st.subheader("🔍 Buscador de Liquidez y Estado de Socio")
    
    df_fuente_giradurias = df_historial_giradurias if not df_historial_giradurias.empty else df_giradurias

    tipo_busqueda = st.radio(
        "Método de búsqueda:", 
        ["💳 Por Número de Cédula", "🏷️ Por Número de Socio", "👤 Por Nombre / Apellido"], 
        horizontal=True
    )
    matches_l = pd.DataFrame()
    matches_g = pd.DataFrame()
    
    if tipo_busqueda == "💳 Por Número de Cédula":
        ci_input = st.text_input("Número de Cédula (C.I.):", placeholder="Ej: 5511820").strip()
        ci_input_clean = limpiar_ci(ci_input)
        if ci_input_clean:
            if not df_liquidez.empty:
                if 'emp_ci_clean' not in df_liquidez.columns:
                    df_liquidez['emp_ci_clean'] = df_liquidez['emp_ci'].astype(str).apply(limpiar_ci)
                matches_l = df_liquidez[df_liquidez['emp_ci_clean'] == ci_input_clean]
            
            if not df_fuente_giradurias.empty:
                if 'emp_ci_clean' not in df_fuente_giradurias.columns and 'emp_ci' in df_fuente_giradurias.columns:
                    df_fuente_giradurias['emp_ci_clean'] = df_fuente_giradurias['emp_ci'].astype(str).apply(limpiar_ci)
                if 'emp_ci_clean' in df_fuente_giradurias.columns:
                    matches_g = df_fuente_giradurias[df_fuente_giradurias['emp_ci_clean'] == ci_input_clean]

    elif tipo_busqueda == "🏷️ Por Número de Socio":
        socio_input = st.text_input("Número de Socio:", placeholder="Ej: 9946").strip()
        if socio_input:
            if not df_fuente_giradurias.empty and 'nro_socio' in df_fuente_giradurias.columns:
                matches_g = df_fuente_giradurias[df_fuente_giradurias['nro_socio'].astype(str).str.strip() == socio_input.strip()]
                if not matches_g.empty:
                    ci_socio_encontrada = limpiar_ci(matches_g.iloc[0].get('emp_ci', ''))
                    if ci_socio_encontrada and not df_liquidez.empty:
                        if 'emp_ci_clean' not in df_liquidez.columns:
                            df_liquidez['emp_ci_clean'] = df_liquidez['emp_ci'].astype(str).apply(limpiar_ci)
                        matches_l = df_liquidez[df_liquidez['emp_ci_clean'] == ci_socio_encontrada]

    else: # Por Nombre / Apellido
        nombre_input = st.text_input("Nombre o Apellido:", placeholder="Ej: Sanabria").strip()
        if nombre_input:
            if not df_liquidez.empty:
                matches_l = df_liquidez[df_liquidez['emp_nomape'].astype(str).str.contains(nombre_input, case=False, na=False)]
            if not df_fuente_giradurias.empty:
                matches_g = df_fuente_giradurias[df_fuente_giradurias['emp_nomape'].astype(str).str.contains(nombre_input, case=False, na=False)]

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
            jubilacion = limpiar_monto(row_l.get('jubilacion', 0))
            giraduria = limpiar_monto(row_l.get('giraduria', 0))
            desc_cf2 = limpiar_monto(row_l.get('descuento_cf2', 0))
            judicial = limpiar_monto(row_l.get('judicial', 0))
            
            total_descuentos = jubilacion + giraduria + desc_cf2 + judicial
            liquido_real = presupuestado - total_descuentos if total_descuentos > 0 else limpiar_monto(row_l.get('liquido', 0))
            base_imponible = presupuestado - jubilacion
            limite_50 = base_imponible / 2.0
            total_deudas_actuales = giraduria + desc_cf2 + judicial
            margen_deuda_restante = limite_50 - total_deudas_actuales
        else:
            row_g_first = matches_g.iloc[0]
            nombre = row_g_first.get('emp_nomape', 'S/N')
            cedula_militar = limpiar_ci(row_g_first.get('emp_ci', '0'))
            u_g_ofic = row_g_first.get('unidad_nombre_oficial', 'Giradurías')
            unidad_militar = f"No figura en Liquidez (GIRADURÍA: {u_g_ofic})"
            categoria = "S/D"

            presupuestado = 0.0
            jubilacion = 0.0
            giraduria = 0.0
            desc_cf2 = 0.0
            judicial = 0.0
            total_descuentos = 0.0
            liquido_real = 0.0
            limite_50 = 0.0
            margen_deuda_restante = 0.0

        es_socio = False
        nro_socio = "No socio"
        monto_enviado = 0.0
        monto_cobrado = 0.0
        monto_rechazado = 0.0
        unidad_enviada_giraduria = ""

        if not df_fuente_giradurias.empty:
            periodos_disponibles = []
            if 'periodo' in df_fuente_giradurias.columns:
                periodos_disponibles = sorted([p for p in df_fuente_giradurias['periodo'].dropna().unique() if str(p).strip() != ""], reverse=True)
            
            if not periodos_disponibles:
                periodos_disponibles = ["Mes Actual Cargado"]

            st.markdown("---")
            col_sel_p, _ = st.columns([2, 2])
            with col_sel_p:
                periodo_seleccionado = st.selectbox(
                    "🗓️ Seleccionar Período / Mes a Consultar (Existente en Base):",
                    options=periodos_disponibles
                )

            if 'periodo' in df_fuente_giradurias.columns and periodo_seleccionado != "Mes Actual Cargado":
                df_gir_periodo = df_fuente_giradurias[df_fuente_giradurias['periodo'] == periodo_seleccionado]
            else:
                df_gir_periodo = df_fuente_giradurias

            match_g = pd.DataFrame()
            if 'emp_ci_clean' in df_gir_periodo.columns and cedula_militar:
                match_g = df_gir_periodo[df_gir_periodo['emp_ci_clean'] == cedula_militar]
            
            if match_g.empty and 'nro_socio' in df_gir_periodo.columns and figura_en_giradurias:
                n_soc_ref = str(matches_g.iloc[0].get('nro_socio', '')).strip()
                match_g = df_gir_periodo[df_gir_periodo['nro_socio'].astype(str).str.strip() == n_soc_ref]

            if not match_g.empty:
                es_socio = True
                row_socio = match_g.iloc[0]
                nro_socio_val = limpiar_texto(row_socio.get('nro_socio', ''))
                nro_socio = nro_socio_val if nro_socio_val else "Socio Registrado"
                
                for _, r_g in match_g.iterrows():
                    monto_enviado += limpiar_monto(r_g.get('monto_enviado', 0))
                    monto_cobrado += limpiar_monto(r_g.get('monto_cobrado', 0))
                    monto_rechazado += limpiar_monto(r_g.get('monto_rechazado', 0))

                if monto_rechazado == 0 and monto_enviado > monto_cobrado:
                    monto_rechazado = monto_enviado - monto_cobrado
                    
                unidad_enviada_giraduria = limpiar_texto(row_socio.get('unidad_nombre_oficial', ''))

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.success(f"👤 **Socio / Militar:** {nombre}\n\n**C.I.:** {cedula_militar} | **Cat:** {categoria}")
        with col_info2:
            if es_socio:
                st.info(f"💳 **Estado de Socio:** SOCIO ACTIVO\n\n**N° Socio:** `{nro_socio}`")
            else:
                st.warning("💳 **Estado de Socio:** `No socio`")
        with col_info3:
            if figura_en_liquidez:
                st.info(f"🏛️ **Unidad en Liquidez:** {unidad_militar}")
            else:
                st.warning(f"🏛️ **Unidad en Liquidez:** No figura en Liquidez (Socio en {unidad_enviada_giraduria if unidad_enviada_giraduria else 'Giraduría Externas'})")

        if es_socio:
            st.markdown(f"### 🏛️ Datos de Descuento en Giraduría ({periodo_seleccionado if 'periodo_seleccionado' in locals() else 'Mes Actual'})")
            col_g1, col_g2, col_g3, col_g4 = st.columns(4)
            col_g1.metric("Giraduría Enviada", unidad_enviada_giraduria if unidad_enviada_giraduria else "Sin Asignar")
            col_g2.metric("Monto Enviado", f"Gs. {formato_guarani(monto_enviado)}")
            col_g3.metric("Monto Descontado/Cobrado", f"Gs. {formato_guarani(monto_cobrado)}")
            
            if monto_rechazado > 0:
                col_g4.metric("Monto Rechazado / Pendiente", f"Gs. {formato_guarani(monto_rechazado)}", delta=f"-Gs. {formato_guarani(monto_rechazado)}", delta_color="inverse")
            else:
                col_g4.metric("Monto Rechazado", "Gs. 0", delta="Cobro 100% OK")

            u_gir_upper = unidad_enviada_giraduria.upper()
            is_jubilado = "JUBILAD" in u_gir_upper or "JUBILADOS" in unidad_militar.upper()
            is_cf2 = "CF2" in u_gir_upper or "CFN2" in u_gir_upper

            if not figura_en_liquidez:
                st.info(
                    f"💡 **INFORMACIÓN DE SOCIO EXTERNO A LIQUIDEZ FF.AA.:**\n"
                    f"El socio pertenece a la giraduría **{unidad_enviada_giraduria}**. Por este motivo no figura en la planilla de salarios de Liquidez de las FF.AA., "
                    f"pero sí se procesan sus descuentos de cobro normalmente a través de su giraduría respectiva."
                )

            elif monto_enviado > 0 and monto_cobrado == 0:
                st.error("🚨 **ALERTA DE DESCUENTO RECHAZADO (Gs. 0 COBRADO)**")
                if is_cf2:
                    unidad_ref = unidad_militar if unidad_militar else "su unidad de origen"
                    st.markdown(
                        f"⚠️ **DIAGNÓSTICO ESPECÍFICO UNIDAD CF2:**\n"
                        f"El descuento enviado a CF2 fue rechazado (Gs. 0 cobrado).\n"
                        f"📌 **Acción Requerida:** REFINANCIACIÓN NO FACTIBLE (Gs. 0 cobrado). Consultar con unidad **{unidad_ref}** o **proceder a notificación formal en caso de mora**."
                    )
                elif unidad_enviada_giraduria and unidad_militar.upper() not in unidad_enviada_giraduria.upper():
                    st.markdown(
                        f"⚠️ **DIAGNÓSTICO DE INCONSISTENCIA EN GIRADURÍA:**\n"
                        f"El socio no registró ningún descuento debido a que la planilla fue enviada a la **{unidad_enviada_giraduria}**, "
                        f"mientras que en la base oficial de Liquidez de las FF.AA. figura asignado a la unidad **{unidad_militar}**.\n"
                        f"📌 **Acción Requerida:** Reasignar el legajo y enviar la solicitud a la giraduría correspondiente ({unidad_militar})."
                    )
                else:
                    st.markdown(
                        f"⚠️ **DIAGNÓSTICO DE CAPACIDAD DE PAGO Y MOROSIDAD:**\n"
                        f"REFINANCIACIÓN NO FACTIBLE (Monto cobrado insuficiente).\n"
                        f"📌 **Acción Requerida:** En caso de registrar atraso en cuotas, **proceder a la emisión de Notificación Formal de Requerimiento de Pago**."
                    )

            elif 0 < monto_cobrado < monto_enviado:
                st.warning("⚠️ **ALERTA DE PAGO PARCIAL DETECTADO**")
                
                # REGLA ESPECIAL MENOR A 100.000 GS.
                if monto_cobrado < 100000:
                    st.error(
                        f"🔴 **REFINANCIACIÓN NO FACTIBLE (Monto Cobrado < Gs. 100.000):**\n"
                        f"El socio registró un pago parcial de tan solo **Gs. {formato_guarani(monto_cobrado)}**, lo cual es inferior al mínimo operativo requerido (Gs. 100.000).\n"
                        f"📌 **Acción Requerida:** No se recomienda estructurar refinanciación. **En caso de contar con cuotas atrasadas, proceder a la notificación formal de pago.**"
                    )
                elif is_jubilado:
                    st.info(
                        f"💡 **DIAGNÓSTICO ESPECÍFICO UNIDAD JUBILADOS:**\n"
                        f"El socio jubilado registró un pago parcial de Gs. {formato_guarani(monto_cobrado)}.\n"
                        f"📌 **Acción Requerida:** Actualizar planilla de autorización o evaluar refinanciación (Último descuento: Gs. {formato_guarani(monto_cobrado)})."
                    )
                elif is_cf2:
                    st.success(
                        f"💡 **DIAGNÓSTICO ESPECÍFICO UNIDAD CF2:**\n"
                        f"Unidad Central de Descuentos (CF2) con pago parcial acumulado.\n"
                        f"✅ **Refinanciación Factible - Tope de cuota recomendada: Gs. {formato_guarani(monto_cobrado)} cobrados.**"
                    )
                elif margen_deuda_restante > 0:
                    st.success(
                        f"💡 **ANÁLISIS DE REFINANCIACIÓN FACTIBLE:**\n"
                        f"El socio realizó un pago parcial. Cuenta con un margen libre de liquidez de **Gs. {formato_guarani(margen_deuda_restante)}**.\n"
                        f"✅ **Es factible reestructurar o refinanciar el saldo pendiente de Gs. {formato_guarani(monto_rechazado)}.**"
                    )
                else:
                    st.info(
                        f"💡 **ANÁLISIS DE RESTRUCTURACIÓN RECOMENDADO:**\n"
                        f"El socio realizó un pago parcial pero no dispone de margen libre en el límite del 50%.\n"
                        f"📌 **Se sugiere evaluar reestructurar/refinanciar fijando la cuota límite en los Gs. {formato_guarani(monto_cobrado)} descontados actualmente.**"
                    )

        if figura_en_liquidez:
            st.markdown("### 📊 Desglose de Haberes y Descuentos (FF.AA.)")
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

        st.markdown("---")
        st.subheader("📜 Historial de Descuentos del Socio")
        
        if es_socio and not df_fuente_giradurias.empty:
            historial_socio = pd.DataFrame()
            if 'emp_ci_clean' in df_fuente_giradurias.columns and cedula_militar:
                historial_socio = df_fuente_giradurias[df_fuente_giradurias['emp_ci_clean'] == cedula_militar]
            
            if historial_socio.empty and 'nro_socio' in df_fuente_giradurias.columns:
                historial_socio = df_fuente_giradurias[df_fuente_giradurias['nro_socio'].astype(str).str.strip() == str(nro_socio).strip()]

            if not historial_socio.empty:
                rows_historia = []
                for _, h_row in historial_socio.iterrows():
                    p_val = h_row.get('periodo', 'Mes Actual')
                    u_env = h_row.get('unidad_nombre_oficial', 'Sin Asignar')
                    m_env = limpiar_monto(h_row.get('monto_enviado', 0))
                    m_cob = limpiar_monto(h_row.get('monto_cobrado', 0))
                    m_rec = limpiar_monto(h_row.get('monto_rechazado', 0))
                    if m_rec == 0 and m_env > m_cob:
                        m_rec = m_env - m_cob

                    if m_cob == m_env and m_env > 0:
                        est_hist = "✅ COBRADO COMPLETO"
                    elif m_cob > 0 and m_cob < m_env:
                        est_hist = "⚠️ PAGO PARCIAL"
                    elif m_env > 0 and m_cob == 0:
                        est_hist = "🚨 RECHAZADO / NULO"
                    else:
                        est_hist = "REGISTRADO"

                    rows_historia.append({
                        "Período / Mes": p_val,
                        "Giraduría Enviada": u_env,
                        "Monto Enviado (Gs.)": f"Gs. {formato_guarani(m_env)}",
                        "Monto Cobrado (Gs.)": f"Gs. {formato_guarani(m_cob)}",
                        "Monto Rechazado (Gs.)": f"Gs. {formato_guarani(m_rec)}",
                        "Estado": est_hist
                    })

                df_hist_view = pd.DataFrame(rows_historia)
                st.dataframe(df_hist_view, use_container_width=True)
            else:
                st.info("No se registran antecedentes previos de descuentos en el historial.")
        else:
            st.info("El militar consultado no figura en el historial registrado de socios.")

        dict_match = df_dictamenes[df_dictamenes['CEDULA'].astype(str).apply(limpiar_ci) == cedula_militar]
        obs_dictamen = dict_match.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_match.empty else "Sin observaciones previas."
        
        if not dict_match.empty:
            st.markdown("---")
            st.warning(f"📌 **Dictamen Registrado por Giraduría:** {obs_dictamen}")

        st.markdown("---")
        pdf_bytes = generar_pdf_constancia("Evaluación de Liquidez", nombre, cedula_militar, unidad_militar, presupuestado, jubilacion, total_descuentos, liquido_real, limite_50, 0.0, "EVALUACIÓN REALIZADA", obs_dictamen)
        
        st.download_button(
            label="📄 Descargar / Imprimir Constancia de Evaluación (PDF)",
            data=pdf_bytes,
            file_name=f"Constancia_Credito_{cedula_militar}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("⚠️ No se encontraron resultados coincidentes en las bases de datos.")

# ==========================================
# 📱 MÓDULO 2: GIRADURÍAS TELÉFONOS (WHATSAPP & CONTACTO)
# ==========================================
elif opcion == "📱 Giradurías Teléfonos":
    st.subheader("📱 Módulo de Gestión de Contacto y Teléfonos de Socios")
    
    if df_telefonos.empty:
        st.warning("⚠️ No se encuentra cargada la base de teléfonos (`Giraduria con numero de telefono.xlsx`). Podés subirla en 'Cargar Base Mensual'.")
    else:
        st.info(f"📊 **Base de datos activa:** {len(df_telefonos):,} socios registrados consolidados de TODAS las pestañas del Excel.")
        
        busq_tel = st.text_input("🔍 Buscar por Cédula (C.I.), N° de Socio o Nombre/Apellido:", placeholder="Ej: 5955048, 9946 o AQUINO").strip()
        busq_clean = limpiar_ci(busq_tel)

        match_tel = pd.DataFrame()
        if busq_tel:
            if busq_clean and 'emp_ci_clean' in df_telefonos.columns:
                match_tel = df_telefonos[df_telefonos['emp_ci_clean'] == busq_clean]
            if match_tel.empty and 'nro_socio' in df_telefonos.columns:
                match_tel = df_telefonos[df_telefonos['nro_socio'].astype(str).str.strip() == busq_tel]
            if match_tel.empty and 'emp_nomape' in df_telefonos.columns:
                match_tel = df_telefonos[df_telefonos['emp_nomape'].astype(str).str.contains(busq_tel, case=False, na=False)]

        if not match_tel.empty:
            socio_t = match_tel.iloc[0]
            nombre_t = socio_t.get('emp_nomape', 'S/D')
            ci_t = socio_t.get('emp_ci_clean', '0')
            socio_num_t = socio_t.get('nro_socio', 'S/D')
            tel_local_t = socio_t.get('telefono', 'Sin Teléfono')
            tel_wa_t = socio_t.get('telefono_wa', '')
            unid_t = socio_t.get('unidad', 'Giraduría')
            hoja_t = socio_t.get('hoja_origen', 'Pestaña')

            st.markdown("---")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown(f"### 👤 {nombre_t}")
                st.write(f"💳 **Cédula N°:** `{ci_t}` | **N° Socio:** `{socio_num_t}`")
                st.write(f"🏛️ **Unidad / Giraduría:** {unid_t} *(Pestaña: {hoja_t})*")
                st.write(f"📞 **Teléfono Registrado:** `{tel_local_t}`")

            with col_t2:
                st.markdown("### 📲 Enviar Mensaje por WhatsApp")
                
                if usuario_actual == "martin":
                    plantilla_nro = 1
                    msg_text = (
                        f"Hola {nombre_t}, te saludamos del área de Giradurías de la Cooperativa. "
                        f"Te informamos que en tu descuento del mes se registró un ajuste al límite disponible. "
                        f"Te ofrecemos la posibilidad de reestructurar tu saldo, con la opción de retirar un pequeño saldo a favor en efectivo "
                        f"(sujeto a análisis y margen de liquidez). ¡Consultanos para más detalles!"
                    )
                elif usuario_actual == "estela":
                    plantilla_nro = 1
                    msg_text = (
                        f"Hola {nombre_t}, te saludamos del área de Giradurías de la Cooperativa. "
                        f"Te informamos que en tu descuento del mes se registró un ajuste al límite disponible. "
                        f"Te ofrecemos la posibilidad de reestructurar tu saldo para regularizar tu cuenta. ¡Consultanos para más detalles!"
                    )
                else: # Arthuro
                    plantilla_sel = st.selectbox("Seleccionar Plantilla a Enviar:", ["Plantilla 1 (Con Opción Efectivo - Martín)", "Plantilla 1 (Estándar - Estela)", "Mensaje Personalizado"])
                    if "Con Opción Efectivo" in plantilla_sel:
                        plantilla_nro = 1
                        msg_text = (
                            f"Hola {nombre_t}, te saludamos del área de Giradurías. Te informamos que en tu descuento se registró un ajuste. "
                            f"Podés reestructurar tu saldo con opción a un pequeño monto en efectivo según análisis y liquidez."
                        )
                    elif "Estándar" in plantilla_sel:
                        plantilla_nro = 1
                        msg_text = (
                            f"Hola {nombre_t}, te saludamos del área de Giradurías. Te informamos que en tu descuento se registró un ajuste. "
                            f"Te ofrecemos la posibilidad de reestructurar tu saldo para regularizar tu cuenta."
                        )
                    else:
                        plantilla_nro = 99
                        msg_text = st.text_area("Escribir mensaje personalizado:", value=f"Hola {nombre_t}, te escribimos del área de Giradurías.")

                st.text_area("Vista previa del mensaje:", value=msg_text, height=120, disabled=True)

                if tel_wa_t:
                    msg_encoded = urllib.parse.quote(msg_text)
                    wa_url = f"https://wa.me/{tel_wa_t}?text={msg_encoded}"
                    
                    if st.button("📲 Abrir WhatsApp y Registrar Contacto", use_container_width=True):
                        registrar_contacto(ci_t, socio_num_t, usuario_actual, plantilla_nro, msg_text)
                        st.success("✅ Contacto registrado correctamente en la bitácora.")
                        st.markdown(f'[👉 Haz Clic Aquí para Abrir el Chat de WhatsApp Directamente]({wa_url})')
                else:
                    st.warning("⚠️ El socio no posee un número de teléfono válido registrado.")

            # HISTORIAL Y BITÁCORA DE CONTACTOS DE LA FICHA
            st.markdown("---")
            st.subheader("📜 Bitácora e Historial de Contactos Realizados")
            df_hist_cont = cargar_historial_contactos()

            match_h_c = df_hist_cont[df_hist_cont['CEDULA'] == ci_t] if not df_hist_cont.empty and 'CEDULA' in df_hist_cont.columns else pd.DataFrame()

            if not match_h_c.empty:
                ult_c = match_h_c.iloc[-1]
                usr_c = ult_c.get('USUARIO', '').capitalize()
                fec_c = ult_c.get('FECHA_HORA', '')
                p_nro = ult_c.get('PLANTILLA_NRO', '')

                st.info(f"🔵 **Última gestión:** Contactado por **{usr_c}** el {fec_c}.")

                if es_admin_base:
                    st.markdown("#### 🛡️ Vista de Auditoría Administrador (Exclusivo Arthuro)")
                    st.dataframe(match_h_c[['FECHA_HORA', 'USUARIO', 'PLANTILLA_NRO', 'MENSAJE_TEXTO']], use_container_width=True)
                else:
                    my_contacts = match_h_c[match_h_c['USUARIO'] == usuario_actual]
                    if not my_contacts.empty:
                        st.caption(f"ℹ️ Has enviado {len(my_contacts)} mensaje(s) a este socio usando la Plantilla N° {p_nro}.")
            else:
                st.success("🟢 **Estado:** Sin contacto previo registrado en el sistema.")

# ==========================================
# 📊 MÓDULO 3: GESTIÓN Y DIAGNÓSTICO DE COBRANZAS
# ==========================================
elif opcion == "📊 Gestión y Diagnóstico de Cobranzas":
    st.subheader("📊 Módulo de Diagnóstico de Cobranzas, Estadísticas y Reportes")
    
    if df_giradurias.empty:
        st.info("👈 Por favor cargá la `Planilla_Descuentos_Consolidada.xlsx` en 'Cargar Base Mensual' para habilitar los reportes.")
    else:
        reporte_list = []

        for idx, row in df_giradurias.iterrows():
            ci = limpiar_ci(row.get('emp_ci', ''))
            socio = limpiar_texto(row.get('nro_socio', 'No socio'))
            enviado = limpiar_monto(row.get('monto_enviado', 0))
            cobrado = limpiar_monto(row.get('monto_cobrado', 0))
            m_rech = limpiar_monto(row.get('monto_rechazado', 0))
            if m_rech == 0 and enviado > cobrado:
                m_rech = enviado - cobrado

            unidad_giraduria = limpiar_texto(row.get('unidad_nombre_oficial', 'Sin Unidad'))

            if enviado == 0:
                continue

            diagnostico = "COBRADO NORMAL"
            unidad_liq = ""
            margen_liq = 0.0

            if not df_liquidez.empty and ci:
                col_search_l = 'emp_ci_clean' if 'emp_ci_clean' in df_liquidez.columns else 'emp_ci'
                m_liq = df_liquidez[df_liquidez[col_search_l].astype(str).apply(limpiar_ci) == ci]
                if not m_liq.empty:
                    r_l = m_liq.iloc[0]
                    unidad_liq = limpiar_texto(r_l.get('UNIDAD', ''))
                    presup = limpiar_monto(r_l.get('presupuestado', 0))
                    jub = limpiar_monto(r_l.get('jubilacion', 0))
                    tot_d = jub + limpiar_monto(r_l.get('giraduria', 0)) + limpiar_monto(r_l.get('descuento_cf2', 0)) + limpiar_monto(r_l.get('judicial', 0))
                    margen_liq = ((presup - jub) / 2.0) - (tot_d - jub)

            if not unidad_liq:
                u_gir_upper = unidad_giraduria.upper()
                if "ARMADA" in u_gir_upper:
                    unidad_liq = "Armada"
                elif "AEREA" in u_gir_upper or "AÉREA" in u_gir_upper:
                    unidad_liq = "Fuerza Aérea"
                elif "POLICIA" in u_gir_upper or "POLICÍA" in u_gir_upper:
                    unidad_liq = "Policía Nacional"
                elif "JUBILAD" in u_gir_upper:
                    unidad_liq = "Jubilado"
                else:
                    unidad_liq = "FFPP / Jubilado"

            u_gir_clean = unidad_giraduria.upper()
            is_jubilado_u = "JUBILAD" in u_gir_clean or "JUBILADOS" in unidad_liq.upper()
            is_cf2_u = "CF2" in u_gir_clean or "CFN2" in u_gir_clean

            # REGLA DE EVALUACIÓN DE REFINANCIACIÓN (LÍMITE GS. 100.000)
            if cobrado < 100000:
                diagnostico = "REFINANCIACIÓN NO FACTIBLE (Tope < Gs. 100.000) - Emitir notificación formal si registra mora"
            elif is_cf2_u:
                diagnostico = f"CF2: Refinanciación factible - Tope cuota recomendada: Gs. {formato_guarani(cobrado)} cobrados"
            elif is_jubilado_u:
                diagnostico = f"JUBILADO: Actualizar planilla de autorización o refinanciar (Último descuento: Gs. {formato_guarani(cobrado)})"
            else:
                if cobrado == 0:
                    if unidad_liq not in ["FFPP / Jubilado", "Jubilado", "Armada", "Fuerza Aérea", "Policía Nacional"] and unidad_giraduria.upper() not in unidad_liq.upper():
                        diagnostico = f"RECHAZADO: Enviado a {unidad_giraduria} pero figura en {unidad_liq} - Proceder a notificación"
                    else:
                        diagnostico = "RECHAZADO: Falta de liquidez - Proceder a notificación formal"
                elif 0 < cobrado < enviado:
                    if margen_liq >= 100000:
                        diagnostico = f"PARCIAL: REFINANCIACIÓN FACTIBLE (Margen libre Gs. {formato_guarani(margen_liq)})"
                    else:
                        diagnostico = f"PARCIAL: Evaluar refinanciación (Cuota límite recomendada: Gs. {formato_guarani(cobrado)} cobrados)"

            if cobrado < enviado:
                socio_num = int(re.sub(r'\D', '', str(socio))) if re.sub(r'\D', '', str(socio)) else 99999999
                reporte_list.append({
                    'SOCIO_NUM': socio_num,
                    'SOCIO': socio,
                    'CEDULA': ci,
                    'NOMBRE': limpiar_texto(row.get('emp_nomape', 'S/D')),
                    'UNIDAD GIRADURIA': unidad_giraduria,
                    'UNIDAD LIQUIDEZ': unidad_liq,
                    'ENVIADO': enviado,
                    'COBRADO': cobrado,
                    'RECHAZADO': m_rech,
                    'DIAGNOSTICO': diagnostico
                })

        df_incidencias = pd.DataFrame(reporte_list)

        if not df_incidencias.empty:
            df_incidencias = df_incidencias.sort_values(by='SOCIO_NUM', ascending=True).reset_index(drop=True)
            df_incidencias.drop(columns=['SOCIO_NUM'], inplace=True, errors='ignore')

        tab_r1, tab_r2 = st.tabs(["📉 Reporte de Pagos Parciales / Rechazados", "📊 Gráfico de Cobrabilidad por Unidad"])

        with tab_r1:
            st.markdown("### 📋 Listado Oficial de Incidencias de Cobro")
            st.caption("Filtro automático de socios con descuentos parciales o nulos (Gs. 0 cobrado).")

            if df_incidencias.empty:
                st.success("✅ ¡Sin incidencias! No se encontraron pagos parciales o rechazados.")
            else:
                st.warning(f"Se encontraron **{len(df_incidencias)}** socios con observaciones de cobro.")
                
                df_view_inc = df_incidencias.copy()
                df_view_inc.insert(0, 'N°', range(1, 1 + len(df_view_inc)))
                st.dataframe(df_view_inc, use_container_width=True)

                col_rep1, col_rep2 = st.columns(2)
                with col_rep1:
                    out_rep = io.BytesIO()
                    with pd.ExcelWriter(out_rep, engine='openpyxl') as writer:
                        df_view_inc.to_excel(writer, sheet_name='Incidencias_Cobro', index=False)
                    st.download_button(
                        label="📥 Descargar Informe Completo de Incidencias (.XLSX)",
                        data=out_rep.getvalue(),
                        file_name="Informe_Socios_Incidencias_Cobro.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                with col_rep2:
                    pdf_inc_bytes = generar_pdf_reporte_incidencias(df_incidencias)
                    st.download_button(
                        label="📄 Descargar Informe Oficial Horizontal (.PDF)",
                        data=pdf_inc_bytes,
                        file_name="Informe_Socios_Incidencias_Cobro.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

        with tab_r2:
            st.markdown("### 📊 Porcentaje de Efectividad de Cobro por Unidad")
            
            if 'unidad_nombre_oficial' in df_giradurias.columns:
                df_g_copy = df_giradurias.copy()
                df_g_copy['monto_enviado_num'] = df_g_copy['monto_enviado'].apply(limpiar_monto)
                df_g_copy['monto_cobrado_num'] = df_g_copy['monto_cobrado'].apply(limpiar_monto)

                df_metrics = df_g_copy.groupby('unidad_nombre_oficial', as_index=False)[['monto_enviado_num', 'monto_cobrado_num']].sum()
                df_metrics['% Cobrado'] = (df_metrics['monto_cobrado_num'] / df_metrics['monto_enviado_num'] * 100).fillna(0).round(1)

                df_metrics_view = df_metrics.copy()
                df_metrics_view.insert(0, 'N°', range(1, 1 + len(df_metrics_view)))
                df_metrics_view['Unidad / Giraduría'] = df_metrics_view['unidad_nombre_oficial']
                df_metrics_view['Monto Total Enviado (Gs.)'] = df_metrics_view['monto_enviado_num'].apply(formato_guarani)
                df_metrics_view['Monto Total Cobrado (Gs.)'] = df_metrics_view['monto_cobrado_num'].apply(formato_guarani)
                df_metrics_view['% Efectividad'] = df_metrics_view['% Cobrado'].astype(str) + " %"

                st.dataframe(df_metrics_view[['N°', 'Unidad / Giraduría', 'Monto Total Enviado (Gs.)', 'Monto Total Cobrado (Gs.)', '% Efectividad']], use_container_width=True)

                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    out_met = io.BytesIO()
                    with pd.ExcelWriter(out_met, engine='openpyxl') as writer:
                        df_metrics_view[['N°', 'Unidad / Giraduría', 'Monto Total Enviado (Gs.)', 'Monto Total Cobrado (Gs.)', '% Efectividad']].to_excel(writer, sheet_name='Cobrabilidad_Unidades', index=False)
                    st.download_button(
                        label="📥 Descargar Cuadro de Cobrabilidad (.XLSX)",
                        data=out_met.getvalue(),
                        file_name="Efectividad_Cobrabilidad_Por_Unidad.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                with col_m2:
                    pdf_met_bytes = generar_pdf_cobrabilidad_unidades(df_metrics)
                    st.download_button(
                        label="📄 Descargar Informe de Cobrabilidad Horizontal (.PDF)",
                        data=pdf_met_bytes,
                        file_name="Efectividad_Cobrabilidad_Por_Unidad.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                st.markdown("#### 📈 Gráfico de Porcentaje de Efectividad de Cobro")
                st.bar_chart(data=df_metrics, x='unidad_nombre_oficial', y='% Cobrado')

# ==========================================
# 📋 MÓDULO 4: DICTAMEN DEL GIRADOR
# ==========================================
elif opcion == "📋 Dictamen del Girador":
    st.subheader("📋 Módulo de Registro de Dictamen de Giraduría")
    
    if df_liquidez.empty and df_giradurias.empty:
        st.info("Cargá las bases de liquidez o giradurías primero.")
    else:
        tipo_busq_g = st.radio("Buscar por:", ["💳 Cédula", "🏷️ N° Socio", "👤 Nombre / Apellido"], horizontal=True)
        matches_g = pd.DataFrame()

        if tipo_busq_g == "💳 Cédula":
            ci_girador = st.text_input("Ingresá la Cédula:", placeholder="Ej: 5511820").strip()
            ci_girador_clean = limpiar_ci(ci_girador)
            if ci_girador_clean:
                if not df_liquidez.empty:
                    if 'emp_ci_clean' not in df_liquidez.columns:
                        df_liquidez['emp_ci_clean'] = df_liquidez['emp_ci'].astype(str).apply(limpiar_ci)
                    matches_g = df_liquidez[df_liquidez['emp_ci_clean'] == ci_girador_clean]
                if matches_g.empty and not df_giradurias.empty:
                    if 'emp_ci_clean' not in df_giradurias.columns:
                        df_giradurias['emp_ci_clean'] = df_giradurias['emp_ci'].astype(str).apply(limpiar_ci)
                    matches_g = df_giradurias[df_giradurias['emp_ci_clean'] == ci_girador_clean]

        elif tipo_busq_g == "🏷️ N° Socio":
            socio_g = st.text_input("Ingresá el N° de Socio:", placeholder="Ej: 9946").strip()
            if socio_g:
                ci_socio_g = ""
                if not df_giradurias.empty and 'nro_socio' in df_giradurias.columns:
                    match_sg = df_giradurias[df_giradurias['nro_socio'].astype(str).str.strip() == socio_g.strip()]
                    if not match_sg.empty:
                        ci_socio_g = limpiar_ci(match_sg.iloc[0].get('emp_ci', ''))
                        matches_g = match_sg
                
                if ci_socio_g and not df_liquidez.empty:
                    if 'emp_ci_clean' not in df_liquidez.columns:
                        df_liquidez['emp_ci_clean'] = df_liquidez['emp_ci'].astype(str).apply(limpiar_ci)
                    match_liq = df_liquidez[df_liquidez['emp_ci_clean'] == ci_socio_g]
                    if not match_liq.empty:
                        matches_g = match_liq

        else:
            nom_girador = st.text_input("Ingresá el Nombre o Apellido:", placeholder="Ej: Sanabria").strip()
            if nom_girador:
                if not df_liquidez.empty:
                    matches_g = df_liquidez[df_liquidez['emp_nomape'].astype(str).str.contains(nom_girador, case=False, na=False)]
                if matches_g.empty and not df_giradurias.empty:
                    matches_g = df_giradurias[df_giradurias['emp_nomape'].astype(str).str.contains(nom_girador, case=False, na=False)]

        if not matches_g.empty:
            if len(matches_g) > 1:
                st.warning(f"Se encontraron {len(matches_g)} coincidencias:")
                opciones_g = [f"{row['emp_nomape']} (C.I.: {row.get('emp_ci', '-')})" for idx, row in matches_g.iterrows()]
                seleccion_g = st.selectbox("Seleccionar Registro:", opciones_g)
                idx_g = opciones_g.index(seleccion_g)
                row_g = matches_g.iloc[idx_g]
            else:
                row_g = matches_g.iloc[0]

            nombre_g = row_g.get('emp_nomape', 'S/N')
            ci_g = limpiar_ci(row_g.get('emp_ci', '0'))
            unidad_g = row_g.get('UNIDAD', row_g.get('unidad_nombre_oficial', '-'))
            
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
                st.text_input("Unidad Militar / Giraduría:", value=unidad_g, disabled=True)
            with col_g2:
                st.text_input("Cédula N°:", value=ci_g, disabled=True)
                st.text_input("Límite de Cuota Máxima (50%):", value=f"Gs. {formato_guarani(limite_50_g)}", disabled=True)

            st.markdown("---")
            dict_previo = df_dictamenes[df_dictamenes['CEDULA'].astype(str).apply(limpiar_ci) == ci_g]
            obs_inicial = dict_previo.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_previo.empty else "Sin dictamen registrado."

            if es_editor:
                st.info("✍️ **Modo Edición Habilitado:** Podés agregar o modificar la observación del Girador.")
                with st.form("form_dictamen"):
                    cuota_evaluando = st.number_input("Monto de Cuota Solicitada (Gs.):", min_value=0.0, step=50000.0, format="%.0f")
                    obs_girador = st.text_area("Observaciones / Respuesta del Girador:", value=obs_inicial, placeholder="Ej: Compra de deuda aprobada / Consultar disponibilidad con CF2")
                    
                    btn_guardar_dictamen = st.form_submit_button("💾 Guardar Dictamen")

                    if btn_guardar_dictamen:
                        if not obs_girador.strip():
                            st.error("Por favor ingresá una observación para guardar el dictamen.")
                        else:
                            df_dictamenes = df_dictamenes[df_dictamenes['CEDULA'].astype(str).apply(limpiar_ci) != ci_g]
                            fecha_dictamen = obtener_fecha_hora_local().strftime("%d/%m/%Y %H:%M")
                            nuevo_dictamen = pd.DataFrame([{
                                'CEDULA': ci_g,
                                'CUOTA_PROPUESTA': formato_guarani(cuota_evaluando),
                                'DICTAMEN_GIRADOR': obs_girador.strip(),
                                'FECHA': fecha_dictamen
                            }])
                            df_dictamenes = pd.concat([df_dictamenes, nuevo_dictamen], ignore_index=True)
                            guardar_dictamenes(df_dictamenes)
                            st.success("✅ ¡Dictamen guardado con éxito!")
                            st.rerun()
            else:
                st.warning("🔒 **Modo Lectura:** Tu usuario tiene acceso para consultar el dictamen pero no para editarlo.")
                st.text_area("Observación / Dictamen de Giraduría Registrado:", value=obs_inicial, disabled=True, height=120)
                cuota_evaluando = 0.0

            st.markdown("---")
            pdf_bytes_g = generar_pdf_constancia("Dictamen de Giraduría", nombre_g, ci_g, unidad_g, presupuestado_g, jubilacion_g, tot_desc_g, liquido_real_g, limite_50_g, cuota_evaluando, "EVALUADO POR GIRADOR", obs_inicial)
            
            st.download_button(
                label="📄 Descargar / Imprimir Dictamen de Giraduría (PDF)",
                data=pdf_bytes_g,
                file_name=f"Dictamen_Giraduria_{ci_g}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ==========================================
# 🛡️ MÓDULO 5: AUDITORÍA Y NOTA DE HACIENDA (RESTRINGIDO)
# ==========================================
elif opcion == "🛡️ Auditoría y Cruce de Planillas":
    st.subheader("🛡️ Sistema de Auditoría y Cruce de Planillas (Hacienda)")
    
    if not es_auditor_hacienda:
        st.error("🔒 **Acceso denegado:** Este módulo es exclusivo para los usuarios autorizados (`Arthuro` y `Martín`).")
    else:
        tab1, tab2 = st.tabs(["🔍 Ejecutar Cruce y Auditoría", "✉️ Generar Nota Oficial (MEF)"])

        with tab1:
            st.markdown("Subí las planillas en formato **Excel (.xlsx / .xls)** o **CSV (.csv)**.")

            col1, col2 = st.columns(2)
            with col1:
                files_anteriores = st.file_uploader(
                    "📥 Planilla(s) Mes Anterior (Referencia - Podés subir 1 o más archivos)", 
                    type=["xlsx", "xls", "csv"], 
                    accept_multiple_files=True
                )
            with col2:
                file_actual = st.file_uploader(
                    "📥 Planilla Mes Actual (A Auditar)", 
                    type=["xlsx", "xls", "csv"]
                )

            if files_anteriores and file_actual:
                if st.button("🚀 Ejecutar Cruce y Auditoría de Planillas", use_container_width=True):
                    try:
                        dfs_ref_list = []
                        for f in files_anteriores:
                            df_temp_raw = cargar_archivo_universal(f)
                            df_temp = mapear_y_desduplicar_columnas_auditoria(df_temp_raw)
                            dfs_ref_list.append(df_temp)
                        
                        df_prev = pd.concat(dfs_ref_list, ignore_index=True)
                        
                        df_curr_raw = cargar_archivo_universal(file_actual)
                        df_curr = mapear_y_desduplicar_columnas_auditoria(df_curr_raw)

                        req_cols = ['cedula', 'operacion', 'fecha_deuda']
                        missing_prev = [c for c in req_cols if c not in df_prev.columns]
                        missing_curr = [c for c in req_cols if c not in df_curr.columns]

                        if missing_prev or missing_curr:
                            st.error("No se pudieron identificar las columnas requeridas ('Cédula', 'Número de la Operación', 'Fecha de la Deuda') en uno o varios de los archivos.")
                        else:
                            ref_operaciones = {}
                            for idx, row in df_prev.iterrows():
                                c_val = limpiar_texto(row.get('cedula'))
                                o_val = limpiar_texto(row.get('operacion'))
                                f_val = limpiar_texto(row.get('fecha_deuda'))
                                m_val = limpiar_monto(row.get('monto_desconto', 0))
                                if c_val and o_val:
                                    key = f"{c_val}_{o_val}"
                                    ref_operaciones[key] = {
                                        'str': f_val,
                                        'dt': parsear_fecha(f_val),
                                        'monto': m_val,
                                        'row_full': row
                                    }

                            errores = []
                            nuevos_registros = []

                            for idx, row in df_curr.iterrows():
                                cedula = limpiar_texto(row.get('cedula', ''))
                                nombre = limpiar_texto(row.get('nombre', 'S/D'))
                                concepto = limpiar_texto(row.get('concepto', ''))
                                operacion = limpiar_texto(row.get('operacion', ''))
                                fecha_deuda_str = limpiar_texto(row.get('fecha_deuda', ''))
                                num_cuota_str = limpiar_texto(row.get('num_cuota', ''))
                                tot_cuota_str = limpiar_texto(row.get('total_cuota', ''))
                                monto_desc = limpiar_monto(row.get('monto_desconto', 0))
                                saldo_deuda = limpiar_monto(row.get('saldo_deuda', 0))
                                fecha_comp_str = limpiar_texto(row.get('fecha_comprobante', ''))

                                if not cedula or not operacion:
                                    continue

                                key_op = f"{cedula}_{operacion}"
                                es_nuevo = key_op not in ref_operaciones

                                dt_deuda = parsear_fecha(fecha_deuda_str)
                                dt_comp = parsear_fecha(fecha_comp_str)

                                if es_nuevo:
                                    nuevos_registros.append({
                                        'Cédula Beneficiario': cedula,
                                        'Nombre y Apellido': nombre,
                                        'Concepto': concepto,
                                        'N° Operación': operacion,
                                        'Fecha Deuda': fecha_deuda_str,
                                        'Cuota Actual': num_cuota_str,
                                        'Total Cuota': tot_cuota_str,
                                        'Monto Descuento': monto_desc,
                                        'Saldo Deuda': saldo_deuda,
                                        'Fecha Comprobante Anterior': fecha_comp_str
                                    })

                                if not es_nuevo:
                                    ref_info = ref_operaciones[key_op]
                                    fecha_ref_str = ref_info['str']
                                    dt_ref = ref_info['dt']
                                    monto_ref = ref_info['monto']

                                    if dt_deuda is not None and dt_ref is not None:
                                        difiere_fecha = (dt_deuda != dt_ref)
                                    else:
                                        difiere_fecha = (fecha_deuda_str != fecha_ref_str)

                                    if difiere_fecha:
                                        errores.append({
                                            'Cédula Beneficiario': cedula,
                                            'Nombre y Apellido': nombre,
                                            'N° Operación': operacion,
                                            'Concepto': concepto,
                                            'Tipo de Inconsistencia': 'Fecha de la deuda no coincide con lo informado previamente',
                                            'Dato Mes Actual': fecha_deuda_str,
                                            'Dato Correcto (Mes Anterior)': fecha_ref_str
                                        })

                                    if monto_desc > monto_ref:
                                        errores.append({
                                            'Cédula Beneficiario': cedula,
                                            'Nombre y Apellido': nombre,
                                            'N° Operación': operacion,
                                            'Concepto': concepto,
                                            'Tipo de Inconsistencia': 'Monto a descontar aumentó respecto al mes anterior (Monto Actual > Anterior)',
                                            'Dato Mes Actual': f"Gs. {formato_guarani(monto_desc)}",
                                            'Dato Correcto (Mes Anterior)': f"Gs. {formato_guarani(monto_ref)}"
                                        })

                                if dt_deuda is not None and dt_comp is not None and dt_comp < dt_deuda:
                                    errores.append({
                                        'Cédula Beneficiario': cedula,
                                        'Nombre y Apellido': nombre,
                                        'N° Operación': operacion,
                                        'Concepto': concepto,
                                        'Tipo de Inconsistencia': 'Fecha comprobante anterior es inferior a la fecha de la deuda',
                                        'Dato Mes Actual': f"Comprobante: {fecha_comp_str}",
                                        'Dato Correcto (Mes Anterior)': f"Fecha Deuda: {fecha_deuda_str}"
                                    })

                                if num_cuota_str.isdigit() and tot_cuota_str.isdigit() and int(num_cuota_str) == int(tot_cuota_str):
                                    if abs(monto_desc - saldo_deuda) > 1.0:
                                        errores.append({
                                            'Cédula Beneficiario': cedula,
                                            'Nombre y Apellido': nombre,
                                            'N° Operación': operacion,
                                            'Concepto': concepto,
                                            'Tipo de Inconsistencia': 'Monto a descontar en última cuota difiere del saldo pendiente',
                                            'Dato Mes Actual': f"Monto Descuento: Gs. {formato_guarani(monto_desc)}",
                                            'Dato Correcto (Mes Anterior)': f"Saldo Pendiente: Gs. {formato_guarani(saldo_deuda)}"
                                        })

                            df_errores = pd.DataFrame(errores)
                            df_nuevos = pd.DataFrame(nuevos_registros)

                            st.markdown("---")
                            c1, c2 = st.columns(2)

                            with c1:
                                st.subheader("🔴 Inconsistencias / Alertas Encontradas")
                                if df_errores.empty:
                                    st.success("✅ ¡Sin errores detectados! La planilla está limpia.")
                                    
                                    df_curr['monto_num'] = df_curr['monto_desconto'].apply(limpiar_monto)
                                    if 'beneficiario' not in df_curr.columns:
                                        df_curr['beneficiario'] = df_curr.get('cedula', '')

                                    df_agg = df_curr.groupby(['beneficiario', 'cedula'], as_index=False)['monto_num'].sum()
                                    df_agg.rename(columns={'monto_num': 'monto_total'}, inplace=True)

                                    st.session_state['auditoria_ejecutada_limpia'] = True
                                    st.session_state['total_monto_auditoria'] = float(df_agg['monto_total'].sum())
                                    st.session_state['total_beneficiarios_auditoria'] = int(len(df_agg))

                                    txt_lines = []
                                    for _, row_a in df_agg.iterrows():
                                        b_str = str(row_a['beneficiario']).strip()
                                        c_str = str(row_a['cedula']).strip()
                                        m_str = str(int(round(row_a['monto_total']))).strip()
                                        linea_fmt = f"{b_str:<14}{c_str:<10}{m_str:>7}"
                                        txt_lines.append(linea_fmt)
                                    
                                    txt_content = "\n".join(txt_lines)

                                    st.markdown("#### 📄 Descarga de Archivos Oficiales:")

                                    col_d1, col_d2 = st.columns(2)
                                    with col_d1:
                                        st.download_button(
                                            label="📥 Descargar Consolidado (.TXT Oficial)",
                                            data=txt_content.encode('latin1'),
                                            file_name="COD_96_COOP_24_DE_OCTUBRE.TXT",
                                            mime="text/plain",
                                            use_container_width=True
                                        )

                                else:
                                    st.session_state['auditoria_ejecutada_limpia'] = False
                                    st.session_state['total_monto_auditoria'] = 0.0
                                    st.session_state['total_beneficiarios_auditoria'] = 0

                                    st.warning(f"Se encontraron {len(df_errores)} alertas/errores.")
                                    st.dataframe(df_errores, use_container_width=True)

                                    out_e = io.BytesIO()
                                    with pd.ExcelWriter(out_e, engine='openpyxl') as writer:
                                        df_errores.to_excel(writer, sheet_name='Errores', index=False)
                                    st.download_button(
                                        label="📥 Descargar Excel de Inconsistencias (.xlsx)",
                                        data=out_e.getvalue(),
                                        file_name="Reporte_Inconsistencias_Hacienda.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )

                            with c2:
                                st.subheader("🟢 Nuevos Registros / Operaciones")
                                if df_nuevos.empty:
                                    st.info("No hay nuevas operaciones registradas.")
                                else:
                                    st.success(f"Se encontraron {len(df_nuevos)} nuevos registros.")
                                    st.dataframe(df_nuevos, use_container_width=True)

                                    out_n = io.BytesIO()
                                    with pd.ExcelWriter(out_n, engine='openpyxl') as writer:
                                        df_nuevos.to_excel(writer, sheet_name='Nuevos_Registros', index=False)
                                    st.download_button(
                                        label="📥 Descargar Excel de Nuevos Registros (.xlsx)",
                                        data=out_n.getvalue(),
                                        file_name="Reporte_Nuevos_Registros_Hacienda.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )

                    except Exception as e:
                        st.error(f"Error al procesar las planillas: {e}")

        with tab2:
            st.subheader("✉️ Generador de Nota Oficial para Hacienda (MEF)")
            
            if not st.session_state.get('auditoria_ejecutada_limpia', False):
                st.warning("⚠️ **Nota Oficial Bloqueada:** Aún no se ha ejecutado el cruce de planillas o se detectaron errores en la auditoría.")
                st.info("📌 **Requisito:** Ejecutá primero la auditoría en la pestaña anterior con planillas 100% limpias (cero errores) para habilitar la generación de la Nota en PDF.")
                m_tot = 0.0
                c_ben = 0
            else:
                st.success("✅ **Auditoría Limpia Verificada:** Podés ajustar la fecha y los anexos para descargar la Nota Oficial.")
                m_tot = st.session_state.get('total_monto_auditoria', 0.0)
                c_ben = st.session_state.get('total_beneficiarios_auditoria', 0)

            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                now_loc = obtener_fecha_hora_local()
                fecha_nota_input = st.text_input("Fecha de Presentación:", value=f"{now_loc.day:02d} de {now_loc.strftime('%B').capitalize()} de {now_loc.year}")
            with col_f2:
                mes_eval_input = st.text_input("Mes Evaluado:", value="septiembre")
            with col_f3:
                anio_eval_input = st.text_input("Año Evaluado:", value=str(now_loc.year))

            st.markdown("---")
            st.markdown("#### 📋 Marque las casillas que corresponden a los anexos presentados:")

            c_chk1, c_chk2 = st.columns(2)
            with c_chk1:
                chk_1 = st.checkbox("1- Planilla de Descuentos (Obligatorio: Archivo .txt)", value=False)
                chk_2 = st.checkbox("2- Nómina de Nuevos Asociados (Archivo TXT y cédulas en PDF)", value=False)
                chk_3 = st.checkbox("3- Planilla de Nuevas Autorizaciones (Archivo CSV)", value=False)
            with c_chk2:
                chk_4 = st.checkbox("4- Planilla de Bajas por Fallecimiento (Anexo PDF)", value=False)
                chk_5 = st.checkbox("5- Planilla de Información (Obligatorio: Archivo TXT/CSV)", value=False)

            st.markdown("---")
            st.write(f"📊 **Totales calculados para la Nota:** Monto Gs. `{formato_guarani(m_tot)}` | Beneficiarios: `{c_ben}`")

# ==========================================
# 🧮 MÓDULO 6: CALCULADORA FINANCIERA DE PRÉSTAMOS
# ==========================================
elif opcion == "🧮 Calculadora de Préstamos":
    st.subheader("🧮 Calculadora Financiera y Simulador de Préstamos")
    
    st.markdown("### 👤 Datos y Cruce del Socio Solicitante")
    
    socio_input = st.text_input("🔍 Ingrese Número de Socio o Cédula (C.I.):", placeholder="Ej: 9946 o 5955048").strip()
    socio_input_clean = limpiar_ci(socio_input)

    socio_encontrado = False
    nombre_socio = "No asignado / Cliente General"
    ci_socio = "S/D"
    ultimo_descuento_cobrado = 0.0
    unidad_giraduria_socio = "Sin Giraduría"
    unidad_liquidez_socio = "Sin Liquidez"
    margen_libre_liquidez = 0.0

    if socio_input:
        if not df_giradurias.empty:
            match_g = pd.DataFrame()
            if 'emp_ci_clean' in df_giradurias.columns:
                match_g = df_giradurias[df_giradurias['emp_ci_clean'] == socio_input_clean]
            if match_g.empty and 'nro_socio' in df_giradurias.columns:
                match_g = df_giradurias[df_giradurias['nro_socio'].astype(str).str.strip() == socio_input.strip()]
            
            if not match_g.empty:
                r_g = match_g.iloc[0]
                socio_encontrado = True
                nombre_socio = limpiar_texto(r_g.get('emp_nomape', 'S/D'))
                ci_socio = limpiar_ci(r_g.get('emp_ci', '0'))
                ultimo_descuento_cobrado = limpiar_monto(r_g.get('monto_cobrado', 0))
                unidad_giraduria_socio = limpiar_texto(r_g.get('unidad_nombre_oficial', 'Sin Asignar'))

        if not df_liquidez.empty and (ci_socio != "S/D" or socio_input_clean):
            search_ci = ci_socio if ci_socio != "S/D" else socio_input_clean
            col_l = 'emp_ci_clean' if 'emp_ci_clean' in df_liquidez.columns else 'emp_ci'
            match_l = df_liquidez[df_liquidez[col_l].astype(str).apply(limpiar_ci) == search_ci]
            
            if not match_l.empty:
                r_l = match_l.iloc[0]
                if not socio_encontrado:
                    nombre_socio = limpiar_texto(r_l.get('emp_nomape', 'S/D'))
                    ci_socio = search_ci
                    socio_encontrado = True
                unidad_liquidez_socio = limpiar_texto(r_l.get('UNIDAD', 'Sin Liquidez'))
                
                presup = limpiar_monto(r_l.get('presupuestado', 0))
                jub = limpiar_monto(r_l.get('jubilacion', 0))
                tot_d = jub + limpiar_monto(r_l.get('giraduria', 0)) + limpiar_monto(r_l.get('descuento_cf2', 0)) + limpiar_monto(r_l.get('judicial', 0))
                margen_libre_liquidez = ((presup - jub) / 2.0) - (tot_d - jub)

    if socio_encontrado:
        st.success(f"👤 **Socio:** {nombre_socio} | **C.I.:** {ci_socio}")
        c_s1, c_s2, c_s3, c_s4 = st.columns(4)
        c_s1.metric("Último Descuento Cobrado", f"Gs. {formato_guarani(ultimo_descuento_cobrado)}")
        c_s2.metric("Giraduría Registrada", unidad_giraduria_socio)
        c_s3.metric("Unidad Oficial (Liquidez)", unidad_liquidez_socio)
        c_s4.metric("Margen Libre (50%)", f"Gs. {formato_guarani(margen_libre_liquidez)}")
    else:
        if socio_input:
            st.warning("⚠️ No se encontraron registros coincidentes para ese Número de Socio o Cédula.")
        else:
            st.info("💡 Ingresá el N° de Socio arriba para cruzar automáticamente sus descuentos y margen de liquidez.")

    st.markdown("---")

    tipos_prestamo = {
        '1': {'nombre': 'Préstamo Ordinario', 'comision': 0},
        '19': {'nombre': 'Préstamo Cumpleaños', 'comision': 0},
        '9': {'nombre': 'Consumo Electrodoméstico', 'comision': '5%'},
        '71': {'nombre': 'Refinanciación Especial', 'comision': 100000},
        '21': {'nombre': 'Consumo Celular', 'comision': '5%'},
        '8': {'nombre': 'Premium', 'comision': 0},
        '65': {'nombre': 'Crédito Aniversario', 'comision': 0}, 
        '18': {'nombre': 'Credito Amigo', 'comision': 0},
        '78': {'nombre': 'Crédito Vehículo', 'comision': '2%'}, 
        '33': {'nombre': 'Prestamo Jubilados', 'comision': 0}
    }

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        monto_input_raw = st.text_input("Monto Capital (Gs.):", value="0", placeholder="Ej: 2.000.000")
        monto_capital = limpiar_monto(monto_input_raw)
        
        if monto_capital > 0:
            st.caption(f"💵 **Monto ingresado:** Gs. {formato_guarani(monto_capital)}")

        plazo = st.number_input("Plazo (meses):", min_value=1, value=12, step=1)
        
        codigo_p = st.selectbox(
            "Código / Tipo de Préstamo:", 
            options=list(tipos_prestamo.keys()),
            format_func=lambda x: f"Código {x}: {tipos_prestamo[x]['nombre']}"
        )
        nombre_p = tipos_prestamo[codigo_p]['nombre']

        es_refinanciacion_natura = (codigo_p == '71' or 'REFINANCIACI' in nombre_p.upper())
        
        if not es_refinanciacion_natura:
            modalidad_credito = st.radio(
                "📌 Modalidad de Crédito:", 
                ["🔄 Con Cancelación / Refinanciación", "➕ Crédito Paralelo"], 
                horizontal=True
            )
        else:
            modalidad_credito = "🔄 Con Cancelación / Refinanciación"
            st.info("ℹ️ Este tipo de crédito opera automáticamente como **Refinanciación / Cancelación**.")

        tasa_auto = 20.0
        if nombre_p == 'Préstamo Ordinario':
            tasa_auto = 26.0
        elif nombre_p == 'Premium':
            tasa_auto = 24.0
        elif nombre_p in ['Préstamo Cumpleaños', 'Consumo Electrodoméstico', 'Consumo Celular', 'Credito Amigo']:
            tasa_auto = 20.0
        elif nombre_p == 'Crédito Aniversario':
            if 1 <= plazo <= 12: tasa_auto = 9.0
            elif 13 <= plazo <= 18: tasa_auto = 12.0
            elif 19 <= plazo <= 24: tasa_auto = 14.0
            elif 25 <= plazo <= 36: tasa_auto = 16.0
        elif nombre_p == 'Crédito Vehículo':
            tasa_auto = 18.0 if 0 < plazo <= 48 else 20.0
        elif nombre_p == 'Refinanciación Especial':
            tasa_auto = 18.0

        tasa_interes = st.number_input("Tasa de Interés Anual (%):", value=tasa_auto, step=0.5)

    with col_c2:
        gastos_admin = st.number_input("Gastos Administrativos (%):", value=2.5, step=0.1)
        fondo_proteccion = st.number_input("Fondo de Protección (%):", value=1.0, step=0.1)

        com_def = tipos_prestamo[codigo_p]['comision']
        if isinstance(com_def, (int, float)):
            comision_val = float(com_def)
        elif isinstance(com_def, str) and com_def.endswith('%'):
            pct = float(com_def.replace('%', '')) / 100.0
            comision_val = monto_capital * pct
        else:
            comision_val = 0.0

        st.text_input("Comisión (Gs.):", value=f"Gs. {formato_guarani(comision_val)}", disabled=True)

        fecha_hoy = obtener_fecha_hora_local().date()
        fecha_desembolso = st.date_input("Fecha Desembolso:", value=fecha_hoy)

        fecha_primer_venc_default = obtener_ultimo_dia_mes_siguiente(fecha_desembolso)
        fecha_primer_venc = st.date_input("Fecha 1er Vencimiento:", value=fecha_primer_venc_default)

    if st.button("🚀 Calcular Plan de Pagos y Evaluar Crédito", use_container_width=True):
        if monto_capital <= 0:
            st.error("Por favor ingresá un Monto Capital mayor a 0 para calcular el plan de pagos.")
        else:
            capital_con_gastos = monto_capital + (monto_capital * (gastos_admin / 100.0)) + (monto_capital * (fondo_proteccion / 100.0)) + comision_val
            diff_days = (fecha_primer_venc - fecha_desembolso).days
            
            plus = 0.0
            if diff_days > 30:
                plus = (capital_con_gastos * (tasa_interes / 100.0) / 365.0) * (diff_days - 30)

            tasa_mensual = (tasa_interes / 100.0) / 12.0

            if tasa_mensual > 0:
                cuota = capital_con_gastos * (tasa_mensual * ((1 + tasa_mensual) ** plazo)) / (((1 + tasa_mensual) ** plazo) - 1)
            else:
                cuota = capital_con_gastos / plazo

            st.markdown("---")
            st.subheader("🎯 Resultado de la Evaluación Automática")

            es_con_cancelacion = "Con Cancelación" in modalidad_credito

            # EVALUACIÓN CON REGLA MÍNIMA DE GS. 100.000
            if es_con_cancelacion and cuota <= ultimo_descuento_cobrado and ultimo_descuento_cobrado >= 100000:
                st.success(
                    f"✅ **CRÉDITO APROBADO (REFINANCIACIÓN / CANCELACIÓN FACTIBLE)**\n\n"
                    f"La cuota calculada (**Gs. {formato_guarani(cuota)}**) es menor o igual al último descuento del socio (**Gs. {formato_guarani(ultimo_descuento_cobrado)}**)."
                )
            elif cuota <= margen_libre_liquidez and margen_libre_liquidez >= 100000:
                st.success(
                    f"✅ **CRÉDITO APROBADO (DENTRO DEL MARGEN LIBRE DE LIQUIDEZ)**\n\n"
                    f"La cuota de **Gs. {formato_guarani(cuota)}** entra cómodamente en el margen libre de liquidez de las FF.AA. (**Gs. {formato_guarani(margen_libre_liquidez)}**)."
                )
            elif ultimo_descuento_cobrado < 100000 and margen_libre_liquidez < 100000:
                st.error(
                    f"🔴 **REFINANCIACIÓN NO FACTIBLE (MARGEN INSUFICIENTE < Gs. 100.000)**\n\n"
                    f"El monto máximo disponible (**Gs. {formato_guarani(max(ultimo_descuento_cobrado, margen_libre_liquidez))}**) es inferior al mínimo operativo requerido.\n"
                    f"📌 **Recomendación:** No es viablemente factible reestructurar. En caso de mora, proceder con notificación formal."
                )
            else:
                unidad_destino = unidad_liquidez_socio if unidad_liquidez_socio not in ["Sin Liquidez", ""] else "CF2"
                st.error(
                    f"⚠️ **ANALIZAR / CONSULTAR CON UNIDAD: {unidad_destino}**\n\n"
                    f"La cuota calculada (**Gs. {formato_guarani(cuota)}**) supera tanto el último descuento (**Gs. {formato_guarani(ultimo_descuento_cobrado)}**) "
                    f"como el margen libre de liquidez (**Gs. {formato_guarani(margen_libre_liquidez)}**)."
                )

            plan_pagos = []
            saldo_restante = capital_con_gastos
            total_pagar = 0.0

            intereses_1 = saldo_restante * tasa_mensual
            amort_1 = cuota - intereses_1
            cuota_final_1 = cuota + plus
            saldo_restante -= amort_1
            total_pagar += cuota_final_1

            plan_pagos.append({
                'Nro. Cuota': 1,
                'Fecha Vencimiento': fecha_primer_venc.strftime('%d/%m/%Y'),
                'Cuota (Gs.)': formato_guarani(cuota_final_1),
                'Amortización': formato_guarani(amort_1),
                'Intereses': formato_guarani(intereses_1),
                'Plus (Gs.)': formato_guarani(plus),
                'Saldo (Gs.)': formato_guarani(saldo_restante),
                'Ahorro (Gs.)': '0'
            })

            curr_venc = fecha_primer_venc
            for i in range(2, plazo + 1):
                next_m = curr_venc.month + 1
                next_y = curr_venc.year
                if next_m > 12:
                    next_m = 1
                    next_y += 1
                
                max_d = calendar.monthrange(next_y, next_m)[1]
                day = min(curr_venc.day, max_d)
                curr_venc = datetime(next_y, next_m, day).date()

                intereses = saldo_restante * tasa_mensual
                amort = cuota - intereses
                saldo_restante -= amort
                cuota_final = cuota

                if i == plazo:
                    if saldo_restante < 0:
                        amort += saldo_restante
                        cuota_final = amort + intereses
                    saldo_restante = 0.0

                total_pagar += cuota_final

                plan_pagos.append({
                    'Nro. Cuota': i,
                    'Fecha Vencimiento': curr_venc.strftime('%d/%m/%Y'),
                    'Cuota (Gs.)': formato_guarani(cuota_final),
                    'Amortización': formato_guarani(amort),
                    'Intereses': formato_guarani(intereses),
                    'Plus (Gs.)': '0',
                    'Saldo (Gs.)': formato_guarani(saldo_restante),
                    'Ahorro (Gs.)': '0'
                })

            df_plan = pd.DataFrame(plan_pagos)

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Capital con Gastos", f"Gs. {formato_guarani(capital_con_gastos)}")
            m2.metric("Plus Primera Cuota", f"Gs. {formato_guarani(plus)}")
            m3.metric("Total a Pagar", f"Gs. {formato_guarani(total_pagar)}")

            st.subheader("📋 Tabla Amortización de Pagos")
            st.dataframe(df_plan, use_container_width=True)

            col_down1, col_down2 = st.columns(2)

            with col_down1:
                out_plan = io.BytesIO()
                with pd.ExcelWriter(out_plan, engine='openpyxl') as writer:
                    df_plan.to_excel(writer, sheet_name='Simulacion_Prestamo', index=False)
                
                st.download_button(
                    label="📥 Descargar Simulación de Préstamo (.XLSX)",
                    data=out_plan.getvalue(),
                    file_name=f"Simulacion_Prestamo_{int(monto_capital)}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col_down2:
                pdf_sim_bytes = generar_pdf_simulacion_prestamo(
                    nombre_socio,
                    ci_socio,
                    f"Código {codigo_p} - {nombre_p}",
                    monto_capital,
                    plazo,
                    tasa_interes,
                    capital_con_gastos,
                    plus,
                    total_pagar,
                    df_plan
                )

                st.download_button(
                    label="📄 Descargar Simulación de Préstamo (.PDF)",
                    data=pdf_sim_bytes,
                    file_name=f"Simulacion_Prestamo_{ci_socio}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# ==========================================
# 📥 MÓDULO 7: CARGAR BASE MENSUAL (ADMIN)
# ==========================================
elif opcion == "📥 Cargar Base Mensual":
    st.subheader("📥 Administración y Carga de Bases Mensuales")
    
    if not es_admin_base:
        st.error("🔒 **Acceso denegado:** Este módulo es reservado únicamente para el usuario Administrador (`Arthuro`).")
    else:
        st.success("🔑 **Permisos de Administrador Verificados:** Podés subir o actualizar las bases de datos permanentes.")
        
        tab_b1, tab_b2, tab_b3, tab_b4 = st.tabs([
            "🪖 Base de Liquidez (FF.AA.)", 
            "🏛️ Base Enviado / Cobrado (Giradurías)", 
            "📱 Base Giradurías Teléfonos",
            "🔑 Credenciales de Usuarios"
        ])

        with tab_b1:
            st.markdown("#### 1. Planilla de Liquidez Militar (FF.AA.)")
            st.caption("Esta base reemplaza el archivo `base_liquidez_militares.csv` permanentemente.")
            
            if not df_liquidez.empty:
                st.info(f"📊 **Estado actual:** {len(df_liquidez):,} registros cargados.")
            else:
                st.warning("⚠️ Sin datos cargados actualmente.")

            archivo_l = st.file_uploader("Seleccioná la planilla de Liquidez (.xlsx / .xls / .csv)", type=["xlsx", "xls", "csv"], key="u_liquidez")
            
            if archivo_l:
                if st.button("⚠️ Procesar e Importar Base de Liquidez", use_container_width=True):
                    try:
                        ext = archivo_l.name.lower().split('.')[-1]
                        if ext == 'csv':
                            df_cargado = pd.read_csv(archivo_l, dtype=str)
                        else:
                            df_cargado = pd.read_excel(archivo_l, dtype=str)

                        df_normalizado = estandarizar_columnas_ffaa(df_cargado)

                        if df_normalizado.empty:
                            st.warning("No se encontraron datos procesables en el archivo.")
                        else:
                            guardar_liquidez(df_normalizado)
                            st.success(f"✅ ¡Base de liquidez importada y guardada permanentemente! Total militares: {len(df_normalizado):,}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al procesar la planilla: {e}")

        with tab_b2:
            st.markdown("#### 2. Base Enviado / Cobrado Giradurías")
            st.caption("Esta base procesa automáticamente planillas de hoja única consolidada o múltiples pestañas indicando la etiqueta del período.")
            
            col_tag1, col_tag2 = st.columns(2)
            with col_tag1:
                mes_tag = st.selectbox("Seleccionar Mes del Período:", ["Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"])
            with col_tag2:
                anio_tag = st.selectbox("Seleccionar Año del Período:", ["2026", "2025", "2027"])

            periodo_etiqueta = f"{mes_tag} {anio_tag}"

            if not df_giradurias.empty:
                st.info(f"📊 **Estado actual:** {len(df_giradurias):,} registros en base actual.")
            else:
                st.warning("⚠️ Sin datos de giradurías cargados actualmente.")

            archivo_g = st.file_uploader("📥 Cargar Base Enviado / Cobrado Giradurías (.xlsx / .xls)", type=["xlsx", "xls"], key="u_giradurias")
            
            if archivo_g:
                if st.button(f"⚠️ Procesar e Importar Base para {periodo_etiqueta}", use_container_width=True):
                    try:
                        df_norm_g = unificar_hojas_excel(archivo_g, periodo_tag=periodo_etiqueta)

                        if df_norm_g.empty:
                            st.warning("No se encontraron datos procesables en la planilla de giradurías.")
                        else:
                            guardar_giradurias(df_norm_g)
                            guardar_historial_giradurias(df_norm_g, periodo_tag=periodo_etiqueta)
                            st.success(f"✅ ¡Se unificaron e importaron los datos para {periodo_etiqueta}! Total registros: {len(df_norm_g):,}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al procesar la planilla de giradurías: {e}")

        with tab_b3:
            st.markdown("#### 3. Base Giradurías Teléfonos")
            st.caption("Subí la planilla `Giraduria con numero de telefono.xlsx` para actualizar la guía de contactos de socios.")
            archivo_t = st.file_uploader("📥 Cargar Base de Teléfonos (.xlsx)", type=["xlsx", "xls"], key="u_tel")
            if archivo_t:
                if st.button("⚠️ Guardar y Actualizar Base de Teléfonos", use_container_width=True):
                    try:
                        guardar_telefonos_excel(archivo_t)
                        st.success("✅ ¡Base de teléfonos cargada y lista para su uso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar la base de teléfonos: {e}")

        with tab_b4:
            st.markdown("#### 4. Consulta de Credenciales de Usuarios (Exclusivo Admin)")
            st.caption("Listado de usuarios registrados en el sistema y sus contraseñas asignadas para respuesta rápida por soporte/WhatsApp.")
            
            data_credenciales = []
            for usr, pwd in USUARIOS_AUTORIZADOS.items():
                if usr == "arthuro":
                    rol_txt = "⭐ Administrador General"
                elif usr in USUARIOS_AUDITORIA_HACIENDA:
                    rol_txt = "🛡️ Auditor / Evaluador"
                elif usr in USUARIOS_EDITORES_DICTAMEN:
                    rol_txt = "✍️ Editor / Evaluador"
                elif usr == "yennifer":
                    rol_txt = "🔍 Operador de Evaluaciones y Créditos"
                else:
                    rol_txt = "🔒 Consulta General"

                data_credenciales.append({
                    "Usuario": usr.capitalize(),
                    "Contraseña Registrada": pwd,
                    "Rol / Permisos": rol_txt
                })

            df_credenciales = pd.DataFrame(data_credenciales)
            st.table(df_credenciales)
