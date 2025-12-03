import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, Search, Phone, MapPin, DollarSign, Calendar, 
  TrendingUp, Star, Clock, ChevronRight, X, ShoppingBag
} from 'lucide-react';
import axios from 'axios';

const API_URL = '/api';

export default function Clientes() {
  const [clientes, setClientes] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCliente, setSelectedCliente] = useState(null);
  const [clienteDetalle, setClienteDetalle] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [clientesRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/clientes?limit=100&order_by=total_gastado DESC`),
        axios.get(`${API_URL}/clientes/stats`)
      ]);
      
      setClientes(clientesRes.data.clientes || []);
      setStats(statsRes.data.stats || null);
    } catch (error) {
      console.error('Error cargando clientes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchData();
      return;
    }
    
    try {
      const res = await axios.get(`${API_URL}/clientes/buscar/${searchQuery}`);
      setClientes(res.data.resultados || []);
    } catch (error) {
      console.error('Error buscando:', error);
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
      currency: 'MXN'
    }).format(value || 0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 text-white"
        >
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-5 h-5" />
            <span className="text-sm opacity-80">Total Clientes</span>
          </div>
          <div className="text-3xl font-bold">{stats?.total_clientes || 0}</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-4 text-white"
        >
          <div className="flex items-center gap-2 mb-2">
            <Star className="w-5 h-5" />
            <span className="text-sm opacity-80">Frecuentes</span>
          </div>
          <div className="text-3xl font-bold">{stats?.clientes_frecuentes || 0}</div>
          <div className="text-xs opacity-70">3+ pedidos</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-4 text-white"
        >
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-5 h-5" />
            <span className="text-sm opacity-80">Ticket Promedio</span>
          </div>
          <div className="text-2xl font-bold">{formatCurrency(stats?.ticket_promedio_global)}</div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-4 text-white"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5" />
            <span className="text-sm opacity-80">Retención</span>
          </div>
          <div className="text-3xl font-bold">{stats?.tasa_retencion || 0}%</div>
          <div className="text-xs opacity-70">Clientes que regresan</div>
        </motion.div>
      </div>


      {/* Lista de Clientes con Búsqueda integrada */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Header con búsqueda */}
        <div className="p-4 border-b border-gray-100">
          <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
            <h3 className="font-bold text-gray-800">Todos los Clientes ({clientes.length})</h3>
            <div className="flex gap-2 w-full sm:w-auto">
              <div className="relative flex-1 sm:w-64">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Buscar nombre o teléfono..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium"
              >
                Buscar
              </button>
              {searchQuery && (
                <button
                  onClick={() => { setSearchQuery(''); fetchData(); }}
                  className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                >
                  Limpiar
                </button>
              )}
            </div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-100 max-h-[500px] overflow-y-auto">
          {clientes.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No hay clientes registrados</p>
              <p className="text-sm">Sube archivos Excel para cargar clientes</p>
            </div>
          ) : (
            clientes.map((cliente, idx) => (
              <motion.div
                key={cliente.telefono}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: idx * 0.02 }}
                onClick={() => handleClienteClick(cliente.telefono)}
                className="p-4 hover:bg-gray-50 cursor-pointer transition-colors flex items-center gap-4"
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  cliente.es_cliente_frecuente ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
                }`}>
                  {cliente.es_cliente_frecuente ? <Star className="w-5 h-5" /> : <Users className="w-5 h-5" />}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-800 truncate">{cliente.nombre || 'Sin nombre'}</div>
                  <div className="flex items-center gap-3 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Phone className="w-3 h-3" />
                      {cliente.telefono}
                    </span>
                    {cliente.direccion_actual && (
                      <span className="flex items-center gap-1 truncate">
                        <MapPin className="w-3 h-3" />
                        {cliente.direccion_actual.substring(0, 30)}...
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="font-bold text-gray-800">{formatCurrency(cliente.total_gastado)}</div>
                  <div className="text-xs text-gray-500">{cliente.total_pedidos} pedidos</div>
                </div>
                
                <ChevronRight className="w-5 h-5 text-gray-300" />
              </motion.div>
            ))
          )}
        </div>
      </div>

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
                {/* Dirección actual */}
                {clienteDetalle.direccion_actual && (
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                      <div className="text-sm text-gray-500">Última dirección</div>
                      <div className="text-gray-800">{clienteDetalle.direccion_actual}</div>
                    </div>
                  </div>
                )}

                {/* Fechas */}
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

                {/* Historial de pedidos */}
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
