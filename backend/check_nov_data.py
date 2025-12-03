import sqlite3

conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT fecha, pizzas_vendidas, pizzas_pastor, total_ventas_dia 
    FROM ventas_diarias 
    WHERE fecha >= "2025-11-11" AND fecha <= "2025-11-17" 
    ORDER BY fecha
''')

print('Datos en BD para nov 11-17:')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  {row[0]}: {row[1]} pizzas ({row[2]} pastor), ${row[3]:.2f}')
else:
    print('  ❌ NO HAY DATOS')

cursor.execute('SELECT MAX(fecha) FROM ventas_diarias')
ultima_fecha = cursor.fetchone()[0]
print(f'\nÚltima fecha en BD: {ultima_fecha}')

cursor.execute('SELECT COUNT(*) FROM ventas_diarias')
total = cursor.fetchone()[0]
print(f'Total registros: {total}')

conn.close()
