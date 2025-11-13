// Utilidades para formatear números y moneda

export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return new Intl.NumberFormat('es-MX').format(num)
}

export const formatCurrency = (num) => {
  if (num === null || num === undefined) return '$0.00'
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num)
}

export const formatPercent = (num) => {
  if (num === null || num === undefined) return '0%'
  return `${num >= 0 ? '+' : ''}${num.toFixed(1)}%`
}

export const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('es-MX', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}
