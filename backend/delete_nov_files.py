import sqlite3

conn = sqlite3.connect('data/pizzeria_max.db')
cursor = conn.cursor()

# Eliminar registros 14 y 15
cursor.execute('DELETE FROM archivos_procesados WHERE id IN (14, 15)')
conn.commit()
print(f'✅ Archivos eliminados: {cursor.rowcount}')

conn.close()
print('\n✅ Ahora puedes subir el archivo de nuevo y se procesará correctamente')
