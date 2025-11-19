"""
Script para procesar archivos Excel y extraer productos nuevos:
- Pizzas Pastor (Pastorera)
- Pizzas Chuleta (Chuli)
- Alitas
"""

import pandas as pd
import glob
from pathlib import Path
from datetime import datetime

# Directorio con los archivos Excel
excel_dir = r"C:\Users\raulc\Downloads\Reportes pruebas"
archivos = glob.glob(f"{excel_dir}/*.xlsx")

print("="*80)
print("PROCESANDO ARCHIVOS EXCEL PARA EXTRAER PRODUCTOS NUEVOS")
print("="*80)

# Dataframe para acumular resultados
resultados = []

for archivo in sorted(archivos):
    print(f"\nProcesando: {Path(archivo).name}")
    
    try:
        # Leer hoja de Productos
        df_productos = pd.read_excel(archivo, sheet_name='Productos')
        
        # Leer hoja de Pedidos para obtener fechas
        df_pedidos = pd.read_excel(archivo, sheet_name='Pedidos')
        
        # Extraer fecha del nombre del archivo
        nombre = Path(archivo).stem
        # Formato: OLACLICK+ventas-2025-11-01-2025-11-12
        partes = nombre.split('-')
        if len(partes) >= 6:
            fecha_inicio = f"{partes[2]}-{partes[3]}-{partes[4]}"
            fecha_fin = f"{partes[5]}-{partes[6]}-{partes[7]}"
            print(f"  Período: {fecha_inicio} a {fecha_fin}")
        
        # Buscar productos específicos
        productos_buscar = {
            'pastor': ['pastorera', 'pastor'],
            'chuleta': ['chuli', 'chuleta'],
            'alitas': ['alitas']
        }
        
        # Contar productos por categoría
        for key, keywords in productos_buscar.items():
            cantidad = 0
            for keyword in keywords:
                mask = df_productos['Nombre de la variante de producto'].str.lower().str.contains(keyword, na=False)
                cantidad += df_productos[mask]['Cantidad vendida'].sum()
            
            print(f"  {key.capitalize()}: {cantidad}")
        
        # Agrupar por fecha (del pedido)
        df_pedidos['Fecha'] = pd.to_datetime(df_pedidos['Fecha de cierre'], format='%d/%m/%Y | %H:%M', errors='coerce')
        df_pedidos['Fecha_solo'] = df_pedidos['Fecha'].dt.date
        
        # Para cada día, contar productos
        for fecha in df_pedidos['Fecha_solo'].dropna().unique():
            # Filtrar pedidos de ese día
            pedidos_dia = df_pedidos[df_pedidos['Fecha_solo'] == fecha]['Id único del pedido'].tolist()
            
            # Aquí necesitaríamos cruzar con Detalles para saber qué productos se vendieron ese día
            # Por ahora, vamos a hacer un approach más simple
            
            resultado = {
                'fecha': fecha,
                'archivo': Path(archivo).name
            }
            
            resultados.append(resultado)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        continue

print("\n" + "="*80)
print("RESUMEN GENERAL")
print("="*80)

# Crear DataFrame con todos los resultados
if resultados:
    df_final = pd.DataFrame(resultados)
    print(f"\nTotal de días procesados: {len(df_final)}")
    print(f"\nFechas únicas: {df_final['fecha'].nunique()}")
else:
    print("\n⚠️ No se encontraron datos")

print("\n" + "="*80)
print("SIGUIENTE PASO: Crear agregación por día")
print("="*80)
