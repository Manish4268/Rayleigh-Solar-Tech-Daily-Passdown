import React, { useState, useEffect } from 'react';
import { ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { chartAPI } from '../lib/api';
import BoxPlot from './BoxPlot';

const ParameterChart = () => {
  const [selectedParameter, setSelectedParameter] = useState('PCE');
  const [chartData, setChartData] = useState([]);
  const [parameters, setParameters] = useState([]);
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

  // Load available parameters on component mount
  useEffect(() => {
    const loadParameters = async () => {
      try {
        const response = await chartAPI.getParameters();
        if (response.success) {
          setParameters(response.parameters);
        }
      } catch (error) {
        console.error('Error loading parameters:', error);
        setError('Failed to load parameters');
      }
    };
    loadParameters();
  }, []);

  // Load chart data when parameter changes
  useEffect(() => {
    const loadChartData = async () => {
      if (!selectedParameter) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const response = await chartAPI.getData(selectedParameter);
        if (response.success) {
          // Data is already in the correct format for box plots
          setChartData(response.data);
        } else {
          setError(response.error || 'Failed to load chart data');
        }
      } catch (error) {
        console.error('Error loading chart data:', error);
        setError('Failed to load chart data');
        // Fallback to mock data to keep UI working
        setChartData([
          { 
            batch: 'B58', 
            min: 0, q1: 0, median: 0, mean: 0, q3: 0, max: 0, 
            std: 0, count: 0 
          },
          { 
            batch: 'B59', 
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
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Solar Cell Parameters</CardTitle>
        
        {/* Parameter Selection Buttons with Horizontal Scroll */}
        <div className="w-full overflow-x-auto scrollbar-thin scrollbar-track-gray-800 scrollbar-thumb-gray-600 hover:scrollbar-thumb-gray-500">
          <div className="flex space-x-2 min-w-max pb-2">
            {parameters.map((param) => (
              <Button
                key={param}
                onClick={() => setSelectedParameter(param)}
                variant={selectedParameter === param ? 'default' : 'outline'}
                size="sm"
                className={`whitespace-nowrap transition-all duration-200 ${
                  selectedParameter === param 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600 shadow-md' 
                    : 'bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white hover:border-gray-500'
                }`}
              >
                {parameterInfo[param]?.label || param}
              </Button>
            ))}
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
          <div className="relative w-full h-48">
            <BoxPlot 
              data={chartData}
              width={400}
              height={180}
              color={currentParam.color}
              unit={currentParam.unit}
            />
          </div>
        )}
        
        {/* Parameter Info */}
        <div className="mt-4 text-sm text-gray-500 text-center">
          Box plot showing distribution: min, Q1, median, mean, Q3, max with standard deviation
        </div>
      </CardContent>
    </Card>
  );
};

export default ParameterChart;