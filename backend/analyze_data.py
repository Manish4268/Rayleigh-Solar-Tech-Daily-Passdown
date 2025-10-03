import pandas as pd
import os
import json
from statistics import mean, stdev

def analyze_excel_structure():
    """Analyze the structure of the Excel files to understand the data format."""
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    
    for batch in ['58', '59']:
        excel_path = os.path.join(base_path, batch, f'{batch}.xlsx')
        if os.path.exists(excel_path):
            print(f"\n=== Batch {batch} Analysis ===")
            try:
                # Try to read the Excel file
                df = pd.read_excel(excel_path)
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"First 3 rows:")
                print(df.head(3))
                
                # Look for specific parameter columns
                parameter_columns = []
                for col in df.columns:
                    if any(param in str(col).upper() for param in ['PCE', 'FF', 'POWER', 'HI', 'ISC', 'VOC', 'SERIES', 'SHUNT']):
                        parameter_columns.append(col)
                
                print(f"Parameter columns found: {parameter_columns}")
                
            except Exception as e:
                print(f"Error reading {excel_path}: {e}")
                # Try reading different sheets
                try:
                    xl_file = pd.ExcelFile(excel_path)
                    print(f"Available sheets: {xl_file.sheet_names}")
                    for sheet in xl_file.sheet_names[:3]:  # Check first 3 sheets
                        print(f"\nSheet '{sheet}':")
                        df = pd.read_excel(excel_path, sheet_name=sheet)
                        print(f"Columns: {list(df.columns)}")
                except Exception as e2:
                    print(f"Error reading sheets: {e2}")

if __name__ == "__main__":
    analyze_excel_structure()