"""
GPT Insights Generator - Genera análisis en lenguaje natural usando OpenAI API
"""
import os
import logging
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI no disponible. Instalar con: pip install openai")

logger = logging.getLogger(__name__)


class GPTInsightGenerator:
    """Generador de insights usando GPT"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.enabled = True
            logger.info("GPT Insights habilitado")
        else:
            self.client = None
            self.enabled = False
            if not self.api_key:
                logger.warning("OPENAI_API_KEY no configurada en variables de entorno")
            logger.warning("GPT Insights deshabilitado - se usarán insights predeterminados")
    
    async def generate_insight(self, data_file, predictions: List[Dict[str, Any]]) -> str:
        """
        Genera insight en lenguaje natural
        
        Args:
            data_file: Path al archivo de datos históricos
            predictions: Lista de predicciones
            
        Returns:
            String con análisis en lenguaje natural
        """
        if not self.enabled:
            return self._generate_fallback_insight(data_file, predictions)
        
        try:
            # Cargar datos históricos
            df = pd.read_parquet(data_file)
            
            # Calcular estadísticas
            stats = self._calculate_stats(df, predictions)
            
            # Crear prompt para GPT
            prompt = self._create_prompt(stats)
            
            # Llamar a GPT
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista de datos experto en ventas de restaurantes. "
                                 "Genera insights concisos, accionables y en español sobre las predicciones de ventas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            insight = response.choices[0].message.content.strip()
            logger.info("Insight generado con GPT")
            
            return insight
            
        except Exception as e:
            logger.error(f"Error generando insight con GPT: {str(e)}")
            return self._generate_fallback_insight(data_file, predictions)
    
    def _calculate_stats(self, df: pd.DataFrame, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estadísticas para el prompt"""
        
        # Últimos 7 días históricos
        last_7_days = df.tail(7)
        
        # Promedios históricos
        avg_ventas_historico = last_7_days['total_ventas_dia'].mean()
        avg_pizzas_historico = last_7_days['pizzas_vendidas'].mean()
        avg_baguettes_historico = last_7_days['baguettes_vendidas'].mean()
        avg_papas_historico = last_7_days['papas_gajo_vendidas'].mean()
        
        # Promedios predichos
        avg_ventas_pred = sum(p['total_ventas_dia'] for p in predictions) / len(predictions)
        avg_pizzas_pred = sum(p['pizzas_vendidas'] for p in predictions) / len(predictions)
        avg_baguettes_pred = sum(p['baguettes_vendidas'] for p in predictions) / len(predictions)
        avg_papas_pred = sum(p['papas_gajo_vendidas'] for p in predictions) / len(predictions)
        
        # Cambios porcentuales
        cambio_ventas = ((avg_ventas_pred - avg_ventas_historico) / avg_ventas_historico * 100) if avg_ventas_historico > 0 else 0
        cambio_pizzas = ((avg_pizzas_pred - avg_pizzas_historico) / avg_pizzas_historico * 100) if avg_pizzas_historico > 0 else 0
        cambio_baguettes = ((avg_baguettes_pred - avg_baguettes_historico) / avg_baguettes_historico * 100) if avg_baguettes_historico > 0 else 0
        cambio_papas = ((avg_papas_pred - avg_papas_historico) / avg_papas_historico * 100) if avg_papas_historico > 0 else 0
        
        # Mejor día predicho
        mejor_dia = max(predictions, key=lambda x: x['total_ventas_dia'])
        
        return {
            'avg_ventas_historico': avg_ventas_historico,
            'avg_ventas_pred': avg_ventas_pred,
            'cambio_ventas': cambio_ventas,
            'avg_pizzas_historico': avg_pizzas_historico,
            'avg_pizzas_pred': avg_pizzas_pred,
            'cambio_pizzas': cambio_pizzas,
            'avg_baguettes_historico': avg_baguettes_historico,
            'avg_baguettes_pred': avg_baguettes_pred,
            'cambio_baguettes': cambio_baguettes,
            'avg_papas_historico': avg_papas_historico,
            'avg_papas_pred': avg_papas_pred,
            'cambio_papas': cambio_papas,
            'mejor_dia': mejor_dia,
            'num_predicciones': len(predictions)
        }
    
    def _create_prompt(self, stats: Dict[str, Any]) -> str:
        """Crea prompt para GPT"""
        
        mejor_fecha = stats['mejor_dia']['fecha'].strftime('%A %d/%m/%Y')
        
        prompt = f"""
Analiza las siguientes predicciones de ventas para Pizzería MAX:

DATOS HISTÓRICOS (últimos 7 días):
- Ventas promedio: ${stats['avg_ventas_historico']:.2f}
- Pizzas promedio: {stats['avg_pizzas_historico']:.0f} unidades
- Baguettes promedio: {stats['avg_baguettes_historico']:.0f} unidades
- Papas gajo promedio: {stats['avg_papas_historico']:.0f} unidades

PREDICCIONES (próximos {stats['num_predicciones']} días):
- Ventas promedio: ${stats['avg_ventas_pred']:.2f} ({stats['cambio_ventas']:+.1f}%)
- Pizzas promedio: {stats['avg_pizzas_pred']:.0f} unidades ({stats['cambio_pizzas']:+.1f}%)
- Baguettes promedio: {stats['avg_baguettes_pred']:.0f} unidades ({stats['cambio_baguettes']:+.1f}%)
- Papas gajo promedio: {stats['avg_papas_pred']:.0f} unidades ({stats['cambio_papas']:+.1f}%)

MEJOR DÍA PREDICHO:
- Fecha: {mejor_fecha}
- Ventas esperadas: ${stats['mejor_dia']['total_ventas_dia']:.2f}

Genera un insight breve (máximo 4 frases) que:
1. Resuma la tendencia general
2. Destaque el producto con mayor cambio
3. Mencione el mejor día predicho
4. Dé una recomendación accionable
"""
        
        return prompt
    
    def _generate_fallback_insight(self, data_file, predictions: List[Dict[str, Any]]) -> str:
        """Genera insight sin GPT (fallback)"""
        
        try:
            df = pd.read_parquet(data_file)
            stats = self._calculate_stats(df, predictions)
            
            # Determinar tendencia
            if stats['cambio_ventas'] > 5:
                tendencia = "un crecimiento significativo"
            elif stats['cambio_ventas'] > 0:
                tendencia = "un crecimiento moderado"
            elif stats['cambio_ventas'] > -5:
                tendencia = "estabilidad"
            else:
                tendencia = "una disminución"
            
            # Producto con mayor cambio
            cambios = {
                'pizzas': stats['cambio_pizzas'],
                'baguettes': stats['cambio_baguettes'],
                'papas gajo': stats['cambio_papas']
            }
            producto_destacado = max(cambios.items(), key=lambda x: abs(x[1]))
            
            # Mejor día
            mejor_fecha = stats['mejor_dia']['fecha'].strftime('%A %d de %B')
            
            insight = f"""
📊 **Análisis de Predicciones**

Las proyecciones indican {tendencia} en las ventas para los próximos {stats['num_predicciones']} días, 
con un cambio del {stats['cambio_ventas']:+.1f}% respecto a la semana anterior.

El producto con mayor variación son las **{producto_destacado[0]}** ({producto_destacado[1]:+.1f}%).

El mejor día predicho es el **{mejor_fecha}** con ventas esperadas de ${stats['mejor_dia']['total_ventas_dia']:.2f}.

💡 **Recomendación**: {"Prepara inventario adicional para el día pico." if stats['cambio_ventas'] > 0 else "Optimiza recursos según la demanda esperada."}
            """.strip()
            
            return insight
            
        except Exception as e:
            logger.error(f"Error generando insight fallback: {str(e)}")
            return "📊 Predicciones generadas exitosamente. Revisa los gráficos para más detalles."
