"""
Script para RESETEAR completamente la base de datos
ADVERTENCIA: Esto borrará TODOS los datos históricos
"""

import sqlite3
import os
from pathlib import Path

print("="*80)
print("⚠️  RESETEAR BASE DE DATOS - BORRAR TODOS LOS DATOS")
print("="*80)
print("\nEsto borrará:")
print("  - Todos los datos de ventas diarias")
print("  - Todos los registros de archivos procesados")
print("  - El archivo parquet de datos")
print()

respuesta = input("¿Estás SEGURO de que quieres continuar? (escribe 'SI' para confirmar): ")

if respuesta.strip().upper() != 'SI':
    print("\n❌ Operación cancelada")
    exit()

print("\n🔄 Iniciando reset...")

# Conectar a la base de datos
db_path = 'data/pizzeria_max.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Borrar todos los datos de ventas_diarias
cursor.execute('DELETE FROM ventas_diarias')
registros_borrados = cursor.rowcount
print(f"✅ Borrados {registros_borrados} registros de ventas_diarias")

# 2. Borrar todos los archivos procesados
cursor.execute('DELETE FROM archivos_procesados')
archivos_borrados = cursor.rowcount
print(f"✅ Borrados {archivos_borrados} registros de archivos_procesados")

# 3. Resetear los IDs autoincrementales
cursor.execute('DELETE FROM sqlite_sequence WHERE name="ventas_diarias"')
cursor.execute('DELETE FROM sqlite_sequence WHERE name="archivos_procesados"')
print("✅ IDs autoincrementales reseteados")

conn.commit()
conn.close()

# 4. Borrar archivo parquet
parquet_path = Path('data/ventas_diarias.parquet')
if parquet_path.exists():
    parquet_path.unlink()
    print("✅ Archivo parquet eliminado")
else:
    print("ℹ️  No había archivo parquet")

# 5. Crear parquet vacío
import pandas as pd

df_vacio = pd.DataFrame(columns=[
    'fecha', 'total_ventas_dia', 'total_pedidos',
    'pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta',
    'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas'
])
df_vacio['fecha'] = pd.to_datetime(df_vacio['fecha'])
df_vacio.to_parquet('data/ventas_diarias.parquet', index=False)
print("✅ Parquet vacío creado")

print("\n" + "="*80)
print("✅ BASE DE DATOS RESETEADA COMPLETAMENTE")
print("="*80)
print("\nAhora puedes:")
print("  1. Subir tus archivos Excel uno por uno desde el dashboard")
print("  2. O ejecutar 'python cargar_datos_iniciales.py' para cargar desde CSV")
print()
