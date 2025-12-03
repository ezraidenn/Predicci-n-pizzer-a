import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, TrendingUp, TrendingDown, Calendar, DollarSign,
  Users, Pizza, ShoppingBag, Award, Target, Percent, Clock
} from 'lucide-react';
import axios from 'axios';

const API_URL = '/api';

export default function Reportes() {
  const [reporte, setReporte] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReporte();
  }, []);

  const fetchReporte = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/reportes/resumen`);
      setReporte(res.data.reporte);
    } catch (error) {
      console.error('Error cargando reporte:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (!reporte) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <p className="text-gray-500">No hay datos para generar reportes</p>
        <p className="text-sm text-gray-400">Sube archivos Excel para comenzar</p>
      </div>
    );
  }

  const { periodo, ventas, clientes, analisis_semanal } = reporte;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Reporte Ejecutivo</h1>
        <p className="opacity-80">
          Período: {periodo?.inicio} al {periodo?.fin} ({periodo?.total_dias} días)
        </p>
      </div>

      {/* KPIs Principales */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg p-5"
        >
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <DollarSign className="w-5 h-5" />
            <span className="text-sm">Ventas Totales</span>
          </div>
          <div className="text-2xl font-bold text-gray-800">
            {formatCurrency(ventas?.total_historico)}
          </div>
          <div className="text-sm text-gray-400 mt-1">Histórico completo</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg p-5"
        >
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <Target className="w-5 h-5" />
            <span className="text-sm">Promedio Diario</span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(ventas?.promedio_diario)}
          </div>
          <div className="text-sm text-gray-400 mt-1">Por día operativo</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg p-5"
        >
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <Users className="w-5 h-5" />
            <span className="text-sm">Clientes</span>
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {clientes?.total_clientes || 0}
          </div>
          <div className="text-sm text-gray-400 mt-1">
            {clientes?.clientes_frecuentes || 0} frecuentes
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-5"
        >
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <Percent className="w-5 h-5" />
            <span className="text-sm">Retención</span>
          </div>
          <div className="text-2xl font-bold text-purple-600">
            {clientes?.tasa_retencion || 0}%
          </div>
          <div className="text-sm text-gray-400 mt-1">Clientes que regresan</div>
        </motion.div>
      </div>

      {/* Tendencia */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-xl shadow-lg p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-gray-800 flex items-center gap-2">
            {ventas?.tendencia?.includes('Creciendo') ? (
              <TrendingUp className="w-5 h-5 text-green-500" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-500" />
            )}
            Tendencia del Negocio
          </h3>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            ventas?.tendencia?.includes('Creciendo') 
              ? 'bg-green-100 text-green-700' 
              : 'bg-red-100 text-red-700'
          }`}>
            {ventas?.tendencia}
          </span>
        </div>
        
        <div className="grid md:grid-cols-2 gap-6">
          {/* Mejor día */}
          <div className="bg-green-50 rounded-xl p-4">
            <div className="flex items-center gap-2 text-green-700 mb-2">
              <Award className="w-5 h-5" />
              <span className="font-medium">Mejor Día de la Semana</span>
            </div>
            <div className="text-3xl font-bold text-green-800">
              {ventas?.mejor_dia_semana?.dia}
            </div>
            <div className="mt-2 space-y-1 text-sm text-green-600">
              <div>Ventas promedio: {formatCurrency(ventas?.mejor_dia_semana?.ventas_promedio)}</div>
              <div>Pizzas promedio: {Math.round(ventas?.mejor_dia_semana?.pizzas_promedio || 0)}</div>
            </div>
          </div>

          {/* Peor día */}
          <div className="bg-orange-50 rounded-xl p-4">
            <div className="flex items-center gap-2 text-orange-700 mb-2">
              <Clock className="w-5 h-5" />
              <span className="font-medium">Día Más Tranquilo</span>
            </div>
            <div className="text-3xl font-bold text-orange-800">
              {ventas?.peor_dia_semana?.dia}
            </div>
            <div className="mt-2 space-y-1 text-sm text-orange-600">
              <div>Ventas promedio: {formatCurrency(ventas?.peor_dia_semana?.ventas_promedio)}</div>
              <div>Pizzas promedio: {Math.round(ventas?.peor_dia_semana?.pizzas_promedio || 0)}</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Análisis Semanal */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white rounded-xl shadow-lg p-6"
      >
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-indigo-500" />
          Rendimiento por Día de la Semana
        </h3>
        
        <div className="space-y-3">
          {analisis_semanal?.map((dia, idx) => {
            const maxVentas = Math.max(...analisis_semanal.map(d => d.ventas_promedio));
            const porcentaje = (dia.ventas_promedio / maxVentas) * 100;
            
            return (
              <motion.div
                key={dia.dia}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * idx }}
                className="flex items-center gap-4"
              >
                <div className="w-24 font-medium text-gray-700">{dia.dia}</div>
                <div className="flex-1">
                  <div className="h-8 bg-gray-100 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${porcentaje}%` }}
                      transition={{ duration: 0.8, delay: 0.1 * idx }}
                      className={`h-full rounded-full ${
                        porcentaje === 100 ? 'bg-gradient-to-r from-green-400 to-green-500' :
                        porcentaje > 70 ? 'bg-gradient-to-r from-blue-400 to-blue-500' :
                        'bg-gradient-to-r from-orange-400 to-orange-500'
                      }`}
                    />
                  </div>
                </div>
                <div className="w-28 text-right">
                  <div className="font-bold text-gray-800">{formatCurrency(dia.ventas_promedio)}</div>
                  <div className="text-xs text-gray-500">{Math.round(dia.pizzas_promedio)} pizzas</div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Top Clientes */}
      {clientes?.top_clientes && clientes.top_clientes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-yellow-500" />
            Top 10 Clientes VIP
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 border-b">
                  <th className="pb-3 font-medium">#</th>
                  <th className="pb-3 font-medium">Cliente</th>
                  <th className="pb-3 font-medium text-center">Pedidos</th>
                  <th className="pb-3 font-medium text-right">Total Gastado</th>
                  <th className="pb-3 font-medium text-right">Ticket Prom.</th>
                </tr>
              </thead>
              <tbody>
                {clientes.top_clientes.map((cliente, idx) => (
                  <tr key={cliente.telefono} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-3">
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                        idx === 0 ? 'bg-yellow-500' : idx === 1 ? 'bg-gray-400' : idx === 2 ? 'bg-orange-400' : 'bg-gray-300'
                      }`}>
                        {idx + 1}
                      </span>
                    </td>
                    <td className="py-3 font-medium text-gray-800">{cliente.nombre || 'Sin nombre'}</td>
                    <td className="py-3 text-center text-gray-600">{cliente.total_pedidos}</td>
                    <td className="py-3 text-right font-bold text-green-600">{formatCurrency(cliente.total_gastado)}</td>
                    <td className="py-3 text-right text-gray-600">{formatCurrency(cliente.ticket_promedio)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  );
}
