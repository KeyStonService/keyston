import { useState, useEffect } from 'react';
import { Activity, Server, Database, Cpu, HardDrive, Network, AlertTriangle, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
}

function MetricCard({ title, value, change, icon, trend = 'stable' }: MetricCardProps) {
  const trendColors = {
    up: 'text-green-500',
    down: 'text-red-500',
    stable: 'text-slate-400'
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-400">{title}</CardTitle>
        <div className="text-slate-400">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white">{value}</div>
        {change && (
          <p className={`text-xs ${trendColors[trend]} flex items-center gap-1 mt-1`}>
            {trend === 'up' && <TrendingUp className="h-3 w-3" />}
            {change}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

interface SystemHealthItem {
  name: string;
  status: 'healthy' | 'warning' | 'critical';
  uptime: string;
  lastCheck: string;
}

function SystemHealthPanel() {
  const [services] = useState<SystemHealthItem[]>([
    { name: 'API Gateway', status: 'healthy', uptime: '99.99%', lastCheck: '2 seconds ago' },
    { name: 'Contract Service L1', status: 'healthy', uptime: '99.95%', lastCheck: '5 seconds ago' },
    { name: 'MCP Servers', status: 'healthy', uptime: '99.98%', lastCheck: '3 seconds ago' },
    { name: 'Database Cluster', status: 'healthy', uptime: '100%', lastCheck: '1 second ago' },
    { name: 'Redis Cache', status: 'warning', uptime: '98.50%', lastCheck: '10 seconds ago' },
    { name: 'ML Pipeline', status: 'healthy', uptime: '99.92%', lastCheck: '8 seconds ago' },
  ]);

  const statusConfig = {
    healthy: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10', border: 'border-green-500/20' },
    warning: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20' },
    critical: { icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-500/10', border: 'border-red-500/20' }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-white">System Health</CardTitle>
        <CardDescription className="text-slate-400">Real-time service status monitoring</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {services.map((service) => {
            const config = statusConfig[service.status];
            const Icon = config.icon;
            return (
              <div key={service.name} className={`p-4 rounded-lg border ${config.bg} ${config.border}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Icon className={`h-5 w-5 ${config.color}`} />
                    <div>
                      <div className="font-medium text-white">{service.name}</div>
                      <div className="text-xs text-slate-400">Last checked: {service.lastCheck}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-white">{service.uptime}</div>
                    <div className="text-xs text-slate-400">Uptime</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

function ResourceUsagePanel() {
  const [resources] = useState([
    { name: 'CPU Usage', value: 45, max: 100, unit: '%', status: 'normal' },
    { name: 'Memory Usage', value: 6.8, max: 16, unit: 'GB', status: 'normal' },
    { name: 'Disk Usage', value: 320, max: 500, unit: 'GB', status: 'warning' },
    { name: 'Network I/O', value: 125, max: 1000, unit: 'Mbps', status: 'normal' },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      default: return 'bg-blue-500';
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-white">Resource Usage</CardTitle>
        <CardDescription className="text-slate-400">Real-time system resource monitoring</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {resources.map((resource) => {
            const percentage = (resource.value / resource.max) * 100;
            return (
              <div key={resource.name}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white">{resource.name}</span>
                  <span className="text-sm text-slate-400">
                    {resource.value} / {resource.max} {resource.unit}
                  </span>
                </div>
                <div className="relative">
                  <Progress value={percentage} className={`h-2 ${getStatusColor(resource.status)}`} />
                  <span className="absolute right-0 -top-6 text-xs text-slate-500">
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

function RecentActivityPanel() {
  const [activities] = useState([
    { id: 1, type: 'deployment', message: 'API Gateway v2.1.0 deployed successfully', time: '2 minutes ago', status: 'success' },
    { id: 2, type: 'alert', message: 'High memory usage detected on worker-03', time: '15 minutes ago', status: 'warning' },
    { id: 3, type: 'task', message: 'Scheduled backup completed', time: '1 hour ago', status: 'success' },
    { id: 4, type: 'deployment', message: 'ML Pipeline updated to v1.8.3', time: '2 hours ago', status: 'success' },
    { id: 5, type: 'alert', message: 'Rate limit exceeded for API key: abc123', time: '3 hours ago', status: 'warning' },
  ]);

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      success: 'default',
      warning: 'secondary',
      error: 'destructive',
    };
    return variants[status] || 'outline';
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-white">Recent Activity</CardTitle>
        <CardDescription className="text-slate-400">Latest system events and notifications</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-3 pb-3 border-b border-slate-800 last:border-0 last:pb-0">
              <Activity className="h-4 w-4 text-slate-400 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white">{activity.message}</p>
                <div className="flex items-center gap-2 mt-1">
                  <Clock className="h-3 w-3 text-slate-500" />
                  <span className="text-xs text-slate-500">{activity.time}</span>
                  <Badge variant={getStatusBadge(activity.status)} className="ml-auto">
                    {activity.status}
                  </Badge>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans">
      <Navbar />
      
      <div className="container mx-auto px-6 py-8 mt-20">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-bold text-white">System Dashboard</h1>
            <div className="text-sm text-slate-400">
              {currentTime.toLocaleString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
              })}
            </div>
          </div>
          <p className="text-slate-400">Real-time monitoring and system health overview</p>
        </div>

        {/* Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Requests"
            value="1,234,567"
            change="+12.5% from last hour"
            trend="up"
            icon={<Server className="h-4 w-4" />}
          />
          <MetricCard
            title="Active Services"
            value="18/20"
            change="2 services down"
            trend="down"
            icon={<Database className="h-4 w-4" />}
          />
          <MetricCard
            title="CPU Usage"
            value="45%"
            change="Normal"
            trend="stable"
            icon={<Cpu className="h-4 w-4" />}
          />
          <MetricCard
            title="Response Time"
            value="125ms"
            change="-15ms from last hour"
            trend="up"
            icon={<Network className="h-4 w-4" />}
          />
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-slate-900 border border-slate-800">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="services">Services</TabsTrigger>
            <TabsTrigger value="resources">Resources</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SystemHealthPanel />
              <ResourceUsagePanel />
            </div>
            <RecentActivityPanel />
          </TabsContent>

          <TabsContent value="services">
            <SystemHealthPanel />
          </TabsContent>

          <TabsContent value="resources">
            <ResourceUsagePanel />
          </TabsContent>

          <TabsContent value="logs">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white">System Logs</CardTitle>
                <CardDescription className="text-slate-400">Real-time log streaming and search</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-slate-950 rounded-lg p-4 font-mono text-sm space-y-1">
                  <div className="text-green-400">[2025-12-16 22:57:01] INFO: API Gateway started on port 8000</div>
                  <div className="text-blue-400">[2025-12-16 22:57:02] INFO: Contract Service L1 connected to database</div>
                  <div className="text-green-400">[2025-12-16 22:57:03] INFO: MCP Servers initialized successfully</div>
                  <div className="text-yellow-400">[2025-12-16 22:57:05] WARN: High memory usage detected on worker-03</div>
                  <div className="text-green-400">[2025-12-16 22:57:10] INFO: Scheduled backup task started</div>
                  <div className="text-blue-400">[2025-12-16 22:57:15] INFO: ML Pipeline processing batch job #12345</div>
                  <div className="text-green-400">[2025-12-16 22:57:20] INFO: Cache hit rate: 95.3%</div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <Footer />
    </div>
  );
}
