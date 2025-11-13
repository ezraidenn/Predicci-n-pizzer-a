import { AlertTriangle, CheckCircle, Info } from 'lucide-react'
import { motion } from 'framer-motion'

export default function DataQualityAlert({ stats }) {
  if (!stats) return null

  const diasDesdeActualizacion = stats.dias_desde_ultima_actualizacion || 0
  const nivelConfianza = stats.nivel_confianza || 0
  const fechaFin = stats.fecha_fin

  // Determinar tipo de alerta
  let alertType = 'success'
  let icon = CheckCircle
  let mensaje = ''
  let color = 'green'

  if (diasDesdeActualizacion <= 3) {
    alertType = 'success'
    icon = CheckCircle
    mensaje = `Datos actualizados (última actualización: ${fechaFin})`
    color = 'green'
  } else if (diasDesdeActualizacion <= 7) {
    alertType = 'info'
    icon = Info
    mensaje = `Datos de hace ${diasDesdeActualizacion} días (última actualización: ${fechaFin})`
    color = 'blue'
  } else if (diasDesdeActualizacion <= 30) {
    alertType = 'warning'
    icon = AlertTriangle
    mensaje = `⚠️ Datos desactualizados: hace ${diasDesdeActualizacion} días (última actualización: ${fechaFin}). Sube datos recientes para mejorar precisión.`
    color = 'yellow'
  } else {
    alertType = 'error'
    icon = AlertTriangle
    mensaje = `⚠️ DATOS MUY ANTIGUOS: hace ${diasDesdeActualizacion} días (última actualización: ${fechaFin}). Las predicciones pueden ser poco confiables.`
    color = 'red'
  }

  const Icon = icon

  const colorClasses = {
    green: 'bg-green-50 border-green-200 text-green-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    yellow: 'bg-yellow-50 border-yellow-300 text-yellow-800',
    red: 'bg-red-50 border-red-200 text-red-700'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-lg border p-4 mb-6 ${colorClasses[color]}`}
    >
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm font-medium">{mensaje}</p>
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs font-medium text-gray-600">Nivel de confianza:</span>
            <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  nivelConfianza >= 80 ? 'bg-green-600' :
                  nivelConfianza >= 60 ? 'bg-yellow-600' :
                  'bg-orange-600'
                }`}
                style={{ width: `${nivelConfianza}%` }}
              />
            </div>
            <span className="text-xs font-bold text-gray-700">{nivelConfianza}%</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
