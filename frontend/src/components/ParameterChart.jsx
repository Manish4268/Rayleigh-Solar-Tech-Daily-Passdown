import React, { useState, useEffect } from 'react';
import { ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { chartAPI } from '../lib/api';
import BoxPlot from './BoxPlot';

const ParameterChart = () => {
  const [selectedParameter, setSelectedParameter] = useState('PCE'); // Back to single parameter selection
  const [chartData, setChartData] = useState([]);
  const [parameters, setParameters] = useState([
    "PCE", "FF", "Max Power", "HI", "I_sc", "V_oc", "R_series", "R_shunt"
  ]); // Initialize with all 8 parameters
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Available parameters with their display names and units
  const parameterInfo = {
    'PCE': { label: 'PCE', unit: '%', color: '#3b82f6' },
    'FF': { label: 'FF', unit: '%', color: '#10b981' },
    'Max Power': { label: 'Max Power', unit: 'mW/cm²', color: '#f59e0b' },
    'HI': { label: 'HI', unit: '%', color: '#ef4444' },
    'I_sc': { label: 'I_sc', unit: 'mA/cm²', color: '#8b5cf6' },
    'V_oc': { label: 'V_oc', unit: 'V', color: '#06b6d4' },
    'R_series': { label: 'R_series', unit: 'Ω·cm²', color: '#f97316' },
    'R_shunt': { label: 'R_shunt', unit: 'Ω·cm²', color: '#84cc16' }
  };

  // Load available parameters on component mount (and also load from API)
  useEffect(() => {
    const loadParameters = async () => {
      try {
        const response = await chartAPI.getParameters();
        if (response.success && response.parameters) {
          setParameters(response.parameters);
          console.log('✅ Loaded parameters from API:', response.parameters);
        } else {
          console.log('⚠️ Using fallback parameters');
          // Keep the hardcoded fallback parameters
        }
      } catch (error) {
        console.error('Error loading parameters:', error);
        console.log('⚠️ Using fallback parameters due to error');
        // Keep the hardcoded fallback parameters
      }
    };
    loadParameters();
  }, []);

  // Load chart data when parameter changes
  useEffect(() => {
    const loadChartData = async () => {
      if (!selectedParameter) return;
      
      console.log('📊 Loading chart data for parameter:', selectedParameter);
      setLoading(true);
      setError(null);
      
      try {
        const response = await chartAPI.getData(selectedParameter);
        console.log('📊 Chart data response:', response);
        
        if (response.success) {
          // Data is already in the correct format for box plots
          setChartData(response.data);
          console.log('✅ Chart data loaded successfully:', response.data);
        } else {
          setError(response.error || 'Failed to load chart data');
          console.log('❌ Chart data failed:', response.error);
        }
      } catch (error) {
        console.error('Error loading chart data:', error);
        setError('Failed to load chart data');
        // Fallback to mock data to keep UI working
        setChartData([
          { 
            batch: 'No Data', 
            min: 0, q1: 0, median: 0, mean: 0, q3: 0, max: 0, 
            std: 0, count: 0 
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadChartData();
  }, [selectedParameter]);

  const currentParam = parameterInfo[selectedParameter] || parameterInfo['PCE'];

  // Custom tooltip to show box plot statistics
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-gray-800 border border-blue-500 rounded-lg p-3 text-white shadow-lg">
          <p className="font-semibold">{`Batch: ${data.batch}`}</p>
          <div className="space-y-1 text-sm">
            <p className="text-blue-300">{`Max: ${data.max} ${currentParam.unit}`}</p>
            <p className="text-green-300">{`Q3: ${data.q3} ${currentParam.unit}`}</p>
            <p className="text-yellow-300">{`Median: ${data.median} ${currentParam.unit}`}</p>
            <p className="text-white">{`Mean: ${data.mean} ${currentParam.unit}`}</p>
            <p className="text-green-300">{`Q1: ${data.q1} ${currentParam.unit}`}</p>
            <p className="text-blue-300">{`Min: ${data.min} ${currentParam.unit}`}</p>
            <p className="text-gray-300">{`Std Dev: ±${data.std} ${currentParam.unit}`}</p>
            <p className="text-gray-400">{`Sample Count: ${data.count}`}</p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-balance">
          {selectedParameter ? `${parameterInfo[selectedParameter]?.label || selectedParameter} Analysis` : 'Parameter Analysis'}
        </CardTitle>
        <div className="text-sm text-gray-500 mb-4">
          Box plot distribution analysis for selected parameter
        </div>
        
        {/* Parameter Selection Buttons with Horizontal Scroll - matching DeviceYieldChart style */}
        <div className="w-full overflow-x-auto scrollbar-thin scrollbar-track-gray-800 scrollbar-thumb-gray-600 hover:scrollbar-thumb-gray-500">
          <div className="flex space-x-2 min-w-max pb-2">
            {parameters.length > 0 ? parameters.map((param) => (
              <Button
                key={param}
                onClick={() => {
                  console.log('🔄 Switching to parameter:', param);
                  setSelectedParameter(param);
                }}
                variant={selectedParameter === param ? 'default' : 'outline'}
                size="sm"
                className={`whitespace-nowrap transition-all duration-200 ${
                  selectedParameter === param
                    ? 'shadow-lg transform scale-105'
                    : 'hover:scale-105'
                }`}
                style={{
                  backgroundColor: selectedParameter === param ? parameterInfo[param]?.color : 'transparent',
                  borderColor: parameterInfo[param]?.color,
                  color: selectedParameter === param ? 'white' : parameterInfo[param]?.color
                }}
              >
                {parameterInfo[param]?.label || param}
              </Button>
            )) : (
              <div className="text-gray-500 text-sm">Loading parameters...</div>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {error && (
          <div className="text-red-500 text-sm mb-4 p-2 bg-red-100 dark:bg-red-900/20 rounded">
            {error}
          </div>
        )}
        
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="text-gray-500">Loading chart data...</div>
          </div>
        ) : (
          <div className="relative w-full h-80">
            <BoxPlot 
              data={chartData}
              width="100%"
              height={320}
              color={currentParam.color}
              unit={currentParam.unit}
            />
          </div>
        )}
        
        {/* Parameter Info */}
        <div className="mt-4 text-sm text-gray-500 text-center">
          Box plot showing distribution: min, Q1, median, mean, Q3, max with standard deviation | 
          Selected: {selectedParameter} | Hover over each box for detailed statistics
        </div>
      </CardContent>
    </Card>
  );
};

export default ParameterChart;