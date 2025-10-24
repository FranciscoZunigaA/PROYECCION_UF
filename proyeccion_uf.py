# proyeccion_uf.py
# Autor: Francisco (ajustado para ejecución local y en CI)
# Objetivo: Generar proyección de UF usando IPC y guardar Excel en ruta portable.

from datetime import date, datetime, timedelta
from pathlib import Path
import os
import sys
import pandas as pd

# =========================
# CONFIGURACIÓN DE SALIDA
# =========================
def get_output_path() -> Path:
    """
    Obtiene la ruta de salida desde la variable de entorno OUTPUT_DIR si existe;
    en caso contrario usa la carpeta local 'output'. Crea la carpeta si no existe.
    """
    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    hoy = date.today()
    nombre_archivo = f"Proyeccion_UF_{hoy:%Y-%m-%d}.xlsx"
    return output_dir / nombre_archivo


# =========================
# FUNCIONES AUXILIARES
# =========================
def obtener_ipc_mensual() -> float:
    """
    Devuelve el IPC mensual como porcentaje (ej: 0.4 => 0.4%).
    En tu implementación real, reemplaza esta función con la lógica
    que ya usas (scraping/API/archivo). Aquí dejamos un ejemplo fijo.
    """
    # TODO: Reemplazar por tu fuente real de IPC
    ipc_porcentaje = 0.4  # 0.4% como ejemplo
    print(f"IPC mensual obtenido: {ipc_porcentaje}%")
    return ipc_porcentaje


def obtener_uf_actual() -> float:
    """
    Devuelve la UF actual (valor base para la proyección).
    Reemplaza con tu lógica real (scraping/API). Ejemplo fijo.
    """
    # TODO: Reemplazar por tu fuente real de UF
    uf_actual = 39562.0
    print(f"UF actual obtenida: {int(uf_actual)}")
    return uf_actual


def generar_rango_fechas_uf() -> pd.DatetimeIndex:
    """
    Genera el rango de fechas desde el 9 del mes en curso hasta el 9 del mes siguiente (inclusive).
    Ej.: si hoy es 2025-10-24 -> del 2025-10-09 al 2025-11-09.
    """
    hoy = date.today()

    dia_9_mes_actual = date(hoy.year, hoy.month, 9)

    # calcular 9 del mes siguiente
    if hoy.month == 12:
        dia_9_mes_siguiente = date(hoy.year + 1, 1, 9)
    else:
        dia_9_mes_siguiente = date(hoy.year, hoy.month + 1, 9)

    # Rango inclusivo
    fechas = pd.date_range(dia_9_mes_actual, dia_9_mes_siguiente, freq="D")
    return fechas


def proyectar_uf(uf_base: float, ipc_porcentaje: float, fechas: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Proyección simplificada: distribuye el IPC mensual (en %) de manera uniforme
    a lo largo de los días entre el 9 del mes en curso y el 9 del mes siguiente.
    Ajusta esta lógica si tu metodología es distinta.
    """
    # Convertir porcentaje a factor mensual
    ipc_factor_mensual = 1 + (ipc_porcentaje / 100.0)

    dias = len(fechas)
    if dias <= 1:
        # Evitar división por cero o proyecciones triviales
        data = [{"Fecha": fechas[0].date(), "UF": uf_base}]
        return pd.DataFrame(data)

    # Distribución diaria del factor mensual (aprox. exponencial diaria)
    # Si prefieres lineal, puedes cambiar la fórmula.
    factor_diario = ipc_factor_mensual ** (1 / (dias - 1))

    valores = []
    valor = uf_base
    for i, f in enumerate(fechas):
        if i == 0:
            valor = uf_base
        else:
            valor *= factor_diario
        valores.append({"Fecha": f.date(), "UF": round(valor, 2)})

    df = pd.DataFrame(valores)
    return df


def guardar_excel(df: pd.DataFrame, ruta_salida: Path) -> None:
    """
    Guarda el DataFrame como Excel en la ruta indicada.
    Usa openpyxl como engine para asegurar compatibilidad.
    """
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(ruta_salida, index=False, engine="openpyxl")
    print(f"Archivo guardado en: {ruta_salida.resolve()}")


# =========================
# PROGRAMA PRINCIPAL
# =========================
def main() -> int:
    try:
        ipc_porcentaje = obtener_ipc_mensual()
        uf_actual = obtener_uf_actual()
        fechas = generar_rango_fechas_uf()
        df = proyectar_uf(uf_actual, ipc_porcentaje, fechas)

        # Orden y nombres de columnas
        df = df[["Fecha", "UF"]]

        ruta_salida = get_output_path()
        guardar_excel(df, ruta_salida)

        # Información final
        print(f"Filas generadas: {len(df)}")
        if len(df) > 0:
            print(f"Primera fecha: {df.iloc[0, 0]} | Última fecha: {df.iloc[-1, 0]}")

        return 0
    except Exception as e:
        print("❌ Error durante la ejecución:", e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())