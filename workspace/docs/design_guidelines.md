# Design Guidelines: GitHub Repository Architecture Platform

## Design Approach

**Selected Approach:** Design System + Reference Hybrid

- **Primary System:** Material Design 3 principles for structured data display
- **Reference Inspiration:** GitHub's interface patterns, Linear's clean developer UX, Vercel's dashboard clarity
- **Rationale:** Developer-focused tool requiring clarity, information density, and familiar patterns for technical users

## Core Design Principles

1. **Information Hierarchy:** Clear visual distinction between primary content (file trees, code) and secondary metadata (stats, timestamps)
2. **Scannable Data:** Easy-to-parse layouts for commits, branches, and file structures
3. **Technical Clarity:** Monospace fonts for code, clear labeling, minimal visual noise

## Typography

**Font Families:**

- **UI Text:** Inter (via Google Fonts) - clean, readable for interface elements
- **Code/Technical:** JetBrains Mono (via Google Fonts) - for file names, code snippets, commits
- **Headings:** Inter Semi-Bold/Bold

**Hierarchy:**

- Page Titles: text-3xl font-bold
- Section Headers: text-xl font-semibold
- Card Titles: text-lg font-medium
- Body Text: text-base
- Metadata/Labels: text-sm
- Code/Technical: text-sm font-mono
- Timestamps/Auxiliary: text-xs

## Layout System

**Spacing Primitives:** Consistent use of Tailwind units: 2, 4, 6, 8, 12, 16

- Component padding: p-4 to p-6
- Section gaps: gap-6 to gap-8
- Card spacing: p-6
- List items: py-3 px-4

**Grid Structure:**

- Main container: max-w-7xl mx-auto px-4
- Dashboard layout: Three-column responsive grid for stat cards (grid-cols-1 md:grid-cols-3 gap-6)
- File browser: Two-column split (tree navigation 1/3 width, content viewer 2/3 width on desktop)
- Commit list: Single column with full-width cards

## Component Library

### Navigation

- **Top Navigation Bar:** Fixed header with repository name, breadcrumbs, user menu
  - Height: h-16
  - Contains: Logo/repo name, navigation tabs, GitHub link button
  
### Dashboard Cards

- **Repository Overview Card:** Full-width header card displaying:
  - Repository name, description, visibility badge
  - Star count, fork count, language indicator
  - Last updated timestamp
  - Quick action buttons (View on GitHub, Clone)
  
- **Stats Cards:** Three-column grid showing:
  - Total Commits count with icon
  - Active Branches count
  - Total Files count
  - Each with subtle icon (Heroicons) and large number display

### File Structure Visualization

- **Tree Navigation Panel:**
  - Collapsible folder structure using nested indentation (pl-4 per level)
  - Folder/file icons (Heroicons: folder, document icons)
  - Expandable/collapsible folders with chevron indicators
  - Hover states on clickable items
  
- **Content Viewer Panel:**
  - File path breadcrumb at top
  - Code display with line numbers (if code file)
  - Markdown rendering (if .md file)
  - Syntax highlighting using Prism.js or highlight.js

### Commits Timeline

- **Commit List:**
  - Card-based layout with shadow (shadow-sm)
  - Each commit shows: message, author avatar (placeholder), timestamp, commit hash (truncated)
  - Commit hash in monospace with copy button
  - Spacing: space-y-4 between commits

### Branches Display

- **Branch Cards:** Two-column grid (grid-cols-1 md:grid-cols-2)
  - Branch name with git icon
  - "Last commit" timestamp
  - "Behind/ahead" indicators if applicable
  - Badge for default branch

### Data Tables

- Standard table structure for technical data:
  - Header: sticky top-0 with medium font weight
  - Rows: hover:bg-gray-50 transition
  - Cell padding: px-4 py-3
  - Borders: border-b on rows

## Icon Library

**Selected Library:** Heroicons via CDN

- Navigation: home, folder, document, code-bracket
- Actions: clipboard, arrow-top-right-on-square, chevron-right/down
- Status: check-circle, x-circle, clock
- Git specific: git-branch (use code-branch alternative), git-commit

## Layout Patterns

### Page Structure

1. **Header Section** (h-16): Fixed navigation bar
2. **Main Content** (min-h-screen pt-16):
   - Repository overview card (full-width)
   - Stats grid (3 columns)
   - Tabbed content area for Files/Commits/Branches

### Tab Navigation

- Horizontal tab bar below overview card
- Active tab indicator (border-b-2)
- Tabs: "Files", "Commits", "Branches"
- Spacing: space-x-8 between tabs

### Responsive Behavior

- Desktop (lg+): Full multi-column layouts, side-by-side file tree + viewer
- Tablet (md): Two-column grids, stacked tree + viewer
- Mobile: Single column, collapsible tree navigation drawer

## Interactive Elements

### Buttons

- **Primary Action:** Solid background, px-6 py-2.5, rounded-lg, font-medium
- **Secondary Action:** Border style, same padding
- **Icon Buttons:** Square p-2, rounded-md

### Cards

- Standard card: rounded-lg, shadow-sm border, p-6
- Hover cards (clickable): hover:shadow-md transition
- Nested cards: Reduce padding to p-4

### Form Elements

- Search bar for file filtering: Full-width, h-10, rounded-md, pl-10 (icon space)
- No distracting animations - keep transitions subtle and functional (200ms)

## No Animations Policy

Minimal transitions only:

- Hover states: Simple opacity or shadow changes (transition-all duration-200)
- No scroll animations, parallax, or decorative motion
- Focus on instant, responsive feel

## Images

**No hero images required** - This is a functional dashboard/tool, not a marketing site. All visual interest comes from data visualization, clear layouts, and structured content display.
