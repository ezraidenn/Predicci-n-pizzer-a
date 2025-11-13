import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { TrendingUp, TrendingDown, Calendar, Award, BarChart3, ChevronRight, X } from 'lucide-react'
import { formatNumber, formatCurrency, formatPercent } from '../utils/formatters'

const API_URL = '/api'

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedMonth, setSelectedMonth] = useState(null)
  const [monthData, setMonthData] = useState(null)

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const response = await axios.get(`${API_URL}/analytics`)
        setAnalytics(response.data)
      } catch (error) {
        console.error('Error cargando análisis:', error)
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [])

  // Cargar datos del mes seleccionado
  const loadMonthData = async (año, mes) => {
    try {
      const response = await axios.get(`${API_URL}/historical`)
      const allData = response.data.data
      
      // Filtrar datos del mes seleccionado
      const monthFiltered = allData.filter(d => {
        const fecha = new Date(d.fecha)
        return fecha.getFullYear() === año && fecha.getMonth() + 1 === mes
      })
      
      setMonthData(monthFiltered)
      setSelectedMonth({ año, mes })
    } catch (error) {
      console.error('Error cargando datos del mes:', error)
    }
  }

  // Generar calendario del mes
  const generateCalendar = (año, mes) => {
    if (!monthData) return []
    
    const firstDay = new Date(año, mes - 1, 1)
    const lastDay = new Date(año, mes, 0)
    const daysInMonth = lastDay.getDate()
    const startDayOfWeek = firstDay.getDay()
    
    const calendar = []
    let week = []
    
    // Días vacíos al inicio
    for (let i = 0; i < startDayOfWeek; i++) {
      week.push(null)
    }
    
    // Días del mes
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${año}-${String(mes).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      const dayData = monthData.find(d => d.fecha === dateStr)
      
      week.push({ day, data: dayData })
      
      if (week.length === 7) {
        calendar.push(week)
        week = []
      }
    }
    
    // Completar última semana
    while (week.length > 0 && week.length < 7) {
      week.push(null)
    }
    if (week.length > 0) {
      calendar.push(week)
    }
    
    return calendar
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-400">Cargando análisis...</p>
        </div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">No hay datos para analizar</p>
      </div>
    )
  }

  const { analisis_mensual, analisis_semanal, top_dias, tendencias, resumen } = analytics

  const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8"
      >
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold mb-2 text-gray-800">📊 Análisis Detallado</h1>
          <p className="text-gray-600">
            Análisis completo de {formatNumber(resumen.total_dias_analizados)} días de ventas
          </p>
        </div>

        {/* Resumen General */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-effect rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <BarChart3 className="w-5 h-5 text-primary-600" />
              <h3 className="text-sm font-medium text-gray-600">Promedio Diario</h3>
            </div>
            <p className="text-2xl font-bold text-primary-600">
              {formatCurrency(resumen.venta_promedio_diaria)}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="glass-effect rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <Award className="w-5 h-5 text-primary-700" />
              <h3 className="text-sm font-medium text-gray-600">Mejor Día</h3>
            </div>
            <p className="text-2xl font-bold text-primary-700">
              {formatCurrency(resumen.mejor_dia_ventas)}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="glass-effect rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="w-5 h-5 text-slate-600" />
              <h3 className="text-sm font-medium text-gray-600">Peor Día</h3>
            </div>
            <p className="text-2xl font-bold text-slate-600">
              {formatCurrency(resumen.peor_dia_ventas)}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="glass-effect rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              {tendencias.cambio_porcentual >= 0 ? (
                <TrendingUp className="w-5 h-5 text-emerald-600" />
              ) : (
                <TrendingDown className="w-5 h-5 text-rose-600" />
              )}
              <h3 className="text-sm font-medium text-gray-600">Tendencia</h3>
            </div>
            <p className={`text-2xl font-bold ${tendencias.cambio_porcentual >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {formatPercent(tendencias.cambio_porcentual)}
            </p>
          </motion.div>
        </div>

        {/* Análisis Mensual */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-effect rounded-xl p-6"
        >
          <h2 className="text-2xl font-bold mb-6 text-gray-800">📅 Análisis Mensual</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-300 bg-gray-50">
                  <th className="text-left py-3 px-4 text-gray-700 font-semibold">Mes</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Ventas Totales</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Promedio Diario</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Pizzas</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Baguettes</th>
                  <th className="text-right py-3 px-4 text-gray-700 font-semibold">Papas Gajo</th>
                </tr>
              </thead>
              <tbody>
                {analisis_mensual.map((mes, idx) => (
                  <tr 
                    key={idx} 
                    onClick={() => loadMonthData(mes.año, mes.mes)}
                    className="border-b border-gray-200 hover:bg-primary-50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-primary-600" />
                      <span className="font-medium text-gray-800">{meses[mes.mes - 1]} {mes.año}</span>
                      <ChevronRight className="w-4 h-4 ml-auto text-gray-400" />
                    </td>
                    <td className="text-right py-3 px-4 font-bold text-primary-600">
                      {formatCurrency(mes.total_ventas_dia_sum || 0)}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-700">
                      {formatCurrency(mes.total_ventas_dia_mean || 0)}
                    </td>
                    <td className="text-right py-3 px-4 text-gray-700">{formatNumber(mes.pizzas_vendidas_sum || 0)}</td>
                    <td className="text-right py-3 px-4 text-gray-700">{formatNumber(mes.baguettes_vendidas_sum || 0)}</td>
                    <td className="text-right py-3 px-4 text-gray-700">{formatNumber(mes.papas_gajo_vendidas_sum || 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Análisis Semanal */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-effect rounded-xl p-6"
        >
          <h2 className="text-2xl font-bold mb-6 text-gray-800">📊 Análisis por Día de la Semana</h2>
          <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
            {analisis_semanal.map((dia, idx) => (
              <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center hover:shadow-md transition-shadow">
                <p className="text-sm text-gray-600 mb-2 font-medium">{dia.dia_nombre}</p>
                <p className="text-xl font-bold text-primary-600 mb-1">
                  {formatCurrency(dia.total_ventas_dia_mean || 0)}
                </p>
                <p className="text-xs text-gray-600">
                  {formatNumber(dia.pizzas_vendidas_mean?.toFixed(0) || '0')} pizzas
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Top 10 Mejores Días */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-effect rounded-xl p-6"
        >
          <h2 className="text-2xl font-bold mb-6 text-gray-800">🏆 Top 10 Mejores Días</h2>
          <div className="space-y-3">
            {top_dias.map((dia, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg p-4 hover:bg-primary-50 hover:border-primary-300 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    idx === 0 ? 'bg-yellow-400 text-gray-900' :
                    idx === 1 ? 'bg-gray-300 text-gray-900' :
                    idx === 2 ? 'bg-orange-400 text-gray-900' :
                    'bg-gray-200 text-gray-700'
                  }`}>
                    {idx + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{dia.fecha}</p>
                    <p className="text-sm text-gray-600">
                      {formatNumber(dia.total_pedidos)} pedidos • {formatNumber(dia.pizzas_vendidas)} pizzas
                    </p>
                  </div>
                </div>
                <p className="text-xl font-bold text-primary-600">
                  {formatCurrency(dia.total_ventas_dia)}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Nota sobre confiabilidad */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="bg-blue-50 border border-blue-200 rounded-xl p-6"
        >
          <h3 className="font-bold text-blue-700 mb-2">💡 Sobre la Confiabilidad del Análisis</h3>
          <p className="text-sm text-gray-700">
            Con <strong>{formatNumber(resumen.total_dias_analizados)} días</strong> de datos, el análisis tiene un nivel de confianza{' '}
            {resumen.total_dias_analizados >= 180 ? (
              <span className="text-green-700 font-bold">ALTO (6+ meses)</span>
            ) : resumen.total_dias_analizados >= 90 ? (
              <span className="text-yellow-700 font-bold">MEDIO (3-6 meses)</span>
            ) : (
              <span className="text-orange-700 font-bold">BAJO (&lt;3 meses)</span>
            )}.
            {resumen.total_dias_analizados < 180 && (
              <span> Sube más datos históricos para mejorar la precisión de las predicciones.</span>
            )}
          </p>
        </motion.div>
      </motion.div>

      {/* Modal de Calendario */}
      <AnimatePresence>
        {selectedMonth && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedMonth(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-3xl font-bold text-gray-800">
                  📅 {meses[selectedMonth.mes - 1]} {selectedMonth.año}
                </h2>
                <button
                  onClick={() => setSelectedMonth(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-600 hover:text-gray-800"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Calendario */}
              <div className="grid grid-cols-7 gap-2">
                {/* Encabezados de días */}
                {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(dia => (
                  <div key={dia} className="text-center font-bold text-gray-700 py-2">
                    {dia}
                  </div>
                ))}

                {/* Días del mes */}
                {generateCalendar(selectedMonth.año, selectedMonth.mes).map((week, weekIdx) => (
                  week.map((day, dayIdx) => (
                    <div
                      key={`${weekIdx}-${dayIdx}`}
                      className={`aspect-square p-2 rounded-lg ${
                        day?.data
                          ? 'bg-primary-50 border border-primary-200 hover:bg-primary-100 cursor-pointer'
                          : day
                          ? 'bg-gray-50'
                          : 'bg-transparent'
                      } transition-colors`}
                    >
                      {day && (
                        <div className="h-full flex flex-col">
                          <span className="text-sm font-bold mb-1">{day.day}</span>
                          {day.data && (
                            <div className="flex-1 flex flex-col justify-between text-xs">
                              <div className="font-bold text-primary-600">
                                ${day.data.total_ventas_dia?.toFixed(0) || '0'}
                              </div>
                              <div className="text-gray-600 space-y-0.5">
                                <div>🍕 {day.data.pizzas_vendidas || 0}</div>
                                <div>🥖 {day.data.baguettes_vendidas || 0}</div>
                                <div>🍟 {day.data.papas_gajo_vendidas || 0}</div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                ))}
              </div>

              {/* Leyenda */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm text-gray-600">
                  <strong>Leyenda:</strong> Cada celda muestra las ventas del día, pizzas 🍕, baguettes 🥖 y papas gajo 🍟
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
