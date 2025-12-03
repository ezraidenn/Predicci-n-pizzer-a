"""
Análisis exhaustivo de los archivos Excel de OlaClick
Para identificar datos que podemos aprovechar
"""
import pandas as pd
from pathlib import Path

excel_dir = Path(r"C:\Users\raulc\Downloads\excel pizza max")

# Tomar el archivo más reciente para análisis
files = list(excel_dir.glob("*.xlsx"))
files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

print("="*100)
print("📊 ANÁLISIS EXHAUSTIVO DE ARCHIVOS EXCEL OLACLICK")
print("="*100)

print(f"\n📁 Archivos encontrados: {len(files)}")
for f in files[:5]:
    print(f"   - {f.name}")
print("   ...")

# Analizar el archivo más reciente
latest_file = files[0]
print(f"\n🔍 Analizando: {latest_file.name}")
print("="*100)

with pd.ExcelFile(latest_file) as excel:
    print(f"\n📑 HOJAS DISPONIBLES: {excel.sheet_names}")
    
    for sheet_name in excel.sheet_names:
        print(f"\n{'='*100}")
        print(f"📄 HOJA: {sheet_name}")
        print("="*100)
        
        df = pd.read_excel(excel, sheet_name=sheet_name)
        
        print(f"\n📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        print(f"\n📋 COLUMNAS DISPONIBLES:")
        for i, col in enumerate(df.columns):
            dtype = df[col].dtype
            non_null = df[col].notna().sum()
            sample = df[col].dropna().head(3).tolist() if non_null > 0 else []
            print(f"   {i+1:2}. {col:<40} | Tipo: {str(dtype):<15} | No-null: {non_null:>5} | Ejemplo: {sample[:2]}")
        
        # Ver primeras filas
        print(f"\n🔎 PRIMERAS 3 FILAS:")
        print(df.head(3).to_string())
        
        # Valores únicos de columnas categóricas importantes
        categorical_cols = ['Estado del pedido', 'Tipo de servicio', 'Método de pago', 
                          'Categoría', 'Nombre del producto', 'Nombre']
        
        print(f"\n📊 VALORES ÚNICOS (columnas categóricas):")
        for col in categorical_cols:
            if col in df.columns:
                unique_vals = df[col].dropna().unique()
                print(f"\n   {col} ({len(unique_vals)} únicos):")
                for val in unique_vals[:10]:
                    count = (df[col] == val).sum()
                    print(f"      - '{val}' ({count})")
                if len(unique_vals) > 10:
                    print(f"      ... y {len(unique_vals) - 10} más")

print("\n" + "="*100)
print("🎯 RESUMEN DE DATOS POTENCIALMENTE ÚTILES")
print("="*100)
print("""
DATOS QUE PODRÍAMOS ESTAR IGNORANDO:
1. Método de pago (efectivo, tarjeta, etc.)
2. Tipo de servicio más detallado
3. Hora del pedido (para análisis por hora del día)
4. Descuentos aplicados
5. Propinas
6. Datos de cliente (si hay)
7. Tiempo de entrega
8. Productos más vendidos por día/hora
9. Ticket promedio por tipo de servicio
10. Correlación entre visitas y conversión
""")
