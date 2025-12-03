"""
Script para cargar datos iniciales desde el CSV
"""

import pandas as pd
import sqlite3
from pathlib import Path

print("="*80)
print("📥 CARGAR DATOS INICIALES DESDE CSV")
print("="*80)

# Cargar CSV
csv_path = 'data/ventas_diarias_con_productos_nuevos.csv'
if not Path(csv_path).exists():
    print(f"❌ No se encontró el archivo: {csv_path}")
    exit()

df = pd.read_csv(csv_path)
df['fecha'] = pd.to_datetime(df['fecha'])

print(f"\n📊 Datos a cargar:")
print(f"  Total filas: {len(df)}")
print(f"  Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")
print(f"  Columnas: {df.columns.tolist()}")

# Verificar que tenga las columnas necesarias
columnas_requeridas = ['fecha', 'total_ventas_dia', 'total_pedidos', 
                       'pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta',
                       'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas']

faltan = [col for col in columnas_requeridas if col not in df.columns]
if faltan:
    print(f"\n❌ Faltan columnas: {faltan}")
    exit()

# Confirmar
respuesta = input("\n¿Continuar con la carga? (SI/no): ")
if respuesta.strip().upper() == 'NO':
    print("❌ Operación cancelada")
    exit()

print("\n🔄 Cargando datos...")

# Conectar a BD
conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

# Insertar datos
insertados = 0
for _, row in df.iterrows():
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO ventas_diarias (
                fecha, total_ventas_dia, total_pedidos,
                pizzas_vendidas, pizzas_pastor, pizzas_chuleta,
                alitas_vendidas, baguettes_vendidas, papas_gajo_vendidas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    except Exception as e:
        print(f"⚠️  Error en fila {row['fecha']}: {e}")

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

conn.close()

print("\n" + "="*80)
print("✅ DATOS CARGADOS CORRECTAMENTE")
print("="*80)
print("\nAhora puedes:")
print("  1. Reiniciar el backend")
print("  2. Hacer clic en 'Reentrenar' en el dashboard")
print("  3. Ver tus predicciones actualizadas")
print()
