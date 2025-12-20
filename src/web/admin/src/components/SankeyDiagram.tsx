import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface SankeyNode {
  sourceLayer: string;
  language: string;
  violationType: string;
  fixTarget: string;
  count?: number;
}

interface SankeyDiagramProps {
  data: SankeyNode[];
}

export default function SankeyDiagram({ data }: SankeyDiagramProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && data.length > 0) {
      // Generate Sankey diagram from data
      const sankeyChart = generateSankeyChart(data);
      // Security: Use mermaid.render for safer rendering with cryptographically secure IDs
      // Use crypto.randomUUID() if available, fallback to timestamp-based ID
      const uniqueId = typeof crypto !== 'undefined' && crypto.randomUUID 
        ? crypto.randomUUID() 
        : `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
      const id = `sankey-${uniqueId}`;
      
      mermaid.render(id, sankeyChart).then(({ svg }) => {
        if (ref.current) {
          const parser = new DOMParser();
          const doc = parser.parseFromString(svg, "image/svg+xml");
          const parsererrorNs = 'http://www.mozilla.org/newlayout/xml/parsererror.xml';
          const hasParserError =
            doc.getElementsByTagName('parsererror').length > 0 ||
            doc.getElementsByTagNameNS(parsererrorNs, 'parsererror').length > 0;

          if (hasParserError) {
            console.error('Error parsing SVG for Sankey diagram:', doc.documentElement.textContent);
            ref.current.textContent = 'Error parsing diagram';
            return;
          }
          const svgElement = doc.documentElement;
          const target = ref.current;
          target.replaceChildren(target.ownerDocument.importNode(svgElement, true));
        }
      }).catch(err => {
        console.error('Sankey diagram rendering error:', err);
        if (ref.current) {
          ref.current.textContent = 'Error rendering diagram';
        }
      });
    }
  }, [data]);

  return (
    <div className="w-full overflow-x-auto">
      <div ref={ref} className="mermaid min-w-[600px]" />
    </div>
  );
}

function sanitizeString(str: string): string {
  // Security: Escape dangerous characters while preserving valid Mermaid syntax
  // Handle ampersands first to avoid double-encoding, then escape other dangerous characters
  return String(str)
    .replace(/&/g, '&amp;')  // Must be first to avoid double-encoding
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    // Remove any Mermaid-specific syntax that could break diagram structure
    .replace(/[\n\r\t]/g, ' ')  // Remove line breaks and tabs
    .replace(/[{}[\]]/g, '_');  // Remove curly braces and brackets that affect Mermaid syntax
}

function generateSankeyChart(data: SankeyNode[]): string {
  // Group by source layer, language, and fix target
  const flows = data.map(node => {
    const count = node.count || 1;
    // Security: Sanitize all user-provided strings to prevent XSS
    // Note: Mermaid with strict security level provides additional protection
    const source = sanitizeString(node.sourceLayer);
    const language = sanitizeString(node.language);
    const violation = sanitizeString(node.violationType);
    const target = sanitizeString(node.fixTarget);
    
    return `${source},${language},${count}\n${language},${violation},${count}\n${violation},${target},${count}`;
  }).join('\n');

  return `
%%{init: {'theme':'dark', 'themeVariables': { 'primaryColor': '#3b82f6', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1e40af', 'lineColor': '#64748b', 'secondaryColor': '#1e293b', 'tertiaryColor': '#0f172a'}}}%%
sankey-beta

${flows}
  `.trim();
}
