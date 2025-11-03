#!/usr/bin/env python3
"""
Test script for BaseLine.xlsx analysis
Tests the analysis API with real data from the Data folder
"""

import pandas as pd
import sys
import os

# Add current directory to path for imports
sys.path.append('.')

def examine_baseline_data():
    """Examine the structure of BaseLine.xlsx"""
    file_path = "../Data/BaseLine.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📄 Examining: {file_path}")
    print("=" * 60)
    
    try:
        # Try to read all sheets
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 Available sheets: {excel_file.sheet_names}")
        
        # Try reading the first sheet or 'Data' sheet
        if 'Data' in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name='Data')
            sheet_name = 'Data'
        else:
            df = pd.read_excel(file_path, sheet_name=0)  # Read first sheet
            sheet_name = excel_file.sheet_names[0]
        
        print(f"\n📊 Reading sheet: '{sheet_name}'")
        print(f"📏 Shape: {df.shape} (rows x columns)")
        print(f"📝 Columns: {list(df.columns)}")
        
        # Check for required columns
        required_cols = ["Batch ID", "Sheet ID", "Device ID", "Pixel ID", "Scan Direction", "PCE (%)"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        found_cols = [col for col in required_cols if col in df.columns]
        
        print(f"\n✅ Found required columns: {found_cols}")
        if missing_cols:
            print(f"❌ Missing required columns: {missing_cols}")
            
            # Try to find similar column names
            print(f"\n🔍 Searching for similar column names:")
            for missing_col in missing_cols:
                similar = [col for col in df.columns if missing_col.lower().replace(" ", "").replace("(", "").replace(")", "") in col.lower().replace(" ", "").replace("(", "").replace(")", "")]
                if similar:
                    print(f"   '{missing_col}' -> Similar: {similar}")
        
        # Show sample data
        print(f"\n📋 First 5 rows:")
        print(df.head())
        
        # Show data types
        print(f"\n📊 Data types:")
        for col in df.columns:
            print(f"   {col}: {df[col].dtype}")
        
        # Check for unique values in key columns
        key_cols = ['Batch ID', 'Sheet ID', 'Device ID', 'Scan Direction']
        for col in key_cols:
            if col in df.columns:
                unique_vals = df[col].nunique()
                sample_vals = df[col].unique()[:5]  # Show first 5 unique values
                print(f"\n🔑 {col}: {unique_vals} unique values")
                print(f"   Sample: {list(sample_vals)}")
        
        return True, df
        
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return False, None

def test_analysis_api():
    """Test the analysis API with BaseLine.xlsx"""
    print("\n" + "=" * 60)
    print("🧪 TESTING ANALYSIS API")
    print("=" * 60)
    
    try:
        from analysis_api import process_excel_analysis
        
        file_path = "../Data/BaseLine.xlsx"
        
        # Test options matching the frontend defaults
        test_options = {
            'sheetsMode': 'top-k',
            'sheetsTopK': 6,
            'devicesMode': 'top-k', 
            'devicesTopK': 6,
            'pixelsPerDevice': 3,
            'method': 'minimize-sd',
            'basis': 'forward',
            'useAllSheets': True,
            'sheetIds': ''
        }
        
        print(f"📁 Processing file: {file_path}")
        print(f"⚙️ Options: {test_options}")
        
        result = process_excel_analysis(file_path, test_options)
        
        print(f"\n📊 RESULT:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('message', 'no message')}")
        
        if result.get('status') == 'success':
            summary = result.get('summary', {})
            print(f"\n📈 SUMMARY:")
            print(f"  Sheets processed: {summary.get('sheetsProcessed', 'N/A')}")
            print(f"  Devices analyzed: {summary.get('devicesAnalyzed', 'N/A')}")
            print(f"  Total pixels: {summary.get('totalPixels', 'N/A')}")
            
            results_data = result.get('results', [])
            print(f"\n📋 ANALYSIS RESULTS: ({len(results_data)} entries)")
            
            if results_data:
                print("Top 3 results:")
                for i, row in enumerate(results_data[:3]):
                    print(f"  {i+1}. Batch {row.get('Batch ID', 'N/A')}, Sheet {row.get('Sheet ID', 'N/A')}")
                    print(f"     Mean PCE: {row.get('Combined mean PCE', 'N/A'):.4f}")
                    print(f"     SD PCE: {row.get('Combined SD PCE', 'N/A'):.4f}")
        
        logs = result.get('logs', [])
        if logs:
            print(f"\n📝 PROCESSING LOGS:")
            for log in logs:
                print(f"  {log}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing analysis API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    print("🚀 BASELINE DATA ANALYSIS TEST")
    print("=" * 60)
    
    # Step 1: Examine the data structure
    success, df = examine_baseline_data()
    
    if not success:
        print("❌ Cannot proceed with API test - data examination failed")
        return
    
    # Step 2: Test the analysis API
    result = test_analysis_api()
    
    if result:
        print(f"\n✅ Test completed successfully!")
        print(f"Result status: {result.get('status', 'unknown')}")
    else:
        print(f"\n❌ Test failed")

if __name__ == "__main__":
    main()