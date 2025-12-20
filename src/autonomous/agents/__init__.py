"""
Intelligent Automation Module
智能自動化模組

High-value capabilities extracted from OJ-agent for autonomous systems.
核心商業價值能力，專為自動化系統設計。
"""

__version__ = "1.0.0"
__author__ = "SLASolve Team"

# Handle both package and standalone imports
try:
    from .pipeline_service import pipeline_service, PipelineService
except ImportError:
    # When running standalone (e.g., in tests), use absolute imports
    try:
        from pipeline_service import pipeline_service, PipelineService
    except ImportError:
        # Module not available in this context
        pipeline_service = None
        PipelineService = None

# Agent system imports (kebab-case filenames require importlib)
import importlib.util
import sys
from pathlib import Path

def _import_kebab_module(module_alias: str, file_name: str, legacy_alias: str | None = None):
    """
    Load kebab-case source files and expose them under underscore-based aliases.

    This helper is used to load Python modules whose source files use kebab-case
    filenames (for example, ``"base-agent.py"``) and to expose them under stable,
    underscore-based aliases in ``sys.modules``.

    Parameters
    ----------
    module_alias:
        The underscore-based alias for the module (e.g. ``"base_agent"``),
        *not* a full dotted module path. This value is combined with this
        package's name to form the primary qualified module name:
        ``qualified_name = f"{__name__}.{module_alias}"``. The module object
        is always registered in ``sys.modules`` under this ``qualified_name``.
    file_name:
        The kebab-case filename of the module to load (e.g. ``"base-agent.py"``),
        resolved relative to the directory containing this ``__init__`` file.
    legacy_alias:
        Optional fully-qualified legacy module path (e.g. ``"agents.base_agent"``).
        When provided, the same module object is additionally registered in
        ``sys.modules[legacy_alias]`` for backwards compatibility, so both
        ``qualified_name`` and ``legacy_alias`` refer to the identical module.

    Returns
    -------
    module | None
        The imported module instance, or ``None`` if the source file does not
        exist or a spec could not be created.
    """
    module_path = Path(__file__).parent / file_name
    if not module_path.exists():
        return None
    qualified_name = f"{__name__}.{module_alias}"
    spec = importlib.util.spec_from_file_location(qualified_name, module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified_name] = module
        if legacy_alias:
            sys.modules[legacy_alias] = module
        spec.loader.exec_module(module)
        return module
    return None

# Import base agent components
_base_agent = _import_kebab_module('base_agent', 'base-agent.py', legacy_alias='agents.base_agent')
if _base_agent:
    BaseAgent = _base_agent.BaseAgent
    AgentStatus = _base_agent.AgentStatus
    AgentColors = _base_agent.Colors
else:
    BaseAgent = None
    AgentStatus = None
    AgentColors = None

# Import coordinator agent
_coordinator_agent = _import_kebab_module('coordinator_agent', 'coordinator-agent.py', legacy_alias='agents.coordinator_agent')
CoordinatorAgent = _coordinator_agent.CoordinatorAgent if _coordinator_agent else None

# Import autopilot agent
_autopilot_agent = _import_kebab_module('autopilot_agent', 'autopilot-agent.py', legacy_alias='agents.autopilot_agent')
AutopilotAgent = _autopilot_agent.AutopilotAgent if _autopilot_agent else None

# Import deployment agent
_deployment_agent = _import_kebab_module('deployment_agent', 'deployment-agent.py', legacy_alias='agents.deployment_agent')
DeploymentAgent = _deployment_agent.DeploymentAgent if _deployment_agent else None

# Import utils
_agent_utils = _import_kebab_module('agent_utils', 'agent-utils.py', legacy_alias='agents.agent_utils')
if _agent_utils:
    print_color = _agent_utils.print_color
    print_info = _agent_utils.print_info
    print_success = _agent_utils.print_success
    print_warn = _agent_utils.print_warn
    print_error = _agent_utils.print_error
else:
    print_color = None
    print_info = None
    print_success = None
    print_warn = None
    print_error = None

__all__ = [
    "pipeline_service",
    "PipelineService",
    "BaseAgent",
    "AgentStatus",
    "AgentColors",
    "CoordinatorAgent",
    "AutopilotAgent",
    "DeploymentAgent",
    "print_color",
    "print_info",
    "print_success",
    "print_warn",
    "print_error",
]
