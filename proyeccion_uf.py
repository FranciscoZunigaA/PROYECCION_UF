import pandas as pd
from datetime import datetime, timedelta
import requests
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== CONFIGURACIÓN =====
ruta_onedrive = r"C:\Users\fzunigaa\OneDrive - Falabella\Escritorio\Automatizaciones\UF"
hoy = datetime.today()

# Determinar mes actual y siguiente
mes_actual = hoy.month
anio_actual = hoy.year
mes_siguiente = mes_actual + 1 if mes_actual < 12 else 1
anio_siguiente = anio_actual if mes_actual < 12 else anio_actual + 1

fecha_inicio = datetime(anio_actual, mes_actual, 9)
fecha_fin = datetime(anio_siguiente, mes_siguiente, 9)

# ===== OBTENER IPC DESDE API =====
url_ipc = "https://mindicador.cl/api/ipc"
response_ipc = requests.get(url_ipc, verify=False)
if response_ipc.status_code == 200:
    ipc_mensual = response_ipc.json()["serie"][0]["valor"]
else:
    raise Exception("Error al obtener IPC desde la API.")
print(f"IPC mensual obtenido: {ipc_mensual}%")

# ===== OBTENER UF ACTUAL DESDE API =====
url_uf = "https://mindicador.cl/api/uf"
response_uf = requests.get(url_uf, verify=False)
if response_uf.status_code == 200:
    uf_actual = response_uf.json()["serie"][0]["valor"]
else:
    raise Exception("Error al obtener UF desde la API.")
print(f"UF actual obtenida: {uf_actual}")

# ===== CÁLCULO DE PROYECCIÓN =====
ipc_decimal = ipc_mensual / 100
num_dias = (fecha_fin - fecha_inicio).days
factor_diario = (1 + ipc_decimal) ** (1 / num_dias)

# Ajuste: usar UF actual como referencia (puedes cambiarlo por el valor exacto del día 9 si lo tienes)
uf_inicial = uf_actual

fechas = [fecha_inicio + timedelta(days=i) for i in range(num_dias + 1)]
valores_uf = [round(uf_inicial * (factor_diario ** i), 2) for i in range(len(fechas))]

df = pd.DataFrame({
    "Fecha": [f.strftime("%d-%m-%Y") for f in fechas],
    "UF proyectada": valores_uf
})

# ===== NOMBRE DEL ARCHIVO =====
# Formato solicitado: PROYECCION_UF DDMMAAAA(1)_DDMMAAAA(2)
fecha_1 = datetime(anio_actual, mes_actual, 10).strftime("%d%m%Y")
fecha_2 = fecha_fin.strftime("%d%m%Y")
nombre_archivo = f"PROYECCION_UF {fecha_1}_{fecha_2}.xlsx"

ruta_completa = os.path.join(ruta_onedrive, nombre_archivo)
df.to_excel(ruta_completa, index=False)

print(f"Archivo generado correctamente: {ruta_completa}")