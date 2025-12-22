"""
MachineNativeOps Auto-Monitor - Main Entry Point
=================================================

Usage:
    python -m machinenativenops_auto_monitor [options]
    
Options:
    --config PATH       Configuration file path (default: /etc/machinenativeops/auto-monitor.yaml)
    --verbose           Enable verbose logging
    --dry-run           Run without actually sending alerts or storing data
    --daemon            Run as daemon process
    
Examples:
    python -m machinenativenops_auto_monitor --config config.yaml
    python -m machinenativenops_auto_monitor --daemon --verbose
"""

import sys
import argparse
import logging
import signal
from pathlib import Path

from .app import AutoMonitorApp
from .config import AutoMonitorConfig


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logging.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point for auto-monitor."""
    parser = argparse.ArgumentParser(
        description='MachineNativeOps Auto-Monitor - Autonomous Monitoring System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='/etc/machinenativeops/auto-monitor.yaml',
        help='Configuration file path'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without actually sending alerts or storing data'
    )
    parser.add_argument(
        '--daemon',
        '-d',
        action='store_true',
        help='Run as daemon process'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        
        logger.info(f"Loading configuration from: {config_path}")
        config = AutoMonitorConfig.from_file(config_path)
        
        # Override with command-line options
        if args.dry_run:
            config.dry_run = True
            logger.info("Running in DRY-RUN mode")
        
        # Create and start application
        app = AutoMonitorApp(config)
        
        logger.info("Starting MachineNativeOps Auto-Monitor...")
        logger.info(f"Version: {config.version}")
        logger.info(f"Namespace: {config.namespace}")
        
        if args.daemon:
            logger.info("Running in daemon mode")
            app.run_daemon()
        else:
            logger.info("Running in foreground mode")
            app.run()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
