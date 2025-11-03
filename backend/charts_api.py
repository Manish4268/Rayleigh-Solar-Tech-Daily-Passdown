"""
Charts API Module
Handles all chart-related endpoints
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for data_processor import
import sys
sys.path.insert(0, os.path.dirname(__file__))

try:
    from data_processor import extract_chart_data, extract_device_yield_data, extract_iv_repeatability_data
    DATA_PROCESSOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Data processor not available: {e}")
    DATA_PROCESSOR_AVAILABLE = False

class ChartsAPI:
    """Charts API class handling all chart-related endpoints"""
    
    def __init__(self):
        self.available_parameters = [
            "PCE", "FF", "Max Power", "HI", 
            "I_sc", "V_oc", "R_series", "R_shunt"
        ]
    
    def get_parameters(self):
        """Get list of available parameters"""
        try:
            return jsonify({
                "success": True,
                "parameters": self.available_parameters
            }), 200
        except Exception as e:
            logging.error(f"Error getting parameters: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_chart_data(self, parameter):
        """Get chart data for a specific parameter"""
        try:
            if not DATA_PROCESSOR_AVAILABLE:
                return jsonify({
                    "success": False,
                    "error": "Data processor not available"
                }), 500
            
            if parameter not in self.available_parameters:
                return jsonify({
                    "success": False,
                    "error": f"Invalid parameter: {parameter}"
                }), 400
            
            # Extract data for ALL parameters, then filter for the requested one
            all_chart_data = extract_chart_data()
            
            # Get data for the specific parameter
            parameter_data = all_chart_data.get(parameter, [])
            
            return jsonify({
                "success": True,
                "parameter": parameter,
                "data": parameter_data
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting chart data for {parameter}: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_device_yield(self):
        """Get device yield data with quantiles"""
        try:
            if not DATA_PROCESSOR_AVAILABLE:
                return jsonify({
                    "success": False,
                    "error": "Data processor not available"
                }), 500
            
            # Extract device yield data
            device_yield_data = extract_device_yield_data()
            
            return jsonify({
                "success": True,
                "data": device_yield_data
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting device yield data: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def get_iv_repeatability(self):
        """Get IV repeatability data"""
        try:
            if not DATA_PROCESSOR_AVAILABLE:
                return jsonify({
                    "success": False,
                    "error": "Data processor not available"
                }), 500
            
            # Extract IV repeatability data
            iv_data = extract_iv_repeatability_data()
            
            return jsonify({
                "success": True,
                "data": iv_data
            }), 200
            
        except Exception as e:
            logging.error(f"Error getting IV repeatability data: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    # Aliases for backward compatibility with app.py
    def get_device_yield_data(self):
        """Alias for get_device_yield"""
        return self.get_device_yield()
    
    def get_iv_repeatability_data(self):
        """Alias for get_iv_repeatability"""
        return self.get_iv_repeatability()

# Lazy singleton instance - will be created on first access
_charts_api_instance = None

def get_charts_api():
    """Get or create the singleton charts API instance"""
    global _charts_api_instance
    if _charts_api_instance is None:
        _charts_api_instance = ChartsAPI()
    return _charts_api_instance

# For backward compatibility
class ChartsAPIProxy:
    """Proxy class that delegates to the lazy-loaded singleton"""
    def __getattr__(self, name):
        return getattr(get_charts_api(), name)

charts_api = ChartsAPIProxy()
