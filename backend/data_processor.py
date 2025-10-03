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
        'count': len(sorted_values)
    }

def extract_chart_data():
    """Extract chart data for all parameters from Excel files in the Data folder."""
    base_path = os.path.dirname(os.path.dirname(__file__))
    data_folder_path = os.path.join(base_path, 'Data')
    
    # Parameter mapping - frontend name to Excel column name
    parameter_mapping = {
        'PCE': 'PCE (%)_AVG',
        'FF': 'FF (%)_AVG', 
        'Max Power': 'Max Power (mW/cm2)_AVG',
        'HI': 'HI (%)',
        'I_sc': 'J_sc (mA/cm2)_AVG',  # Using J_sc instead of I_sc as it's more standard
        'V_oc': 'V_oc (V)_AVG',
        'R_series': 'R_series (Ohm.cm2)_AVG',
        'R_shunt': 'R_shunt (Ohm.cm2)_AVG'
    }
    
    chart_data = {}
    
    for param_name, excel_column in parameter_mapping.items():
        chart_data[param_name] = []
        
        # Get all batch folders from the Data directory
        batch_folders = []
        if os.path.exists(data_folder_path):
            for item in os.listdir(data_folder_path):
                item_path = os.path.join(data_folder_path, item)
                if os.path.isdir(item_path) and item.isdigit():
                    batch_folders.append(item)
        
        batch_folders.sort(key=int)  # Sort batch numbers numerically
        
        for batch in batch_folders:
            batch_folder_path = os.path.join(data_folder_path, batch)
            
            # Look for Excel files in the batch folder
            excel_files = []
            if os.path.exists(batch_folder_path):
                for file in os.listdir(batch_folder_path):
                    if file.endswith('.xlsx') and not file.startswith('~$'):
                        excel_files.append(file)
            
            # Process the first valid Excel file found (usually should be {batch}.xlsx)
            processed = False
            for excel_file in excel_files:
                excel_path = os.path.join(batch_folder_path, excel_file)
                if os.path.exists(excel_path):
                    try:
                        df = pd.read_excel(excel_path)
                        
                        # Extract the parameter values, excluding NaN values
                        if excel_column in df.columns:
                            values = df[excel_column].dropna().tolist()
                            if values:
                                box_stats = calculate_box_plot_stats(values)
                                box_stats['batch'] = f'B{batch}'
                                chart_data[param_name].append(box_stats)
                                processed = True
                                break
                        else:
                            print(f"Warning: Column '{excel_column}' not found in batch {batch}")
                            
                    except Exception as e:
                        print(f"Error processing batch {batch} file {excel_file}: {e}")
                        continue
            
            # If no valid data was processed for this batch, add zero values
            if not processed:
                chart_data[param_name].append({
                    'batch': f'B{batch}',
                    'min': 0, 'q1': 0, 'median': 0, 'q3': 0, 'max': 0,
                    'mean': 0, 'std': 0, 'count': 0
                })
    
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