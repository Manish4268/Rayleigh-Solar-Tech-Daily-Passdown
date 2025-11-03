import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { chartAPI } from '../lib/api';

const IVRepeatabilityChart = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedParameters, setSelectedParameters] = useState(['PCE']); // Default to show PCE only

  // Color mapping for parameters (matching ParameterChart colors)
  const parameterColors = {
    'PCE': '#3b82f6',        // Blue
    'FF': '#10b981',         // Green  
    'Max Power': '#f59e0b',  // Orange
    'HI': '#ef4444',         // Red
    'I_sc': '#8b5cf6',       // Purple
    'V_oc': '#06b6d4',       // Cyan
    'R_series': '#f97316',   // Orange (darker)
    'R_shunt': '#84cc16'     // Lime
  };

  // Parameter info with units (matching ParameterChart)
  const parameterInfo = {
    'PCE': { label: 'PCE', unit: '%' },
    'FF': { label: 'FF', unit: '%' },
    'Max Power': { label: 'Max Power', unit: 'mW/cm²' },
    'HI': { label: 'HI', unit: '%' },
    'I_sc': { label: 'I_sc', unit: 'mA/cm²' },
    'V_oc': { label: 'V_oc', unit: 'V' },
    'R_series': { label: 'R_series', unit: 'Ω·cm²' },
    'R_shunt': { label: 'R_shunt', unit: 'Ω·cm²' }
  };

  useEffect(() => {
    const loadIVRepeatabilityData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await chartAPI.getIVRepeatability();
        if (response.success) {
          setData(response.data);
        } else {
          setError('Failed to load IV repeatability data');
        }
      } catch (err) {
        console.error('Error loading IV repeatability data:', err);
        setError('Failed to load IV repeatability data');
      } finally {
        setLoading(false);
      }
    };

    loadIVRepeatabilityData();
  }, []);

  const toggleParameter = (param) => {
    setSelectedParameters(prev => {
      if (prev.includes(param)) {
        // Remove parameter (but keep at least one selected)
        return prev.length > 1 ? prev.filter(p => p !== param) : prev;
      } else {
        // Add parameter (limit to 6 parameters for better visibility)
        return prev.length < 6 ? [...prev, param] : prev;
      }
    });
  };

  const selectAllParameters = () => {
    if (data && data.parameters) {
      // Select first 6 parameters to avoid overcrowding
      setSelectedParameters(data.parameters.slice(0, 6));
    }
  };

  const clearAllParameters = () => {
    setSelectedParameters(['PCE']); // Keep at least PCE selected
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-xl font-semibold text-balance">IV Repeatability Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <div className="text-gray-500">Loading IV repeatability data...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data || !data.repeatability_data || data.repeatability_data.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-xl font-semibold text-balance">IV Repeatability Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-80">
            <div className="text-red-500">{error || 'No IV repeatability data available'}</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-lg">
          <p className="text-white font-semibold">{`Date: ${label}`}</p>
          {payload.filter(entry => selectedParameters.includes(entry.dataKey.replace('_avg', ''))).map((entry, index) => {
            const paramName = entry.dataKey.replace('_avg', '');
            const info = parameterInfo[paramName] || {};
            
            return (
              <div key={index} className="text-sm mt-1">
                <div style={{ color: entry.color }}>
                  {info.label || paramName}: {entry.value?.toFixed(3)}{info.unit}
                </div>
              </div>
            );
          })}
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-balance">IV Repeatability Analysis</CardTitle>
        <div className="text-sm text-gray-500 mb-4">
          Daily averages for all parameters over the last {data?.repeatability_data?.length || 0} days (select up to 6 parameters)
        </div>
        
        {/* Parameter Selection Controls */}
        <div className="space-y-3">
          {/* Control Buttons */}
          <div className="flex space-x-2">
            <Button
              onClick={selectAllParameters}
              variant="outline"
              size="sm"
              className="text-xs"
            >
              Select First 6
            </Button>
            <Button
              onClick={clearAllParameters}
              variant="outline"
              size="sm"
              className="text-xs"
            >
              Clear All
            </Button>
            <span className="text-xs text-gray-500 self-center ml-2">
              Selected: {selectedParameters.length}/6 parameter{selectedParameters.length !== 1 ? 's' : ''}
            </span>
          </div>
          
          {/* Parameter Selection Buttons */}
          <div className="w-full overflow-x-auto scrollbar-thin scrollbar-track-gray-800 scrollbar-thumb-gray-600 hover:scrollbar-thumb-gray-500">
            <div className="flex space-x-2 min-w-max pb-2">
              {data && data.parameters && data.parameters.map((param) => (
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
                  disabled={!selectedParameters.includes(param) && selectedParameters.length >= 6}
                >
                  {parameterInfo[param]?.label || param}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart
            data={data.repeatability_data}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis 
              dataKey="date_short" 
              stroke="#94a3b8" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              stroke="#94a3b8" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false}
              domain={['dataMin - 0.5', 'dataMax + 0.5']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="line"
            />
            
            {/* Render average lines for selected IV parameters only */}
            {selectedParameters.map(param => {
              const dataKey = `${param}_avg`;
              const paramInfo = parameterInfo[param] || {};
              const displayName = `${paramInfo.label} Average`;
              
              return (
                <Line
                  key={dataKey}
                  type="monotone"
                  dataKey={dataKey}
                  stroke={parameterColors[param]}
                  strokeWidth={3}
                  dot={{ 
                    fill: parameterColors[param], 
                    strokeWidth: 2, 
                    r: 5 
                  }}
                  activeDot={{ 
                    r: 7, 
                    fill: parameterColors[param], 
                    stroke: '#ffffff', 
                    strokeWidth: 2 
                  }}
                  name={displayName}
                  connectNulls={false}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
        
        <div className="mt-4 text-xs text-gray-500 text-center">
          Daily averages show parameter trends over the most recent {data?.repeatability_data?.length || 0} days | 
          Selected: {selectedParameters.join(', ')} | All parameters available for comprehensive analysis
        </div>
      </CardContent>
    </Card>
  );
};

export default IVRepeatabilityChart;