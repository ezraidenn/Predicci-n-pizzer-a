"""
Script TODO-EN-UNO: Resetear BD y cargar datos desde CSV
"""

import pandas as pd
import sqlite3
from pathlib import Path

print("="*80)
print("🔄 RESET COMPLETO Y CARGA DE DATOS")
print("="*80)
print("\n⚠️  ADVERTENCIA: Esto borrará TODOS los datos actuales")
print("\nPasos que se ejecutarán:")
print("  1. Borrar todos los datos de la base de datos")
print("  2. Borrar registros de archivos procesados")
print("  3. Cargar datos desde ventas_diarias_con_productos_nuevos.csv")
print("  4. Actualizar archivo parquet")
print()

respuesta = input("¿Continuar? (escribe 'SI' para confirmar): ")
if respuesta.strip().upper() != 'SI':
    print("\n❌ Operación cancelada")
    exit()

print("\n" + "="*80)
print("PASO 1: LIMPIAR BASE DE DATOS")
print("="*80)

# Conectar a BD
conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

# Borrar datos
cursor.execute('DELETE FROM ventas_diarias')
print(f"✅ Borrados {cursor.rowcount} registros de ventas_diarias")

cursor.execute('DELETE FROM archivos_procesados')
print(f"✅ Borrados {cursor.rowcount} registros de archivos_procesados")

cursor.execute('DELETE FROM sqlite_sequence WHERE name="ventas_diarias"')
cursor.execute('DELETE FROM sqlite_sequence WHERE name="archivos_procesados"')
print("✅ IDs reseteados")

conn.commit()

print("\n" + "="*80)
print("PASO 2: CARGAR DATOS DESDE CSV")
print("="*80)

# Cargar CSV
csv_path = 'data/ventas_diarias_con_productos_nuevos.csv'
if not Path(csv_path).exists():
    print(f"❌ No se encontró: {csv_path}")
    conn.close()
    exit()

df = pd.read_csv(csv_path)
df['fecha'] = pd.to_datetime(df['fecha'])

print(f"\n📊 Cargando {len(df)} registros...")
print(f"📅 Rango: {df['fecha'].min().date()} a {df['fecha'].max().date()}")

# Insertar datos
insertados = 0
errores = 0

for _, row in df.iterrows():
    try:
        cursor.execute('''
            INSERT INTO ventas_diarias (
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
        errores += 1
        if errores <= 3:  # Mostrar solo los primeros 3 errores
            print(f"⚠️  Error en {row['fecha'].date()}: {e}")

conn.commit()
print(f"✅ Insertados: {insertados} registros")
if errores > 0:
    print(f"⚠️  Errores: {errores}")

print("\n" + "="*80)
print("PASO 3: ACTUALIZAR PARQUET")
print("="*80)

# Actualizar parquet
df.to_parquet('data/ventas_diarias.parquet', index=False)
print("✅ Parquet actualizado")

print("\n" + "="*80)
print("PASO 4: VERIFICACIÓN")
print("="*80)

# Verificar
cursor.execute('SELECT COUNT(*) FROM ventas_diarias')
total_bd = cursor.fetchone()[0]

cursor.execute('SELECT MIN(fecha), MAX(fecha) FROM ventas_diarias')
min_fecha, max_fecha = cursor.fetchone()

cursor.execute('''
    SELECT 
        SUM(pizzas_vendidas) as total_pizzas,
        SUM(pizzas_pastor) as total_pastor,
        SUM(pizzas_chuleta) as total_chuleta,
        SUM(alitas_vendidas) as total_alitas
    FROM ventas_diarias
''')
stats = cursor.fetchone()

print(f"\n✅ Registros en BD: {total_bd}")
print(f"✅ Rango de fechas: {min_fecha} a {max_fecha}")
print(f"\n📊 Totales:")
print(f"   Pizzas: {stats[0]}")
print(f"   Pastor: {stats[1]}")
print(f"   Chuleta: {stats[2]}")
print(f"   Alitas: {stats[3]}")

conn.close()

# Verificar parquet
df_parquet = pd.read_parquet('data/ventas_diarias.parquet')
print(f"\n✅ Registros en Parquet: {len(df_parquet)}")
print(f"✅ Columnas: {df_parquet.columns.tolist()}")

print("\n" + "="*80)
print("✅✅✅ PROCESO COMPLETADO EXITOSAMENTE ✅✅✅")
print("="*80)
print("\n🎯 PRÓXIMOS PASOS:")
print("   1. Reinicia el backend (Ctrl+C y vuelve a iniciar)")
print("   2. Recarga el frontend (F5)")
print("   3. Haz clic en 'Reentrenar' en el dashboard")
print("   4. ¡Listo! Tus predicciones estarán actualizadas")
print()
