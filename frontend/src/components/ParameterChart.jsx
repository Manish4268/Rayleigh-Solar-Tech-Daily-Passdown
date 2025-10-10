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

  // Function to generate realistic mock data based on parameter
  const getMockData = (parameter) => {
    const mockDataMap = {
      'PCE': [
        { batch: 'B58', min: 18.2, q1: 19.1, median: 19.8, mean: 19.7, q3: 20.4, max: 21.1, std: 0.8, count: 48 },
        { batch: 'B59', min: 17.9, q1: 19.3, median: 20.1, mean: 20.0, q3: 20.7, max: 21.4, std: 0.7, count: 52 },
        { batch: 'B60', min: 18.5, q1: 19.2, median: 19.9, mean: 19.8, q3: 20.5, max: 21.0, std: 0.6, count: 50 }
      ],
      'FF': [
        { batch: 'B58', min: 76.2, q1: 77.1, median: 78.8, mean: 78.7, q3: 79.4, max: 81.1, std: 1.2, count: 48 },
        { batch: 'B59', min: 75.9, q1: 77.3, median: 79.1, mean: 79.0, q3: 80.7, max: 82.4, std: 1.1, count: 52 },
        { batch: 'B60', min: 76.5, q1: 77.2, median: 78.9, mean: 78.8, q3: 80.5, max: 81.0, std: 1.0, count: 50 }
      ],
      'V_oc': [
        { batch: 'B58', min: 0.65, q1: 0.67, median: 0.68, mean: 0.68, q3: 0.69, max: 0.71, std: 0.02, count: 48 },
        { batch: 'B59', min: 0.64, q1: 0.67, median: 0.69, mean: 0.69, q3: 0.70, max: 0.72, std: 0.02, count: 52 },
        { batch: 'B60', min: 0.66, q1: 0.68, median: 0.69, mean: 0.69, q3: 0.70, max: 0.71, std: 0.01, count: 50 }
      ],
      'I_sc': [
        { batch: 'B58', min: 38.2, q1: 39.1, median: 39.8, mean: 39.7, q3: 40.4, max: 41.1, std: 0.8, count: 48 },
        { batch: 'B59', min: 37.9, q1: 39.3, median: 40.1, mean: 40.0, q3: 40.7, max: 41.4, std: 0.7, count: 52 },
        { batch: 'B60', min: 38.5, q1: 39.2, median: 39.9, mean: 39.8, q3: 40.5, max: 41.0, std: 0.6, count: 50 }
      ]
    };
    
    return mockDataMap[parameter] || [
      { batch: 'B58', min: 0, q1: 0, median: 0, mean: 0, q3: 0, max: 0, std: 0, count: 0 },
      { batch: 'B59', min: 0, q1: 0, median: 0, mean: 0, q3: 0, max: 0, std: 0, count: 0 },
      { batch: 'B60', min: 0, q1: 0, median: 0, mean: 0, q3: 0, max: 0, std: 0, count: 0 }
    ];
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
        // Use fallback parameters from parameterInfo
        setParameters(Object.keys(parameterInfo));
      }
    };
    
    // Initialize with mock data for PCE
    setChartData(getMockData('PCE'));
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
          // Use mock data as fallback
          setChartData(getMockData(selectedParameter));
        }
      } catch (error) {
        console.error('Error loading chart data:', error);
        setError('API connection failed - using demo data');
        // Fallback to mock data to keep UI working
        setChartData(getMockData(selectedParameter));
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
          <div className="text-yellow-600 text-sm mb-4 p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded">
            ⚠️ {error}
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