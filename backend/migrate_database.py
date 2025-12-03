"""
Migrar base de datos para agregar columnas nuevas
"""
import sqlite3
import pandas as pd

print("="*60)
print("MIGRANDO BASE DE DATOS")
print("="*60)

# Conectar a la base de datos
conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

# Verificar columnas actuales
cursor.execute('PRAGMA table_info(ventas_diarias)')
columnas_actuales = [row[1] for row in cursor.fetchall()]
print(f"\nColumnas actuales: {columnas_actuales}")

# Columnas nuevas a agregar
columnas_nuevas = {
    'pizzas_pastor': 'INTEGER DEFAULT 0',
    'pizzas_chuleta': 'INTEGER DEFAULT 0',
    'alitas_vendidas': 'INTEGER DEFAULT 0'
}

# Agregar columnas si no existen
for columna, tipo in columnas_nuevas.items():
    if columna not in columnas_actuales:
        try:
            cursor.execute(f'ALTER TABLE ventas_diarias ADD COLUMN {columna} {tipo}')
            print(f"✅ Columna '{columna}' agregada")
        except Exception as e:
            print(f"⚠️ Error agregando '{columna}': {e}")
    else:
        print(f"ℹ️ Columna '{columna}' ya existe")

conn.commit()

# Cargar datos del parquet y actualizar la BD
print("\n" + "="*60)
print("ACTUALIZANDO DATOS")
print("="*60)

df = pd.read_parquet('data/ventas_diarias.parquet')
print(f"\nDatos del parquet: {len(df)} filas")
print(f"Columnas: {df.columns.tolist()}")

# Limpiar tabla y recargar todos los datos
cursor.execute('DELETE FROM ventas_diarias')
print("✅ Tabla limpiada")

# Insertar datos
for _, row in df.iterrows():
    cursor.execute('''
        INSERT OR REPLACE INTO ventas_diarias (
            fecha, total_ventas_dia, total_pedidos,
            pizzas_vendidas, pizzas_pastor, pizzas_chuleta,
            alitas_vendidas, baguettes_vendidas, papas_gajo_vendidas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['fecha'].strftime('%Y-%m-%d'),
        row['total_ventas_dia'],
        row['total_pedidos'],
        row['pizzas_vendidas'],
        row['pizzas_pastor'],
        row['pizzas_chuleta'],
        row['alitas_vendidas'],
        row['baguettes_vendidas'],
        row['papas_gajo_vendidas']
    ))

conn.commit()
print(f"✅ {len(df)} filas insertadas")

# Verificar
cursor.execute('SELECT COUNT(*) FROM ventas_diarias')
count = cursor.fetchone()[0]
print(f"\nTotal filas en BD: {count}")

# Verificar columnas finales
cursor.execute('PRAGMA table_info(ventas_diarias)')
columnas_finales = [row[1] for row in cursor.fetchall()]
print(f"Columnas finales: {columnas_finales}")

# Mostrar ejemplo
cursor.execute('SELECT fecha, pizzas_vendidas, pizzas_pastor, pizzas_chuleta, alitas_vendidas FROM ventas_diarias ORDER BY fecha DESC LIMIT 5')
print("\nÚltimos 5 días:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} pizzas ({row[2]} pastor, {row[3]} chuleta), {row[4]} alitas")

conn.close()

print("\n" + "="*60)
print("✅ MIGRACIÓN COMPLETADA")
print("="*60)
