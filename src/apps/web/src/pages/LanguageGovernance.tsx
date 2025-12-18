import { useEffect, useState } from 'react';
import { Activity, AlertCircle, CheckCircle, TrendingDown, TrendingUp, GitBranch, Flame, ArrowRightLeft } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import Mermaid from '@/components/Mermaid';
import SankeyDiagram from '@/components/SankeyDiagram';
import HotspotHeatmap from '@/components/HotspotHeatmap';
import MigrationFlow from '@/components/MigrationFlow';

interface SankeyNode {
  sourceLayer: string;
  language: string;
  violationType: string;
  fixTarget: string;
  count?: number;
  file?: string;
  reason?: string;
}

interface HotspotData {
  file: string;
  layer: string;
  language: string;
  violations: string[];
  security_issues: number;
  repeated_count: number;
  score: number;
}

interface MigrationEdge {
  source: string;
  target: string;
  count: number;
  type: 'history' | 'suggested';
}

interface MigrationData {
  edges: MigrationEdge[];
  statistics: {
    totalMigrations: number;
    historicalMigrations: number;
    suggestedMigrations: number;
    mostCommonSource: string;
    mostCommonTarget: string;
  };
}

interface GovernanceReport {
  healthScore: number;
  violations: Violation[];
  semgrep: SemgrepReport;
  history: HistoryEvent[];
  sankeyData?: SankeyNode[];
  hotspotData?: HotspotData[];
  migrationData?: MigrationData;
  generatedAt: string;
  metrics: {
    totalViolations: number;
    securityFindings: number;
    architectureCompliance: number;
    fixSuccessRate: number;
  };
}

interface Violation {
  file: string;
  reason: string;
  severity: 'critical' | 'error' | 'warning';
  layer?: string;
}

interface SemgrepReport {
  errors: number;
  results: Array<{
    check_id: string;
    path: string;
    message: string;
    severity: string;
  }>;
}

interface HistoryEvent {
  timestamp: string;
  event: string;
  details: string;
  type: 'fix' | 'violation' | 'scan';
}

export default function LanguageGovernanceDashboard() {
  const [data, setData] = useState<GovernanceReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch data from API
    const fetchData = async () => {
      try {
        // Try to fetch from actual API, fallback to mock data if API not available
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/language-governance`);
        
        if (response.ok) {
          const apiData = await response.json();
          setData(apiData);
        } else {
          // Fallback to mock data
          throw new Error('API not available');
        }
      } catch (error) {
        console.warn('API not available, using mock data:', error);
        
        // Fallback mock data
        const mockData: GovernanceReport = {
          healthScore: 85,
          violations: [
            {
              file: 'apps/web/src/legacy-code.js',
              reason: 'JavaScript file in TypeScript project',
              severity: 'warning',
              layer: 'L5: Applications',
            },
            {
              file: 'core/engine/utils.py',
              reason: 'Python file needs type hints',
              severity: 'error',
              layer: 'L1: Core Engine',
            },
          ],
          semgrep: {
            errors: 1,
            results: [
              {
                check_id: 'javascript.lang.security.audit.xss',
                path: 'apps/web/src/utils/render.ts',
                message: 'Potential XSS vulnerability detected',
                severity: 'WARNING',
              },
            ],
          },
          history: [
            {
              timestamp: '2025-12-06T14:30:00Z',
              event: 'Auto-fix applied',
              details: 'Fixed 3 TypeScript violations in core module',
              type: 'fix',
            },
            {
              timestamp: '2025-12-06T12:00:00Z',
              event: 'Language scan completed',
              details: 'Scanned 1,247 files across 6 layers',
              type: 'scan',
            },
            {
              timestamp: '2025-12-05T18:45:00Z',
              event: 'New violation detected',
              details: 'Cross-layer import violation in governance module',
              type: 'violation',
            },
          ],
          sankeyData: [
            {
              sourceLayer: 'L5: Applications',
              language: 'JavaScript',
              violationType: 'Policy Violation',
              fixTarget: 'Rewrite to TypeScript',
              count: 1,
              file: 'apps/web/src/legacy-code.js',
              reason: 'JavaScript file in TypeScript project',
            },
            {
              sourceLayer: 'L1: Core Engine',
              language: 'Python',
              violationType: 'Type Safety',
              fixTarget: 'Add Type Hints',
              count: 1,
              file: 'core/engine/utils.py',
              reason: 'Python file needs type hints',
            },
            {
              sourceLayer: 'L4: Services',
              language: 'C++',
              violationType: 'Layer Violation',
              fixTarget: 'Move to L0: Hardware',
              count: 1,
            },
          ],
          hotspotData: [
            {
              file: 'apps/web/src/legacy-code.js',
              layer: 'L5: Applications',
              language: 'JavaScript',
              violations: ['policy_violation'],
              security_issues: 0,
              repeated_count: 2,
              score: 45,
            },
            {
              file: 'services/gateway/router.cpp',
              layer: 'L4: Services',
              language: 'C++',
              violations: ['forbidden_language', 'layer_violation'],
              security_issues: 1,
              repeated_count: 1,
              score: 90,
            },
            {
              file: 'core/engine/utils.py',
              layer: 'L1: Core Engine',
              language: 'Python',
              violations: ['type_safety'],
              security_issues: 0,
              repeated_count: 1,
              score: 20,
            },
            {
              file: 'automation/scripts/config.lua',
              layer: 'L3: AI/Automation',
              language: 'Lua',
              violations: ['forbidden_language'],
              security_issues: 0,
              repeated_count: 0,
              score: 55,
            },
          ],
          migrationData: {
            edges: [
              {
                source: 'services:cpp',
                target: 'automation/autonomous:cpp',
                count: 3,
                type: 'suggested' as const,
              },
              {
                source: 'apps/web:javascript',
                target: 'apps/web:typescript',
                count: 2,
                type: 'suggested' as const,
              },
              {
                source: 'core/engine:typescript',
                target: 'core/engine:typescript',
                count: 2,
                type: 'history' as const,
              },
              {
                source: 'governance:typescript',
                target: 'core:typescript',
                count: 1,
                type: 'suggested' as const,
              },
              {
                source: 'automation:lua',
                target: 'removed:removed',
                count: 1,
                type: 'suggested' as const,
              },
            ],
            statistics: {
              totalMigrations: 9,
              historicalMigrations: 2,
              suggestedMigrations: 7,
              mostCommonSource: 'services:cpp',
              mostCommonTarget: 'automation/autonomous:cpp',
            },
          },
          generatedAt: new Date().toISOString(),
          metrics: {
            totalViolations: 2,
            securityFindings: 1,
            architectureCompliance: 92,
            fixSuccessRate: 87,
          },
        };
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getHealthGrade = (score: number): string => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const getHealthColor = (score: number): string => {
    if (score >= 90) return 'text-green-500';
    if (score >= 80) return 'text-blue-500';
    if (score >= 70) return 'text-yellow-500';
    if (score >= 60) return 'text-orange-500';
    return 'text-red-500';
  };

  const getMostCommonViolationType = (sankeyData: SankeyNode[]): string => {
    const typeCounts: Record<string, number> = {};
    sankeyData.forEach(node => {
      const type = node.violationType;
      typeCounts[type] = (typeCounts[type] || 0) + (node.count || 1);
    });
    
    let maxType = 'None';
    let maxCount = 0;
    Object.entries(typeCounts).forEach(([type, count]) => {
      if (count > maxCount) {
        maxCount = count;
        maxType = type;
      }
    });
    
    return maxType;
  };

  const getTopFixTarget = (sankeyData: SankeyNode[]): string => {
    const targetCounts: Record<string, number> = {};
    sankeyData.forEach(node => {
      const target = node.fixTarget;
      targetCounts[target] = (targetCounts[target] || 0) + (node.count || 1);
    });
    
    let maxTarget = 'None';
    let maxCount = 0;
    Object.entries(targetCounts).forEach(([target, count]) => {
      if (count > maxCount) {
        maxCount = count;
        maxTarget = target;
      }
    });
    
    return maxTarget;
  };

  const getHottestLayer = (hotspotData: HotspotData[]): string => {
    const layerScores: Record<string, number> = {};
    hotspotData.forEach(hotspot => {
      const layer = hotspot.layer;
      layerScores[layer] = (layerScores[layer] || 0) + hotspot.score;
    });
    
    let maxLayer = 'None';
    let maxScore = 0;
    Object.entries(layerScores).forEach(([layer, score]) => {
      if (score > maxScore) {
        maxScore = score;
        maxLayer = layer;
      }
    });
    
    return maxLayer;
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'error':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'warning':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-12 w-12 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-lg">Loading Language Governance Dashboard...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 mx-auto mb-4 text-red-500" />
          <p className="text-lg">Failed to load dashboard data</p>
        </div>
      </div>
    );
  }

  const mermaidChart = `flowchart TD
    UI[L5: UI Layer<br/>TypeScript/React] --> Services[L4: Business Services<br/>Go/TypeScript]
    Services --> AI[L3: AI & Automation<br/>Python/TypeScript]
    AI --> Core[L1: SynergyMesh Core<br/>TypeScript/Python]
    Core --> Autonomous[L0: C++ / ROS 2 Layer]
    
    style UI fill:#3b82f6,stroke:#1e40af,color:#fff
    style Services fill:#10b981,stroke:#059669,color:#fff
    style AI fill:#f59e0b,stroke:#d97706,color:#fff
    style Core fill:#8b5cf6,stroke:#7c3aed,color:#fff
    style Autonomous fill:#ef4444,stroke:#dc2626,color:#fff`;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 font-sans selection:bg-blue-500/30">
      <Navbar />

      <div className="container mx-auto px-6 py-24">
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            🏝️ Language Governance Dashboard
          </h1>
          <p className="text-slate-400 text-lg">
            Real-time monitoring and visualization of language policy compliance
          </p>
          <p className="text-slate-500 text-sm mt-2">
            Generated at: {new Date(data.generatedAt).toLocaleString()}
          </p>
        </div>

        {/* Health Score Overview */}
        <section className="mb-12">
          <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Activity className="h-6 w-6 text-blue-500" />
              Health Score
            </h2>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="bg-slate-900/50 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">Overall Score</div>
                <div className={`text-5xl font-bold ${getHealthColor(data.healthScore)}`}>
                  {data.healthScore}
                  <span className="text-2xl">/100</span>
                </div>
                <div className="text-sm text-slate-500 mt-2">
                  Grade: {getHealthGrade(data.healthScore)}
                </div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">Total Violations</div>
                <div className="text-5xl font-bold text-orange-500">{data.metrics.totalViolations}</div>
                <div className="flex items-center gap-1 text-sm text-green-500 mt-2">
                  <TrendingDown className="h-4 w-4" />
                  12% from last week
                </div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">Security Findings</div>
                <div className="text-5xl font-bold text-yellow-500">{data.metrics.securityFindings}</div>
                <div className="flex items-center gap-1 text-sm text-slate-500 mt-2">
                  <CheckCircle className="h-4 w-4" />
                  Within threshold
                </div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">Fix Success Rate</div>
                <div className="text-5xl font-bold text-green-500">
                  {data.metrics.fixSuccessRate}
                  <span className="text-2xl">%</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-green-500 mt-2">
                  <TrendingUp className="h-4 w-4" />
                  5% improvement
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Language Layer Model */}
        <section className="mb-12">
          <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
            <h2 className="text-2xl font-bold mb-6">Language Layer Model</h2>
            <div className="bg-slate-900/50 rounded-lg p-6 overflow-x-auto">
              <Mermaid chart={mermaidChart} />
            </div>
          </div>
        </section>

        {/* Sankey Diagram - Language Violation Flow */}
        {data.sankeyData && data.sankeyData.length > 0 && (
          <section className="mb-12">
            <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <GitBranch className="h-6 w-6 text-purple-500" />
                Language Violation Flow (Sankey Diagram)
              </h2>
              <p className="text-slate-400 mb-4">
                Visualizes the flow from source layers through violation types to fix targets. 
                Each path shows where violations occur and how they should be resolved.
              </p>
              <div className="bg-slate-900/50 rounded-lg p-6 overflow-x-auto">
                <SankeyDiagram data={data.sankeyData} />
              </div>
              <div className="mt-4 grid md:grid-cols-3 gap-4">
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="text-sm text-slate-400 mb-1">Total Flow Paths</div>
                  <div className="text-2xl font-bold text-purple-500">{data.sankeyData.length}</div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="text-sm text-slate-400 mb-1">Most Common Violation</div>
                  <div className="text-lg font-semibold text-slate-200">
                    {getMostCommonViolationType(data.sankeyData)}
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="text-sm text-slate-400 mb-1">Top Fix Action</div>
                  <div className="text-lg font-semibold text-slate-200">
                    {getTopFixTarget(data.sankeyData)}
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Hotspot Heatmap */}
        {data.hotspotData && data.hotspotData.length > 0 && (
          <section className="mb-12">
            <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Flame className="h-6 w-6 text-orange-500" />
                Violation Hotspot Heatmap
              </h2>
              <p className="text-slate-400 mb-6">
                Interactive heatmap showing violation concentration across files. 
                Darker colors indicate higher violation intensity based on forbidden languages, 
                cross-layer violations, security issues, and repeated violations.
              </p>
              <div className="bg-slate-900/50 rounded-lg p-6">
                <HotspotHeatmap hotspots={data.hotspotData} />
              </div>
              <div className="mt-6 grid md:grid-cols-4 gap-4">
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="text-sm text-slate-400 mb-1">Total Hotspots</div>
                  <div className="text-2xl font-bold text-orange-500">{data.hotspotData.length}</div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="text-sm text-slate-400 mb-1">Critical Hotspots</div>
                  <div className="text-2xl font-bold text-red-500">
                    {data.hotspotData.filter(h => h.score >= 70).length}
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="text-sm text-slate-400 mb-1">Max Intensity</div>
                  <div className="text-2xl font-bold text-slate-200">
                    {Math.max(...data.hotspotData.map(h => h.score))}/100
                  </div>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="text-sm text-slate-400 mb-1">Hottest Layer</div>
                  <div className="text-lg font-semibold text-slate-200">
                    {getHottestLayer(data.hotspotData)}
                  </div>
                </div>
              </div>
              <div className="mt-6 bg-slate-900/30 rounded-lg p-4 border border-slate-700">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">Top 5 Hotspots</h3>
                <div className="space-y-2">
                  {data.hotspotData.slice(0, 5).map((hotspot, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-3 flex-1">
                        <span className={`text-2xl ${hotspot.score >= 70 ? '🔴' : hotspot.score >= 40 ? '🟠' : '🟡'}`}>
                          {hotspot.score >= 70 ? '🔴' : hotspot.score >= 40 ? '🟠' : '🟡'}
                        </span>
                        <span className="font-mono text-blue-400">{hotspot.file}</span>
                      </div>
                      <span className="text-slate-400">{hotspot.score}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Migration Flow Model */}
        {data.migrationData && data.migrationData.edges.length > 0 && (
          <section className="mb-12">
            <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <ArrowRightLeft className="h-6 w-6 text-purple-500" />
                Language Migration Flow Model
              </h2>
              <p className="text-slate-400 mb-6">
                Visualizes language migration patterns between directory clusters. Shows how languages 
                spread, are fixed, rewritten, or removed across the architecture. Historical migrations 
                represent completed changes, while suggested migrations are based on current violations.
              </p>
              <MigrationFlow 
                edges={data.migrationData.edges}
                statistics={data.migrationData.statistics}
              />
            </div>
          </section>
        )}

        {/* Violations Table */}
        <section className="mb-12">
          <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
            <h2 className="text-2xl font-bold mb-6">Active Violations</h2>
            {data.violations.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                <p>No violations found! 🎉</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="border-b border-slate-700">
                    <tr>
                      <th className="pb-3 pr-4 text-slate-400 font-medium">Severity</th>
                      <th className="pb-3 pr-4 text-slate-400 font-medium">File</th>
                      <th className="pb-3 pr-4 text-slate-400 font-medium">Layer</th>
                      <th className="pb-3 text-slate-400 font-medium">Issue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.violations.map((violation, i) => (
                      <tr key={i} className="border-b border-slate-800">
                        <td className="py-3 pr-4">
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(violation.severity)}`}
                          >
                            {violation.severity}
                          </span>
                        </td>
                        <td className="py-3 pr-4 font-mono text-sm text-blue-400">{violation.file}</td>
                        <td className="py-3 pr-4 text-sm text-slate-300">{violation.layer}</td>
                        <td className="py-3 text-sm text-slate-300">{violation.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>

        {/* Semgrep Security Issues */}
        {data.semgrep.results.length > 0 && (
          <section className="mb-12">
            <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <AlertCircle className="h-6 w-6 text-yellow-500" />
                Semgrep Security Issues
              </h2>
              <div className="space-y-4">
                {data.semgrep.results.map((result, i) => (
                  <div key={i} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5" />
                      <div className="flex-1">
                        <div className="font-mono text-sm text-blue-400 mb-1">{result.path}</div>
                        <div className="text-sm text-slate-300 mb-2">{result.message}</div>
                        <div className="flex gap-2 text-xs">
                          <span className="text-slate-500">Rule: {result.check_id}</span>
                          <span
                            className={`px-2 py-0.5 rounded border ${getSeverityColor(result.severity)}`}
                          >
                            {result.severity}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Language History */}
        <section className="mb-12">
          <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
            <h2 className="text-2xl font-bold mb-6">Recent Activity</h2>
            <div className="space-y-3">
              {data.history.map((event, i) => (
                <div key={i} className="flex items-start gap-3 bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div
                    className={`h-2 w-2 rounded-full mt-2 ${
                      event.type === 'fix'
                        ? 'bg-green-500'
                        : event.type === 'violation'
                          ? 'bg-red-500'
                          : 'bg-blue-500'
                    }`}
                  />
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <strong className="text-slate-200">{event.event}</strong>
                        <span className="text-slate-400 ml-2">—</span>
                        <span className="text-slate-400 ml-2">{event.details}</span>
                      </div>
                      <div className="text-sm text-slate-500 whitespace-nowrap">
                        {new Date(event.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <Footer />
    </div>
  );
}
