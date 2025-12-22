#!/usr/bin/env python3
"""
MachineNativeOps Auto-Monitor CLI Entry Point
機器原生運維自動監控 CLI 入口

Usage:
    python -m machinenativenops_auto_monitor [options]
    python -m machinenativenops_auto_monitor --config config.yaml
    python -m machinenativenops_auto_monitor --mode production
"""

import sys
import argparse
import logging
from pathlib import Path

from .app import AutoMonitorApp
from .config import MonitorConfig

def setup_logging(verbose: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('auto-monitor.log')
        ]
    )

def main():
    """Main entry point for the auto-monitor application."""
    parser = argparse.ArgumentParser(
        description='MachineNativeOps Auto-Monitor - 自動監控系統',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with default configuration
  python -m machinenativenops_auto_monitor
  
  # Start with custom config file
  python -m machinenativenops_auto_monitor --config /path/to/config.yaml
  
  # Start in production mode with verbose logging
  python -m machinenativenops_auto_monitor --mode production --verbose
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (YAML)'
    )
    parser.add_argument(
        '--mode',
        choices=['development', 'production'],
        default='development',
        help='Running mode (default: development)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port to run the monitoring server (default: 8080)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                sys.exit(1)
            config = MonitorConfig.from_file(config_path)
        else:
            config = MonitorConfig.default()
        
        # Override with CLI arguments
        config.mode = args.mode
        config.port = args.port
        
        logger.info(f"🚀 Starting MachineNativeOps Auto-Monitor")
        logger.info(f"📊 Mode: {config.mode}")
        logger.info(f"🔌 Port: {config.port}")
        
        # Create and run the application
        app = AutoMonitorApp(config)
        app.run()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
MachineNativeOps Auto Monitor CLI Entry Point
Provides multiple command modes for different use cases
"""

import argparse
import sys
import logging
from pathlib import Path

from .app import MachineNativeOpsAutoMonitor
from .config import Config, load_config
from .storage import DatabaseManager

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr)
        ]
    )

def cmd_serve(args):
    """Start monitoring service in daemon mode"""
    setup_logging(args.log_level)
    
    config = load_config(args.config)
    app = MachineNativeOpsAutoMonitor(config)
    
    print(f"🚀 Starting MachineNativeOps Auto Monitor service...")
    print(f"📊 Metrics available on: http://localhost:{config.monitoring.prometheus_port}/metrics")
    print(f"💚 Health check: http://localhost:{config.monitoring.prometheus_port}/health")
    
    try:
        app.run_serve()
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Service error: {e}")
        sys.exit(1)

def cmd_once(args):
    """Run monitoring collection once"""
    setup_logging(args.log_level)
    
    config = load_config(args.config)
    app = MachineNativeOpsAutoMonitor(config)
    
    print("🔄 Running one-time monitoring collection...")
    
    try:
        metrics = app.collect_once()
        print(f"✅ Collection complete")
        print(f"📊 Collected {len(metrics)} metrics")
        
        if args.output:
            import json
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            print(f"💾 Results saved to: {output_path}")
        else:
            print("📈 Metrics Summary:")
            for key, value in metrics.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"❌ Collection error: {e}")
        sys.exit(1)

def cmd_validate_config(args):
    """Validate configuration file"""
    try:
        config = load_config(args.config)
        print(f"✅ Configuration file '{args.config}' is valid")
        
        # Print key configuration values
        print(f"📊 Prometheus port: {config.monitoring.prometheus_port}")
        print(f"🔍 Monitoring interval: {config.monitoring.interval}s")
        print(f"⚛️  Quantum monitoring: {config.quantum.enabled}")
        print(f"🔧 Auto repair: {config.auto_repair.enabled}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        sys.exit(1)

def cmd_print_default_config(args):
    """Print default configuration"""
    default_config = Config()
    
    import yaml
    config_yaml = yaml.dump(default_config.dict(), default_flow_style=False, indent=2)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            f.write(config_yaml)
        print(f"📄 Default config saved to: {output_path}")
    else:
        print("# MachineNativeOps Auto Monitor - Default Configuration")
        print("# Copy to your config file and customize as needed")
        print()
        print(config_yaml)

def cmd_database_stats(args):
    """Show database statistics"""
    try:
        config = load_config(args.config)
        db_manager = DatabaseManager(config.database.path)
        
        stats = db_manager.get_stats()
        print("📊 Database Statistics:")
        print(f"  Total records: {stats.get('total_records', 0)}")
        print(f"  Database size: {stats.get('size_bytes', 0)} bytes")
        print(f"  Oldest record: {stats.get('oldest_record', 'N/A')}")
        print(f"  Newest record: {stats.get('newest_record', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Database stats error: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="machinenativenops-auto-monitor",
        description="MachineNativeOps Auto Monitor - System monitoring with quantum state tracking"
    )
    
    # Global arguments
    parser.add_argument("--config", "-c", 
                       default="/etc/machinenativenops/monitor_config.yaml",
                       help="Configuration file path")
    parser.add_argument("--log-level", "-l",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO",
                       help="Logging level")
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start monitoring service")
    serve_parser.set_defaults(func=cmd_serve)
    
    # Once command
    once_parser = subparsers.add_parser("once", help="Run collection once")
    once_parser.add_argument("--output", "-o", help="Output file for results")
    once_parser.set_defaults(func=cmd_once)
    
    # Validate config command
    validate_parser = subparsers.add_parser("validate-config", help="Validate configuration")
    validate_parser.set_defaults(func=cmd_validate_config)
    
    # Print default config command
    default_parser = subparsers.add_parser("print-default-config", 
                                          help="Print default configuration")
    default_parser.add_argument("--output", "-o", help="Output file for config")
    default_parser.set_defaults(func=cmd_print_default_config)
    
    # Database stats command
    stats_parser = subparsers.add_parser("database-stats", help="Show database statistics")
    stats_parser.set_defaults(func=cmd_database_stats)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)

if __name__ == "__main__":
    main()
