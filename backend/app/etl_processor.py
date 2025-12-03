"""
ETL Processor - Procesamiento de archivos Excel de ventas
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ETLProcessor:
    """Procesador ETL para archivos Excel de ventas de Pizzería MAX"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        
    def process_excel(self, file_path: Path) -> pd.DataFrame:
        """
        Procesa archivo Excel y genera dataset diario
        
        Args:
            file_path: Ruta al archivo Excel
            
        Returns:
            DataFrame con datos diarios agregados
        """
        logger.info(f"Procesando archivo: {file_path}")
        
        # Leer hojas del Excel con context manager
        try:
            with pd.ExcelFile(file_path) as excel_data:
                logger.info(f"Hojas encontradas: {excel_data.sheet_names}")
                
                # Validar hojas requeridas
                required_sheets = ['Pedidos', 'Detalles', 'Visitas']
                missing_sheets = [s for s in required_sheets if s not in excel_data.sheet_names]
                if missing_sheets:
                    raise ValueError(f"Faltan hojas requeridas: {', '.join(missing_sheets)}")
                
                # Leer hojas
                df_pedidos = pd.read_excel(excel_data, sheet_name='Pedidos')
                df_detalles = pd.read_excel(excel_data, sheet_name='Detalles')
                df_visitas = pd.read_excel(excel_data, sheet_name='Visitas')
        except Exception as e:
            raise ValueError(f"Error leyendo archivo Excel: {str(e)}")
        
        logger.info(f"Pedidos: {len(df_pedidos)} registros")
        logger.info(f"Detalles: {len(df_detalles)} registros")
        logger.info(f"Visitas: {len(df_visitas)} registros")
        
        # Procesar cada hoja
        df_pedidos_clean = self._process_pedidos(df_pedidos)
        df_detalles_clean = self._process_detalles(df_detalles)
        df_visitas_clean = self._process_visitas(df_visitas)
        
        # Combinar datos por fecha
        df_daily = self._aggregate_daily(df_pedidos_clean, df_detalles_clean, df_visitas_clean)
        
        # Extraer datos de clientes
        df_clientes = self._extract_clientes(df_pedidos)
        
        logger.info(f"Dataset diario generado: {len(df_daily)} días")
        logger.info(f"Clientes extraídos: {len(df_clientes)} registros")
        
        # Guardar clientes como atributo para acceso posterior
        self.clientes_data = df_clientes
        
        return df_daily
    
    def _extract_clientes(self, df_pedidos: pd.DataFrame) -> pd.DataFrame:
        """
        Extrae datos de clientes de la hoja de Pedidos
        
        Returns:
            DataFrame con datos de clientes para insertar en BD
        """
        cliente_cols = ['Cliente', 'Teléfono', 'Dirección', 'Total', 'Tipo de servicio', 'Fecha de creación']
        
        # Verificar que existan las columnas necesarias
        available_cols = [col for col in cliente_cols if col in df_pedidos.columns]
        if 'Teléfono' not in available_cols:
            logger.warning("No se encontró columna 'Teléfono' para extraer clientes")
            return pd.DataFrame()
        
        df_clientes = df_pedidos[available_cols].copy()
        
        # Limpiar datos
        df_clientes = df_clientes.rename(columns={
            'Cliente': 'nombre',
            'Teléfono': 'telefono',
            'Dirección': 'direccion',
            'Total': 'total_pedido',
            'Tipo de servicio': 'tipo_servicio',
            'Fecha de creación': 'fecha_pedido'
        })
        
        # Convertir fecha
        if 'fecha_pedido' in df_clientes.columns:
            df_clientes['fecha_pedido'] = pd.to_datetime(
                df_clientes['fecha_pedido'], 
                format='%d/%m/%Y | %H:%M', 
                errors='coerce'
            )
            df_clientes['fecha_pedido'] = df_clientes['fecha_pedido'].dt.date
        
        # Filtrar registros sin teléfono válido
        df_clientes = df_clientes[df_clientes['telefono'].notna()]
        df_clientes = df_clientes[df_clientes['telefono'].astype(str).str.len() >= 5]
        
        logger.info(f"✅ Extraídos {len(df_clientes)} registros de clientes")
        
        return df_clientes
    
    def get_clientes_data(self) -> pd.DataFrame:
        """Retorna los datos de clientes extraídos del último procesamiento"""
        return getattr(self, 'clientes_data', pd.DataFrame())
    
    def _process_pedidos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa hoja de Pedidos"""
        df = df.copy()
        
        # Mapear columnas de OlaClick al formato esperado
        column_mapping = {
            'Estado del pedido': 'Estado',
            'Fecha de creación': 'Fecha de creación'
        }
        
        # Renombrar columnas si existen
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]
        
        # Validar columnas requeridas (flexibles)
        fecha_col = 'Fecha de creación'
        total_col = 'Total'
        estado_col = 'Estado del pedido' if 'Estado del pedido' in df.columns else 'Estado'
        servicio_col = 'Tipo de servicio'
        
        required_cols = [fecha_col, total_col, estado_col, servicio_col]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Faltan columnas en Pedidos: {', '.join(missing_cols)}")
        
        # Convertir fecha
        df['fecha'] = pd.to_datetime(df[fecha_col], format='%d/%m/%Y | %H:%M', errors='coerce')
        if df['fecha'].isna().all():
            # Intentar otro formato
            df['fecha'] = pd.to_datetime(df[fecha_col], errors='coerce')
        df = df.dropna(subset=['fecha'])
        df['fecha'] = df['fecha'].dt.date
        
        # Filtrar solo pedidos finalizados/completados
        df = df[df[estado_col].str.lower().str.contains('finalizado|completado|entregado', na=False)]
        
        # Limpiar valores numéricos
        df['Total'] = pd.to_numeric(df[total_col], errors='coerce').fillna(0)
        df['Tipo de servicio'] = df[servicio_col]
        
        return df
    
    def _process_detalles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa hoja de Detalles"""
        df = df.copy()
        
        # Mapear columnas de OlaClick
        fecha_col = 'Fecha de creación'
        nombre_col = 'Nombre del producto' if 'Nombre del producto' in df.columns else 'Nombre'
        cantidad_col = 'Cantidad'
        categoria_col = 'Categoría'
        
        # Validar columnas
        required_cols = [fecha_col, nombre_col, cantidad_col]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Faltan columnas en Detalles: {', '.join(missing_cols)}")
        
        # Convertir fecha
        df['fecha'] = pd.to_datetime(df[fecha_col], format='%d/%m/%Y | %H:%M', errors='coerce')
        if df['fecha'].isna().all():
            df['fecha'] = pd.to_datetime(df[fecha_col], errors='coerce')
        df = df.dropna(subset=['fecha'])
        df['fecha'] = df['fecha'].dt.date
        
        # Limpiar cantidad
        df['Cantidad'] = pd.to_numeric(df[cantidad_col], errors='coerce').fillna(0)
        
        # Categorizar productos
        df['Nombre'] = df[nombre_col].astype(str).str.lower()
        
        # === DETECTAR PAQUETES DE MÚLTIPLES PIZZAS ===
        # "2 pizzas grandes", "2 pizzas de 3 ing", etc. = 2 pizzas por unidad
        # "3 pizzas", etc. = 3 pizzas por unidad
        df['multiplicador_pizza'] = 1  # Por defecto 1 pizza
        
        # Detectar "2 pizzas" en el nombre
        df.loc[df['Nombre'].str.contains(r'2\s*pizzas?', na=False, case=False, regex=True), 'multiplicador_pizza'] = 2
        
        # Detectar "3 pizzas" en el nombre
        df.loc[df['Nombre'].str.contains(r'3\s*pizzas?', na=False, case=False, regex=True), 'multiplicador_pizza'] = 3
        
        # Detectar "4 pizzas" en el nombre
        df.loc[df['Nombre'].str.contains(r'4\s*pizzas?', na=False, case=False, regex=True), 'multiplicador_pizza'] = 4
        
        # Log para debug
        paquetes_2 = df[df['multiplicador_pizza'] == 2]
        paquetes_3 = df[df['multiplicador_pizza'] == 3]
        if len(paquetes_2) > 0:
            logger.info(f"🍕 Detectados {len(paquetes_2)} productos de 2 pizzas")
        if len(paquetes_3) > 0:
            logger.info(f"🍕 Detectados {len(paquetes_3)} productos de 3 pizzas")
        
        # Identificar categorías
        df['es_pizza'] = df['Nombre'].str.contains('pizza', na=False, case=False)
        df['es_pizza_pastor'] = df['Nombre'].str.contains('pastor', na=False, case=False)
        df['es_pizza_chuleta'] = df['Nombre'].str.contains('chuli|chuleta', na=False, case=False)
        df['es_alitas'] = df['Nombre'].str.contains('alita', na=False, case=False)
        df['es_baguette'] = df['Nombre'].str.contains('baguette', na=False, case=False)
        df['es_papas_gajo'] = df['Nombre'].str.contains('papas gajo|papa gajo|papas a gajo|orden de papas', na=False, case=False)
        
        # También considerar categoría "Paquetes" que contenga "pizza" como pizza
        if categoria_col in df.columns:
            df['Categoría'] = df[categoria_col].astype(str).str.lower()
            # Paquetes con pizza en el nombre también cuentan
            df['es_pizza'] = df['es_pizza'] | (
                df['Categoría'].str.contains('paquete', na=False, case=False) & 
                df['Nombre'].str.contains('pizza', na=False, case=False)
            )
            df['es_pizza'] = df['es_pizza'] | df['Categoría'].str.contains('pizza', na=False, case=False)
            df['es_baguette'] = df['es_baguette'] | df['Categoría'].str.contains('baguette', na=False, case=False)
            df['es_papas_gajo'] = df['es_papas_gajo'] | df['Categoría'].str.contains('papas|papa', na=False, case=False)
        
        # Calcular cantidad real de pizzas (cantidad * multiplicador)
        df['cantidad_pizzas_real'] = df['Cantidad'] * df['multiplicador_pizza']
        
        return df
    
    def _process_visitas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Procesa hoja de Visitas"""
        df = df.copy()
        
        # Validar columnas
        required_cols = ['Fecha']
        if 'Fecha' not in df.columns:
            raise ValueError("Falta columna 'Fecha' en Visitas")
        
        # Convertir fecha
        df['fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
        if df['fecha'].isna().all():
            df['fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        df['fecha'] = df['fecha'].dt.date
        
        # Mapear columnas de OlaClick
        column_mapping = {
            'Menús Vistos': 'Total de visitas',
            'Pedido iniciado': 'Pedidos iniciados',
            'Pedido creado': 'Pedidos creados'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df[new_col] = pd.to_numeric(df[old_col], errors='coerce').fillna(0)
        
        # Limpiar columnas numéricas (si ya existen)
        numeric_cols = ['Total de visitas', 'Pedidos iniciados', 'Pedidos creados']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    
    def _aggregate_daily(self, df_pedidos: pd.DataFrame, df_detalles: pd.DataFrame, 
                        df_visitas: pd.DataFrame) -> pd.DataFrame:
        """Agrega datos por día con métricas avanzadas"""
        
        # === ANÁLISIS TEMPORAL POR HORA ===
        if 'fecha_hora' not in df_pedidos.columns:
            # Extraer hora del pedido si existe fecha completa
            if 'Fecha de creación' in df_pedidos.columns:
                df_pedidos['fecha_hora'] = pd.to_datetime(
                    df_pedidos['Fecha de creación'], 
                    format='%d/%m/%Y | %H:%M', 
                    errors='coerce'
                )
                df_pedidos['hora'] = df_pedidos['fecha_hora'].dt.hour
        
        # Agregar pedidos por día
        pedidos_daily = df_pedidos.groupby('fecha').agg({
            'Total': 'sum',
            'Tipo de servicio': lambda x: x.value_counts().to_dict()
        }).reset_index()
        
        pedidos_daily.columns = ['fecha', 'total_ventas_dia', 'tipo_servicio_dict']
        pedidos_daily['total_pedidos'] = df_pedidos.groupby('fecha').size().values
        
        # === TICKET PROMEDIO ===
        pedidos_daily['ticket_promedio'] = (
            pedidos_daily['total_ventas_dia'] / pedidos_daily['total_pedidos'].replace(0, 1)
        ).round(2)
        
        # === ANÁLISIS POR HORA (pedidos en hora pico 18-22) ===
        if 'hora' in df_pedidos.columns:
            hora_pico = df_pedidos[df_pedidos['hora'].between(18, 22)].groupby('fecha').size()
            hora_almuerzo = df_pedidos[df_pedidos['hora'].between(12, 15)].groupby('fecha').size()
            
            pedidos_daily = pedidos_daily.merge(
                hora_pico.reset_index().rename(columns={0: 'pedidos_hora_pico'}),
                on='fecha', how='left'
            )
            pedidos_daily = pedidos_daily.merge(
                hora_almuerzo.reset_index().rename(columns={0: 'pedidos_hora_almuerzo'}),
                on='fecha', how='left'
            )
            pedidos_daily['pedidos_hora_pico'] = pedidos_daily['pedidos_hora_pico'].fillna(0).astype(int)
            pedidos_daily['pedidos_hora_almuerzo'] = pedidos_daily['pedidos_hora_almuerzo'].fillna(0).astype(int)
        else:
            pedidos_daily['pedidos_hora_pico'] = 0
            pedidos_daily['pedidos_hora_almuerzo'] = 0
        
        # === VENTAS POR TIPO DE SERVICIO ===
        def calc_ventas_servicio(df, fecha, tipo):
            mask = (df['fecha'] == fecha) & (df['Tipo de servicio'].str.lower().str.contains(tipo, na=False))
            return df.loc[mask, 'Total'].sum()
        
        pedidos_daily['ventas_domicilio'] = pedidos_daily['fecha'].apply(
            lambda f: calc_ventas_servicio(df_pedidos, f, 'domicilio')
        )
        pedidos_daily['ventas_local'] = pedidos_daily['fecha'].apply(
            lambda f: calc_ventas_servicio(df_pedidos, f, 'llevar')
        )
        
        # === PORCENTAJES DE TIPO DE SERVICIO ===
        def calc_servicio_pct(row, tipo):
            if isinstance(row['tipo_servicio_dict'], dict):
                total = sum(row['tipo_servicio_dict'].values())
                if total > 0:
                    for key, val in row['tipo_servicio_dict'].items():
                        if tipo.lower() in str(key).lower():
                            return (val / total) * 100
            return 0.0
        
        pedidos_daily['tipo_servicio_domicilio'] = pedidos_daily.apply(
            lambda x: calc_servicio_pct(x, 'domicilio'), axis=1
        ).fillna(0.0)
        pedidos_daily['tipo_servicio_llevar'] = pedidos_daily.apply(
            lambda x: calc_servicio_pct(x, 'llevar'), axis=1
        ).fillna(0.0)
        pedidos_daily = pedidos_daily.drop('tipo_servicio_dict', axis=1)
        
        # Agregar detalles por día
        # IMPORTANTE: Para pizzas, usar cantidad_pizzas_real que ya considera paquetes de 2, 3, 4 pizzas
        detalles_daily = df_detalles.groupby('fecha').agg({
            # Pizzas: usar cantidad_pizzas_real (considera multiplicador por paquetes)
            'es_pizza': lambda x: (x * df_detalles.loc[x.index, 'cantidad_pizzas_real']).sum(),
            'es_pizza_pastor': lambda x: (x * df_detalles.loc[x.index, 'cantidad_pizzas_real']).sum(),
            'es_pizza_chuleta': lambda x: (x * df_detalles.loc[x.index, 'cantidad_pizzas_real']).sum(),
            # Otros productos: usar Cantidad normal
            'es_alitas': lambda x: (x * df_detalles.loc[x.index, 'Cantidad']).sum(),
            'es_baguette': lambda x: (x * df_detalles.loc[x.index, 'Cantidad']).sum(),
            'es_papas_gajo': lambda x: (x * df_detalles.loc[x.index, 'Cantidad']).sum(),
        }).reset_index()
        
        detalles_daily.columns = ['fecha', 'pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta', 'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas']
        
        # Agregar visitas por día
        visitas_cols = ['fecha']
        if 'Total de visitas' in df_visitas.columns:
            visitas_cols.append('Total de visitas')
        if 'Pedidos iniciados' in df_visitas.columns:
            visitas_cols.append('Pedidos iniciados')
        if 'Pedidos creados' in df_visitas.columns:
            visitas_cols.append('Pedidos creados')
        
        visitas_daily = df_visitas[visitas_cols].groupby('fecha').sum().reset_index()
        visitas_daily.columns = ['fecha', 'total_visitas', 'pedidos_iniciados', 'pedidos_creados']
        
        # === TASA DE CONVERSIÓN ===
        visitas_daily['tasa_conversion'] = (
            visitas_daily['pedidos_creados'] / visitas_daily['total_visitas'].replace(0, 1) * 100
        ).round(2)
        
        # Combinar todos los datos
        df_daily = pedidos_daily.merge(detalles_daily, on='fecha', how='left')
        df_daily = df_daily.merge(visitas_daily, on='fecha', how='left')
        
        # Rellenar NaN con 0
        df_daily = df_daily.fillna(0)
        
        # Convertir fecha a datetime
        df_daily['fecha'] = pd.to_datetime(df_daily['fecha'])
        
        # Ordenar por fecha
        df_daily = df_daily.sort_values('fecha').reset_index(drop=True)
        
        # Asegurar tipos correctos
        int_cols = ['total_pedidos', 'pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta', 
                   'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas', 
                   'total_visitas', 'pedidos_iniciados', 'pedidos_creados',
                   'pedidos_hora_pico', 'pedidos_hora_almuerzo']
        for col in int_cols:
            if col in df_daily.columns:
                df_daily[col] = pd.to_numeric(df_daily[col], errors='coerce').fillna(0).astype(int)
        
        float_cols = ['total_ventas_dia', 'tipo_servicio_domicilio', 'tipo_servicio_llevar',
                     'ticket_promedio', 'ventas_domicilio', 'ventas_local', 'tasa_conversion']
        for col in float_cols:
            if col in df_daily.columns:
                df_daily[col] = pd.to_numeric(df_daily[col], errors='coerce').fillna(0.0).astype(float)
        
        logger.info(f"📊 Nuevas métricas agregadas: ticket_promedio, hora_pico, ventas_por_servicio, tasa_conversion")
        
        # Verificación final: reemplazar cualquier NaN, inf o -inf restante
        df_daily = df_daily.replace([float('inf'), float('-inf')], 0)
        df_daily = df_daily.fillna(0)
        
        return df_daily
