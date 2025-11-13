"""
CALENDARIO DE EVENTOS ESPECIALES
Quincenas, festivos y eventos que impactan ventas
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CalendarioEventos:
    """
    Maneja eventos especiales que impactan ventas
    """
    
    def __init__(self):
        # Festivos fijos (mes, día)
        self.festivos_fijos = {
            (1, 1): {'nombre': 'Año Nuevo', 'multiplicador': 1.75, 'tier': 1},
            (1, 6): {'nombre': 'Día de Reyes', 'multiplicador': 1.55, 'tier': 2},
            (2, 14): {'nombre': 'San Valentín', 'multiplicador': 1.50, 'tier': 2},
            (4, 30): {'nombre': 'Día del Niño', 'multiplicador': 1.45, 'tier': 2},
            (5, 1): {'nombre': 'Día del Trabajo', 'multiplicador': 1.25, 'tier': 3},
            (9, 15): {'nombre': 'Independencia (víspera)', 'multiplicador': 1.35, 'tier': 3},
            (9, 16): {'nombre': 'Independencia', 'multiplicador': 1.35, 'tier': 3},
            (10, 31): {'nombre': 'Halloween', 'multiplicador': 1.40, 'tier': 2},
            (11, 1): {'nombre': 'Día de Muertos', 'multiplicador': 1.40, 'tier': 2},
            (11, 2): {'nombre': 'Día de Muertos', 'multiplicador': 1.40, 'tier': 2},
            (11, 20): {'nombre': 'Revolución', 'multiplicador': 1.25, 'tier': 3},
            (12, 24): {'nombre': 'Nochebuena', 'multiplicador': 1.65, 'tier': 1},
            (12, 25): {'nombre': 'Navidad', 'multiplicador': 1.65, 'tier': 1},
            (12, 31): {'nombre': 'Fin de Año', 'multiplicador': 1.75, 'tier': 1},
        }
    
    def es_quincena(self, fecha: datetime) -> Dict:
        """
        Detecta si es día de quincena y calcula multiplicador
        
        Quincenas en México:
        - Días 1-4 del mes (pago inicio de mes)
        - Días 15-18 del mes (pago mitad de mes)
        """
        dia = fecha.day
        
        # Primera quincena (1-4)
        if 1 <= dia <= 4:
            dias_desde_pago = dia - 1
            if dias_desde_pago == 0:
                return {'es_quincena': True, 'tipo': 'dia_pago', 'multiplicador': 1.15, 'dias_desde': 0}
            elif dias_desde_pago == 1:
                return {'es_quincena': True, 'tipo': 'dia_pico', 'multiplicador': 1.40, 'dias_desde': 1}
            elif dias_desde_pago == 2:
                return {'es_quincena': True, 'tipo': 'dia_alto', 'multiplicador': 1.25, 'dias_desde': 2}
            elif dias_desde_pago == 3:
                return {'es_quincena': True, 'tipo': 'dia_moderado', 'multiplicador': 1.10, 'dias_desde': 3}
        
        # Segunda quincena (15-18)
        elif 15 <= dia <= 18:
            dias_desde_pago = dia - 15
            if dias_desde_pago == 0:
                return {'es_quincena': True, 'tipo': 'dia_pago', 'multiplicador': 1.15, 'dias_desde': 0}
            elif dias_desde_pago == 1:
                return {'es_quincena': True, 'tipo': 'dia_pico', 'multiplicador': 1.40, 'dias_desde': 1}
            elif dias_desde_pago == 2:
                return {'es_quincena': True, 'tipo': 'dia_alto', 'multiplicador': 1.25, 'dias_desde': 2}
            elif dias_desde_pago == 3:
                return {'es_quincena': True, 'tipo': 'dia_moderado', 'multiplicador': 1.10, 'dias_desde': 3}
        
        return {'es_quincena': False, 'tipo': None, 'multiplicador': 1.0, 'dias_desde': None}
    
    def es_festivo(self, fecha: datetime) -> Dict:
        """
        Detecta si es día festivo y devuelve multiplicador
        """
        clave = (fecha.month, fecha.day)
        
        if clave in self.festivos_fijos:
            festivo = self.festivos_fijos[clave]
            return {
                'es_festivo': True,
                'nombre': festivo['nombre'],
                'multiplicador': festivo['multiplicador'],
                'tier': festivo['tier']
            }
        
        # Festivos móviles
        festivo_movil = self._calcular_festivo_movil(fecha)
        if festivo_movil:
            return festivo_movil
        
        return {'es_festivo': False, 'nombre': None, 'multiplicador': 1.0, 'tier': None}
    
    def _calcular_festivo_movil(self, fecha: datetime) -> Optional[Dict]:
        """
        Calcula festivos que cambian de fecha cada año
        """
        # Día de las Madres (2do domingo de mayo)
        if fecha.month == 5:
            primer_dia = datetime(fecha.year, 5, 1)
            # Encontrar primer domingo
            dias_hasta_domingo = (6 - primer_dia.weekday()) % 7
            primer_domingo = primer_dia + timedelta(days=dias_hasta_domingo)
            segundo_domingo = primer_domingo + timedelta(days=7)
            
            if fecha.date() == segundo_domingo.date():
                return {
                    'es_festivo': True,
                    'nombre': 'Día de las Madres',
                    'multiplicador': 1.80,
                    'tier': 1
                }
        
        # Día del Padre (3er domingo de junio)
        if fecha.month == 6:
            primer_dia = datetime(fecha.year, 6, 1)
            dias_hasta_domingo = (6 - primer_dia.weekday()) % 7
            primer_domingo = primer_dia + timedelta(days=dias_hasta_domingo)
            tercer_domingo = primer_domingo + timedelta(days=14)
            
            if fecha.date() == tercer_domingo.date():
                return {
                    'es_festivo': True,
                    'nombre': 'Día del Padre',
                    'multiplicador': 1.70,
                    'tier': 1
                }
        
        return None
    
    def get_multiplicador_total(self, fecha: datetime) -> Dict:
        """
        Calcula multiplicador total considerando quincenas y festivos
        
        Si coinciden quincena y festivo, usa el mayor
        """
        quincena_info = self.es_quincena(fecha)
        festivo_info = self.es_festivo(fecha)
        
        # Usar el multiplicador mayor
        if quincena_info['es_quincena'] and festivo_info['es_festivo']:
            mult_final = max(quincena_info['multiplicador'], festivo_info['multiplicador'])
            evento = f"{festivo_info['nombre']} + Quincena"
        elif festivo_info['es_festivo']:
            mult_final = festivo_info['multiplicador']
            evento = festivo_info['nombre']
        elif quincena_info['es_quincena']:
            mult_final = quincena_info['multiplicador']
            evento = f"Quincena ({quincena_info['tipo']})"
        else:
            mult_final = 1.0
            evento = None
        
        return {
            'multiplicador': mult_final,
            'evento': evento,
            'quincena': quincena_info,
            'festivo': festivo_info
        }
    
    def aplicar_multiplicador(self, prediccion_base: float, fecha: datetime) -> Dict:
        """
        Aplica multiplicador a una predicción base
        """
        info = self.get_multiplicador_total(fecha)
        prediccion_ajustada = prediccion_base * info['multiplicador']
        
        return {
            'prediccion_base': prediccion_base,
            'prediccion_ajustada': prediccion_ajustada,
            'multiplicador': info['multiplicador'],
            'evento': info['evento'],
            'incremento_pct': (info['multiplicador'] - 1) * 100
        }
