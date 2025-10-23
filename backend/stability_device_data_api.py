"""
Stability Device Data API
Provides graph data for individual devices from device_FR_averaged.csv
"""

import pandas as pd
import os
from pathlib import Path
from flask import jsonify
import requests
from io import StringIO

class StabilityDeviceDataAPI:
    """API for stability device performance data"""
    
    def __init__(self):
        # Azure configuration for CSV files
        self.azure_container_url = os.getenv('AZURE_CONTAINER_URL')
        self.azure_container_sas = os.getenv('AZURE_CONTAINER_SAS')
        
        # Cache for dataframes
        self._fr_df = None
        self._t80_df = None
        
        # Available parameters for graphing
        self.available_parameters = [
            'PCE', 'Max_Power', 'FF', 'J_sc', 'V_oc', 'HI', 'R_shunt', 'R_series'
        ]
    
    def _download_csv_from_azure(self, filename):
        """Download CSV file from Azure Blob Storage"""
        try:
            if not self.azure_container_url or not self.azure_container_sas:
                print(f"⚠️ Azure credentials not configured")
                return pd.DataFrame()
            
            # Construct blob URL with SAS token
            blob_url = f"{self.azure_container_url}/{filename}?{self.azure_container_sas}"
            
            # Download the file
            response = requests.get(blob_url)
            response.raise_for_status()
            
            # Parse CSV
            df = pd.read_csv(StringIO(response.text))
            print(f"✅ Downloaded {filename} from Azure: {len(df)} rows")
            return df
            
        except Exception as e:
            print(f"❌ Error downloading {filename} from Azure: {e}")
            return pd.DataFrame()
    
    def _load_fr_data(self):
        """Load device_FR_averaged.csv from Azure with caching"""
        if self._fr_df is None:
            self._fr_df = self._download_csv_from_azure("device_FR_averaged.csv")
        return self._fr_df
    
    def _load_t80_data(self):
        """Load T80_summary.csv from Azure with caching"""
        if self._t80_df is None:
            self._t80_df = self._download_csv_from_azure("T80_summary.csv")
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
            
            # Filter data for this device - check both 'Device' and 'Device_ID' columns
            if 'Device' in fr_df.columns:
                device_data = fr_df[fr_df['Device'] == device_id].copy()
            elif 'Device_ID' in fr_df.columns:
                device_data = fr_df[fr_df['Device_ID'] == device_id].copy()
            else:
                return jsonify({
                    'success': False,
                    'error': 'Device column not found in CSV'
                }), 404
            
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
            
            # Check for both 'Device' and 'Device_ID' columns
            if 'Device' in fr_df.columns:
                devices = sorted(fr_df['Device'].unique().tolist())
            elif 'Device_ID' in fr_df.columns:
                devices = sorted(fr_df['Device_ID'].unique().tolist())
            else:
                devices = []
            
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
    
    def check_device_t80_status(self, device_id):
        """Check if a device has reached T80"""
        try:
            t80_df = self._load_t80_data()
            
            if t80_df.empty:
                # T80 summary doesn't exist or is empty - this is normal
                return {'has_t80': False}
            
            # Check both 'Device_ID' and 'Device' columns for compatibility
            if 'Device' in t80_df.columns:
                device_t80 = t80_df[t80_df['Device'] == device_id]
            elif 'Device_ID' in t80_df.columns:
                device_t80 = t80_df[t80_df['Device_ID'] == device_id]
            else:
                print(f"⚠️ T80 summary has no Device_ID or Device column")
                return {'has_t80': False}
            
            if device_t80.empty:
                # Device not in T80 summary - hasn't reached T80 yet
                return {'has_t80': False}
            
            # Device found in T80 summary - it has reached T80
            t80_row = device_t80.iloc[0]
            return {
                'has_t80': bool(t80_row['Reached_T80']) if 'Reached_T80' in t80_row and pd.notna(t80_row['Reached_T80']) else False,
                't80_hours': float(t80_row['T80_hours']) if 'T80_hours' in t80_row and pd.notna(t80_row['T80_hours']) else None,
                'initial_pce': float(t80_row['Baseline_PCE']) if 'Baseline_PCE' in t80_row and pd.notna(t80_row['Baseline_PCE']) else None,
                't80_pce': float(t80_row['Threshold_PCE']) if 'Threshold_PCE' in t80_row and pd.notna(t80_row['Threshold_PCE']) else None
            }
            
        except Exception as e:
            print(f"❌ Error checking T80 status for {device_id}: {e}")
            import traceback
            traceback.print_exc()
            return {'has_t80': False}
    
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
