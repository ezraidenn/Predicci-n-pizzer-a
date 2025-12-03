"""
Script para migrar datos con productos nuevos (pastor, chuleta, alitas)
"""

import pandas as pd
import sqlite3
from pathlib import Path

print("="*80)
print("📥 MIGRANDO DATOS CON PRODUCTOS NUEVOS")
print("="*80)

# Cargar CSV
csv_path = 'data/ventas_diarias_con_productos_nuevos.csv'
df = pd.read_csv(csv_path)
df['fecha'] = pd.to_datetime(df['fecha'])

print(f"\n📊 Datos a migrar:")
print(f"  Total filas: {len(df)}")
print(f"  Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")
print(f"  Columnas: {df.columns.tolist()}")

# Estadísticas de productos nuevos
print(f"\n📈 Estadísticas productos nuevos:")
print(f"  Pizzas Pastor: {df['pizzas_pastor'].sum()} total, {df['pizzas_pastor'].mean():.1f}/día promedio")
print(f"  Pizzas Chuleta: {df['pizzas_chuleta'].sum()} total, {df['pizzas_chuleta'].mean():.1f}/día promedio")
print(f"  Alitas: {df['alitas_vendidas'].sum()} total, {df['alitas_vendidas'].mean():.1f}/día promedio")

# Conectar a BD
conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

# Limpiar tabla existente
cursor.execute('DELETE FROM ventas_diarias')
print(f"\n🗑️  Tabla limpiada")

# Insertar datos
insertados = 0
for _, row in df.iterrows():
    cursor.execute('''
        INSERT OR REPLACE INTO ventas_diarias (
            fecha, total_ventas_dia, total_pedidos,
            pizzas_vendidas, pizzas_pastor, pizzas_chuleta,
            alitas_vendidas, baguettes_vendidas, papas_gajo_vendidas,
            total_visitas, pedidos_iniciados, pedidos_creados,
            tipo_servicio_domicilio, tipo_servicio_llevar
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0)
    ''', (
        row['fecha'].strftime('%Y-%m-%d'),
        float(row['total_ventas_dia']),
        int(row['total_pedidos']),
        int(row['pizzas_vendidas']),
        int(row['pizzas_pastor']),
        int(row['pizzas_chuleta']),
        int(row['alitas_vendidas']),
        int(row['baguettes_vendidas']),
        int(row['papas_gajo_vendidas'])
    ))
    insertados += 1

conn.commit()
print(f"✅ Insertados {insertados} registros en BD")

# Actualizar parquet
df.to_parquet('data/ventas_diarias.parquet', index=False)
print(f"✅ Parquet actualizado")

# Verificar
cursor.execute('SELECT COUNT(*) FROM ventas_diarias')
total = cursor.fetchone()[0]
print(f"\n📊 Total registros en BD: {total}")

cursor.execute('SELECT MIN(fecha), MAX(fecha) FROM ventas_diarias')
min_fecha, max_fecha = cursor.fetchone()
print(f"📅 Rango: {min_fecha} a {max_fecha}")

# Verificar productos nuevos
cursor.execute('SELECT SUM(pizzas_pastor), SUM(pizzas_chuleta), SUM(alitas_vendidas) FROM ventas_diarias')
pastor, chuleta, alitas = cursor.fetchone()
print(f"\n🍕 Productos nuevos en BD:")
print(f"  Pastor: {pastor}")
print(f"  Chuleta: {chuleta}")
print(f"  Alitas: {alitas}")

conn.close()
print("\n" + "="*80)
print("✅ MIGRACIÓN COMPLETADA")
print("="*80)
