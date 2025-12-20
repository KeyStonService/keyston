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
    
    def _generate_header_component(self) -> str:
        """生成Header組件"""
        return """
import React from 'react';

function Header() {
  return (
    <header className="bg-blue-600 text-white p-4">
      <div className="container mx-auto">
        <h1 className="text-2xl font-bold">MyApp</h1>
      </div>
    </header>
  );
}

export default Header;
"""
    
    def _generate_footer_component(self) -> str:
        """生成Footer組件"""
        return """
import React from 'react';

function Footer() {
  return (
    <footer className="bg-gray-800 text-white p-4 mt-8">
      <div className="container mx-auto text-center">
        <p>&copy; 2024 MyApp. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
"""
    
    def _generate_home_component(self, analysis: Dict[str, Any]) -> str:
        """生成Home組件"""
        return """
import React from 'react';

function Home() {
  return (
    <div className="container mx-auto p-8">
      <h2 className="text-3xl font-bold mb-4">Welcome to MyApp</h2>
      <p className="text-lg mb-4">This is a generated React application.</p>
      <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
        Get Started
      </button>
    </div>
  );
}

export default Home;
"""
    
    def _generate_main_css(self) -> str:
        """生成主CSS文件"""
        return """
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
"""
    
    def _generate_app_css(self) -> str:
        """生成App CSS文件"""
        return """
.App {
  text-align: center;
}

.App-logo {
  height: 40vmin;
  pointer-events: none;
}

@media (prefers-reduced-motion: no-preference) {
  .App-logo {
    animation: App-logo-spin infinite 20s linear;
  }
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

.App-link {
  color: #61dafb;
}

@keyframes App-logo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
"""
    
    def _generate_index_html(self, app_name: str) -> str:
        """生成HTML模板"""
        return f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{app_name.title()} - Generated application" />
    <title>{app_name.title()}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
    
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
    
    def _generate_requirements_txt(self, config: Dict[str, Any]) -> str:
        """生成requirements.txt"""
        return """
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
"""
    
    def _generate_user_model(self) -> str:
        """生成用戶模型"""
        return """
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
"""
    
    def _generate_base_model(self) -> str:
        """生成基礎模型"""
        return """
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"""
    
    def _generate_users_routes(self) -> str:
        """生成用戶路由"""
        return """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.user_service import UserService
from database import get_db

router = APIRouter()
user_service = UserService()

@router.get("/")
async def get_users(db: Session = Depends(get_db)):
    return await user_service.get_all_users(db)

@router.post("/")
async def create_user(user_data: dict, db: Session = Depends(get_db)):
    return await user_service.create_user(user_data, db)

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = await user_service.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
"""
    
    def _generate_auth_routes(self) -> str:
        """生成認證路由"""
        return """
from fastapi import APIRouter, Depends, HTTPException
from services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()

@router.post("/login")
async def login(credentials: dict):
    return await auth_service.authenticate_user(credentials)

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
"""
    
    def _generate_user_service(self) -> str:
        """生成用戶服務"""
        return """
from typing import List, Optional
from sqlalchemy.orm import Session
from models.user import User

class UserService:
    async def get_all_users(self, db: Session) -> List[User]:
        return db.query(User).all()
    
    async def get_user_by_id(self, user_id: int, db: Session) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    async def create_user(self, user_data: dict, db: Session) -> User:
        # 實際實現中需要密碼哈希等
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
"""
    
    def _generate_auth_service(self) -> str:
        """生成認證服務"""
        return """
from typing import Optional

class AuthService:
    async def authenticate_user(self, credentials: dict) -> dict:
        # 實際實現中需要驗證用戶名密碼
        email = credentials.get("email")
        password = credentials.get("password")
        
        # 簡化實現
        if email and password:
            return {
                "access_token": "generated_token",
                "token_type": "bearer",
                "user": {"email": email}
            }
        
        raise ValueError("Invalid credentials")
"""
    
    def _generate_config_file(self, config: Dict[str, Any]) -> str:
        """生成配置文件"""
        return """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/app"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
"""
    
    def _generate_database_config(self, database_config: Dict[str, Any]) -> str:
        """生成數據庫配置"""
        return """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
    
    async def _generate_database_scripts(self, database_config: Dict[str, Any]) -> Dict[str, str]:
        """生成數據庫腳本"""
        return {
            "init.sql": """
-- 初始化數據庫腳本
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 創建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
""",
            "migrate.sql": """
-- 數據庫遷移腳本
-- 可以在此處添加表結構變更
"""
        }
    
    async def _generate_configs(self, tech_specs: Dict[str, Any]) -> Dict[str, Any]:
        """生成配置文件"""
        configs = {}
        
        # Docker配置
        if "infrastructure" in tech_specs and tech_specs["infrastructure"]["deployment"] == "docker":
            configs["docker"] = await self._generate_docker_configs(tech_specs)
        
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
    
    def _generate_dockerfile(self, tech_specs: Dict[str, Any]) -> str:
        """生成Dockerfile"""
        return """
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def _generate_docker_compose(self, tech_specs: Dict[str, Any]) -> str:
        """生成docker-compose.yml"""
        return """
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""
    
    def _generate_dockerignore(self) -> str:
        """生成.dockerignore"""
        return """
__pycache__
*.pyc
.env
.git
.gitignore
README.md
Dockerfile
.dockerignore
"""
    
    def _generate_env_configs(self, tech_specs: Dict[str, Any]) -> Dict[str, str]:
        """生成環境配置"""
        return {
            ".env.example": """
DATABASE_URL=postgresql://user:password@localhost:5432/app
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
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
    
    def _generate_readme(self, tech_specs: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """生成README"""
        return """
# Generated Application

This is an auto-generated full-stack application.

## Features

- Modern React frontend
- FastAPI backend
- PostgreSQL database
- User authentication
- RESTful API

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Contributing

This is an auto-generated project. Please modify as needed.
"""
    
    def _generate_api_documentation(self, tech_specs: Dict[str, Any]) -> str:
        """生成API文檔"""
        return """
# API Documentation

## Authentication

### Login
POST /api/v1/auth/login
Content-Type: application/json

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

### Logout
POST /api/v1/auth/logout

## Users

### Get All Users
GET /api/v1/users

### Create User
POST /api/v1/users
Content-Type: application/json

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

### Get User by ID
GET /api/v1/users/{id}
"""
    
    def _generate_deployment_guide(self, tech_specs: Dict[str, Any]) -> str:
        """生成部署指南"""
        return """
# Deployment Guide

## Docker Deployment

1. Build and run with docker-compose:
```bash
docker-compose up --build
```

2. The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Database: localhost:5432

## Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

## Health Checks

- Backend health: http://localhost:8000/health
- API docs: http://localhost:8000/docs
"""
    
    def _extract_env_vars(self, components: Dict[str, Any], configs: Dict[str, Any]) -> List[str]:
        """提取環境變量"""
        env_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES"
        ]
        return env_vars
    
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
    
    # 模板加載方法
    def _load_react_templates(self) -> Dict[str, str]:
        """加載React模板"""
        return {
            "app_js": "// React App Component\nimport React from 'react';\nimport { BrowserRouter as Router, Routes, Route } from 'react-router-dom';\nimport Header from './components/Header';\nimport Footer from './components/Footer';\nimport Home from './components/Home';\n\nfunction App() {\n  return (\n    <Router>\n      <div className=&quot;min-h-screen flex flex-col&quot;>\n        <Header />\n        <main className=&quot;flex-grow&quot;>\n          <Routes>\n            <Route path=&quot;/&quot; element={<Home />} />\n          </Routes>\n        </main>\n        <Footer />\n      </div>\n    </Router>\n  );\n}\n\nexport default App;",
            "index_js": "// React Entry Point\nimport React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport './styles/index.css';\nimport App from './App';\n\nconst root = ReactDOM.createRoot(document.getElementById('root'));\nroot.render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);"
        }
    
    def _load_fastapi_templates(self) -> Dict[str, str]:
        """加載FastAPI模板"""
        return {
            "main_py": "from fastapi import FastAPI, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom routes import users, auth\nfrom config import settings\n\napp = FastAPI(\n    title=&quot;Generated API&quot;,\n    description=&quot;Auto-generated API&quot;,\n    version=&quot;1.0.0&quot;\n)\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[&quot;*&quot;],\n    allow_credentials=True,\n    allow_methods=[&quot;*&quot;],\n    allow_headers=[&quot;*&quot;],\n)\n\napp.include_router(users.router, prefix=&quot;/api/v1/users&quot;, tags=[&quot;users&quot;])\napp.include_router(auth.router, prefix=&quot;/api/v1/auth&quot;, tags=[&quot;auth&quot;])\n\n@app.get(&quot;/health&quot;)\nasync def health_check():\n    return {&quot;status&quot;: &quot;healthy&quot;}\n\nif __name__ == &quot;__main__&quot;:\n    import uvicorn\n    uvicorn.run(app, host=&quot;0.0.0.0&quot;, port=8000)"
        }
    
    def _load_docker_templates(self) -> Dict[str, str]:
        """加載Docker模板"""
        return {
            "dockerfile": "FROM python:3.11-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nEXPOSE 8000\n\nCMD [&quot;uvicorn&quot;, &quot;main:app&quot;, &quot;--host&quot;, &quot;0.0.0.0&quot;, &quot;--port&quot;, &quot;8000&quot;]"
        }

__all__ = ["CodeGenerationAgent"]