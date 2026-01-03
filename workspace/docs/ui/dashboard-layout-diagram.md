# Dashboard Layout Diagram

## Overview

This document provides the visual layout specifications for the Phase 1 monitoring dashboard.

## Main Dashboard Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ Navbar                                                                  │
│ [Logo] [Dashboard] [Jobs] [Analytics] [Settings]            [User] 👤  │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                          Dashboard Header                               │
│                     System Monitoring & Status                          │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────┬─────────────────────┬──────┐
│  📊 Metric Card 1   │  📊 Metric Card 2   │  📊 Metric Card 3   │ Card │
│  Total Requests     │  Active Services    │  CPU Usage          │  4   │
│  12,345            │  6/8               │  45%               │      │
│  +12% ↑            │  All Healthy ✓     │  Normal ⚡         │      │
└─────────────────────┴─────────────────────┴─────────────────────┴──────┘

┌─────────────────────────────────────┬─────────────────────────────────┐
│  System Health                      │  Resource Usage                 │
│  ┌─────────────────────────────┐   │  ┌─────────────────────────┐   │
│  │ ✅ API Gateway   [Healthy]  │   │  │ CPU:  ████████░░  76%   │   │
│  │ ✅ Scheduler     [Healthy]  │   │  │ Memory: ████████░░ 82%  │   │
│  │ ✅ Redis         [Healthy]  │   │  │ Disk:   ███░░░░░░░ 34%  │   │
│  │ ✅ Database      [Healthy]  │   │  │ Network: ██████░░░ 68%  │   │
│  │ ✅ Auth Service  [Healthy]  │   │  └─────────────────────────┘   │
│  │ ⚠️  Monitoring   [Degraded] │   │                                 │
│  └─────────────────────────────┘   │  [Last 24 hours]                │
└─────────────────────────────────────┴─────────────────────────────────┘

┌─────────────────────────────────────┬─────────────────────────────────┐
│  Recent Activity Feed               │  System Logs                    │
│  ┌─────────────────────────────┐   │  ┌─────────────────────────┐   │
│  │ 🔵 Job scheduled: backup    │   │  │ [INFO] Request received │   │
│  │    2 minutes ago            │   │  │ [INFO] Task queued      │   │
│  │                              │   │  │ [WARN] Slow response    │   │
│  │ ✅ Task completed: cleanup  │   │  │ [INFO] Job completed    │   │
│  │    5 minutes ago            │   │  │ [ERROR] Connection lost │   │
│  │                              │   │  │ [INFO] Reconnected      │   │
│  │ ⚠️  Alert: High memory      │   │  └─────────────────────────┘   │
│  │    12 minutes ago           │   │                                 │
│  │                              │   │  [Filter: All | Errors | Warn] │
│  └─────────────────────────────┘   │                                 │
└─────────────────────────────────────┴─────────────────────────────────┘
```

## Component Hierarchy

```
Dashboard
├── Navbar
│   ├── Logo
│   ├── Navigation Links
│   └── User Menu
├── Header
│   └── Title
├── Metrics Row (Grid: 4 columns)
│   ├── MetricCard (Requests)
│   ├── MetricCard (Services)
│   ├── MetricCard (CPU)
│   └── MetricCard (Response Time)
├── Main Content (Grid: 2 columns)
│   ├── Left Column
│   │   ├── SystemHealthPanel
│   │   │   └── ServiceStatusList
│   │   └── ActivityFeedPanel
│   │       └── ActivityList
│   └── Right Column
│       ├── ResourceUsagePanel
│       │   └── ResourceCharts
│       └── LogViewerPanel
│           ├── LogList
│           └── LogFilters
└── Footer (optional)
```

## Responsive Breakpoints

### Desktop (>= 1024px)

- 4 metric cards in a row
- 2-column layout for main content
- Full sidebar navigation

### Tablet (768px - 1023px)

- 2 metric cards per row
- 2-column layout (narrower)
- Collapsible sidebar

### Mobile (< 768px)

- 1 metric card per row
- Single column layout
- Hamburger menu navigation

## Color Scheme

### Status Colors

- ✅ Healthy/Success: `#10b981` (green-500)
- ⚠️ Warning/Degraded: `#f59e0b` (amber-500)
- ❌ Error/Critical: `#ef4444` (red-500)
- 🔵 Info/Pending: `#3b82f6` (blue-500)

### Background Colors

- Primary Background: `#0f172a` (slate-900)
- Secondary Background: `#1e293b` (slate-800)
- Card Background: `#334155` (slate-700)
- Border Color: `#475569` (slate-600)

### Text Colors

- Primary Text: `#f1f5f9` (slate-100)
- Secondary Text: `#cbd5e1` (slate-300)
- Muted Text: `#94a3b8` (slate-400)

## Data Flow

```
┌─────────────────┐
│   Dashboard     │
│   Component     │
└────────┬────────┘
         │
         ├─── Fetch Metrics ──────→ GET /api/v1/metrics/timeseries
         │
         ├─── Fetch Health ────────→ GET /api/v1/system/health
         │
         ├─── Fetch Activity ──────→ GET /api/v1/metrics/events
         │
         └─── Fetch Logs ──────────→ GET /api/v1/metrics/logs
                 │
                 ↓
         ┌──────────────┐
         │  Update UI   │
         │  Every 5s    │
         └──────────────┘
```

## Interaction Patterns

### Metric Cards

- Click: Navigate to detailed metrics view
- Hover: Show tooltip with additional info
- Auto-refresh: Every 5 seconds

### Service Status

- Click service: Show detailed health check
- Status indicator: Real-time color updates
- Hover: Show last check timestamp

### Activity Feed

- Click activity: Show full details
- Auto-scroll: New items appear at top
- Filter: By type (all/errors/warnings)

### Logs Viewer

- Search: Full-text search in logs
- Filter: By level (info/warn/error)
- Auto-refresh: Live log streaming
- Export: Download logs as CSV/JSON

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support (Tab, Enter, Escape)
- Screen reader compatible
- High contrast mode support
- Focus indicators on all focusable elements

## Performance Targets

- Initial load: < 2 seconds
- Metrics update: < 100ms
- Smooth animations: 60 FPS
- Max bundle size: < 500KB (gzipped)

## Future Enhancements (Phase 2/3)

- Customizable dashboard layouts
- Drag-and-drop widget positioning
- Custom metric cards
- Real-time collaboration indicators
- Dark/light theme toggle
- Multiple dashboard views
- Export dashboard as PDF/image
