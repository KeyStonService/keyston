import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'strict', // Security: Changed from 'loose' to 'strict' to prevent XSS
  themeVariables: {
    primaryColor: '#3b82f6',
    primaryTextColor: '#fff',
    primaryBorderColor: '#1e40af',
    lineColor: '#64748b',
    secondaryColor: '#1e293b',
    tertiaryColor: '#0f172a',
  },
});

interface MermaidProps {
  chart: string;
}

export default function Mermaid({ chart }: MermaidProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      // Security: Use mermaid.render with strict security level for safe rendering
      // The strict security level handles sanitization internally
      // Use crypto.randomUUID() if available, fallback to timestamp-based ID
      const uniqueId = typeof crypto !== 'undefined' && crypto.randomUUID 
        ? crypto.randomUUID() 
        : `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
      const id = `mermaid-${uniqueId}`;
      
      mermaid.render(id, chart).then(({ svg }) => {
        if (ref.current) {
          ref.current.innerHTML = svg;
        }
      }).catch(err => {
        console.error('Mermaid rendering error:', err);
        if (ref.current) {
          ref.current.textContent = 'Error rendering diagram';
        }
      });
    }
  }, [chart]);

  return <div ref={ref} className="mermaid" />;
}
