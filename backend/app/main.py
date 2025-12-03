"""
FastAPI Main Application - Pizzería MAX Predicción de Ventas
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
import uvicorn
import pandas as pd

from app.etl_processor import ETLProcessor
from app.predictor_simple import PredictorSimple
from app.predictor_pro import PredictorPro
from app.gpt_insights import GPTInsightGenerator
from app.database import SalesDatabase

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Pizzería MAX - Predicción de Ventas API",
    description="Sistema inteligente de predicción de ventas con ML Profesional",
    version="2.0.0"
)

# CORS para permitir conexión con frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorios
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Inicializar procesadores
etl_processor = ETLProcessor(DATA_DIR)
predictor_simple = PredictorSimple(MODELS_DIR)  # Predictor básico (promedios)
predictor_pro = PredictorPro(MODELS_DIR, DATA_DIR)  # Predictor ML avanzado
predictor = predictor_pro  # Usar el predictor profesional por defecto
gpt_generator = GPTInsightGenerator()
db = SalesDatabase(DATA_DIR / "pizzeria_max.db")


@app.get("/")
async def root():
    """Endpoint raíz - Health check"""
    return {
        "status": "online",
        "service": "Pizzería MAX - Predicción de Ventas",
        "version": "1.0.0"
    }


@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Endpoint para subir archivo Excel y procesarlo
    
    Args:
        file: Archivo Excel con hojas Pedidos, Detalles, Visitas
        
    Returns:
        JSON con datos procesados y estadísticas
    """
    try:
        logger.info(f"Recibiendo archivo: {file.filename}")
        
        # Validar extensión
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser formato Excel (.xlsx o .xls)"
            )
        
        # Guardar archivo temporalmente
        temp_file = DATA_DIR / f"temp_{file.filename}"
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Procesar Excel
        logger.info("Procesando archivo Excel...")
        df_daily = etl_processor.process_excel(temp_file)
        
        # Guardar en base de datos (acumular, no sobrescribir)
        db_result = db.insert_daily_data(df_daily, file.filename)
        logger.info(f"Datos guardados en BD: {db_result}")
        
        # Obtener todos los datos históricos
        df_all = db.get_all_data()
        
        # Asegurar que las columnas nuevas existan (rellenar con 0 si faltan)
        required_columns = ['pizzas_pastor', 'pizzas_chuleta', 'alitas_vendidas']
        for col in required_columns:
            if col not in df_all.columns:
                logger.warning(f"⚠️ Columna {col} no existe, agregando con valores 0")
                df_all[col] = 0
        
        # Guardar dataset completo en parquet (para modelos)
        output_file = DATA_DIR / "ventas_diarias.parquet"
        df_all.to_parquet(output_file, index=False)
        logger.info(f"✅ Dataset completo guardado: {len(df_all)} registros con {len(df_all.columns)} columnas")
        
        # Eliminar archivo temporal (con retry por si está bloqueado)
        try:
            import time
            time.sleep(0.5)  # Esperar un momento
            temp_file.unlink()
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal: {e}")
            # No es crítico, continuar
        
        # Generar estadísticas del archivo subido
        stats_archivo = {
            "registros_nuevos": db_result.get('registros_nuevos', 0),
            "registros_actualizados": db_result.get('registros_actualizados', 0),
            "fechas_duplicadas": db_result.get('fechas_duplicadas', 0),
            "fecha_inicio_archivo": db_result.get('fecha_inicio', 'N/A'),
            "fecha_fin_archivo": db_result.get('fecha_fin', 'N/A')
        }
        
        # Generar mensaje de advertencia si hay duplicados
        mensaje = "Archivo procesado exitosamente"
        if stats_archivo['fechas_duplicadas'] > 0:
            mensaje += f". ⚠️ {stats_archivo['fechas_duplicadas']} fechas duplicadas fueron REEMPLAZADAS (no sumadas)"
        
        # Estadísticas históricas completas
        db_stats = db.get_statistics()
        
        # Calcular gap temporal y confianza
        from datetime import datetime, date
        try:
            if db_stats['fecha_fin']:
                # Intentar parsear la fecha
                fecha_fin_str = str(db_stats['fecha_fin'])
                fecha_fin_datos = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            else:
                fecha_fin_datos = None
        except Exception as e:
            logger.warning(f"Error parseando fecha_fin: {e}, valor: {db_stats['fecha_fin']}")
            fecha_fin_datos = None
        
        fecha_hoy = date.today()
        dias_desde_ultima_actualizacion = (fecha_hoy - fecha_fin_datos).days if fecha_fin_datos else 999
        
        logger.info(f"Gap temporal: {dias_desde_ultima_actualizacion} días (última: {fecha_fin_datos}, hoy: {fecha_hoy})")
        
        # Calcular nivel de confianza (0-100)
        if dias_desde_ultima_actualizacion <= 3:
            confianza = 95
        elif dias_desde_ultima_actualizacion <= 7:
            confianza = 85
        elif dias_desde_ultima_actualizacion <= 14:
            confianza = 70
        elif dias_desde_ultima_actualizacion <= 30:
            confianza = 50
        else:
            confianza = 30
        
        # Reemplazar NaN antes de calcular stats
        df_all = df_all.fillna(0)
        
        stats = {
            "total_dias": db_stats['total_registros'],
            "fecha_inicio": str(db_stats['fecha_inicio']) if db_stats['fecha_inicio'] else None,
            "fecha_fin": str(db_stats['fecha_fin']) if db_stats['fecha_fin'] else None,
            "dias_desde_ultima_actualizacion": dias_desde_ultima_actualizacion,
            "nivel_confianza": confianza,
            "ventas_totales": float(db_stats['ventas_totales_historicas']) if db_stats['ventas_totales_historicas'] else 0.0,
            "promedio_ventas_dia": float(df_all['total_ventas_dia'].mean()) if len(df_all) > 0 else 0.0,
            "total_pizzas": int(df_all['pizzas_vendidas'].sum()) if len(df_all) > 0 else 0,
            "total_baguettes": int(df_all['baguettes_vendidas'].sum()) if len(df_all) > 0 else 0,
            "total_papas_gajo": int(df_all['papas_gajo_vendidas'].sum()) if len(df_all) > 0 else 0,
            "total_pedidos": int(df_all['total_pedidos'].sum()) if len(df_all) > 0 else 0,
            "total_archivos_procesados": db_stats['total_archivos_procesados'],
            **stats_archivo
        }
        
        # Datos recientes (últimos 30 días del histórico completo)
        recent_data = df_all.tail(30).to_dict('records')
        for record in recent_data:
            if isinstance(record['fecha'], str):
                pass  # Ya es string
            else:
                record['fecha'] = record['fecha'].strftime('%Y-%m-%d')
        
        return JSONResponse(content={
            "success": True,
            "message": mensaje,
            "stats": stats,
            "recent_data": recent_data
        })
        
    except ValueError as e:
        error_msg = f"Error de validación: {str(e)}"
        logger.error(error_msg)
        print(f"ERROR DETALLADO: {error_msg}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = f"Error procesando archivo: {str(e)}"
        logger.error(error_msg)
        print(f"ERROR DETALLADO: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.post("/reset_database")
async def reset_database():
    """
    RESETEAR COMPLETAMENTE la base de datos
    ⚠️ BORRA TODOS LOS DATOS
    """
    try:
        logger.warning("🔥 INICIANDO RESET COMPLETO DE BASE DE DATOS")
        
        import sqlite3
        
        # Conectar a BD
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Borrar todos los datos
        cursor.execute('DELETE FROM ventas_diarias')
        ventas_borradas = cursor.rowcount
        
        cursor.execute('DELETE FROM archivos_procesados')
        archivos_borrados = cursor.rowcount
        
        # Resetear IDs
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="ventas_diarias"')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="archivos_procesados"')
        
        conn.commit()
        conn.close()
        
        logger.warning(f"✅ Borrados {ventas_borradas} registros de ventas")
        logger.warning(f"✅ Borrados {archivos_borrados} archivos procesados")
        
        # Crear parquet vacío
        import pandas as pd
        df_vacio = pd.DataFrame(columns=[
            'fecha', 'total_ventas_dia', 'total_pedidos',
            'pizzas_vendidas', 'pizzas_pastor', 'pizzas_chuleta',
            'alitas_vendidas', 'baguettes_vendidas', 'papas_gajo_vendidas'
        ])
        df_vacio['fecha'] = pd.to_datetime(df_vacio['fecha'])
        
        parquet_path = DATA_DIR / "ventas_diarias.parquet"
        df_vacio.to_parquet(parquet_path, index=False)
        
        logger.warning("✅ Parquet reseteado")
        
        return {
            "success": True,
            "message": "Base de datos reseteada completamente",
            "ventas_borradas": ventas_borradas,
            "archivos_borrados": archivos_borrados
        }
        
    except Exception as e:
        logger.error(f"Error reseteando BD: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train_model")
async def train_model():
    """
    Entrenar modelos de predicción con los datos procesados
    
    Returns:
        JSON con métricas de entrenamiento
    """
    try:
        logger.info("Iniciando entrenamiento de modelos...")
        
        # Cargar datos
        data_file = DATA_DIR / "ventas_diarias.parquet"
        if not data_file.exists():
            raise HTTPException(
                status_code=400,
                detail="No hay datos procesados. Primero sube un archivo Excel."
            )
        
        # Entrenar modelos
        metrics = predictor.train_models(data_file)
        
        return JSONResponse(content={
            "success": True,
            "message": "Modelos entrenados exitosamente",
            "metrics": metrics
        })
        
    except Exception as e:
        logger.error(f"Error entrenando modelos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/predict")
async def get_predictions(days: int = 7):
    """
    Obtener predicciones para los próximos días
    
    Args:
        days: Número de días a predecir (default: 7)
        
    Returns:
        JSON con predicciones
    """
    try:
        logger.info(f"Generando predicciones para {days} días...")
        
        # Cargar datos
        data_file = DATA_DIR / "ventas_diarias.parquet"
        if not data_file.exists():
            raise HTTPException(
                status_code=400,
                detail="No hay datos procesados. Primero sube un archivo Excel."
            )
        
        # Cargar modelos (por si el servidor se reinició)
        predictor.cargar_modelos()
        
        # Generar predicciones
        predictions = predictor.predict_next_days(data_file, days=days)
        
        # Convertir fechas a string
        for pred in predictions:
            pred['fecha'] = pred['fecha'].strftime('%Y-%m-%d')
        
        return JSONResponse(content={
            "success": True,
            "predictions": predictions
        })
        
    except Exception as e:
        logger.error(f"Error generando predicciones: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/historical")
async def get_historical_data():
    """
    Obtiene todos los datos históricos de la base de datos
    
    Returns:
        JSON con datos históricos completos y estadísticas
    """
    try:
        logger.info("Obteniendo datos históricos...")
        
        # Obtener estadísticas
        stats = db.get_statistics()
        
        # Obtener todos los datos
        df_all = db.get_all_data()
        
        # Reemplazar NaN, inf, -inf con 0
        df_all = df_all.replace([float('inf'), float('-inf')], 0)
        df_all = df_all.fillna(0)
        
        if len(df_all) == 0:
            return JSONResponse(content={
                "success": True,
                "message": "No hay datos históricos",
                "stats": stats,
                "data": []
            })
        
        # Calcular gap temporal y confianza
        from datetime import datetime, date
        try:
            if stats['fecha_fin']:
                fecha_fin_str = str(stats['fecha_fin'])
                fecha_fin_datos = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            else:
                fecha_fin_datos = None
        except Exception as e:
            logger.warning(f"Error parseando fecha_fin en /historical: {e}, valor: {stats['fecha_fin']}")
            fecha_fin_datos = None
        
        fecha_hoy = date.today()
        dias_desde_ultima_actualizacion = (fecha_hoy - fecha_fin_datos).days if fecha_fin_datos else 999
        
        # Calcular nivel de confianza
        if dias_desde_ultima_actualizacion <= 3:
            confianza = 95
        elif dias_desde_ultima_actualizacion <= 7:
            confianza = 85
        elif dias_desde_ultima_actualizacion <= 14:
            confianza = 70
        elif dias_desde_ultima_actualizacion <= 30:
            confianza = 50
        else:
            confianza = 30
        
        # Calcular estadísticas completas
        stats_completas = {
            "total_dias": stats['total_registros'],
            "fecha_inicio": stats['fecha_inicio'],
            "fecha_fin": stats['fecha_fin'],
            "dias_desde_ultima_actualizacion": dias_desde_ultima_actualizacion,
            "nivel_confianza": confianza,
            "ventas_totales": stats['ventas_totales_historicas'],
            "promedio_ventas_dia": float(df_all['total_ventas_dia'].mean()) if len(df_all) > 0 else 0,
            "total_pizzas": int(df_all['pizzas_vendidas'].sum()) if len(df_all) > 0 else 0,
            "total_baguettes": int(df_all['baguettes_vendidas'].sum()) if len(df_all) > 0 else 0,
            "total_papas_gajo": int(df_all['papas_gajo_vendidas'].sum()) if len(df_all) > 0 else 0,
            "total_pedidos": int(df_all['total_pedidos'].sum()) if len(df_all) > 0 else 0,
            "total_archivos_procesados": stats['total_archivos_procesados']
        }
        
        # Convertir a lista de diccionarios
        data = df_all.to_dict('records')
        for record in data:
            if not isinstance(record['fecha'], str):
                record['fecha'] = record['fecha'].strftime('%Y-%m-%d')
            if 'fecha_carga' in record and not isinstance(record['fecha_carga'], str):
                record['fecha_carga'] = record['fecha_carga'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Datos recientes (últimos 30 días)
        recent_data = df_all.tail(30).to_dict('records')
        for record in recent_data:
            if not isinstance(record['fecha'], str):
                record['fecha'] = record['fecha'].strftime('%Y-%m-%d')
        
        return JSONResponse(content={
            "success": True,
            "stats": stats_completas,
            "data": data,
            "recent_data": recent_data
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo histórico: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/analytics")
async def get_analytics():
    """
    Obtiene análisis detallado de datos históricos
    Incluye análisis por día, semana, mes
    
    Returns:
        JSON con análisis detallado
    """
    try:
        logger.info("Generando análisis detallado...")
        
        # Obtener todos los datos
        df_all = db.get_all_data()
        
        if len(df_all) == 0:
            raise HTTPException(status_code=400, detail="No hay datos para analizar")
        
        # Convertir fecha a datetime para análisis
        df_all['fecha'] = pd.to_datetime(df_all['fecha'])
        df_all['año'] = df_all['fecha'].dt.year
        df_all['mes'] = df_all['fecha'].dt.month
        df_all['dia_semana'] = df_all['fecha'].dt.dayofweek
        df_all['semana'] = df_all['fecha'].dt.isocalendar().week
        
        # Análisis por mes
        analisis_mensual = df_all.groupby(['año', 'mes']).agg({
            'total_ventas_dia': ['sum', 'mean', 'std'],
            'total_pedidos': 'sum',
            'pizzas_vendidas': 'sum',
            'baguettes_vendidas': 'sum',
            'papas_gajo_vendidas': 'sum'
        }).reset_index()
        
        analisis_mensual.columns = ['_'.join(col).strip('_') for col in analisis_mensual.columns.values]
        analisis_mensual_dict = analisis_mensual.to_dict('records')
        
        # Análisis por día de la semana
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        analisis_semanal = df_all.groupby('dia_semana').agg({
            'total_ventas_dia': ['mean', 'sum'],
            'total_pedidos': 'mean',
            'pizzas_vendidas': 'mean'
        }).reset_index()
        
        analisis_semanal.columns = ['_'.join(col).strip('_') for col in analisis_semanal.columns.values]
        analisis_semanal['dia_nombre'] = analisis_semanal['dia_semana'].apply(lambda x: dias_semana[int(x)])
        analisis_semanal_dict = analisis_semanal.to_dict('records')
        
        # Top 10 mejores días
        top_dias = df_all.nlargest(10, 'total_ventas_dia')[
            ['fecha', 'total_ventas_dia', 'total_pedidos', 'pizzas_vendidas']
        ].copy()
        top_dias['fecha'] = top_dias['fecha'].dt.strftime('%Y-%m-%d')
        top_dias_dict = top_dias.to_dict('records')
        
        # Tendencias
        primer_mes_ventas = df_all.head(7)['total_ventas_dia'].mean()
        ultimo_mes_ventas = df_all.tail(7)['total_ventas_dia'].mean()
        tendencia_porcentaje = ((ultimo_mes_ventas - primer_mes_ventas) / primer_mes_ventas * 100) if primer_mes_ventas > 0 else 0
        
        return JSONResponse(content={
            "success": True,
            "analisis_mensual": analisis_mensual_dict,
            "analisis_semanal": analisis_semanal_dict,
            "top_dias": top_dias_dict,
            "tendencias": {
                "primer_periodo_promedio": float(primer_mes_ventas),
                "ultimo_periodo_promedio": float(ultimo_mes_ventas),
                "cambio_porcentual": float(tendencia_porcentaje)
            },
            "resumen": {
                "total_dias_analizados": len(df_all),
                "venta_promedio_diaria": float(df_all['total_ventas_dia'].mean()),
                "mejor_dia_ventas": float(df_all['total_ventas_dia'].max()),
                "peor_dia_ventas": float(df_all['total_ventas_dia'].min())
            }
        })
        
    except Exception as e:
        logger.error(f"Error generando análisis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.post("/insight")
async def generate_insight():
    """
    Generar insights con GPT basados en predicciones
    
    Returns:
        JSON con análisis en lenguaje natural
    """
    try:
        logger.info("Generando insights con GPT...")
        
        # Cargar datos y predicciones
        data_file = DATA_DIR / "ventas_diarias.parquet"
        if not data_file.exists():
            raise HTTPException(
                status_code=400,
                detail="No hay datos procesados."
            )
        
        # Cargar modelos
        predictor.cargar_modelos()
        
        # Generar predicciones
        predictions = predictor.predict_next_days(data_file, days=7)
        
        # Generar insight con GPT
        insight = await gpt_generator.generate_insight(data_file, predictions)
        
        return JSONResponse(content={
            "success": True,
            "insight": insight
        })
        
    except Exception as e:
        logger.error(f"Error generando insight: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# ==================== ENDPOINTS ML AVANZADO ====================

@app.get("/model/info")
async def get_model_info():
    """
    Obtiene información del modelo ML actual
    
    Returns:
        JSON con versión, métricas, features importantes, etc.
    """
    try:
        info = predictor.get_model_info()
        return JSONResponse(content={
            "success": True,
            "model_info": info
        })
    except Exception as e:
        logger.error(f"Error obteniendo info del modelo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/accuracy")
async def get_model_accuracy(days: int = 30):
    """
    Obtiene métricas de precisión del modelo
    
    Args:
        days: Días a evaluar (default: 30)
        
    Returns:
        JSON con MAPE, MAE, coverage por variable
    """
    try:
        report = predictor.get_accuracy_report(days)
        return JSONResponse(content={
            "success": True,
            "accuracy_report": report
        })
    except Exception as e:
        logger.error(f"Error obteniendo precisión: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/features")
async def get_feature_importance(top_n: int = 20):
    """
    Obtiene las features más importantes del modelo
    
    Args:
        top_n: Número de features a retornar
        
    Returns:
        JSON con features ordenadas por importancia
    """
    try:
        importance = predictor.get_feature_importance(top_n)
        return JSONResponse(content={
            "success": True,
            "feature_importance": importance
        })
    except Exception as e:
        logger.error(f"Error obteniendo features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/retrain-check")
async def check_retrain_needed():
    """
    Evalúa si el modelo necesita reentrenamiento
    
    Returns:
        JSON con recomendación y razones
    """
    try:
        result = predictor.should_retrain()
        return JSONResponse(content={
            "success": True,
            "retrain_check": result
        })
    except Exception as e:
        logger.error(f"Error evaluando reentrenamiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/advanced")
async def get_advanced_predictions(days: int = 7):
    """
    Predicciones avanzadas con intervalos de confianza reales
    
    Args:
        days: Días a predecir
        
    Returns:
        JSON con predicciones, intervalos, y metadata del modelo
    """
    try:
        data_file = DATA_DIR / "ventas_diarias.parquet"
        if not data_file.exists():
            raise HTTPException(status_code=400, detail="No hay datos procesados")
        
        # Cargar modelos
        predictor.cargar_modelos()
        
        # Generar predicciones
        predictions = predictor.predict_next_days(data_file, days=days)
        
        # Convertir fechas a string
        for pred in predictions:
            pred['fecha'] = pred['fecha'].strftime('%Y-%m-%d') if hasattr(pred['fecha'], 'strftime') else str(pred['fecha'])
        
        # Obtener info del modelo
        model_info = predictor.get_model_info()
        
        return JSONResponse(content={
            "success": True,
            "predictions": predictions,
            "model_info": {
                "version": model_info.get('version', '2.0.0'),
                "last_trained": model_info.get('last_trained'),
                "mape_validation": model_info.get('metrics', {}).get('total_ventas_dia', {}).get('mape')
            }
        })
        
    except Exception as e:
        logger.error(f"Error en predicciones avanzadas: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
