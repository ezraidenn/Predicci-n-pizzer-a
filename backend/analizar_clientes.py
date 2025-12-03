"""
Análisis de datos de clientes en los archivos Excel de OlaClick
"""
import pandas as pd
from pathlib import Path

excel_dir = Path(r"C:\Users\raulc\Downloads\excel pizza max")
files = list(excel_dir.glob("*.xlsx"))

print("="*100)
print("🔍 BUSCANDO DATOS DE CLIENTES EN ARCHIVOS EXCEL")
print("="*100)

# Analizar archivo más reciente
latest_file = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
print(f"\n📁 Analizando: {latest_file.name}")

with pd.ExcelFile(latest_file) as excel:
    print(f"\n📑 Hojas disponibles: {excel.sheet_names}")
    
    for sheet_name in excel.sheet_names:
        df = pd.read_excel(excel, sheet_name=sheet_name)
        
        # Buscar columnas relacionadas con clientes
        cliente_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in 
                       ['cliente', 'nombre', 'teléfono', 'telefono', 'dirección', 'direccion', 
                        'email', 'correo', 'celular', 'móvil', 'movil', 'calle', 'colonia',
                        'código postal', 'cp', 'ciudad', 'contacto', 'whatsapp'])]
        
        if cliente_cols:
            print(f"\n{'='*80}")
            print(f"📄 HOJA: {sheet_name}")
            print(f"{'='*80}")
            print(f"\n🎯 COLUMNAS RELACIONADAS CON CLIENTES:")
            for col in cliente_cols:
                non_null = df[col].notna().sum()
                unique = df[col].nunique()
                samples = df[col].dropna().head(3).tolist()
                print(f"\n   📌 {col}")
                print(f"      No-nulos: {non_null} | Únicos: {unique}")
                print(f"      Ejemplos: {samples[:2]}")
        
        # Mostrar TODAS las columnas de cada hoja
        print(f"\n📋 TODAS LAS COLUMNAS DE '{sheet_name}':")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2}. {col}")

print("\n" + "="*100)
print("📊 ANÁLISIS DETALLADO DE HOJA PEDIDOS")
print("="*100)

with pd.ExcelFile(latest_file) as excel:
    df_pedidos = pd.read_excel(excel, sheet_name='Pedidos')
    
    print(f"\nTotal pedidos: {len(df_pedidos)}")
    print(f"\nColumnas completas:")
    for col in df_pedidos.columns:
        non_null = df_pedidos[col].notna().sum()
        dtype = df_pedidos[col].dtype
        print(f"   - {col:<40} | {dtype} | {non_null} valores")
    
    # Ver primeras filas
    print(f"\n🔎 PRIMERAS 3 FILAS COMPLETAS:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df_pedidos.head(3).T)  # Transpuesto para mejor lectura
