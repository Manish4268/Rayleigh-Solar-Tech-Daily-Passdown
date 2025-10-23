"""
Stability Device Data API
Provides graph data for individual devices from device_FR_averaged.csv
"""

import pandas as pd
import os
from pathlib import Path
from flask import jsonify

class StabilityDeviceDataAPI:
    """API for stability device performance data"""
    
    def __init__(self):
        # Path to the CSV files (in root directory)
        self.root_dir = Path(__file__).parent.parent
        self.fr_csv_path = self.root_dir / "device_FR_averaged.csv"
        self.t80_csv_path = self.root_dir / "T80_summary.csv"
        
        # Cache for dataframes
        self._fr_df = None
        self._t80_df = None
        
        # Available parameters for graphing
        self.available_parameters = [
            'PCE', 'Max_Power', 'FF', 'J_sc', 'V_oc', 'HI', 'R_shunt', 'R_series'
        ]
    
    def _load_fr_data(self):
        """Load device_FR_averaged.csv with caching"""
        if self._fr_df is None:
            try:
                if not self.fr_csv_path.exists():
                    print(f"⚠️ device_FR_averaged.csv not found at {self.fr_csv_path}")
                    return pd.DataFrame()
                
                self._fr_df = pd.read_csv(self.fr_csv_path)
                print(f"✅ Loaded device_FR_averaged.csv: {len(self._fr_df)} rows")
            except Exception as e:
                print(f"❌ Error loading device_FR_averaged.csv: {e}")
                return pd.DataFrame()
        
        return self._fr_df
    
    def _load_t80_data(self):
        """Load T80_summary.csv with caching"""
        if self._t80_df is None:
            try:
                if not self.t80_csv_path.exists():
                    print(f"⚠️ T80_summary.csv not found at {self.t80_csv_path}")
                    return pd.DataFrame()
                
                self._t80_df = pd.read_csv(self.t80_csv_path)
                print(f"✅ Loaded T80_summary.csv: {len(self._t80_df)} rows")
            except Exception as e:
                print(f"❌ Error loading T80_summary.csv: {e}")
                return pd.DataFrame()
        
        return self._t80_df
    
    def get_device_data(self, device_id):
        """
        Get all performance data for a specific device
        
        Args:
            device_id: Device identifier (e.g., "B25-65-S005-B2")
            
        Returns:
            dict: Device data including time series and T80 info
        """
        try:
            # Load data
            fr_df = self._load_fr_data()
            t80_df = self._load_t80_data()
            
            if fr_df.empty:
                return jsonify({
                    'success': False,
                    'error': 'Device FR data not available'
                }), 404
            
            # Filter data for this device
            device_data = fr_df[fr_df['Device'] == device_id].copy()
            
            if device_data.empty:
                return jsonify({
                    'success': False,
                    'error': f'No data found for device {device_id}'
                }), 404
            
            # Sort by time
            device_data = device_data.sort_values('Time_hrs')
            
            # Prepare time series data
            time_series = []
            for _, row in device_data.iterrows():
                data_point = {
                    'time_hrs': float(row['Time_hrs']),
                    'batch': int(row['Batch']) if pd.notna(row['Batch']) else 0
                }
                
                # Add all available parameters
                for param in self.available_parameters:
                    if param in row and pd.notna(row[param]):
                        data_point[param] = float(row[param])
                    else:
                        data_point[param] = None
                
                time_series.append(data_point)
            
            # Get T80 info if available
            t80_info = {}
            if not t80_df.empty:
                t80_row = t80_df[t80_df['Device'] == device_id]
                if not t80_row.empty:
                    t80_row = t80_row.iloc[0]
                    t80_info = {
                        'reached_t80': bool(t80_row['Reached_T80']),
                        't80_hours': float(t80_row['T80_hours']) if pd.notna(t80_row['T80_hours']) else None,
                        'baseline_pce': float(t80_row['Baseline_PCE']) if pd.notna(t80_row['Baseline_PCE']) else None,
                        'threshold_pce': float(t80_row['Threshold_PCE']) if pd.notna(t80_row['Threshold_PCE']) else None
                    }
            
            return jsonify({
                'success': True,
                'device_id': device_id,
                'data_points': len(time_series),
                'time_series': time_series,
                't80_info': t80_info,
                'available_parameters': self.available_parameters
            })
            
        except Exception as e:
            print(f"❌ Error getting device data: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_available_devices(self):
        """Get list of all devices with data"""
        try:
            fr_df = self._load_fr_data()
            
            if fr_df.empty:
                return jsonify({
                    'success': False,
                    'error': 'No device data available'
                }), 404
            
            devices = sorted(fr_df['Device'].unique().tolist())
            
            return jsonify({
                'success': True,
                'devices': devices,
                'count': len(devices)
            })
            
        except Exception as e:
            print(f"❌ Error getting available devices: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def refresh_data(self):
        """Clear cache and reload data from files"""
        self._fr_df = None
        self._t80_df = None
        
        # Attempt to reload
        fr_df = self._load_fr_data()
        t80_df = self._load_t80_data()
        
        return jsonify({
            'success': True,
            'message': 'Data refreshed successfully',
            'fr_rows': len(fr_df) if not fr_df.empty else 0,
            't80_rows': len(t80_df) if not t80_df.empty else 0
        })


# Singleton instance
_device_data_api_instance = None

def get_device_data_api():
    """Get or create the singleton device data API instance"""
    global _device_data_api_instance
    if _device_data_api_instance is None:
        _device_data_api_instance = StabilityDeviceDataAPI()
    return _device_data_api_instance
