import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { DollarSign, Pizza, Croissant, Beef, X, Info } from 'lucide-react'
import KPICard from './KPICard'
import SalesChart from './SalesChart'
import ProductsChart from './ProductsChart'
import InsightBox from './InsightBox'
import DataQualityAlert from './DataQualityAlert'
import PredictionIntervals from './PredictionIntervals'
import PredictionExplanation from './PredictionExplanation'
import { formatNumber, formatCurrency } from '../utils/formatters'

export default function Dashboard({ data, predictions, insight, loading }) {
  const [selectedPrediction, setSelectedPrediction] = useState(null)
  
  if (!data) return null

  const stats = data?.stats || {}
  const historicalData = data?.data || []
  const recentData = data.recent_data || []

  // Calcular KPIs
  const totalVentas = stats.ventas_totales || 0
  const promedioVentas = stats.promedio_ventas_dia || 0
  const totalPizzas = stats.total_pizzas || 0
  const totalBaguettes = stats.total_baguettes || 0
  const totalPapas = stats.total_papas_gajo || 0

  // Predicciones: primera es de AYER, segunda es de HOY
  const yesterdayPrediction = predictions && predictions.length > 0 ? predictions[0] : null
  const todayPrediction = predictions && predictions.length > 1 ? predictions[1] : null
  
  // Determinar fechas
  const lastDataDate = stats.fecha_fin ? new Date(stats.fecha_fin) : null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h2 className="text-3xl font-bold mb-2 text-gray-800">Dashboard de Ventas</h2>
        <p className="text-gray-600">
          Datos desde {stats.fecha_inicio} hasta {stats.fecha_fin} ({formatNumber(stats.total_dias)} días)
        </p>
      </motion.div>

      {/* Data Quality Alert */}
      <motion.div variants={itemVariants}>
        <DataQualityAlert stats={stats} />
      </motion.div>

      {/* KPI Cards */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <KPICard
          title="Ventas Totales"
          value={totalVentas}
          format="currency"
          icon={DollarSign}
          color="green"
          subtitle={`Promedio: ${formatCurrency(promedioVentas)}/día`}
          prediction={yesterdayPrediction?.total_ventas_dia}
          avgDaily={promedioVentas}
          predictionLabel="Predicción ayer (12/11)"
        />
        <KPICard
          title="Pizzas Vendidas"
          value={totalPizzas}
          format="number"
          icon={Pizza}
          color="blue"
          subtitle={`${formatNumber((totalPizzas / stats.total_dias).toFixed(1))}/día`}
          prediction={yesterdayPrediction?.pizzas_vendidas}
          avgDaily={totalPizzas / stats.total_dias}
          predictionLabel="Predicción ayer (12/11)"
        />
        <KPICard
          title="Baguettes"
          value={totalBaguettes}
          format="number"
          icon={Croissant}
          color="amber"
          subtitle={`${formatNumber((totalBaguettes / stats.total_dias).toFixed(1))}/día`}
          prediction={yesterdayPrediction?.baguettes_vendidas}
          avgDaily={totalBaguettes / stats.total_dias}
          predictionLabel="Predicción ayer (12/11)"
        />
        <KPICard
          title="Papas Gajo"
          value={totalPapas}
          format="number"
          icon={Beef}
          color="orange"
          subtitle={`${formatNumber((totalPapas / stats.total_dias).toFixed(1))}/día`}
          prediction={yesterdayPrediction?.papas_gajo_vendidas}
          avgDaily={totalPapas / stats.total_dias}
          predictionLabel="Predicción ayer (12/11)"
        />
      </motion.div>

      {/* Insight Box */}
      {insight && (
        <motion.div variants={itemVariants}>
          <InsightBox insight={insight} loading={loading} />
        </motion.div>
      )}

      {/* Prediction Intervals - DESACTIVADO (modelos quantile no entrenados) */}
      {/* {nextDayPrediction && (
        <motion.div variants={itemVariants}>
          <PredictionIntervals 
            prediction={nextDayPrediction} 
            title={isPredictingToday ? "Predicción para Hoy" : "Predicción para Mañana"}
          />
        </motion.div>
      )} */}

      {/* Prediction Explanation - DESACTIVADO (SHAP no entrenado) */}
      {/* {nextDayPrediction && (
        <motion.div variants={itemVariants}>
          <PredictionExplanation prediction={nextDayPrediction} />
        </motion.div>
      )} */}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <SalesChart
            historicalData={recentData}
            predictions={predictions}
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <ProductsChart
            pizzas={totalPizzas}
            baguettes={totalBaguettes}
            papas={totalPapas}
          />
        </motion.div>
      </div>

      {/* Predictions Table */}
      {predictions && predictions.length > 0 && (
        <motion.div variants={itemVariants} className="glass-effect rounded-xl p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-800">Predicciones Próximos 7 Días</h3>
          <p className="text-sm text-gray-600 mb-4">
            Predicción base con rangos realistas (pesimista - optimista)
          </p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300 bg-gray-50">
                  <th className="text-left py-3 px-4 text-gray-700 font-semibold">Fecha</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Ventas</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Pizzas</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Baguettes</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Papas</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred, index) => (
                  <motion.tr
                    key={pred.fecha}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => setSelectedPrediction(pred)}
                    className="border-b border-gray-200 hover:bg-primary-50 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4">
                      <div className="font-medium text-gray-800">{pred.fecha}</div>
                      <div className="text-xs text-gray-500">{pred.dia_nombre}</div>
                      {pred.evento && (
                        <div className="text-xs font-semibold text-orange-600 mt-1">
                          🎉 {pred.evento}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-primary-600 font-semibold">
                        {formatCurrency(pred.total_ventas_dia)}
                      </div>
                      {pred.ventas_min && pred.ventas_max && (
                        <div className="text-xs text-gray-500">
                          {formatCurrency(pred.ventas_min)} - {formatCurrency(pred.ventas_max)}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-gray-700 font-medium">
                        {formatNumber(Math.round(pred.pizzas_vendidas))}
                      </div>
                      {pred.pizzas_min && pred.pizzas_max && (
                        <div className="text-xs text-gray-500">
                          {Math.round(pred.pizzas_min)} - {Math.round(pred.pizzas_max)}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-gray-700 font-medium">
                        {formatNumber(Math.round(pred.baguettes_vendidas))}
                      </div>
                      {pred.baguettes_min && pred.baguettes_max && (
                        <div className="text-xs text-gray-500">
                          {Math.round(pred.baguettes_min)} - {Math.round(pred.baguettes_max)}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="text-gray-700 font-medium">
                        {formatNumber(Math.round(pred.papas_gajo_vendidas))}
                      </div>
                      {pred.papas_min && pred.papas_max && (
                        <div className="text-xs text-gray-500">
                          {Math.round(pred.papas_min)} - {Math.round(pred.papas_max)}
                        </div>
                      )}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Leyenda */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm text-gray-700">
              <span className="font-semibold">💡 Cómo interpretar:</span>
              <ul className="mt-2 space-y-1 text-xs">
                <li><strong>Valor principal:</strong> Predicción más probable (mediana histórica)</li>
                <li><strong>Rango inferior:</strong> Escenario pesimista (15% de días son peores)</li>
                <li><strong>Rango superior:</strong> Escenario optimista (15% de días son mejores)</li>
                <li className="text-gray-600 italic">Rangos amplios para capturar crecimiento y variabilidad</li>
              </ul>
            </div>
          </div>
        </motion.div>
      )}

      {/* Modal de Explicación de Predicción */}
      <AnimatePresence>
        {selectedPrediction && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedPrediction(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">
                    📊 Explicación de Predicción
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {selectedPrediction.fecha} - {selectedPrediction.dia_nombre}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedPrediction(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600 hover:text-gray-800"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Predicción Principal */}
              <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6 mb-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Ventas Esperadas</p>
                    <p className="text-3xl font-bold text-primary-600">
                      {formatCurrency(selectedPrediction.total_ventas_dia)}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Rango: {formatCurrency(selectedPrediction.ventas_min)} - {formatCurrency(selectedPrediction.ventas_max)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Pizzas Esperadas</p>
                    <p className="text-3xl font-bold text-primary-600">
                      {Math.round(selectedPrediction.pizzas_vendidas)}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Rango: {Math.round(selectedPrediction.pizzas_min)} - {Math.round(selectedPrediction.pizzas_max)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Justificación */}
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-800">🎯 ¿Por qué esta predicción?</h3>
                
                {/* Día de la Semana */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                      1
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800 mb-1">Patrón del día: {selectedPrediction.dia_nombre}</p>
                      <p className="text-sm text-gray-600">
                        Basado en el promedio de los últimos 40 {selectedPrediction.dia_nombre}s en tu pizzería.
                        Cada día de la semana tiene su propio patrón de ventas.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Evento Especial */}
                {selectedPrediction.evento && (
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                        2
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-800 mb-1">🎉 Evento Especial: {selectedPrediction.evento}</p>
                        <p className="text-sm text-gray-600 mb-2">
                          {selectedPrediction.evento.includes('Quincena') && 
                            'Los días de quincena históricamente tienen mayor demanda debido a que es día de pago. Las personas tienden a gastar más en restaurantes.'
                          }
                          {selectedPrediction.evento.includes('Navidad') && 
                            'Navidad es uno de los días con mayor demanda del año. Las familias celebran en casa y piden pizzas.'
                          }
                          {selectedPrediction.evento.includes('Año Nuevo') && 
                            'Fin de año es un día de alta demanda. Fiestas y reuniones incrementan los pedidos.'
                          }
                        </p>
                        <p className="text-sm font-semibold text-orange-700">
                          Multiplicador aplicado: {selectedPrediction.multiplicador ? `${((selectedPrediction.multiplicador - 1) * 100).toFixed(0)}%` : '0%'} adicional
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Rangos */}
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                      {selectedPrediction.evento ? '3' : '2'}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800 mb-1">Rangos de variabilidad</p>
                      <p className="text-sm text-gray-600 mb-2">
                        Los rangos representan la variabilidad natural de tu negocio:
                      </p>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li><strong>Escenario pesimista:</strong> 15% de días similares tuvieron ventas menores</li>
                        <li><strong>Predicción base:</strong> Valor más probable (mediana histórica)</li>
                        <li><strong>Escenario optimista:</strong> 15% de días similares tuvieron ventas mayores</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Recomendaciones */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                      💡
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800 mb-1">Recomendaciones para este día</p>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• Comprar ingredientes para: <strong>{Math.round(selectedPrediction.pizzas_max)} pizzas</strong> (escenario optimista)</li>
                        <li>• Personal recomendado: <strong>{Math.round(selectedPrediction.pizzas_vendidas / 25)} personas</strong> (1 por cada 25 pizzas)</li>
                        <li>• Si al mediodía llevas {Math.round(selectedPrediction.pizzas_vendidas / 2)} pizzas, vas en buen ritmo</li>
                        {selectedPrediction.evento && (
                          <li className="text-orange-700 font-semibold">• ⚠️ Día especial: considera tener personal extra disponible</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  Esta predicción se basa en 322 días de datos históricos de tu pizzería y se actualiza automáticamente con cada nuevo dato.
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
