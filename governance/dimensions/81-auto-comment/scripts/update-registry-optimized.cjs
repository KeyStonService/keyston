/**
 * =============================================================================
 * SynergyMesh Governance - Update Events Registry (Optimized)
 * 81-auto-comment: Update Registry Script - Performance Optimized Version
 * =============================================================================
 *
 * Performance improvements:
 * - Async file operations to prevent blocking
 * - Caching for frequently accessed data
 * - Reduced JSON parsing/stringifying operations
 * - Error handling improvements
 *
 * 功能：
 * - 將自動評論事件寫入 governance/index/events/registry.json
 * - 維護事件歷史記錄
 * - 更新統計資訊
 *
 * 使用方式：
 * node update-registry-optimized.js --event-id "auto-comment-xxx" --status "failure"
 *
 * =============================================================================
 */

const fs = require("fs").promises;
const fsSync = require("fs");
const path = require("path");

// =============================================================================
// CONFIGURATION
// =============================================================================

const REGISTRY_PATH = path.join(
  process.cwd(),
  "governance",
  "index",
  "events",
  "registry.json"
);

const EVENT_FILE_PATH = path.join(
  process.cwd(),
  "governance",
  "dimensions",
  "81-auto-comment",
  "output",
  "event.json"
);

// Cache for registry to avoid repeated parsing
let registryCache = null;
let registryCacheTime = 0;
// Cache TTL in milliseconds (default: 5s, configurable via environment variable)
// 5 seconds provides a good balance between reducing file I/O and ensuring fresh data
// for most CI/CD scenarios where multiple updates may occur in quick succession
const CACHE_TTL = parseInt(process.env.REGISTRY_CACHE_TTL || "5000", 10);

// =============================================================================
// ARGUMENT PARSING
// =============================================================================

function parseArgs() {
  const args = process.argv.slice(2);
  const params = {
    eventId: `auto-comment-${Date.now()}`,
    status: "failure",
    workflow: "CI Pipeline",
    commit: "unknown-commit",
    branch: null,
    prNumber: null,
    autoFixed: false,
    errorType: null,
    fixType: null,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--event-id":
        params.eventId = args[++i] || params.eventId;
        break;
      case "--status":
        params.status = args[++i] || params.status;
        break;
      case "--workflow":
        params.workflow = args[++i] || params.workflow;
        break;
      case "--commit":
        params.commit = args[++i] || params.commit;
        break;
      case "--branch":
        params.branch = args[++i];
        break;
      case "--pr-number":
        params.prNumber = args[++i];
        break;
      case "--auto-fixed":
        params.autoFixed = args[++i] === "true";
        break;
      case "--error-type":
        params.errorType = args[++i];
        break;
      case "--fix-type":
        params.fixType = args[++i];
        break;
      case "--from-file":
        // Mark to load from file later (async operation)
        params.loadFromFile = true;
        break;
    }
  }

  return params;
}

// =============================================================================
// ASYNC FILE OPERATIONS
// =============================================================================

/**
 * Load event data from file asynchronously
 */
async function loadEventFromFile() {
  try {
    if (!fsSync.existsSync(EVENT_FILE_PATH)) {
      return null;
    }
    
    const content = await fs.readFile(EVENT_FILE_PATH, "utf-8");
    return JSON.parse(content);
  } catch (err) {
    console.error(`Error loading event file: ${err.message}`);
    return null;
  }
}

/**
 * Load registry with caching to reduce file I/O
 */
async function loadRegistry() {
  // Check cache
  const now = Date.now();
  if (registryCache && (now - registryCacheTime) < CACHE_TTL) {
    return { ...registryCache }; // Return copy to prevent mutations
  }

  // Check if file exists
  if (!fsSync.existsSync(REGISTRY_PATH)) {
    const defaultRegistry = createDefaultRegistry();
    registryCache = defaultRegistry;
    registryCacheTime = now;
    return defaultRegistry;
  }

  try {
    const content = await fs.readFile(REGISTRY_PATH, "utf-8");
    const registry = JSON.parse(content);
    
    // Update cache
    registryCache = registry;
    registryCacheTime = now;
    
    return registry;
  } catch (err) {
    console.error("無法解析 registry.json，將建立新的檔案。");
    const defaultRegistry = createDefaultRegistry();
    registryCache = defaultRegistry;
    registryCacheTime = now;
    return defaultRegistry;
  }
}

/**
 * Save registry asynchronously with atomic write
 */
async function saveRegistry(registry) {
  // Create temp file in same directory for atomic rename
  const dir = path.dirname(REGISTRY_PATH);
  const tempPath = path.join(dir, '.registry.tmp');
  
  try {
    // Ensure directory exists
    const dir = path.dirname(REGISTRY_PATH);
    await fs.mkdir(dir, { recursive: true });
    
    // Write file atomically
    await fs.writeFile(tempPath, JSON.stringify(registry, null, 2), "utf-8");
    await fs.rename(tempPath, REGISTRY_PATH);
    
    // Update cache
    registryCache = registry;
    registryCacheTime = Date.now();
    
    return true;
  } catch (err) {
    console.error(`Error saving registry: ${err.message}`);
    
    // Clean up temporary file if it exists
    try {
      if (fsSync.existsSync(tempPath)) {
        await fs.unlink(tempPath);
      }
    } catch (cleanupErr) {
      console.error(`Error cleaning up temp file: ${cleanupErr.message}`);
    }
    
    return false;
  }
}

// =============================================================================
// REGISTRY OPERATIONS
// =============================================================================

function createDefaultRegistry() {
  return {
    $schema: "../schemas/event-registry.schema.json",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
    metadata: {
      name: "Governance Event Registry",
      description: "持久化事件索引 - 解決代理失憶問題",
      purpose: "讓所有代理啟動時都能讀取完整事件上下文",
      status: "production",
      ready: "immediate",
    },
    bootstrap_contract: {
      description: "入口協定 - 強制代理讀取事件",
      required_context: [
        "events/registry.json",
        "events/vector-index.json",
        "events/current-session.json",
      ],
      validation: {
        ci_gate: true,
        block_on_missing: true,
        error_message: "Agent must read events before execution",
      },
    },
    storage: {
      logs_path: "events/logs/",
      compressed_path: "events/compressed/",
      retention_days: 90,
      compression: {
        enabled: true,
        format: "gzip",
        threshold_days: 7,
      },
    },
    events: [],
    statistics: {
      total_events: 0,
      failures: 0,
      successes: 0,
      auto_fixed: 0,
      manual_fixed: 0,
      by_type: {},
      by_workflow: {},
      by_status: {},
      last_updated: new Date().toISOString(),
    },
  };
}

function updateStatistics(registry, newEvent) {
  const stats = registry.statistics;

  // Update counters
  stats.total_events = (stats.total_events || 0) + 1;

  if (newEvent.status === "failure") {
    stats.failures = (stats.failures || 0) + 1;
  } else if (newEvent.status === "success") {
    stats.successes = (stats.successes || 0) + 1;
  }

  if (newEvent.auto_fixed) {
    stats.auto_fixed = (stats.auto_fixed || 0) + 1;
  }

  // Initialize nested objects if they don't exist
  stats.by_type = stats.by_type || {};
  stats.by_workflow = stats.by_workflow || {};
  stats.by_status = stats.by_status || {};

  // Update by_type
  if (newEvent.error_type) {
    stats.by_type[newEvent.error_type] =
      (stats.by_type[newEvent.error_type] || 0) + 1;
  }

  // Update by_workflow
  if (newEvent.workflow) {
    stats.by_workflow[newEvent.workflow] =
      (stats.by_workflow[newEvent.workflow] || 0) + 1;
  }

  // Update by_status
  stats.by_status[newEvent.status] =
    (stats.by_status[newEvent.status] || 0) + 1;

  stats.last_updated = new Date().toISOString();
}

function createEvent(params) {
  return {
    id: params.eventId,
    timestamp: new Date().toISOString(),
    status: params.status,
    workflow: params.workflow,
    commit: params.commit,
    branch: params.branch,
    pr_number: params.prNumber,
    auto_fixed: params.autoFixed,
    error_type: params.errorType,
    fix_type: params.fixType,
    metadata: {
      agent_version: "2.0.0",
      recorded_by: "auto-comment-system",
    },
  };
}

// =============================================================================
// MAIN EXECUTION
// =============================================================================

async function main() {
  try {
    console.log("🚀 Starting registry update (optimized)...");
    
    // Parse arguments
    let params = parseArgs();
    
    // Load event from file if requested
    if (params.loadFromFile) {
      const eventData = await loadEventFromFile();
      if (eventData) {
        Object.assign(params, {
          eventId: eventData.id || params.eventId,
          status: eventData.status || params.status,
          workflow: eventData.workflow || params.workflow,
          commit: eventData.commit || params.commit,
          autoFixed: eventData.auto_fixed || params.autoFixed,
          errorType: eventData.error_type || params.errorType,
          fixType: eventData.fix_type || params.fixType,
        });
      }
    }
    
    // Load registry (uses cache if available)
    console.log("📖 Loading registry...");
    const registry = await loadRegistry();
    
    // Create new event
    const newEvent = createEvent(params);
    
    // Add to events array
    registry.events = registry.events || [];
    registry.events.push(newEvent);
    
    // Update statistics
    updateStatistics(registry, newEvent);
    
    // Update timestamp
    registry.timestamp = new Date().toISOString();
    
    // Save registry
    console.log("💾 Saving registry...");
    const saved = await saveRegistry(registry);
    
    if (saved) {
      console.log("✅ Registry updated successfully!");
      console.log(`   Event ID: ${newEvent.id}`);
      console.log(`   Status: ${newEvent.status}`);
      console.log(`   Total events: ${registry.statistics.total_events}`);
      
      // Output summary
      console.log("\n📊 Statistics:");
      console.log(JSON.stringify(registry.statistics, null, 2));
    } else {
      console.error("❌ Failed to save registry");
      process.exit(1);
    }
  } catch (err) {
    console.error("❌ Error:", err.message);
    console.error(err.stack);
    process.exit(1);
  }
}

// Run main function
if (require.main === module) {
  main();
}

module.exports = {
  loadRegistry,
  saveRegistry,
  createEvent,
  updateStatistics,
};
