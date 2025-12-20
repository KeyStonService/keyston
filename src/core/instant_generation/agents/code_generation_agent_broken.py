"""
Code Generation Agent
代碼生成代理

負責根據技術規格自動生成完整系統代碼
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from . import BaseAgent, AgentTask, AgentResult, AgentType

class CodeGenerationAgent(BaseAgent):
    """代碼生成代理 - 第二階段處理"""
    
    def __init__(self, agent_type: AgentType, config: Dict[str, Any] = None):
        super().__init__(agent_type, config)
        self.code_templates = {
            "react": self._load_react_templates(),
            "fastapi": self._load_fastapi_templates(),
            "docker": self._load_docker_templates()
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據格式"""
        required_fields = ["tech_specs", "execution_plan", "analysis"]
        return all(field in input_data for field in required_fields)
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """處理代碼生成任務"""
        start_time = datetime.now()
        
        try:
            # 提取技術規格和執行計劃
            tech_specs = task.input_data.get("tech_specs", {})
            execution_plan = task.input_data.get("execution_plan", {})
            analysis = task.input_data.get("analysis", {})
            
            # 並行生成各個組件
            code_components = await self._generate_components(tech_specs, analysis)
            
            # 生成配置文件
            config_files = await self._generate_configs(tech_specs)
            
            # 創建部署清單
            deployment_manifest = await self._create_deployment_manifest(code_components, config_files)
            
            # 生成文檔
            documentation = await self._generate_documentation(tech_specs, analysis)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=True,
                output_data={
                    "code_components": code_components,
                    "config_files": config_files,
                    "deployment_manifest": deployment_manifest,
                    "documentation": documentation,
                    "generated_files": self._count_generated_files(code_components, config_files),
                    "code_quality_score": self._calculate_quality_score(code_components)
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=False,
                output_data={},
                execution_time=0,
                error_message=str(e)
            )
    
    async def _generate_components(self, tech_specs: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """並行生成各個組件"""
        components = {}
        
        # 生成前端組件
        if "frontend" in tech_specs:
            components["frontend"] = await self._generate_frontend(tech_specs["frontend"], analysis)
        
        # 生成後端組件
        if "backend" in tech_specs:
            components["backend"] = await self._generate_backend(tech_specs["backend"], analysis)
        
        # 生成數據庫腳本
        if "backend" in tech_specs and "database" in tech_specs["backend"]:
            components["database"] = await self._generate_database_scripts(tech_specs["backend"]["database"])
        
        return components
    
    async def _generate_frontend(self, frontend_config: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成前端代碼"""
        framework = frontend_config.get("framework", "react")
        
        if framework == "react":
            return await self._generate_react_app(frontend_config, analysis)
        
        return {"error": f"Unsupported frontend framework: {framework}"}
    
    async def _generate_react_app(self, config: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成React應用"""
        app_name = analysis.get("key_entities", ["app"])[0].lower() or "myapp"
        
        return {
            "package.json": {
                "name": app_name,
                "version": "1.0.0",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.8.0",
                    "axios": "^1.3.0",
                    "tailwindcss": "^3.2.0"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build",
                    "test": "react-scripts test"
                }
            },
            "src": {
                "App.js": self._generate_app_js(app_name, analysis),
                "index.js": self._generate_index_js(),
                "components": {
                    "Header.js": self._generate_header_component(),
                    "Footer.js": self._generate_footer_component(),
                    "Home.js": self._generate_home_component(analysis)
                },
                "styles": {
                    "index.css": self._generate_main_css(),
                    "App.css": self._generate_app_css()
                }
            },
            "public": {
                "index.html": self._generate_index_html(app_name)
            }
        }
    
    async def _generate_backend(self, backend_config: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成後端代碼"""
        framework = backend_config.get("framework", "fastapi")
        
        if framework == "fastapi":
            return await self._generate_fastapi_app(backend_config, analysis)
        
        return {"error": f"Unsupported backend framework: {framework}"}
    
    async def _generate_fastapi_app(self, config: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成FastAPI應用"""
        app_name = analysis.get("key_entities", ["api"])[0].lower() or "myapi"
        
        return {
            "requirements.txt": self._generate_requirements_txt(config),
            "main.py": self._generate_fastapi_main(app_name, analysis),
            "models": {
                "__init__.py": "",
                "user.py": self._generate_user_model(),
                "base.py": self._generate_base_model()
            },
            "routes": {
                "__init__.py": "",
                "users.py": self._generate_users_routes(),
                "auth.py": self._generate_auth_routes()
            },
            "services": {
                "__init__.py": "",
                "user_service.py": self._generate_user_service(),
                "auth_service.py": self._generate_auth_service()
            },
            "config.py": self._generate_config_file(config),
            "database.py": self._generate_database_config(config["database"])
        }
    
    async def _generate_configs(self, tech_specs: Dict[str, Any]) -> Dict[str, Any]:
        """生成配置文件"""
        configs = {}
        
        # Docker配置
        if "infrastructure" in tech_specs and tech_specs["infrastructure"]["deployment"] == "docker":
            configs["docker"] = await self._generate_docker_configs(tech_specs)
        
        # Kubernetes配置
        if "infrastructure" in tech_specs and tech_specs["infrastructure"]["orchestration"] == "kubernetes":
            configs["kubernetes"] = await self._generate_k8s_configs(tech_specs)
        
        # 環境配置
        configs["environment"] = self._generate_env_configs(tech_specs)
        
        return configs
    
    async def _generate_docker_configs(self, tech_specs: Dict[str, Any]) -> Dict[str, str]:
        """生成Docker配置"""
        return {
            "Dockerfile": self._generate_dockerfile(tech_specs),
            "docker-compose.yml": self._generate_docker_compose(tech_specs),
            ".dockerignore": self._generate_dockerignore()
        }
    
    async def _create_deployment_manifest(self, components: Dict[str, Any], configs: Dict[str, Any]) -> Dict[str, Any]:
        """創建部署清單"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "components": list(components.keys()),
            "configs": list(configs.keys()),
            "deployment_order": ["database", "backend", "frontend"],
            "health_checks": {
                "backend": "/health",
                "frontend": "/"
            },
            "environment_variables": self._extract_env_vars(components, configs)
        }
    
    async def _generate_documentation(self, tech_specs: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, str]:
        """生成文檔"""
        return {
            "README.md": self._generate_readme(tech_specs, analysis),
            "API.md": self._generate_api_documentation(tech_specs),
            "DEPLOYMENT.md": self._generate_deployment_guide(tech_specs)
        }
    
    # 模板加載方法
    def _load_react_templates(self) -> Dict[str, str]:
        """加載React模板"""
        return {
            "app_js": "// React App Component\nimport React from 'react';\nimport {{ BrowserRouter as Router, Routes, Route }} from 'react-router-dom';\nimport Header from './components/Header';\nimport Footer from './components/Footer';\nimport Home from './components/Home';\n\nfunction App() {{\n  return (\n    <Router>\n      <div className=&quot;min-h-screen flex flex-col&quot;>\n        <Header />\n        <main className=&quot;flex-grow&quot;>\n          <Routes>\n            <Route path=&quot;/&quot; element={<Home />} />\n          </Routes>\n        </main>\n        <Footer />\n      </div>\n    </Router>\n  );\n}}\n\nexport default App;",
            "index_js": "// React Entry Point\nimport React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport './styles/index.css';\nimport App from './App';\n\nconst root = ReactDOM.createRoot(document.getElementById('root'));\nroot.render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);"
        }
    
    def _load_fastapi_templates(self) -> Dict[str, str]:
        """加載FastAPI模板"""
        return {
            "main_py": "from fastapi import FastAPI, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom routes import users, auth\nfrom config import settings\n\napp = FastAPI(\n    title=&quot;{app_name}&quot;,\n    description=&quot;Generated API&quot;,\n    version=&quot;1.0.0&quot;\n)\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[&quot;*&quot;],\n    allow_credentials=True,\n    allow_methods=[&quot;*&quot;],\n    allow_headers=[&quot;*&quot;],\n)\n\napp.include_router(users.router, prefix=&quot;/api/v1/users&quot;, tags=[&quot;users&quot;])\napp.include_router(auth.router, prefix=&quot;/api/v1/auth&quot;, tags=[&quot;auth&quot;])\n\n@app.get(&quot;/health&quot;)\nasync def health_check():\n    return {{&quot;status&quot;: &quot;healthy&quot;}}\n\nif __name__ == &quot;__main__&quot;:\n    import uvicorn\n    uvicorn.run(app, host=&quot;0.0.0.0&quot;, port=8000)"
        }
    
    def _load_docker_templates(self) -> Dict[str, str]:
        """加載Docker模板"""
        return {
            "dockerfile": "FROM python:3.11-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nEXPOSE 8000\n\nCMD [&quot;uvicorn&quot;, &quot;main:app&quot;, &quot;--host&quot;, &quot;0.0.0.0&quot;, &quot;--port&quot;, &quot;8000&quot;]"
        }
    
    # 代碼生成輔助方法
    def _generate_app_js(self, app_name: str, analysis: Dict[str, Any]) -> str:
        """生成React App組件"""
        app_name_capitalized = app_name.title()
        return f"""
import React from 'react';
import {{ BrowserRouter as Router, Routes, Route }} from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './components/Home';

function {app_name_capitalized}() {{
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={{<Home />}} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}}

export default {app_name_capitalized};
"""
    
    def _generate_index_js(self) -> str:
        """生成React入口文件"""
        return """
import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    def _generate_fastapi_main(self, app_name: str, analysis: Dict[str, Any]) -> str:
        """生成FastAPI主文件"""
        return f"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import users, auth
from config import settings

app = FastAPI(
    title="{app_name.title()} API",
    description="Generated API for {app_name}",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "service": "{app_name}"}}

@app.get("/")
async def root():
    return {{"message": "Welcome to {app_name} API"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    
    def _count_generated_files(self, components: Dict[str, Any], configs: Dict[str, Any]) -> int:
        """計算生成的文件數量"""
        count = 0
        for component in components.values():
            if isinstance(component, dict):
                count += len([k for k, v in component.items() if isinstance(v, str)])
                # 遞歸計算子目錄中的文件
                for sub_component in component.values():
                    if isinstance(sub_component, dict):
                        count += len([k for k, v in sub_component.items() if isinstance(v, str)])
        
        for config in configs.values():
            if isinstance(config, dict):
                count += len(config)
            elif isinstance(config, str):
                count += 1
        
        return count
    
    def _calculate_quality_score(self, components: Dict[str, Any]) -> float:
        """計算代碼質量分數"""
        # 簡化的質量評分
        base_score = 85.0
        
        # 檢查是否有完整的前後端
        if "frontend" in components and "backend" in components:
            base_score += 5.0
        
        # 檢查是否有數據庫配置
        if "database" in components:
            base_score += 5.0
        
        # 檢查是否有配置文件
        if any("config" in key.lower() for key in components.keys()):
            base_score += 5.0
        
        return min(base_score, 100.0)

__all__ = ["CodeGenerationAgent"]