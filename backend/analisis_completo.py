"""
Análisis completo y detallado de los archivos Excel de OlaClick
"""
import pandas as pd
from pathlib import Path

excel_dir = Path(r"C:\Users\raulc\Downloads\excel pizza max")
latest_file = list(excel_dir.glob("*.xlsx"))[-1]  # Más reciente por nombre

print("="*100)
print(f"📊 ANALIZANDO: {latest_file.name}")
print("="*100)

with pd.ExcelFile(latest_file) as excel:
    
    # ============ HOJA PEDIDOS ============
    print("\n" + "🔴"*50)
    print("📄 HOJA: PEDIDOS")
    print("🔴"*50)
    
    df = pd.read_excel(excel, sheet_name='Pedidos')
    print(f"\nColumnas: {list(df.columns)}")
    
    print("\n📋 COLUMNAS DETALLADAS:")
    for col in df.columns:
        print(f"\n   🔹 {col}")
        if df[col].dtype == 'object':
            unique = df[col].dropna().unique()[:8]
            print(f"      Valores: {list(unique)}")
        else:
            print(f"      Min: {df[col].min()}, Max: {df[col].max()}, Media: {df[col].mean():.2f}")
    
    # ============ HOJA DETALLES ============
    print("\n" + "🟢"*50)
    print("📄 HOJA: DETALLES")
    print("🟢"*50)
    
    df = pd.read_excel(excel, sheet_name='Detalles')
    print(f"\nColumnas: {list(df.columns)}")
    
    print("\n📋 COLUMNAS DETALLADAS:")
    for col in df.columns:
        print(f"\n   🔹 {col}")
        if df[col].dtype == 'object':
            unique = df[col].dropna().unique()[:8]
            print(f"      Valores: {list(unique)}")
        else:
            print(f"      Min: {df[col].min()}, Max: {df[col].max()}, Media: {df[col].mean():.2f}")
    
    # ============ ANÁLISIS DE PRODUCTOS ============
    print("\n" + "🟡"*50)
    print("📊 ANÁLISIS DE PRODUCTOS")
    print("🟡"*50)
    
    df = pd.read_excel(excel, sheet_name='Detalles')
    
    # Productos más vendidos
    print("\n🏆 TOP 15 PRODUCTOS MÁS VENDIDOS:")
    if 'Nombre del producto' in df.columns:
        top = df.groupby('Nombre del producto')['Cantidad'].sum().sort_values(ascending=False).head(15)
        for i, (prod, cant) in enumerate(top.items(), 1):
            print(f"   {i:2}. {prod[:50]:<50} | {cant:>5} unidades")
    
    # Por categoría
    print("\n📁 VENTAS POR CATEGORÍA:")
    if 'Categoría' in df.columns:
        cats = df.groupby('Categoría')['Cantidad'].sum().sort_values(ascending=False)
        for cat, cant in cats.items():
            print(f"   - {cat}: {cant} unidades")
    
    # ============ ANÁLISIS TEMPORAL ============
    print("\n" + "🔵"*50)
    print("⏰ ANÁLISIS TEMPORAL")
    print("🔵"*50)
    
    df = pd.read_excel(excel, sheet_name='Pedidos')
    if 'Fecha de creación' in df.columns:
        df['fecha_dt'] = pd.to_datetime(df['Fecha de creación'], format='%d/%m/%Y | %H:%M', errors='coerce')
        df['hora'] = df['fecha_dt'].dt.hour
        df['dia_semana'] = df['fecha_dt'].dt.dayofweek
        
        print("\n📊 PEDIDOS POR HORA DEL DÍA:")
        por_hora = df.groupby('hora').size().sort_index()
        for hora, count in por_hora.items():
            bar = "█" * (count // 2)
            print(f"   {int(hora):02d}:00 | {bar} {count}")
        
        print("\n📊 PEDIDOS POR DÍA DE SEMANA:")
        dias = {0:'Lun', 1:'Mar', 2:'Mié', 3:'Jue', 4:'Vie', 5:'Sáb', 6:'Dom'}
        por_dia = df.groupby('dia_semana').size().sort_index()
        for dia, count in por_dia.items():
            bar = "█" * (count // 3)
            print(f"   {dias.get(dia, dia)} | {bar} {count}")
    
    # ============ ANÁLISIS DE TIPO DE SERVICIO ============
    print("\n" + "🟣"*50)
    print("🚗 ANÁLISIS TIPO DE SERVICIO")
    print("🟣"*50)
    
    if 'Tipo de servicio' in df.columns:
        servicios = df.groupby('Tipo de servicio').agg({
            'Total': ['count', 'sum', 'mean']
        }).round(2)
        print("\n📊 VENTAS POR TIPO DE SERVICIO:")
        print(servicios.to_string())
    
    # ============ ANÁLISIS DE MÉTODO DE PAGO ============
    print("\n" + "🟠"*50)
    print("💳 ANÁLISIS MÉTODO DE PAGO")
    print("🟠"*50)
    
    if 'Método de pago' in df.columns:
        pagos = df.groupby('Método de pago').agg({
            'Total': ['count', 'sum', 'mean']
        }).round(2)
        print("\n📊 VENTAS POR MÉTODO DE PAGO:")
        print(pagos.to_string())
    
    # ============ DATOS DE VISITAS ============
    print("\n" + "⚪"*50)
    print("👁️ ANÁLISIS DE VISITAS")
    print("⚪"*50)
    
    df_visitas = pd.read_excel(excel, sheet_name='Visitas')
    print(f"\nDatos de visitas disponibles:")
    print(df_visitas.to_string())
    
    if len(df_visitas) > 0:
        total_visitas = df_visitas['Menús Vistos'].sum()
        total_pedidos = df_visitas['Pedido creado'].sum()
        conversion = (total_pedidos / total_visitas * 100) if total_visitas > 0 else 0
        print(f"\n📈 Tasa de conversión: {conversion:.1f}%")

print("\n" + "="*100)
print("🎯 OPORTUNIDADES DE MEJORA IDENTIFICADAS")
print("="*100)
print("""
1. ⏰ HORA DEL DÍA
   - Tenemos la hora exacta de cada pedido
   - Podemos predecir por franjas horarias (almuerzo, cena, etc.)
   - Feature: 'hora_pico' (12-14, 19-22)

2. 💳 MÉTODO DE PAGO
   - Efectivo vs Tarjeta vs Transferencia
   - Correlación con ticket promedio

3. 🚗 TIPO DE SERVICIO
   - Domicilio vs Para llevar vs En local
   - Cada uno tiene patrones diferentes

4. 👁️ VISITAS Y CONVERSIÓN
   - Menús vistos → Pedidos iniciados → Pedidos creados
   - Tasa de conversión por día

5. 🍕 PRODUCTOS ESPECÍFICOS
   - Tracking de productos más vendidos
   - Detección de tendencias por producto

6. 📦 MODIFICADORES/INGREDIENTES EXTRA
   - Qué ingredientes extras se piden más
   - Correlación con ventas

7. 🔄 TICKET PROMEDIO
   - Por día de semana
   - Por hora del día
   - Por tipo de servicio
""")
