import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart3, TrendingUp, TrendingDown, Calendar, DollarSign,
  Users, ShoppingBag, Target, Percent, Clock,
  MapPin, Phone, X, Zap, CheckCircle, Activity, Star
} from 'lucide-react';
import axios from 'axios';

const API_URL = '/api';

export default function Reportes() {
  const [reporte, setReporte] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCliente, setSelectedCliente] = useState(null);
  const [clienteDetalle, setClienteDetalle] = useState(null);

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

  const handleClienteClick = async (telefono) => {
    try {
      const res = await axios.get(`${API_URL}/clientes/${telefono}`);
      setClienteDetalle(res.data.cliente);
      setSelectedCliente(telefono);
    } catch (error) {
      console.error('Error obteniendo detalle:', error);
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
  
  // Calcular insights
  const ventasPorDia = ventas?.promedio_diario || 0;
  const mejorDia = ventas?.mejor_dia_semana;
  const peorDia = ventas?.peor_dia_semana;
  const diferenciaVentas = mejorDia && peorDia ? 
    ((mejorDia.ventas_promedio - peorDia.ventas_promedio) / peorDia.ventas_promedio * 100).toFixed(0) : 0;

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
              <Star className="w-5 h-5" />
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

      {/* Top Clientes - Dos tablas lado a lado */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="grid md:grid-cols-2 gap-6"
      >
        {/* Top por Dinero Gastado */}
        {clientes?.top_por_dinero && clientes.top_por_dinero.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              Top 10 por Dinero Gastado
            </h3>
            
            <div className="space-y-2">
              {clientes.top_por_dinero.map((cliente, idx) => (
                <div 
                  key={cliente.telefono} 
                  onClick={() => handleClienteClick(cliente.telefono)}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-green-50 cursor-pointer transition-colors"
                >
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                    idx === 0 ? 'bg-yellow-500' : idx === 1 ? 'bg-gray-400' : idx === 2 ? 'bg-orange-400' : 'bg-gray-300'
                  }`}>
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-800 truncate">{cliente.nombre || 'Sin nombre'}</div>
                    <div className="text-xs text-gray-400">{cliente.total_pedidos} pedidos</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-600">{formatCurrency(cliente.total_gastado)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top por Cantidad de Pedidos */}
        {clientes?.top_por_pedidos && clientes.top_por_pedidos.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-blue-500" />
              Top 10 por Cantidad de Pedidos
            </h3>
            
            <div className="space-y-2">
              {clientes.top_por_pedidos.map((cliente, idx) => (
                <div 
                  key={cliente.telefono} 
                  onClick={() => handleClienteClick(cliente.telefono)}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                    idx === 0 ? 'bg-yellow-500' : idx === 1 ? 'bg-gray-400' : idx === 2 ? 'bg-orange-400' : 'bg-gray-300'
                  }`}>
                    {idx + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-800 truncate">{cliente.nombre || 'Sin nombre'}</div>
                    <div className="text-xs text-gray-400">{formatCurrency(cliente.total_gastado)}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-blue-600">{cliente.total_pedidos}</div>
                    <div className="text-xs text-gray-400">pedidos</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>

      {/* Insights y Recomendaciones */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl shadow-lg p-6 border border-amber-200"
      >
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-500" />
          Insights y Recomendaciones
        </h3>
        
        <div className="grid md:grid-cols-2 gap-4">
          {/* Insight 1: Diferencia entre días */}
          <div className="bg-white rounded-lg p-4 border border-amber-100">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-800">Oportunidad de Ventas</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Los <strong>{mejorDia?.dia}</strong> vendes <strong>{diferenciaVentas}% más</strong> que los {peorDia?.dia}. 
                  Considera promociones especiales para días lentos.
                </p>
              </div>
            </div>
          </div>

          {/* Insight 2: Clientes frecuentes */}
          <div className="bg-white rounded-lg p-4 border border-amber-100">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-800">Fidelización</h4>
                <p className="text-sm text-gray-600 mt-1">
                  <strong>{clientes?.tasa_retencion || 0}%</strong> de tus clientes regresan. 
                  {clientes?.tasa_retencion >= 50 ? 
                    ' ¡Excelente retención! Mantén la calidad.' : 
                    ' Implementa un programa de lealtad para mejorar.'}
                </p>
              </div>
            </div>
          </div>

          {/* Insight 3: Ticket promedio */}
          <div className="bg-white rounded-lg p-4 border border-amber-100">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <DollarSign className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-800">Ticket Promedio</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Tu ticket promedio es <strong>{formatCurrency(clientes?.ticket_promedio_global)}</strong>. 
                  Sugiere combos o extras para aumentarlo.
                </p>
              </div>
            </div>
          </div>

          {/* Insight 4: Top cliente */}
          <div className="bg-white rounded-lg p-4 border border-amber-100">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Star className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-800">Cliente Estrella</h4>
                <p className="text-sm text-gray-600 mt-1">
                  <strong>{clientes?.top_clientes?.[0]?.nombre || 'Tu mejor cliente'}</strong> ha gastado {formatCurrency(clientes?.top_clientes?.[0]?.total_gastado)}. 
                  ¡Considera un trato VIP!
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Resumen Rápido para Imprimir */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="bg-white rounded-xl shadow-lg p-6 print:shadow-none"
      >
        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-500" />
          Resumen Ejecutivo
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-gray-800">{periodo?.total_dias}</div>
            <div className="text-sm text-gray-500">Días analizados</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600">{formatCurrency(ventas?.total_historico)}</div>
            <div className="text-sm text-gray-500">Ventas totales</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">{clientes?.total_clientes || 0}</div>
            <div className="text-sm text-gray-500">Clientes únicos</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">{formatCurrency(clientes?.ticket_promedio_global)}</div>
            <div className="text-sm text-gray-500">Ticket promedio</div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
          <div className="flex items-center gap-2 text-green-700 font-medium">
            <CheckCircle className="w-5 h-5" />
            Conclusión
          </div>
          <p className="text-sm text-gray-700 mt-2">
            En el período analizado, el negocio generó <strong>{formatCurrency(ventas?.total_historico)}</strong> en ventas 
            con un promedio de <strong>{formatCurrency(ventas?.promedio_diario)}</strong> por día. 
            Los <strong>{mejorDia?.dia}</strong> son los días más fuertes. 
            Se cuenta con <strong>{clientes?.total_clientes || 0}</strong> clientes únicos, 
            de los cuales <strong>{clientes?.clientes_frecuentes || 0}</strong> son frecuentes (3+ pedidos).
          </p>
        </div>
      </motion.div>

      {/* Modal Detalle Cliente */}
      <AnimatePresence>
        {selectedCliente && clienteDetalle && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedCliente(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6 text-white relative">
                <button
                  onClick={() => setSelectedCliente(null)}
                  className="absolute top-4 right-4 p-1 hover:bg-white/20 rounded-full"
                >
                  <X className="w-5 h-5" />
                </button>
                
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                    {clienteDetalle.es_cliente_frecuente ? (
                      <Star className="w-8 h-8" />
                    ) : (
                      <Users className="w-8 h-8" />
                    )}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">{clienteDetalle.nombre || 'Sin nombre'}</h2>
                    <p className="opacity-80 flex items-center gap-1">
                      <Phone className="w-4 h-4" />
                      {clienteDetalle.telefono}
                    </p>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-800">{clienteDetalle.total_pedidos}</div>
                  <div className="text-xs text-gray-500">Pedidos</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{formatCurrency(clienteDetalle.total_gastado)}</div>
                  <div className="text-xs text-gray-500">Total Gastado</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{formatCurrency(clienteDetalle.ticket_promedio)}</div>
                  <div className="text-xs text-gray-500">Ticket Prom.</div>
                </div>
              </div>

              {/* Info */}
              <div className="p-4 space-y-4">
                {clienteDetalle.direccion_actual && (
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                      <div className="text-sm text-gray-500">Última dirección</div>
                      <div className="text-gray-800">{clienteDetalle.direccion_actual}</div>
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <div className="text-sm text-gray-500">Primer pedido</div>
                    <div className="text-gray-800">{clienteDetalle.primer_pedido}</div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <div className="text-sm text-gray-500">Último pedido</div>
                    <div className="text-gray-800">{clienteDetalle.ultimo_pedido}</div>
                  </div>
                </div>

                {clienteDetalle.historial && clienteDetalle.historial.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-2">
                      <ShoppingBag className="w-4 h-4" />
                      Historial de Pedidos
                    </h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {clienteDetalle.historial.slice(0, 10).map((pedido, idx) => (
                        <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded-lg text-sm">
                          <span className="text-gray-600">{pedido.fecha_pedido}</span>
                          <span className="text-gray-500">{pedido.tipo_servicio}</span>
                          <span className="font-medium text-green-600">{formatCurrency(pedido.total_pedido)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
