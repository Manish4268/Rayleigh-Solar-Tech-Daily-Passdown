import pandas as pd
import os
from statistics import mean, stdev, median, quantiles
from flask import jsonify

def calculate_box_plot_stats(values):
    """Calculate box plot statistics from a list of values."""
    if not values or len(values) == 0:
        return {
            'min': 0,
            'q1': 0,
            'median': 0,
            'q3': 0,
            'max': 0,
            'mean': 0,
            'std': 0,
            'count': 0
        }
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    # Calculate quartiles
    if n >= 4:
        q_values = quantiles(sorted_values, n=4)
        q1, median_val, q3 = q_values[0], q_values[1], q_values[2]
    else:
        # Fallback for small datasets
        q1 = sorted_values[0]
        median_val = median(sorted_values)
        q3 = sorted_values[-1]
    
    return {
        'min': round(min(sorted_values), 2),
        'q1': round(q1, 2),
        'median': round(median_val, 2),
        'q3': round(q3, 2),
        'max': round(max(sorted_values), 2),
        'mean': round(mean(sorted_values), 2),
        'std': round(stdev(sorted_values) if len(sorted_values) > 1 else 0, 2),
        'count': len(sorted_values) / 4
    }


def extract_chart_data():
    """Extract chart data from the actual Baseline.xlsx file"""
    xlsx_path = r"C:\Users\ManishJadhav\ReactProject\Rayleigh-Solar-Tech-Daily-Passdown\Data\BaseLine.xlsx"

    parameter_mapping = {
        'PCE': 'PCE (%)',
        'FF': 'FF (%)',
        'Max Power': 'Max Power (mW/cm2)',
        'HI': 'HI (%)',
        'I_sc': 'J_sc (mA/cm2)',
        'V_oc': 'V_oc (V)',
        'R_series': 'R_series (Ohm.cm2)',
        'R_shunt': 'R_shunt (Ohm.cm2)'
    }

    # Default empty stats row
    empty_stats = {'min': 0, 'q1': 0, 'median': 0, 'q3': 0, 'max': 0, 'mean': 0, 'std': 0, 'count': 0}

    chart_data = {k: [] for k in parameter_mapping}

    if not os.path.exists(xlsx_path):
        print(f"⚠️ Excel file not found at: {xlsx_path}")
        for k in chart_data:
            entry = dict(empty_stats)
            entry['batch'] = 'No Data'
            chart_data[k].append(entry)
        return chart_data

    try:
        print(f"📊 Reading Excel file: {xlsx_path}")
        df = pd.read_excel(xlsx_path)
        print(f"✅ Excel file loaded successfully. Shape: {df.shape}")
        print(f"📋 Available columns: {list(df.columns)}")
        
        # If there's a batch column, group by it
        batch_column = None
        for col in df.columns:
            if 'batch' in str(col).lower() or 'id' in str(col).lower():
                batch_column = col
                break
        
        if batch_column:
            print(f"📊 Found batch column: {batch_column}")
            batches = df[batch_column].unique()
            print(f"📋 Available batches: {batches}")
        else:
            # Treat all data as one batch
            batches = ['Baseline']
            print("📊 No batch column found, treating all data as 'Baseline'")
        
    except Exception as e:
        print(f"❌ Unable to read BaseLine.xlsx: {e}")
        for k in chart_data:
            entry = dict(empty_stats)
            entry['batch'] = 'Error'
            chart_data[k].append(entry)
        return chart_data

    # Case-insensitive column access helper
    colmap = {str(c).upper(): c for c in df.columns}

    for param, col in parameter_mapping.items():
        col_key = colmap.get(col.upper())
        if col_key is None:
            print(f"⚠️ Column not found: {col}")
            # Try alternative column names
            for alt_col in df.columns:
                if param.lower() in str(alt_col).lower():
                    col_key = alt_col
                    print(f"✅ Found alternative column for {param}: {alt_col}")
                    break
        
        if col_key is None:
            # No data found for this parameter
            stats = dict(empty_stats)
            stats['batch'] = 'No Data'
            chart_data[param].append(stats)
            continue
        
        # Process data by batch or as single batch
        if batch_column and batch_column in df.columns:
            for batch in batches:
                batch_data = df[df[batch_column] == batch]
                vals = pd.to_numeric(batch_data[col_key], errors='coerce').dropna().tolist()
                stats = calculate_box_plot_stats(vals) if vals else dict(empty_stats)
                stats['batch'] = str(batch)
                chart_data[param].append(stats)
        else:
            # Single batch (all data)
            vals = pd.to_numeric(df[col_key], errors='coerce').dropna().tolist()
            stats = calculate_box_plot_stats(vals) if vals else dict(empty_stats)
            stats['batch'] = 'Baseline'
            chart_data[param].append(stats)

    return chart_data

def get_parameter_data(parameter):
    """Get data for a specific parameter."""
    try:
        all_data = extract_chart_data()
        if parameter in all_data:
            return all_data[parameter]
        else:
            return []
    except Exception as e:
        print(f"Error getting parameter data: {e}")
        return []

def get_all_parameters():
    """Get list of available parameters."""
    return ['PCE', 'FF', 'Max Power', 'HI', 'I_sc', 'V_oc', 'R_series', 'R_shunt']

def extract_device_yield_data():
    """Extract device yield data with 2.5% quantiles and batch averages for 6 key parameters."""
    xlsx_path = r"C:\Users\ManishJadhav\ReactProject\Rayleigh-Solar-Tech-Daily-Passdown\Data\BaseLine.xlsx"
    
    # Focus on 6 key parameters for device yield
    yield_parameters = {
        'PCE': 'PCE (%)',
        'FF': 'FF (%)', 
        'Max Power': 'Max Power (mW/cm2)',
        'HI': 'HI (%)',
        'I_sc': 'J_sc (mA/cm2)',
        'V_oc': 'V_oc (V)'
    }
    
    if not os.path.exists(xlsx_path):
        print(f"⚠️ Excel file not found at: {xlsx_path}")
        return {'parameters': [], 'batches': [], 'quantiles': {}, 'batch_averages': {}}
    
    try:
        print(f"📊 Reading Excel file for device yield: {xlsx_path}")
        df = pd.read_excel(xlsx_path)
        
        # Find batch column
        batch_column = None
        for col in df.columns:
            if 'batch' in str(col).lower() or 'id' in str(col).lower():
                batch_column = col
                break
        
        if not batch_column:
            print("❌ No batch column found for device yield analysis")
            return {'parameters': [], 'batches': [], 'quantiles': {}, 'batch_averages': {}}
        
        batches = sorted(df[batch_column].unique())
        print(f"📋 Processing {len(batches)} batches for device yield")
        
        # Case-insensitive column mapping
        colmap = {str(c).upper(): c for c in df.columns}
        
        result = {
            'parameters': list(yield_parameters.keys()),
            'batches': [str(b) for b in batches],
            'quantiles': {},
            'batch_averages': {}
        }
        
        # Calculate 2.5% quantiles and batch averages for each parameter
        for param, col_name in yield_parameters.items():
            col_key = colmap.get(col_name.upper())
            if col_key is None:
                print(f"⚠️ Column not found for {param}: {col_name}")
                continue
            
            # Get all values for this parameter (aggregated across all batches)
            all_values = pd.to_numeric(df[col_key], errors='coerce').dropna().tolist()
            
            if len(all_values) > 0:
                # Calculate 2.5% quantile (lower threshold)
                quantile_2_5 = round(quantiles(all_values, n=40)[0], 3)  # 2.5% = 1/40
                result['quantiles'][param] = quantile_2_5
                
                # Calculate batch averages
                batch_avgs = []
                for batch in batches:
                    batch_data = df[df[batch_column] == batch]
                    batch_values = pd.to_numeric(batch_data[col_key], errors='coerce').dropna().tolist()
                    if batch_values:
                        avg = round(mean(batch_values), 3)
                        batch_avgs.append(avg)
                    else:
                        batch_avgs.append(0)
                
                result['batch_averages'][param] = batch_avgs
                print(f"✅ {param}: 2.5% quantile = {quantile_2_5}, batch averages calculated")
            else:
                print(f"❌ No valid data for {param}")
                result['quantiles'][param] = 0
                result['batch_averages'][param] = [0] * len(batches)
        
        return result
        
    except Exception as e:
        print(f"❌ Error extracting device yield data: {e}")
        return {'parameters': [], 'batches': [], 'quantiles': {}, 'batch_averages': {}}