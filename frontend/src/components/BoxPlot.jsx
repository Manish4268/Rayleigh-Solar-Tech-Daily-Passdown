import React, { useState, useRef, useEffect } from 'react';

const BoxPlot = ({ data, width = 100, height = 200, color = '#3b82f6', unit = '' }) => {
  const [hoveredData, setHoveredData] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [actualWidth, setActualWidth] = useState(400);
  const containerRef = useRef(null);

  // Handle responsive width
  useEffect(() => {
    if (width === "100%" && containerRef.current) {
      const updateWidth = () => {
        setActualWidth(containerRef.current.offsetWidth);
      };
      
      updateWidth();
      window.addEventListener('resize', updateWidth);
      return () => window.removeEventListener('resize', updateWidth);
    } else if (typeof width === 'number') {
      setActualWidth(width);
    }
  }, [width]);

  if (!data || data.length === 0) return null;

  // Use actualWidth for calculations
  const svgWidth = actualWidth;

  // Calculate scale based on data range
  const allValues = data.flatMap(d => [d.min, d.max]);
  const dataMin = Math.min(...allValues);
  const dataMax = Math.max(...allValues);
  const dataRange = dataMax - dataMin;
  const padding = dataRange * 0.1; // 10% padding
  const scaleMin = dataMin - padding;
  const scaleMax = dataMax + padding;
  const scaleRange = scaleMax - scaleMin;

  // Scale function
  const scale = (value) => {
    return height - ((value - scaleMin) / scaleRange) * height;
  };

  const boxWidth = Math.min(60, svgWidth / data.length * 0.6);
  const spacing = svgWidth / data.length;

  return (
    <div ref={containerRef} className="relative w-full h-full">
      <svg width={svgWidth} height={height} className="overflow-visible">
        {/* Background grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
          const y = height * ratio;
          const value = scaleMax - (scaleRange * ratio);
          return (
            <g key={i}>
              <line
                x1={0}
                y1={y}
                x2={svgWidth}
                y2={y}
                stroke="#374151"
                strokeWidth={0.5}
                strokeDasharray="2,2"
                opacity={0.3}
              />
              <text
                x={-5}
                y={y + 3}
                fontSize="10"
                fill="#9CA3AF"
                textAnchor="end"
              >
                {value.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* Box plots */}
        {data.map((d, i) => {
          const x = spacing * i + spacing / 2;
          
          // Calculate positions
          const minY = scale(d.min);
          const q1Y = scale(d.q1);
          const medianY = scale(d.median);
          const q3Y = scale(d.q3);
          const maxY = scale(d.max);
          const meanY = scale(d.mean);

          return (
            <g key={d.batch} transform={`translate(${x}, 0)`}>
              {/* Whiskers */}
              <line
                x1={0}
                y1={minY}
                x2={0}
                y2={q1Y}
                stroke={color}
                strokeWidth={2}
              />
              <line
                x1={0}
                y1={q3Y}
                x2={0}
                y2={maxY}
                stroke={color}
                strokeWidth={2}
              />
              
              {/* Min/Max caps */}
              <line
                x1={-boxWidth/4}
                y1={minY}
                x2={boxWidth/4}
                y2={minY}
                stroke={color}
                strokeWidth={2}
              />
              <line
                x1={-boxWidth/4}
                y1={maxY}
                x2={boxWidth/4}
                y2={maxY}
                stroke={color}
                strokeWidth={2}
              />

              {/* Box (IQR) */}
              <rect
                x={-boxWidth/2}
                y={q3Y}
                width={boxWidth}
                height={q1Y - q3Y}
                fill={color}
                fillOpacity={0.3}
                stroke={color}
                strokeWidth={2}
              />

              {/* Median line */}
              <line
                x1={-boxWidth/2}
                y1={medianY}
                x2={boxWidth/2}
                y2={medianY}
                stroke="#ffffff"
                strokeWidth={3}
              />

              {/* Mean point */}
              <circle
                cx={0}
                cy={meanY}
                r={3}
                fill="#ffffff"
                stroke={color}
                strokeWidth={2}
              />

              {/* Batch label */}
              <text
                x={0}
                y={height + 15}
                fontSize="12"
                fill="#9CA3AF"
                textAnchor="middle"
              >
                {d.batch}
              </text>

              {/* Interactive area for tooltip */}
              <rect
                x={-boxWidth/2}
                y={0}
                width={boxWidth}
                height={height}
                fill="transparent"
                className="cursor-pointer"
                onMouseEnter={(e) => {
                  setHoveredData(d);
                  setMousePosition({ x: e.clientX, y: e.clientY });
                }}
                onMouseMove={(e) => {
                  setMousePosition({ x: e.clientX, y: e.clientY });
                }}
                onMouseLeave={() => {
                  setHoveredData(null);
                }}
              />
            </g>
          );
        })}
      </svg>

      {/* Custom Tooltip */}
      {hoveredData && (
        <div 
          className="fixed z-50 bg-gray-800 border border-blue-500 rounded-lg p-3 text-white shadow-lg pointer-events-none"
          style={{
            left: mousePosition.x + 10,
            top: mousePosition.y - 10,
            transform: 'translate(0, -100%)'
          }}
        >
          <p className="font-semibold">{`Batch: ${hoveredData.batch}`}</p>
          <div className="space-y-1 text-sm">
            <p className="text-blue-300">{`Max: ${hoveredData.max} ${unit}`}</p>
            <p className="text-green-300">{`Q3: ${hoveredData.q3} ${unit}`}</p>
            <p className="text-yellow-300">{`Median: ${hoveredData.median} ${unit}`}</p>
            <p className="text-white">{`Mean: ${hoveredData.mean} ${unit}`}</p>
            <p className="text-green-300">{`Q1: ${hoveredData.q1} ${unit}`}</p>
            <p className="text-blue-300">{`Min: ${hoveredData.min} ${unit}`}</p>
            <p className="text-gray-300">{`Std Dev: ±${hoveredData.std} ${unit}`}</p>
            <p className="text-gray-400">{`Sample Count: ${hoveredData.count}`}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BoxPlot;