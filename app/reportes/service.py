from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.compras.models import Compra
# 👇 IMPORTANTE: Importa tu modelo de Venta
from app.ventas.models import Venta 

def obtener_datos_dashboard(db: Session, id_microempresa: int, periodo: str):
    now = datetime.now()
    fecha_inicio = now

    # 1. Definir rango de fechas
    if periodo == 'mes':
        fecha_inicio = now.replace(day=1)
    elif periodo == 'trimestre':
        fecha_inicio = now - timedelta(days=90)
    elif periodo == 'anio':
        fecha_inicio = now.replace(month=1, day=1)

    # 2. Consultar Totales GASTOS (Compras)
    gastos = db.query(func.sum(Compra.total))\
        .filter(Compra.id_microempresa == id_microempresa)\
        .filter(Compra.fecha >= fecha_inicio)\
        .scalar() or 0

    # 3. Consultar Totales INGRESOS (Ventas) ✅ AHORA SÍ FUNCIONA
    ingresos = db.query(func.sum(Venta.total))\
        .filter(Venta.id_microempresa == id_microempresa)\
        .filter(Venta.fecha >= fecha_inicio)\
        .scalar() or 0

    # 4. Construir Gráfico (Mezclando Ventas y Compras por día)
    
    # A) Agrupar Compras por día
    compras_query = db.query(
        func.date(Compra.fecha).label('fecha'),
        func.sum(Compra.total).label('total')
    ).filter(
        Compra.id_microempresa == id_microempresa,
        Compra.fecha >= fecha_inicio
    ).group_by(func.date(Compra.fecha)).all()
    mapa_compras = {str(c.fecha): float(c.total) for c in compras_query}

    # B) Agrupar Ventas por día ✅
    ventas_query = db.query(
        func.date(Venta.fecha).label('fecha'),
        func.sum(Venta.total).label('total')
    ).filter(
        Venta.id_microempresa == id_microempresa,
        Venta.fecha >= fecha_inicio
    ).group_by(func.date(Venta.fecha)).all()
    mapa_ventas = {str(v.fecha): float(v.total) for v in ventas_query}

    # C) Unificar en una linea de tiempo
    grafico = []
    delta_dias = (now - fecha_inicio).days + 1
    
    for i in range(delta_dias):
        dia_actual = fecha_inicio + timedelta(days=i)
        fecha_str = dia_actual.strftime('%Y-%m-%d')
        label = dia_actual.strftime('%d/%m') # Ej: 23/01

        grafico.append({
            "name": label,
            "ventas": mapa_ventas.get(fecha_str, 0),   # Dato real de ventas
            "compras": mapa_compras.get(fecha_str, 0)  # Dato real de compras
        })

    return {
        "ventas_totales": ingresos,
        "gastos_totales": gastos,
        "ganancia_neta": ingresos - gastos,
        "grafico": grafico
    }