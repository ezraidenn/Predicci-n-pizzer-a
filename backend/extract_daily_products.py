"""
Extraer ventas diarias de productos específicos:
- Pizzas totales
- Pizzas Pastor (Pastorera)
- Pizzas Chuleta (Chuli)  
- Alitas (todas las variantes)
- Baguettes
- Papas gajo
"""

import pandas as pd
import glob
from pathlib import Path
from datetime import datetime
import numpy as np

# Directorio con los archivos Excel
excel_dir = r"C:\Users\raulc\Downloads\Reportes pruebas"
archivos = glob.glob(f"{excel_dir}/*.xlsx")

print("="*80)
print("EXTRAYENDO VENTAS DIARIAS POR PRODUCTO")
print("="*80)

# Lista para acumular datos diarios
datos_diarios = []

for archivo in sorted(archivos):
    print(f"\n📁 {Path(archivo).name}")
    
    try:
        # Leer hojas necesarias
        df_pedidos = pd.read_excel(archivo, sheet_name='Pedidos')
        df_detalles = pd.read_excel(archivo, sheet_name='Detalles')
        
        # Procesar fechas
        df_pedidos['Fecha'] = pd.to_datetime(
            df_pedidos['Fecha de cierre'], 
            format='%d/%m/%Y | %H:%M', 
            errors='coerce'
        )
        df_pedidos['Fecha_solo'] = df_pedidos['Fecha'].dt.date
        
        # Filtrar solo pedidos finalizados
        df_pedidos = df_pedidos[df_pedidos['Estado del pedido'] == 'Finalizado']
        
        # Merge detalles con pedidos para tener la fecha
        df_merged = df_detalles.merge(
            df_pedidos[['Id único del pedido', 'Fecha_solo', 'Total pagado']],
            on='Id único del pedido',
            how='left'
        )
        
        # Agrupar por fecha
        fechas_unicas = df_merged['Fecha_solo'].dropna().unique()
        
        for fecha in sorted(fechas_unicas):
            df_dia = df_merged[df_merged['Fecha_solo'] == fecha]
            
            # Contar productos por categoría
            productos_dia = {
                'fecha': fecha,
                'total_ventas_dia': df_pedidos[df_pedidos['Fecha_solo'] == fecha]['Total pagado'].sum(),
                'total_pedidos': len(df_pedidos[df_pedidos['Fecha_solo'] == fecha]),
            }
            
            # PIZZAS TOTALES (todas las categorías de pizza)
            mask_pizzas = df_dia['Nombre del producto'].str.lower().str.contains('pizza', na=False)
            productos_dia['pizzas_vendidas'] = int(df_dia[mask_pizzas]['Cantidad'].sum())
            
            # PIZZAS PASTOR
            mask_pastor = df_dia['Nombre del producto'].str.lower().str.contains('pastor', na=False)
            productos_dia['pizzas_pastor'] = int(df_dia[mask_pastor]['Cantidad'].sum())
            
            # PIZZAS CHULETA (Chuli)
            mask_chuleta = df_dia['Nombre del producto'].str.lower().str.contains('chuli', na=False)
            productos_dia['pizzas_chuleta'] = int(df_dia[mask_chuleta]['Cantidad'].sum())
            
            # ALITAS (todas las variantes)
            mask_alitas = df_dia['Nombre del producto'].str.lower().str.contains('alita', na=False)
            productos_dia['alitas_vendidas'] = int(df_dia[mask_alitas]['Cantidad'].sum())
            
            # BAGUETTES
            mask_baguette = df_dia['Nombre del producto'].str.lower().str.contains('baguette', na=False)
            productos_dia['baguettes_vendidas'] = int(df_dia[mask_baguette]['Cantidad'].sum())
            
            # PAPAS GAJO
            mask_papas = df_dia['Nombre del producto'].str.lower().str.contains('papa', na=False)
            productos_dia['papas_gajo_vendidas'] = int(df_dia[mask_papas]['Cantidad'].sum())
            
            datos_diarios.append(productos_dia)
        
        print(f"  ✅ Procesados {len(fechas_unicas)} días")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        continue

print("\n" + "="*80)
print("CREANDO DATASET FINAL")
print("="*80)

# Crear DataFrame final
df_final = pd.DataFrame(datos_diarios)

# Ordenar por fecha
df_final = df_final.sort_values('fecha')

# Convertir fecha a datetime
df_final['fecha'] = pd.to_datetime(df_final['fecha'])

print(f"\n📊 Total de días procesados: {len(df_final)}")
print(f"📅 Rango de fechas: {df_final['fecha'].min()} a {df_final['fecha'].max()}")

print("\n" + "="*80)
print("ESTADÍSTICAS POR PRODUCTO")
print("="*80)

productos_stats = {
    'Pizzas Totales': 'pizzas_vendidas',
    'Pizzas Pastor': 'pizzas_pastor',
    'Pizzas Chuleta': 'pizzas_chuleta',
    'Alitas': 'alitas_vendidas',
    'Baguettes': 'baguettes_vendidas',
    'Papas Gajo': 'papas_gajo_vendidas'
}

for nombre, columna in productos_stats.items():
    promedio = df_final[columna].mean()
    total = df_final[columna].sum()
    maximo = df_final[columna].max()
    print(f"\n{nombre}:")
    print(f"  Promedio diario: {promedio:.1f}")
    print(f"  Total: {total}")
    print(f"  Máximo en un día: {maximo}")

# Guardar a CSV para revisión
output_file = 'data/ventas_diarias_con_productos_nuevos.csv'
df_final.to_csv(output_file, index=False)
print(f"\n💾 Datos guardados en: {output_file}")

# Mostrar primeras filas
print("\n" + "="*80)
print("PRIMERAS 10 FILAS")
print("="*80)
print(df_final.head(10).to_string())

# Mostrar últimas filas
print("\n" + "="*80)
print("ÚLTIMAS 10 FILAS")
print("="*80)
print(df_final.tail(10).to_string())

print("\n✅ PROCESO COMPLETADO")
