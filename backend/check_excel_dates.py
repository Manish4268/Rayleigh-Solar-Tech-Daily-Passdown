#!/usr/bin/env python3
"""
Check date columns in Excel file
"""

import pandas as pd
import os

def check_excel_columns():
    """Check what columns are available in the Excel file"""
    xlsx_path = r"C:\Users\ManishJadhav\ReactProject\Rayleigh-Solar-Tech-Daily-Passdown\Data\BaseLine.xlsx"
    
    if not os.path.exists(xlsx_path):
        print(f"❌ Excel file not found at: {xlsx_path}")
        return
    
    try:
        print(f"📊 Reading Excel file: {xlsx_path}")
        df = pd.read_excel(xlsx_path)
        print(f"✅ Excel file loaded successfully. Shape: {df.shape}")
        print()
        
        print("📋 All available columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")
        print()
        
        # Look for date-related columns
        date_columns = []
        for col in df.columns:
            if any(word in str(col).lower() for word in ['date', 'time', 'day']):
                date_columns.append(col)
        
        print(f"📅 Potential date columns: {date_columns}")
        
        # Check sample data from date columns
        for col in date_columns:
            print(f"\n📊 Sample data from '{col}':")
            print(df[col].head(10).tolist())
            print(f"Data type: {df[col].dtype}")
            
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")

if __name__ == "__main__":
    check_excel_columns()