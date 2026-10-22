import streamlit as st
import pandas as pd
import os
import io
import re
import calendar
import urllib.parse
from datetime import datetime, timedelta
from fpdf import FPDF

Intentar ajustar la zona horaria a Paraguay (America/Asuncion)

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

==========================================

🔐 CONFIGURACIÓN DE USUARIOS Y PERMISOS

==========================================

USUARIOS_AUTORIZADOS = {
"arthuro": "19942008",
"fio": "credfio",
"agustin": "cobragus",
"estela": "giradurias",
"martin": "mllamas",
"yennifer": "280308",
"juan": "coop2024",
"milena": "coop2024"
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

==========================================

⚙️ MENÚ LATERAL, SOPORTE Y NAVEGACIÓN

==========================================

usuario_actual = st.session_state['usuario_actual'].lower()
es_editor = usuario_actual in USUARIOS_EDITORES_DICTAMEN
es_auditor_hacienda = usuario_actual in USUARIOS_AUDITORIA_HACIENDA
es_admin_base = (usuario_actual == USUARIO_ADMIN_BASE)

st.sidebar.title("🏛️ SICOC")
st.sidebar.markdown(f"👤 Usuario activo: {usuario_actual.capitalize()}")
if es_admin_base:
st.sidebar.caption("⭐ Rol: Administrador General")
elif es_auditor_hacienda:
st.sidebar.caption("🛡️ Rol: Auditor / Evaluador")
elif es_editor:
st.sidebar.caption("✍️ Rol: Editor / Evaluador")
elif usuario_actual in ["yennifer", "juan", "milena"]:
st.sidebar.caption("🔍 Rol: Operador de Evaluaciones y Créditos")
else:
st.sidebar.caption("🔒 Rol: Consulta general")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
st.session_state["autenticado"] = False
st.session_state["usuario_actual"] = ""
st.rerun()

st.sidebar.markdown("---")
if usuario_actual in ["yennifer", "juan", "milena"]:
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
st.sidebar.caption("Desarrollado por Arturo Arrua")
url_whatsapp = "https://wa.me/595983474662?text=Hola%20Arturo,%20tengo%20una%20consulta%20sobre%20el%20sistema%20SICOC"
st.sidebar.markdown(f'')

DB_LIQUIDEZ_FILE = "base_liquidez_militares.csv"
DB_GIRADURIAS_FILE = "Planilla_Descuentos_Consolidada.xlsx"
DB_HISTORIAL_GIRADURIAS_FILE = "base_historial_giradurias.csv"
DB_DICTAMENES_FILE = "dictamenes_giraduria.csv"
DB_TELEFONOS_FILE = "Giraduria con numero de telefono.xlsx"
DB_HISTORIAL_CONTACTOS_FILE = "base_historial_contactos.csv"

MAPEO_UNIDADES = {
"1": "1RA DC", "2": "2da DC", "3": "3ra Dc", "4": "Epoe", "5": "I CE",
"6": "Cimee", "7": "TEE", "8": "Ejercito", "9": "Edefisfa", "10": "Jubilados",
"12": "Eceme", "13": "Academil", "14": "FFMM", "15": "CFN5", "17": "Diserinte",
"18": "Dimabel", "20": "C. Logistico", "22": "Comisoe", "23": "CFN2", "24": "II CE",
"25": "III CE", "26": "4ta DI", "27": "5ta DI", "28": "6ta DI", "29": "2da DI",
"30": "3ra DI", "31": "Ingenieria", "32": "1ra DI",
"35": "Comcome Oficiales", "36": "Comcome Sub Oficiales", "37": "Suprema corte", "39": "Comcome Empleados",
"42": "Regimiento", "44": "Sanidad", "46": "Digetren", "50": "Esc. Caballeria",
"54": "IAEE", "62": "EIME", "70": "Batallon", "73": "CECOPAZ", "82": "Armada",
"83": "Aerea", "86": "Policia"
}

def limpiar_texto(val):
try:
if isinstance(val, (pd.Series, list)):
val = val[0] if len(val) > 0 else ""
s = str(val).strip()
return "" if s.upper() in ["NAN", "NONE", ""] else s
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
if isinstance(val, (pd.Series, list)):
val = val[0] if len(val) > 0 else 0.0
s = str(val).replace('.', '').replace(',', '.').strip()
numeros = re.findall(r'[-+]?\d*.\d+|\d+', s)
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
'nro_socio': re.sub(r'.0$', '', c1.strip()),
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
if 'CEDULA' in c_clean or 'N° DE CEDULE' in c_clean or 'CEDULA DE IDENTIDAD' in c_clean or 'C.I' in c_clean:
cols_map[c] = 'cedula'
elif 'NÚMERO DEL BENEFICIARIO' in c_clean or 'NUMERO DEL BENEFICIARIO' in c_clean:
cols_map[c] = 'beneficiario'
elif 'NOMBRES Y APELLIDOS' in c_clean or 'BENEFICIARIO' in c_clean or 'NOMBRE' in c_clean:
cols_map[c] = 'nombre'
elif 'CONCEPTO' in c_clean:
cols_map[c] = 'concepto'
elif 'OPERACION' in c_clean or 'NUMERO DE LA OPERACION' in c_clean or 'OPERACIÓN' in c_clean:
cols_map[c] = 'operacion'
elif 'FECHA DE LA DEUDA' in c_clean or 'FECHA DEUDA' in c_clean:
cols_map[c] = 'fecha_deuda'
elif 'NUMERO DE CUOTA' in c_clean or 'NRO CUOTA' in c_clean or 'CUOTA' in c_clean:
cols_map[c] = 'num_cuota'
elif 'TOTAL CUOTA' in c_clean or 'TOTAL CUOTAS' in c_clean:
cols_map[c] = 'total_cuota'
elif 'MONTO POR DESCONTARSE' in c_clean or 'DESCONTARSE' in c_clean or 'MONTO DESCUENTO' in c_clean:
cols_map[c] = 'monto_desconto'
elif 'SALDO (DEUDA)' in c_clean or 'SALDO' in c_clean or 'SALDO PENDIENTE' in c_clean:
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


@st.cache_data(ttl=2592000)
def cargar_telefonos():
if os.path.exists(DB_TELEFONOS_FILE):
try:
xls = pd.ExcelFile(DB_TELEFONOS_FILE)
records = []
for sheet in xls.sheet_names:
df_sheet = pd.read_excel(DB_TELEFONOS_FILE, sheet_name=sheet, header=None, dtype=str)
current_unit = str(sheet).strip()

            for idx, row in df_sheet.iterrows():
                col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
                col1 = str(row[1]).strip() if pd.notna(row[1]) else ""
                col2 = str(row[2]).strip() if pd.notna(row[2]) else ""
                col3 = str(row[3]).strip() if pd.notna(row[3]) else ""
                col4 = str(row[4]).strip() if pd.notna(row[4]) else ""
                if 'UNIDAD:' in col0.upper():
                    current_unit = f"{col0} {col1}".strip()
                    continue
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
pdf.cell(0, 6, f"Constancia Oficial de {limpiar_texto_pdf(tipo_reporte)}", border=0, ln=True, align="C")
pdf.ln(5)
pdf.line(10, 28, 200, 28)
pdf.ln(5)
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "1. DATOS DEL MILITAR / SOCIO", ln=True)
pdf.set_font("Helvetica", "", 10)
pdf.cell(100, 6, f"Nombre y Apellido: {limpiar_texto_pdf(nombre)}")
pdf.cell(90, 6, f"Cédula N°: {ci}", ln=True)
pdf.cell(100, 6, f"Unidad / Dependencia: {limpiar_texto_pdf(unidad)}", ln=True)
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
pdf.cell(90, 6, f"Estado de Factibilidad: {limpiar_texto_pdf(estado)}", ln=True)

if obs:
    pdf.ln(2)
    pdf.multi_cell(0, 6, f"Observación / Dictamen de Giraduría: {limpiar_texto_pdf(obs)}")
pdf.ln(15)
pdf.cell(0, 6, "_____________________________", align="C", ln=True)
pdf.cell(0, 6, "Firma / Sello de Recepción", align="C", ln=True)
return bytes(pdf.output())


df_liquidez = cargar_liquidez()
df_giradurias = cargar_giradurias()
df_historial_giradurias = cargar_historial_giradurias()
df_telefonos = cargar_telefonos()
df_dictamenes = cargar_dictamenes()

==========================================

🪖 MÓDULO 1: EVALUADOR DE LIQUIDEZ

==========================================

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
else:
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
            st.warning("💳 **Estado de Socio:** `No socio` ")
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

    dict_match = df_dictamenes[df_dictamenes['CEDULA'].astype(str).apply(limpiar_ci) == cedula_militar]
    obs_dictamen = dict_match.iloc[-1]['DICTAMEN_GIRADOR'] if not dict_match.empty else "Sin observaciones previas."
    
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


==========================================

📱 MÓDULO 2: GIRADURÍAS TELÉFONOS

==========================================

elif opcion == "📱 Giradurías Teléfonos":
st.subheader("📱 Módulo de Gestión de Contacto y Teléfonos de Socios")

if df_telefonos.empty:
    st.warning("⚠️ No se encuentra cargada la base de teléfonos (`Giraduria con numero de telefono.xlsx`). Podés subirla en 'Cargar Base Mensual'.")
else:
    st.info(f"📊 **Base de datos activa:** {len(df_telefonos):,} socios registrados consolidados.")
    
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
        
        st.markdown("---")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"### 👤 {nombre_t}")
            st.write(f"💳 **Cédula N°:** `{ci_t}` | **N° Socio:** `{socio_num_t}`")
            st.write(f"🏛️ **Unidad / Giraduría:** {unid_t}")
            st.write(f"📞 **Teléfono Registrado:** `{tel_local_t}`")
        with col_t2:
            st.markdown("### 📲 Enviar Mensaje por WhatsApp")
            plantilla_sel = st.selectbox("Seleccionar Plantilla a Enviar:", ["Plantilla 1 (Estándar)", "Mensaje Personalizado"])
            msg_text = f"Hola {nombre_t}, te saludamos del área de Giradurías. Por favor comunicate con nosotros."
            st.text_area("Vista previa del mensaje:", value=msg_text, height=100, disabled=True)
            
            if tel_wa_t:
                msg_encoded = urllib.parse.quote(msg_text)
                wa_url = f"https://wa.me/{tel_wa_t}?text={msg_encoded}"
                if st.button("📲 Abrir WhatsApp y Registrar Contacto", use_container_width=True):
                    registrar_contacto(ci_t, socio_num_t, usuario_actual, 1, msg_text)
                    st.success("✅ Contacto registrado correctamente en la bitácora.")
                    st.markdown(f'[👉 Haz Clic Aquí para Abrir el Chat de WhatsApp Directamente]({wa_url})')


==========================================

📊 MÓDULO 3: GESTIÓN DE COBRANZAS

==========================================

elif opcion == "📊 Gestión y Diagnóstico de Cobranzas":
st.subheader("📊 Módulo de Diagnóstico de Cobranzas, Estadísticas y Reportes")

if df_giradurias.empty:
    st.info("👈 Por favor cargá la `Planilla_Descuentos_Consolidada.xlsx` en 'Cargar Base Mensual' para habilitar los reportes.")
else:
    st.success(f"Base de descuentos cargada correctamente ({len(df_giradurias):,} registros).")


==========================================

📋 MÓDULO 4: DICTAMEN DEL GIRADOR

==========================================

elif opcion == "📋 Dictamen del Girador":
st.subheader("📋 Módulo de Registro de Dictamen de Giraduría")

==========================================

🛡️ MÓDULO 5: AUDITORÍA Y CRUCE DE PLANILLAS (HACIENDA/MEF)

==========================================

elif opcion == "🛡️ Auditoría y Cruce de Planillas":
st.subheader("🛡️ Sistema de Auditoría y Cruce de Planillas (Hacienda)")

if not es_auditor_hacienda:
    st.error("🔒 **Acceso denegado:** Este módulo es exclusivo para los usuarios autorizados (`Arthuro` y `Martín`).")
else:
    tab1, tab2 = st.tabs(["🔍 Ejecutar Cruce y Auditoría", "✉️ Generar Nota Oficial (MEF)"])
    
    with tab1:
        st.markdown("Subí las planillas de referencia y la actual en formato **Excel (.xlsx / .xls)** o **CSV (.csv)**.")
        col1, col2 = st.columns(2)
        with col1:
            files_anteriores = st.file_uploader(
                "📥 Planilla(s) Mes Anterior / Referencia (1 o más archivos Excel/CSV)", 
                type=["xlsx", "xls", "csv"], 
                accept_multiple_files=True
            )
        with col2:
            file_actual = st.file_uploader(
                "📥 Planilla Mes Actual (Excel o CSV)", 
                type=["xlsx", "xls", "csv"]
            )
            
        if files_anteriores and file_actual:
            if st.button("🚀 Cruce de Datos y Generar Informe de Inconsistencias", use_container_width=True):
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
                        st.error("⚠️ No se pudieron identificar automáticamente las columnas requeridas ('Cédula', 'Número de la Operación', 'Fecha de la Deuda'). Verifique los encabezados de los archivos.")
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
                                    'Monto Descuento': f"Gs. {formato_guarani(monto_desc)}",
                                    'Saldo Deuda': f"Gs. {formato_guarani(saldo_deuda)}",
                                    'Fecha Comprobante': fecha_comp_str
                                })
                            else:
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
                                        'Tipo de Inconsistencia': 'Monto a descontar aumentó respecto al mes anterior',
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
                            st.subheader("🔴 Informe de Inconsistencias Encontradas")
                            if df_errores.empty:
                                st.success("✅ ¡Sin errores detectados! La planilla coincide al 100%.")
                                
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
                                st.markdown("##### 📄 Descarga de Archivos Oficiales:")
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
                                st.warning(f"Se encontraron **{len(df_errores)}** inconsistencias/alertas.")
                                st.dataframe(df_errores, use_container_width=True)
                                
                                out_e = io.BytesIO()
                                with pd.ExcelWriter(out_e, engine='openpyxl') as writer:
                                    df_errores.to_excel(writer, sheet_name='Errores', index=False)
                                st.download_button(
                                    label="📥 Descargar Reporte de Inconsistencias (.xlsx)",
                                    data=out_e.getvalue(),
                                    file_name="Reporte_Inconsistencias_Hacienda.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                                
                        with c2:
                            st.subheader("🟢 Nuevos Registros / Operaciones")
                            if df_nuevos.empty:
                                st.info("No hay nuevas operaciones registradas en el mes actual.")
                            else:
                                st.success(f"Se encontraron **{len(df_nuevos)}** nuevos registros.")
                                st.dataframe(df_nuevos, use_container_width=True)
                                
                                out_n = io.BytesIO()
                                with pd.ExcelWriter(out_n, engine='openpyxl') as writer:
                                    df_nuevos.to_excel(writer, sheet_name='Nuevos_Registros', index=False)
                                st.download_button(
                                    label="📥 Descargar Reporte de Nuevos Registros (.xlsx)",
                                    data=out_n.getvalue(),
                                    file_name="Reporte_Nuevos_Registros_Hacienda.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                except Exception as e:
                    st.error(f"Error al procesar el cruce de planillas: {e}")

    with tab2:
        st.subheader("✉️ Generador de Nota Oficial para Hacienda (MEF)")
        
        if not st.session_state.get('auditoria_ejecutada_limpia', False):
            st.warning("⚠️ **Nota Oficial Bloqueada:** Aún no se ha ejecutado el cruce de planillas o se detectaron errores en la auditoría.")
            m_tot = 0.0
            c_ben = 0
        else:
            st.success("✅ **Auditoría Limpia Verificada:** Podés descargar la Nota Oficial.")
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


==========================================

🧮 MÓDULO 6: CALCULADORA DE PRÉSTAMOS

==========================================

elif opcion == "🧮 Calculadora de Préstamos":
st.subheader("🧮 Calculadora y Simulador de Amortizaciones")

==========================================

📥 MÓDULO 7: CARGAR BASE MENSUAL

==========================================

elif opcion == "📥 Cargar Base Mensual":
st.subheader("📥 Cargar Bases de Datos y Planillas Mensuales")

if es_admin_base:
    st.markdown("#### 🔑 Consulta de Credenciales de Usuarios (Exclusivo Admin)")
    st.caption("Listado de usuarios registrados en el sistema y sus contraseñas asignadas para respuesta rápida por soporte/WhatsApp:")
    
    data_credenciales = []
    for usr, pwd in USUARIOS_AUTORIZADOS.items():
        if usr == "arthuro":
            rol_txt = "⭐ Administrador General"
        elif usr in USUARIOS_AUDITORIA_HACIENDA:
            rol_txt = "🛡️ Auditor / Evaluador"
        elif usr in USUARIOS_EDITORES_DICTAMEN:
            rol_txt = "✍️ Editor / Evaluador"
        elif usr in ["yennifer", "juan", "milena"]:
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
