import sqlite3

conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

# Ver archivos procesados
cursor.execute('SELECT * FROM archivos_procesados')
print('Archivos procesados:')
for row in cursor.fetchall():
    print(f'  {row}')

# Eliminar registros de noviembre 13-17
cursor.execute('DELETE FROM archivos_procesados WHERE archivo LIKE "%2025-11-13%"')
conn.commit()
print(f'\n✅ Archivos eliminados: {cursor.rowcount}')

conn.close()
print('\nAhora puedes subir el archivo de nuevo')
