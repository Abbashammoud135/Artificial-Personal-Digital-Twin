import { useState } from 'react';

export default function TrendChart({ testName, units, points = [], trend }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!points || points.length === 0) {
    return (
      <div style={{ height: '240px', display: 'flex', alignItems: 'center', justify: 'center', color: 'var(--text-muted)' }}>
        No trend data available for {testName}
      </div>
    );
  }

  // Dimension settings
  const width = 500;
  const height = 200;
  const paddingLeft = 45;
  const paddingRight = 15;
  const paddingTop = 20;
  const paddingBottom = 30;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  // Find min/max values to scale Y axis
  const values = points.map(p => p.value);
  let maxVal = Math.max(...values);
  let minVal = Math.min(...values);

  // Buffer so chart line doesn't hug top/bottom limits
  const range = maxVal - minVal;
  if (range === 0) {
    maxVal = maxVal + 1;
    minVal = minVal - 1;
  } else {
    maxVal = maxVal + range * 0.15;
    minVal = minVal - range * 0.15;
  }

  // Map data to SVG coordinate space
  const getCoordinates = () => {
    return points.map((p, index) => {
      const x = paddingLeft + (index / (points.length - 1 || 1)) * chartWidth;
      const y = height - paddingBottom - ((p.value - minVal) / (maxVal - minVal)) * chartHeight;
      return { x, y, ...p };
    });
  };

  const coords = getCoordinates();

  // Create path strings
  let linePath = '';
  let areaPath = '';

  if (coords.length > 0) {
    linePath = `M ${coords[0].x} ${coords[0].y} ` + coords.slice(1).map(c => `L ${c.x} ${c.y}`).join(' ');
    areaPath = linePath + ` L ${coords[coords.length - 1].x} ${height - paddingBottom} L ${coords[0].x} ${height - paddingBottom} Z`;
  }

  // Setup color based on trend state
  let trendColor = 'var(--primary)'; // blue/cyan
  if (trend === 'INCREASING') trendColor = 'var(--danger)'; // red
  if (trend === 'DECREASING') trendColor = 'var(--success)'; // green

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <svg viewBox={`0 0 ${width} ${height}`} className="trend-chart-svg">
        <defs>
          <linearGradient id={`areaGlow-${testName}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={trendColor} stopOpacity="0.25" />
            <stop offset="100%" stopColor={trendColor} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Grid lines (horizontal) */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, index) => {
          const y = paddingTop + ratio * chartHeight;
          const val = maxVal - ratio * (maxVal - minVal);
          return (
            <g key={index}>
              <line
                x1={paddingLeft}
                y1={y}
                x2={width - paddingRight}
                y2={y}
                stroke="rgba(255,255,255,0.04)"
                strokeDasharray="4 4"
              />
              <text
                x={paddingLeft - 8}
                y={y + 4}
                fill="var(--text-muted)"
                fontSize="10"
                textAnchor="end"
              >
                {val.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* Date labels along X axis */}
        {coords.map((c, idx) => {
          // Only render labels for first, middle, last to prevent overlap
          const shouldShowLabel = idx === 0 || idx === coords.length - 1 || (coords.length > 2 && idx === Math.floor(coords.length / 2));
          if (!shouldShowLabel) return null;

          const dateStr = new Date(c.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

          return (
            <text
              key={idx}
              x={c.x}
              y={height - 8}
              fill="var(--text-muted)"
              fontSize="9"
              textAnchor="middle"
            >
              {dateStr}
            </text>
          );
        })}

        {/* Gradient fill area */}
        {areaPath && (
          <path d={areaPath} fill={`url(#areaGlow-${testName})`} />
        )}

        {/* Plot line */}
        {linePath && (
          <path
            d={linePath}
            fill="none"
            stroke={trendColor}
            strokeWidth="2.5"
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0px 2px 6px ${trendColor}44)` }}
          />
        )}

        {/* Interactive hover points */}
        {coords.map((c, idx) => (
          <g key={idx}>
            <circle
              cx={c.x}
              cy={c.y}
              r={hoveredPoint?.x === c.x && hoveredPoint?.y === c.y ? 6 : 4}
              fill="#050D1A"
              stroke={c.status === 'HIGH' || c.status === 'LOW' ? 'var(--warning)' : trendColor}
              strokeWidth="2"
              onMouseEnter={() => setHoveredPoint(c)}
              onMouseLeave={() => setHoveredPoint(null)}
              style={{ cursor: 'pointer', transition: 'r 0.15s ease' }}
            />
          </g>
        ))}
      </svg>

      {/* Floating Interactive Tooltip */}
      {hoveredPoint && (
        <div
          className="chart-tooltip"
          style={{
            display: 'block',
            left: `${(hoveredPoint.x / width) * 100}%`,
            top: `${(hoveredPoint.y / height) * 100 - 45}%`,
            transform: 'translateX(-50%)',
          }}
        >
          <div style={{ fontWeight: 'bold' }}>{hoveredPoint.value} {units}</div>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
            {new Date(hoveredPoint.date).toLocaleDateString()}
          </div>
          {hoveredPoint.status && hoveredPoint.status !== 'NORMAL' && (
            <div style={{ fontSize: '10px', color: 'var(--warning)', marginTop: '2px' }}>
              ⚠️ {hoveredPoint.status}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
