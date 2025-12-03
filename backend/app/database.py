"""
Módulo de Base de Datos - Pizzería MAX
Gestiona la persistencia de datos históricos usando SQLite
"""
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class SalesDatabase:
    """Gestiona la base de datos de ventas históricas"""
    
    def __init__(self, db_path: Path):
        """
        Inicializa la conexión a la base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Crea las tablas si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla principal de ventas diarias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas_diarias (
                    fecha DATE PRIMARY KEY,
                    total_ventas_dia REAL,
                    total_pedidos INTEGER,
                    pizzas_vendidas INTEGER,
                    baguettes_vendidas INTEGER,
                    papas_gajo_vendidas INTEGER,
                    total_visitas INTEGER,
                    pedidos_iniciados INTEGER,
                    pedidos_creados INTEGER,
                    tipo_servicio_domicilio REAL,
                    tipo_servicio_llevar REAL,
                    ticket_promedio REAL,
                    pedidos_hora_pico INTEGER,
                    pedidos_hora_almuerzo INTEGER,
                    ventas_domicilio REAL,
                    ventas_local REAL,
                    tasa_conversion REAL,
                    pizzas_pastor INTEGER,
                    pizzas_chuleta INTEGER,
                    alitas_vendidas INTEGER,
                    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    archivo_origen TEXT
                )
            """)
            
            # Agregar columnas nuevas si no existen (para tablas existentes)
            nuevas_columnas = [
                ('ticket_promedio', 'REAL'),
                ('pedidos_hora_pico', 'INTEGER'),
                ('pedidos_hora_almuerzo', 'INTEGER'),
                ('ventas_domicilio', 'REAL'),
                ('ventas_local', 'REAL'),
                ('tasa_conversion', 'REAL'),
                ('pizzas_pastor', 'INTEGER'),
                ('pizzas_chuleta', 'INTEGER'),
                ('alitas_vendidas', 'INTEGER'),
            ]
            for col_name, col_type in nuevas_columnas:
                try:
                    cursor.execute(f"ALTER TABLE ventas_diarias ADD COLUMN {col_name} {col_type} DEFAULT 0")
                except sqlite3.OperationalError:
                    pass  # Columna ya existe
            
            # Tabla de archivos procesados (para evitar duplicados)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS archivos_procesados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_archivo TEXT UNIQUE,
                    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    registros_agregados INTEGER,
                    fecha_inicio DATE,
                    fecha_fin DATE
                )
            """)
            
            # Tabla de días festivos (para análisis de patrones)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dias_festivos (
                    fecha DATE PRIMARY KEY,
                    nombre_festivo TEXT,
                    tipo TEXT
                )
            """)
            
            # === TABLA DE CLIENTES ===
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    telefono TEXT PRIMARY KEY,
                    nombre TEXT,
                    direccion_actual TEXT,
                    todas_direcciones TEXT,
                    total_pedidos INTEGER DEFAULT 0,
                    total_gastado REAL DEFAULT 0,
                    ticket_promedio REAL DEFAULT 0,
                    tipo_servicio_preferido TEXT,
                    primer_pedido DATE,
                    ultimo_pedido DATE,
                    frecuencia_dias REAL DEFAULT 0,
                    es_cliente_frecuente INTEGER DEFAULT 0,
                    notas TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de historial de pedidos por cliente
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_cliente (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telefono TEXT,
                    fecha_pedido DATE,
                    total_pedido REAL,
                    tipo_servicio TEXT,
                    direccion TEXT,
                    productos TEXT,
                    FOREIGN KEY (telefono) REFERENCES clientes(telefono)
                )
            """)
            
            conn.commit()
            logger.info("Base de datos inicializada correctamente (incluyendo tabla clientes)")
    
    def insert_daily_data(self, df: pd.DataFrame, archivo_origen: str) -> Dict[str, Any]:
        """
        Inserta o actualiza datos diarios en la base de datos
        
        Args:
            df: DataFrame con datos diarios
            archivo_origen: Nombre del archivo de origen
            
        Returns:
            Diccionario con estadísticas de la operación
        """
        with sqlite3.connect(self.db_path) as conn:
            # Verificar si el archivo ya fue procesado
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM archivos_procesados WHERE nombre_archivo = ?",
                (archivo_origen,)
            )
            if cursor.fetchone()[0] > 0:
                logger.warning(f"Archivo {archivo_origen} ya fue procesado anteriormente")
                # Obtener fechas del DataFrame para mantener consistencia
                fecha_min = df['fecha'].min()
                fecha_max = df['fecha'].max()
                return {
                    "status": "skipped",
                    "message": "Archivo ya procesado",
                    "registros_nuevos": 0,
                    "registros_actualizados": 0,
                    "fecha_inicio": str(fecha_min),
                    "fecha_fin": str(fecha_max)
                }
            
            # Preparar datos
            df_copy = df.copy()
            df_copy['archivo_origen'] = archivo_origen
            df_copy['fecha_carga'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Guardar min/max antes de convertir a string
            fecha_min = df['fecha'].min()
            fecha_max = df['fecha'].max()
            
            # Convertir fecha a string para SQLite
            if 'fecha' in df_copy.columns:
                df_copy['fecha'] = df_copy['fecha'].astype(str)
            
            registros_nuevos = 0
            registros_actualizados = 0
            
            # Detectar fechas duplicadas
            fechas_existentes = set()
            cursor.execute("SELECT fecha FROM ventas_diarias")
            fechas_existentes = {row[0] for row in cursor.fetchall()}
            
            fechas_en_archivo = set(df_copy['fecha'].unique())
            fechas_duplicadas = fechas_existentes & fechas_en_archivo
            
            # Insertar o actualizar cada registro
            for _, row in df_copy.iterrows():
                # Obtener valores con defaults para nuevas columnas
                ticket_promedio = row.get('ticket_promedio', 0)
                pedidos_hora_pico = row.get('pedidos_hora_pico', 0)
                pedidos_hora_almuerzo = row.get('pedidos_hora_almuerzo', 0)
                ventas_domicilio = row.get('ventas_domicilio', 0)
                ventas_local = row.get('ventas_local', 0)
                tasa_conversion = row.get('tasa_conversion', 0)
                pizzas_pastor = row.get('pizzas_pastor', 0)
                pizzas_chuleta = row.get('pizzas_chuleta', 0)
                alitas_vendidas = row.get('alitas_vendidas', 0)
                
                if row['fecha'] in fechas_duplicadas:
                    # REEMPLAZAR registro existente (no sumar)
                    cursor.execute("""
                        UPDATE ventas_diarias SET
                            total_ventas_dia = ?,
                            total_pedidos = ?,
                            pizzas_vendidas = ?,
                            baguettes_vendidas = ?,
                            papas_gajo_vendidas = ?,
                            total_visitas = ?,
                            pedidos_iniciados = ?,
                            pedidos_creados = ?,
                            tipo_servicio_domicilio = ?,
                            tipo_servicio_llevar = ?,
                            ticket_promedio = ?,
                            pedidos_hora_pico = ?,
                            pedidos_hora_almuerzo = ?,
                            ventas_domicilio = ?,
                            ventas_local = ?,
                            tasa_conversion = ?,
                            pizzas_pastor = ?,
                            pizzas_chuleta = ?,
                            alitas_vendidas = ?,
                            fecha_carga = ?,
                            archivo_origen = ?
                        WHERE fecha = ?
                    """, (
                        row['total_ventas_dia'],
                        row['total_pedidos'],
                        row['pizzas_vendidas'],
                        row['baguettes_vendidas'],
                        row['papas_gajo_vendidas'],
                        row['total_visitas'],
                        row['pedidos_iniciados'],
                        row['pedidos_creados'],
                        row['tipo_servicio_domicilio'],
                        row['tipo_servicio_llevar'],
                        ticket_promedio,
                        pedidos_hora_pico,
                        pedidos_hora_almuerzo,
                        ventas_domicilio,
                        ventas_local,
                        tasa_conversion,
                        pizzas_pastor,
                        pizzas_chuleta,
                        alitas_vendidas,
                        row['fecha_carga'],
                        row['archivo_origen'],
                        row['fecha']
                    ))
                    registros_actualizados += 1
                else:
                    # Insertar nuevo registro
                    cursor.execute("""
                        INSERT INTO ventas_diarias (
                            fecha, total_ventas_dia, total_pedidos,
                            pizzas_vendidas, baguettes_vendidas, papas_gajo_vendidas,
                            total_visitas, pedidos_iniciados, pedidos_creados,
                            tipo_servicio_domicilio, tipo_servicio_llevar,
                            ticket_promedio, pedidos_hora_pico, pedidos_hora_almuerzo,
                            ventas_domicilio, ventas_local, tasa_conversion,
                            pizzas_pastor, pizzas_chuleta, alitas_vendidas,
                            fecha_carga, archivo_origen
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['fecha'],
                        row['total_ventas_dia'],
                        row['total_pedidos'],
                        row['pizzas_vendidas'],
                        row['baguettes_vendidas'],
                        row['papas_gajo_vendidas'],
                        row['total_visitas'],
                        row['pedidos_iniciados'],
                        row['pedidos_creados'],
                        row['tipo_servicio_domicilio'],
                        row['tipo_servicio_llevar'],
                        ticket_promedio,
                        pedidos_hora_pico,
                        pedidos_hora_almuerzo,
                        ventas_domicilio,
                        ventas_local,
                        tasa_conversion,
                        pizzas_pastor,
                        pizzas_chuleta,
                        alitas_vendidas,
                        row['fecha_carga'],
                        row['archivo_origen']
                    ))
                    registros_nuevos += 1
            
            # Registrar archivo procesado
            cursor.execute("""
                INSERT INTO archivos_procesados (
                    nombre_archivo, registros_agregados, fecha_inicio, fecha_fin
                ) VALUES (?, ?, ?, ?)
            """, (
                archivo_origen,
                registros_nuevos + registros_actualizados,
                str(fecha_min),
                str(fecha_max)
            ))
            
            conn.commit()
            
            logger.info(f"Datos insertados: {registros_nuevos} nuevos, {registros_actualizados} actualizados")
            if len(fechas_duplicadas) > 0:
                logger.warning(f"Se detectaron {len(fechas_duplicadas)} fechas duplicadas y fueron REEMPLAZADAS (no sumadas)")
            
            return {
                "status": "success",
                "registros_nuevos": registros_nuevos,
                "registros_actualizados": registros_actualizados,
                "fechas_duplicadas": len(fechas_duplicadas),
                "fecha_inicio": str(fecha_min),
                "fecha_fin": str(fecha_max)
            }
    
    def get_all_data(self) -> pd.DataFrame:
        """
        Obtiene todos los datos históricos
        
        Returns:
            DataFrame con todos los datos ordenados por fecha
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                """SELECT fecha, total_ventas_dia, total_pedidos, pizzas_vendidas, 
                   baguettes_vendidas, papas_gajo_vendidas, total_visitas, 
                   pedidos_iniciados, pedidos_creados, tipo_servicio_domicilio, 
                   tipo_servicio_llevar FROM ventas_diarias ORDER BY fecha""",
                conn
            )
            # Convertir fecha de string a date
            if len(df) > 0:
                df['fecha'] = pd.to_datetime(df['fecha']).dt.date
            logger.info(f"Datos históricos cargados: {len(df)} registros")
            return df
    
    def get_data_range(self, fecha_inicio: Optional[date] = None, 
                       fecha_fin: Optional[date] = None) -> pd.DataFrame:
        """
        Obtiene datos en un rango de fechas
        
        Args:
            fecha_inicio: Fecha de inicio (opcional)
            fecha_fin: Fecha de fin (opcional)
            
        Returns:
            DataFrame con datos filtrados
        """
        with sqlite3.connect(self.db_path) as conn:
            # Especificar columnas explícitamente para asegurar que se incluyan las nuevas
            query = """
                SELECT 
                    fecha, total_ventas_dia, total_pedidos,
                    pizzas_vendidas, pizzas_pastor, pizzas_chuleta,
                    alitas_vendidas, baguettes_vendidas, papas_gajo_vendidas,
                    total_visitas, pedidos_iniciados, pedidos_creados,
                    tipo_servicio_domicilio, tipo_servicio_llevar,
                    fecha_carga, archivo_origen
                FROM ventas_diarias 
                WHERE 1=1
            """
            params = []
            
            if fecha_inicio:
                query += " AND fecha >= ?"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND fecha <= ?"
                params.append(fecha_fin)
            
            query += " ORDER BY fecha"
            
            df = pd.read_sql_query(
                query, conn, params=params,
                parse_dates=['fecha', 'fecha_carga']
            )
            return df
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de la base de datos
        
        Returns:
            Diccionario con estadísticas
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total de registros
            cursor.execute("SELECT COUNT(*) FROM ventas_diarias")
            total_registros = cursor.fetchone()[0]
            
            # Rango de fechas
            cursor.execute("SELECT MIN(fecha), MAX(fecha) FROM ventas_diarias")
            fecha_min, fecha_max = cursor.fetchone()
            
            # Total de archivos procesados
            cursor.execute("SELECT COUNT(*) FROM archivos_procesados")
            total_archivos = cursor.fetchone()[0]
            
            # Ventas totales
            cursor.execute("SELECT SUM(total_ventas_dia) FROM ventas_diarias")
            ventas_totales = cursor.fetchone()[0] or 0
            
            return {
                "total_registros": total_registros,
                "fecha_inicio": fecha_min,
                "fecha_fin": fecha_max,
                "total_archivos_procesados": total_archivos,
                "ventas_totales_historicas": float(ventas_totales)
            }
    
    def add_festivo(self, fecha: date, nombre: str, tipo: str = "nacional"):
        """
        Agrega un día festivo
        
        Args:
            fecha: Fecha del festivo
            nombre: Nombre del festivo
            tipo: Tipo de festivo (nacional, local, etc.)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO dias_festivos (fecha, nombre_festivo, tipo)
                VALUES (?, ?, ?)
            """, (fecha, nombre, tipo))
            conn.commit()
            logger.info(f"Festivo agregado: {nombre} - {fecha}")
    
    def get_festivos(self) -> pd.DataFrame:
        """Obtiene todos los días festivos registrados"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                "SELECT * FROM dias_festivos ORDER BY fecha",
                conn,
                parse_dates=['fecha']
            )
    
    # ============ GESTIÓN DE CLIENTES ============
    
    def upsert_cliente(self, telefono: str, nombre: str, direccion: str, 
                       fecha_pedido: date, total_pedido: float, tipo_servicio: str,
                       productos: str = None) -> Dict[str, Any]:
        """
        Inserta o actualiza un cliente y registra su pedido
        
        Args:
            telefono: Número de teléfono (identificador único)
            nombre: Nombre del cliente
            direccion: Dirección de entrega
            fecha_pedido: Fecha del pedido
            total_pedido: Total del pedido en $
            tipo_servicio: 'domicilio' o 'para llevar'
            productos: JSON con productos del pedido
        """
        if not telefono or telefono == 'nan' or len(str(telefono).strip()) < 5:
            return {"status": "skipped", "reason": "teléfono inválido"}
        
        telefono = str(telefono).strip()
        nombre = str(nombre).strip() if nombre and nombre != 'nan' else 'Sin nombre'
        direccion = str(direccion).strip() if direccion and direccion != 'nan' else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si el cliente existe
            cursor.execute("SELECT * FROM clientes WHERE telefono = ?", (telefono,))
            cliente_existente = cursor.fetchone()
            
            if cliente_existente:
                # Actualizar cliente existente
                cursor.execute("SELECT total_pedidos, total_gastado, todas_direcciones, primer_pedido FROM clientes WHERE telefono = ?", (telefono,))
                total_pedidos, total_gastado, todas_dirs, primer_pedido = cursor.fetchone()
                
                # Actualizar direcciones (mantener historial)
                direcciones_lista = todas_dirs.split('|||') if todas_dirs else []
                if direccion and direccion not in direcciones_lista:
                    direcciones_lista.append(direccion)
                todas_direcciones = '|||'.join(direcciones_lista[-5:])  # Últimas 5 direcciones
                
                # Calcular nueva frecuencia
                nuevo_total_pedidos = total_pedidos + 1
                nuevo_total_gastado = total_gastado + total_pedido
                nuevo_ticket_promedio = nuevo_total_gastado / nuevo_total_pedidos
                
                # Calcular frecuencia (días entre pedidos)
                if primer_pedido:
                    dias_cliente = (fecha_pedido - pd.to_datetime(primer_pedido).date()).days
                    frecuencia = dias_cliente / nuevo_total_pedidos if nuevo_total_pedidos > 1 else 0
                else:
                    frecuencia = 0
                
                # Es cliente frecuente si tiene más de 3 pedidos
                es_frecuente = 1 if nuevo_total_pedidos >= 3 else 0
                
                cursor.execute("""
                    UPDATE clientes SET
                        nombre = COALESCE(?, nombre),
                        direccion_actual = COALESCE(?, direccion_actual),
                        todas_direcciones = ?,
                        total_pedidos = ?,
                        total_gastado = ?,
                        ticket_promedio = ?,
                        ultimo_pedido = ?,
                        frecuencia_dias = ?,
                        es_cliente_frecuente = ?,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE telefono = ?
                """, (
                    nombre if nombre != 'Sin nombre' else None,
                    direccion,
                    todas_direcciones,
                    nuevo_total_pedidos,
                    nuevo_total_gastado,
                    nuevo_ticket_promedio,
                    str(fecha_pedido),
                    frecuencia,
                    es_frecuente,
                    telefono
                ))
                status = "updated"
            else:
                # Insertar nuevo cliente
                cursor.execute("""
                    INSERT INTO clientes (
                        telefono, nombre, direccion_actual, todas_direcciones,
                        total_pedidos, total_gastado, ticket_promedio,
                        tipo_servicio_preferido, primer_pedido, ultimo_pedido,
                        frecuencia_dias, es_cliente_frecuente
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    telefono, nombre, direccion, direccion or '',
                    1, total_pedido, total_pedido,
                    tipo_servicio, str(fecha_pedido), str(fecha_pedido),
                    0, 0
                ))
                status = "created"
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO historial_cliente (
                    telefono, fecha_pedido, total_pedido, tipo_servicio, direccion, productos
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (telefono, str(fecha_pedido), total_pedido, tipo_servicio, direccion, productos))
            
            conn.commit()
            
            return {"status": status, "telefono": telefono}
    
    def get_clientes(self, limit: int = 100, order_by: str = "ultimo_pedido DESC") -> pd.DataFrame:
        """Obtiene lista de clientes"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                f"""SELECT telefono, nombre, direccion_actual, total_pedidos, 
                    total_gastado, ticket_promedio, primer_pedido, ultimo_pedido,
                    es_cliente_frecuente, frecuencia_dias
                    FROM clientes ORDER BY {order_by} LIMIT ?""",
                conn, params=(limit,)
            )
    
    def get_cliente_detalle(self, telefono: str) -> Dict[str, Any]:
        """Obtiene detalle completo de un cliente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM clientes WHERE telefono = ?", (telefono,))
            cliente = cursor.fetchone()
            
            if not cliente:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            cliente_dict = dict(zip(columns, cliente))
            
            # Obtener historial de pedidos
            historial = pd.read_sql_query(
                "SELECT * FROM historial_cliente WHERE telefono = ? ORDER BY fecha_pedido DESC",
                conn, params=(telefono,)
            )
            cliente_dict['historial'] = historial.to_dict('records')
            
            return cliente_dict
    
    def get_clientes_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de clientes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM clientes")
            total_clientes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE es_cliente_frecuente = 1")
            clientes_frecuentes = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(total_gastado) FROM clientes")
            gasto_promedio = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(ticket_promedio) FROM clientes")
            ticket_promedio = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE total_pedidos = 1")
            clientes_unicos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE total_pedidos >= 5")
            clientes_muy_frecuentes = cursor.fetchone()[0]
            
            # Top 10 por dinero gastado
            top_por_dinero = pd.read_sql_query(
                """SELECT nombre, telefono, total_pedidos, total_gastado, ticket_promedio
                   FROM clientes ORDER BY total_gastado DESC LIMIT 10""",
                conn
            )
            
            # Top 10 por cantidad de pedidos
            top_por_pedidos = pd.read_sql_query(
                """SELECT nombre, telefono, total_pedidos, total_gastado, ticket_promedio
                   FROM clientes ORDER BY total_pedidos DESC LIMIT 10""",
                conn
            )
            
            return {
                "total_clientes": total_clientes,
                "clientes_frecuentes": clientes_frecuentes,
                "clientes_unicos": clientes_unicos,
                "clientes_muy_frecuentes": clientes_muy_frecuentes,
                "gasto_promedio_por_cliente": round(gasto_promedio, 2),
                "ticket_promedio_global": round(ticket_promedio, 2),
                "tasa_retencion": round((total_clientes - clientes_unicos) / total_clientes * 100, 1) if total_clientes > 0 else 0,
                "top_clientes": top_por_dinero.to_dict('records'),
                "top_por_dinero": top_por_dinero.to_dict('records'),
                "top_por_pedidos": top_por_pedidos.to_dict('records')
            }
    
    def buscar_cliente(self, query: str) -> pd.DataFrame:
        """Busca clientes por nombre o teléfono"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                """SELECT telefono, nombre, direccion_actual, total_pedidos, total_gastado
                   FROM clientes 
                   WHERE nombre LIKE ? OR telefono LIKE ?
                   ORDER BY total_gastado DESC LIMIT 20""",
                conn, params=(f'%{query}%', f'%{query}%')
            )
