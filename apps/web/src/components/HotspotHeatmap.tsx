import { useEffect, useRef } from 'react';

interface HotspotData {
  file: string;
  layer: string;
  language: string;
  violations: string[];
  security_issues: number;
  repeated_count: number;
  score: number;
}

interface HotspotHeatmapProps {
  hotspots: HotspotData[];
}

export default function HotspotHeatmap({ hotspots }: HotspotHeatmapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || hotspots.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const width = canvas.clientWidth;
    const height = 400;
    canvas.width = width;
    canvas.height = height;

    // Calculate treemap layout
    const layout = calculateTreemap(hotspots, width, height);

    // Draw heatmap
    layout.forEach((rect, index) => {
      const hotspot = hotspots[index];
      const color = getHeatColor(hotspot.score);

      // Draw rectangle
      ctx.fillStyle = color;
      ctx.fillRect(rect.x, rect.y, rect.width, rect.height);

      // Draw border
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 2;
      ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);

      // Draw text if rectangle is large enough
      if (rect.width > 80 && rect.height > 40) {
        ctx.fillStyle = '#ffffff';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        const fileName = hotspot.file.split('/').pop() || hotspot.file;
        const text = `${fileName.substring(0, 15)}${fileName.length > 15 ? '...' : ''}`;
        ctx.fillText(text, rect.x + rect.width / 2, rect.y + rect.height / 2 - 10);

        ctx.font = 'bold 16px sans-serif';
        ctx.fillText(`${hotspot.score}`, rect.x + rect.width / 2, rect.y + rect.height / 2 + 10);
      }
    });
  }, [hotspots]);

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        className="w-full rounded-lg"
        style={{ height: '400px' }}
      />
      <div className="mt-4 flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#dc2626' }} />
            <span className="text-slate-400">Critical (70-100)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#f59e0b' }} />
            <span className="text-slate-400">High (40-69)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#fbbf24' }} />
            <span className="text-slate-400">Moderate (1-39)</span>
          </div>
        </div>
        <div className="text-slate-500">
          Hover over blocks for details
        </div>
      </div>
    </div>
  );
}

function getHeatColor(score: number): string {
  if (score >= 70) return '#dc2626'; // red-600
  if (score >= 40) return '#f59e0b'; // amber-500
  if (score >= 20) return '#fbbf24'; // amber-400
  return '#fcd34d'; // amber-300
}

function calculateTreemap(
  hotspots: HotspotData[],
  width: number,
  height: number
): Array<{ x: number; y: number; width: number; height: number }> {
  // Simple squarified treemap algorithm
  const totalScore = hotspots.reduce((sum, h) => sum + h.score, 0);
  const rects: Array<{ x: number; y: number; width: number; height: number }> = [];

  let x = 0;
  let y = 0;
  let remainingWidth = width;
  let remainingHeight = height;

  hotspots.forEach((hotspot, index) => {
    const ratio = hotspot.score / totalScore;
    const area = width * height * ratio;

    let rectWidth: number;
    let rectHeight: number;

    // Alternate between horizontal and vertical splits
    if (index % 2 === 0) {
      rectWidth = Math.min(remainingWidth, Math.sqrt(area * (remainingWidth / remainingHeight)));
      rectHeight = area / rectWidth;
    } else {
      rectHeight = Math.min(remainingHeight, Math.sqrt(area * (remainingHeight / remainingWidth)));
      rectWidth = area / rectHeight;
    }

    rects.push({
      x: x,
      y: y,
      width: Math.max(40, rectWidth), // Minimum width
      height: Math.max(40, rectHeight), // Minimum height
    });

    // Update position for next rectangle
    if (index % 2 === 0) {
      x += rectWidth;
      remainingWidth -= rectWidth;
    } else {
      y += rectHeight;
      remainingHeight -= rectHeight;
    }
  });

  return rects;
}
