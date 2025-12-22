#!/usr/bin/env python3
"""
MachineNativeOps Config Manager Module
First real module implementation to fix false success metrics
"""

import os
import sys
import json
import yaml
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
)
logger = logging.getLogger('config-manager')

# Module Configuration
class ConfigManager:
    """Real configuration management module"""
    
    def __init__(self):
        self.config = {}
        self.config_path = os.getenv('CONFIG_PATH', '/etc/machinenativenops/config')
        self.port = int(os.getenv('PORT', '8080'))
        self.service_name = 'config-manager'
        self.version = '1.0.0'
        self.startup_time = datetime.utcnow().isoformat()
        
        logger.info(f"Initializing {self.service_name} v{self.version}")
        logger.info(f"Config path: {self.config_path}")
        logger.info(f"Port: {self.port}")

    def load_config(self) -> bool:
        """Load configuration from files and environment"""
        try:
            # Load from YAML files
            config_files = [
                'root.config.yaml',
                'root.governance.yaml',
                'root.modules.yaml'
            ]
            
            for config_file in config_files:
                file_path = Path(f"/workspace/{config_file}")
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        file_config = yaml.safe_load(f)
                        self.config[config_file.replace('.yaml', '')] = file_config
                        logger.info(f"Loaded config from {config_file}")
            
            # Override with environment variables
            for key, value in os.environ.items():
                if key.startswith('MNO_'):
                    config_key = key[4:].lower()
                    self.config[config_key] = value
                    logger.info(f"Environment override: {config_key}")
            
            logger.info("Configuration loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Health check response"""
        return {
            "status": "healthy",
            "service": self.service_name,
            "version": self.version,
            "startup_time": self.startup_time,
            "timestamp": datetime.utcnow().isoformat(),
            "config_loaded": len(self.config) > 0,
            "config_count": len(self.config)
        }

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting config value for key '{key}': {str(e)}")
            return default

    def reload_config(self) -> bool:
        """Reload configuration"""
        logger.info("Reloading configuration...")
        self.config.clear()
        return self.load_config()

# Initialize Config Manager
config_manager = ConfigManager()

# FastAPI Application
app = FastAPI(
    title="MachineNativeOps Config Manager",
    description="Configuration management service for MachineNativeOps platform",
    version=config_manager.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic Models
class ConfigRequest(BaseModel):
    key: str
    default: Optional[Any] = None

class ReloadRequest(BaseModel):
    force: bool = False

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_data = config_manager.health_check()
        return JSONResponse(
            status_code=200,
            content=health_data
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "Service is currently unhealthy. Please try again later.",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": config_manager.service_name,
        "version": config_manager.version,
        "description": "MachineNativeOps Configuration Manager",
        "endpoints": {
            "health": "/health",
            "config": "/config/{key}",
            "all_configs": "/config",
            "reload": "/reload",
            "docs": "/docs"
        },
        "startup_time": config_manager.startup_time
    }

@app.get("/config")
async def get_all_configs():
    """Get all configuration values"""
    try:
        # Return config keys only (avoid exposing sensitive data)
        config_keys = list(config_manager.config.keys())
        return {
            "config_keys": config_keys,
            "config_count": len(config_keys),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting all configs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/{key}")
async def get_config(key: str, default: Optional[str] = None):
    """Get specific configuration value"""
    try:
        value = config_manager.get_config_value(key, default)
        if value is not None:
            return {
                "key": key,
                "value": value,
                "found": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "key": key,
                "value": default,
                "found": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting config for key '{key}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reload")
async def reload_config(request: ReloadRequest, background_tasks: BackgroundTasks):
    """Reload configuration"""
    try:
        def reload_task():
            success = config_manager.reload_config()
            if success:
                logger.info("Configuration reloaded successfully")
            else:
                logger.error("Configuration reload failed")
        
        background_tasks.add_task(reload_task)
        
        return {
            "message": "Configuration reload initiated",
            "force": request.force,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error initiating config reload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    return {
        "service": config_manager.service_name,
        "version": config_manager.version,
        "uptime_seconds": (datetime.utcnow() - datetime.fromisoformat(config_manager.startup_time)).total_seconds(),
        "config_count": len(config_manager.config),
        "timestamp": datetime.utcnow().isoformat()
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Service startup"""
    logger.info(f"Starting {config_manager.service_name} v{config_manager.version}")
    
    # Load configuration
    if not config_manager.load_config():
        logger.error("Failed to load initial configuration")
        sys.exit(1)
    
    logger.info(f"{config_manager.service_name} started successfully")
    logger.info(f"Health check available at: http://localhost:{config_manager.port}/health")

@app.on_event("shutdown")
async def shutdown_event():
    """Service shutdown"""
    logger.info(f"Shutting down {config_manager.service_name}")

# Main execution
if __name__ == "__main__":
    # Load configuration before starting
    if not config_manager.load_config():
        logger.error("Failed to load initial configuration")
        sys.exit(1)
    
    # Start the service
    logger.info(f"Starting {config_manager.service_name} on port {config_manager.port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config_manager.port,
        log_config=None,  # Use our own logging configuration
        access_log=True
    )