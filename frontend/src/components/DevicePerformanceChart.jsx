import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Button } from './ui/button';

const DevicePerformanceChart = ({ deviceId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedParameters, setSelectedParameters] = useState(['PCE']); // Default to PCE

  // Color mapping for parameters
  const parameterColors = {
    'PCE': '#3b82f6',        // Blue
    'FF': '#10b981',         // Green  
    'Max_Power': '#f59e0b',  // Orange
    'HI': '#ef4444',         // Red
    'J_sc': '#8b5cf6',       // Purple
    'V_oc': '#06b6d4',       // Cyan
    'R_series': '#f97316',   // Orange (darker)
    'R_shunt': '#84cc16'     // Lime
  };

  // Parameter info with units
  const parameterInfo = {
    'PCE': { label: 'PCE', unit: '%' },
    'FF': { label: 'FF', unit: '%' },
    'Max_Power': { label: 'Max Power', unit: 'mW' },
    'HI': { label: 'HI', unit: '%' },
    'J_sc': { label: 'J_sc', unit: 'mA/cm²' },
    'V_oc': { label: 'V_oc', unit: 'V' },
    'R_series': { label: 'R_series', unit: 'Ω·cm²' },
    'R_shunt': { label: 'R_shunt', unit: 'Ω·cm²' }
  };

  // Load device performance data
  useEffect(() => {
    const loadDeviceData = async () => {
      if (!deviceId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Import stabilityAPI dynamically to avoid circular dependencies
        const { stabilityAPI } = await import('../lib/api');
        const result = await stabilityAPI.getDevicePerformanceData(deviceId);

        setData(result);
        console.log('✅ Device performance data loaded:', result);
      } catch (err) {
        console.error('❌ Error loading device performance data:', err);
        setError(err.message || 'Failed to load device performance data');
      } finally {
        setLoading(false);
      }
    };

    loadDeviceData();
  }, [deviceId]);

  const toggleParameter = (param) => {
    setSelectedParameters(prev => {
      if (prev.includes(param)) {
        // Don't allow deselecting if it's the last one
        if (prev.length === 1) return prev;
        return prev.filter(p => p !== param);
      } else {
        // Limit to 6 parameters to avoid overcrowding
        return prev.length < 6 ? [...prev, param] : prev;
      }
    });
  };

  const selectAllParameters = () => {
    if (data && data.available_parameters) {
      // Select first 6 parameters
      setSelectedParameters(data.available_parameters.slice(0, 6));
    }
  };

  const clearAllParameters = () => {
    setSelectedParameters(['PCE']); // Keep at least PCE
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-lg text-white">
          <p className="font-semibold">{`Time: ${label} hrs`}</p>
          {payload.filter(entry => selectedParameters.includes(entry.dataKey)).map((entry, index) => {
            const param = entry.dataKey;
            const info = parameterInfo[param] || {};
            
            return (
              <div key={index} className="text-sm mt-1" style={{ color: entry.color }}>
                {info.label || param}: {entry.value?.toFixed(3)}{info.unit}
              </div>
            );
          })}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading device performance data...</div>
      </div>
    );
  }

  if (error || !data || !data.time_series || data.time_series.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">{error || 'No performance data available for this device'}</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* T80 Info Banner */}
      {data.t80_info && data.t80_info.reached_t80 && (
        <div className="bg-green-900/20 border border-green-600 rounded px-3 py-2 text-sm">
          <span className="text-green-400 font-semibold">✅ T80 Reached</span>
          <span className="text-gray-300 ml-2">
            at {data.t80_info.t80_hours} hours | 
            Baseline PCE: {data.t80_info.baseline_pce?.toFixed(2)}% | 
            Threshold: {data.t80_info.threshold_pce?.toFixed(2)}%
          </span>
        </div>
      )}

      {/* Parameter Selection Controls */}
      <div className="space-y-2">
        <div className="flex space-x-2">
          <Button
            onClick={selectAllParameters}
            variant="outline"
            size="sm"
            className="text-xs bg-gray-800 text-white border-gray-600"
          >
            Select All
          </Button>
          <Button
            onClick={clearAllParameters}
            variant="outline"
            size="sm"
            className="text-xs bg-gray-800 text-white border-gray-600"
          >
            Clear All
          </Button>
          <span className="text-xs text-gray-400 self-center ml-2">
            Selected: {selectedParameters.length} parameter{selectedParameters.length !== 1 ? 's' : ''}
          </span>
        </div>
        
        {/* Parameter Selection Buttons */}
        <div className="w-full overflow-x-auto">
          <div className="flex space-x-2 min-w-max pb-2">
            {data.available_parameters && data.available_parameters.map((param) => (
              <Button
                key={param}
                onClick={() => toggleParameter(param)}
                variant={selectedParameters.includes(param) ? 'default' : 'outline'}
                size="sm"
                className={`whitespace-nowrap transition-all duration-200 ${
                  selectedParameters.includes(param)
                    ? 'shadow-lg transform scale-105'
                    : 'hover:scale-105'
                }`}
                style={{
                  backgroundColor: selectedParameters.includes(param) ? parameterColors[param] : 'transparent',
                  borderColor: parameterColors[param],
                  color: selectedParameters.includes(param) ? 'white' : parameterColors[param]
                }}
              >
                {parameterInfo[param]?.label || param}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data.time_series}
          margin={{ top: 10, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis 
            dataKey="time_hrs" 
            stroke="#94a3b8" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            label={{ value: 'Time (hours)', position: 'insideBottom', offset: -5, style: { fill: '#94a3b8', fontSize: 12 } }}
          />
          <YAxis 
            stroke="#94a3b8" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Render lines for selected parameters */}
          {selectedParameters.map(param => (
            <Line
              key={param}
              type="monotone"
              dataKey={param}
              stroke={parameterColors[param]}
              strokeWidth={2}
              dot={{ 
                fill: parameterColors[param], 
                strokeWidth: 2, 
                r: 3 
              }}
              activeDot={{ 
                r: 5, 
                fill: parameterColors[param], 
                stroke: '#ffffff', 
                strokeWidth: 2 
              }}
              connectNulls={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
        {selectedParameters.map(param => (
          <div key={param} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded"
              style={{ backgroundColor: parameterColors[param] }}
            />
            <span className="text-gray-300">
              {parameterInfo[param]?.label || param}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DevicePerformanceChart;
