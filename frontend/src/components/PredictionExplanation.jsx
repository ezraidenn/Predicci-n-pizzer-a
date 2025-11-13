import { motion } from 'framer-motion'
import { Lightbulb, TrendingUp, TrendingDown } from 'lucide-react'

export default function PredictionExplanation({ prediction }) {
  if (!prediction || !prediction.total_ventas_dia_explanation) return null

  const explanation = prediction.total_ventas_dia_explanation
  const topExplanations = explanation.top_explanations || []

  // Traducir nombres de features
  const featureNames = {
    'es_viernes': 'Es viernes',
    'es_sabado': 'Es sábado',
    'es_domingo': 'Es domingo',
    'es_fin_semana': 'Es fin de semana',
    'es_primera_quincena': 'Primera quincena',
    'es_segunda_quincena': 'Segunda quincena',
    'es_dia_pago': 'Día de pago',
    'es_inicio_mes': 'Inicio de mes',
    'es_fin_mes': 'Fin de mes',
    'dia_semana': 'Día de la semana',
    'dia_mes': 'Día del mes',
    'mes': 'Mes',
    'total_ventas_dia_ma7': 'Promedio últimos 7 días',
    'total_ventas_dia_lag1': 'Ventas de ayer',
    'total_ventas_dia_lag7': 'Ventas hace 7 días',
  }

  const translateFeature = (feature) => {
    return featureNames[feature] || feature
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-xl p-6 mb-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-amber-500" />
        <h3 className="text-lg font-bold text-gray-800">¿Por qué esta predicción?</h3>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        Estos son los factores más importantes que influyen en la predicción:
      </p>

      <div className="space-y-3">
        {topExplanations.map((exp, idx) => {
          const isPositive = exp.impact > 0
          const Icon = isPositive ? TrendingUp : TrendingDown
          const colorClass = isPositive ? 'text-green-600 bg-green-50 border-green-200' : 'text-red-600 bg-red-50 border-red-200'
          const iconColor = isPositive ? 'text-green-600' : 'text-red-600'

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`flex items-center gap-3 p-4 rounded-lg border ${colorClass}`}
            >
              <Icon className={`w-5 h-5 ${iconColor} flex-shrink-0`} />
              <div className="flex-1">
                <div className="font-semibold text-gray-800 text-sm">
                  {translateFeature(exp.feature)}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  {isPositive ? 'Aumenta' : 'Disminuye'} la predicción en{' '}
                  <span className="font-bold">
                    ${Math.abs(exp.impact).toLocaleString('es-MX', {maximumFractionDigits: 0})}
                  </span>
                </div>
              </div>
              <div className={`text-2xl font-bold ${iconColor}`}>
                {isPositive ? '+' : '-'}${Math.abs(exp.impact).toLocaleString('es-MX', {maximumFractionDigits: 0})}
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-xs text-gray-600">
          <strong>Nota:</strong> Estos valores muestran cómo cada factor contribuye a la predicción final.
          Los factores positivos aumentan las ventas esperadas, mientras que los negativos las disminuyen.
        </p>
      </div>
    </motion.div>
  )
}
