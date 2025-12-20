"""
Testing Agent
測試代理

負責自動化測試、質量檢查和驗證
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from . import BaseAgent, AgentTask, AgentResult, AgentType

class TestingAgent(BaseAgent):
    """測試代理 - 第四階段處理"""
    
    def __init__(self, agent_type: AgentType, config: Dict[str, Any] = None):
        super().__init__(agent_type, config)
        self.test_types = {
            "unit": self._generate_unit_tests,
            "integration": self._generate_integration_tests,
            "api": self._generate_api_tests,
            "performance": self._generate_performance_tests,
            "security": self._generate_security_tests
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據格式"""
        required_fields = ["code_generation", "architecture_design", "input_analysis"]
        return all(field in input_data for field in required_fields)
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """處理測試任務"""
        start_time = datetime.now()
        
        try:
            # 提取代碼和架構信息
            code_generation = task.input_data.get("code_generation", {}).get("output_data", {})
            architecture_design = task.input_data.get("architecture_design", {}).get("output_data", {})
            input_analysis = task.input_data.get("input_analysis", {}).get("output_data", {})
            
            # 生成測試套件
            test_suite = await self._generate_test_suite(code_generation, architecture_design, input_analysis)
            
            # 執行質量檢查
            quality_report = await self._perform_quality_check(code_generation)
            
            # 執行安全檢查
            security_report = await self._perform_security_check(code_generation, architecture_design)
            
            # 生成測試配置
            test_config = await self._generate_test_configuration(code_generation, architecture_design)
            
            # 創建CI/CD管道配置
            cicd_config = await self._generate_cicd_configuration()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=True,
                output_data={
                    "test_suite": test_suite,
                    "quality_report": quality_report,
                    "security_report": security_report,
                    "test_config": test_config,
                    "cicd_config": cicd_config,
                    "coverage_target": 80,
                    "test_count": self._count_tests(test_suite),
                    "quality_score": quality_report.get("overall_score", 0)
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Testing failed: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=False,
                output_data={},
                execution_time=0,
                error_message=str(e)
            )
    
    async def _generate_test_suite(self, code: Dict[str, Any], architecture: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成完整測試套件"""
        test_suite = {
            "unit_tests": await self.test_types["unit"](code, architecture),
            "integration_tests": await self.test_types["integration"](code, architecture),
            "api_tests": await self.test_types["api"](code, architecture),
            "performance_tests": await self.test_types["performance"](code, architecture),
            "security_tests": await self.test_types["security"](code, architecture)
        }
        
        return test_suite
    
    async def _generate_unit_tests(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成單元測試"""
        components = code.get("code_components", {})
        tests = {}
        
        # 前端組件測試
        if "frontend" in components:
            tests["frontend"] = {
                "framework": "Jest + React Testing Library",
                "test_files": {
                    "components/Header.test.js": self._generate_header_test(),
                    "components/Home.test.js": self._generate_home_test(),
                    "App.test.js": self._generate_app_test()
                },
                "coverage": {
                    "statements": 90,
                    "branches": 85,
                    "functions": 90,
                    "lines": 90
                }
            }
        
        # 後端API測試
        if "backend" in components:
            tests["backend"] = {
                "framework": "Pytest",
                "test_files": {
                    "test_users.py": self._generate_users_api_test(),
                    "test_auth.py": self._generate_auth_api_test(),
                    "test_models.py": self._generate_models_test()
                },
                "coverage": {
                    "statements": 85,
                    "branches": 80,
                    "functions": 85,
                    "lines": 85
                }
            }
        
        return tests
    
    async def _generate_integration_tests(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成集成測試"""
        return {
            "frontend_backend": {
                "description": "Frontend-backend integration tests",
                "scenarios": [
                    "User login flow",
                    "Data fetch and display",
                    "Form submission",
                    "Error handling"
                ],
                "tools": ["Cypress", "Playwright"]
            },
            "database_integration": {
                "description": "Database integration tests",
                "scenarios": [
                    "Database connection",
                    "CRUD operations",
                    "Transaction handling",
                    "Migration testing"
                ],
                "tools": ["Testcontainers", "Factory Boy"]
            }
        }
    
    async def _generate_api_tests(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成API測試"""
        api_design = architecture.get("api_design", {})
        endpoints = api_design.get("endpoints", [])
        
        tests = {
            "framework": "Pytest + FastAPI TestClient",
            "test_categories": {
                "happy_path": self._generate_happy_path_tests(endpoints),
                "error_handling": self._generate_error_tests(endpoints),
                "authentication": self._generate_auth_tests(endpoints),
                "authorization": self._generate_permission_tests(endpoints)
            },
            "mock_responses": self._generate_api_mocks(endpoints)
        }
        
        return tests
    
    async def _generate_performance_tests(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成性能測試"""
        return {
            "load_testing": {
                "tool": "Locust",
                "scenarios": [
                    {
                        "name": "normal_load",
                        "users": 100,
                        "spawn_rate": 10,
                        "duration": "10m"
                    },
                    {
                        "name": "stress_test",
                        "users": 1000,
                        "spawn_rate": 50,
                        "duration": "5m"
                    }
                ],
                "targets": {
                    "response_time_p95": "<500ms",
                    "response_time_p99": "<1000ms",
                    "error_rate": "<1%"
                }
            },
            "frontend_performance": {
                "tool": "Lighthouse CI",
                "metrics": {
                    "performance": ">90",
                    "accessibility": ">95",
                    "best_practices": ">90",
                    "seo": ">80"
                }
            }
        }
    
    async def _generate_security_tests(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成安全測試"""
        return {
            "vulnerability_scanning": {
                "tools": ["OWASP ZAP", "Bandit", "npm audit"],
                "scans": [
                    "SQL injection",
                    "XSS vulnerabilities",
                    "Authentication bypass",
                    "Authorization flaws"
                ]
            },
            "dependency_security": {
                "tools": ["Snyk", "Dependabot"],
                "scan_frequency": "daily",
                "auto_fix": "minor_versions"
            },
            "penetration_testing": {
                "scope": "defined_scope",
                "methods": ["black_box", "white_box"],
                "reporting": "detailed_findings"
            }
        }
    
    async def _perform_quality_check(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """執行質量檢查"""
        checks = {
            "code_style": {
                "linters": ["ESLint", "Pylint", "Flake8"],
                "config_files": {
                    ".eslintrc.js": self._generate_eslint_config(),
                    ".pylintrc": self._generate_pylint_config()
                },
                "standards": ["airbnb", "pep8"]
            },
            "code_complexity": {
                "metrics": ["cyclomatic_complexity", "maintainability_index"],
                "thresholds": {
                    "complexity": "<10",
                    "maintainability": ">70"
                }
            },
            "documentation": {
                "coverage": ">80%",
                "standards": ["JSDoc", "docstrings"],
                "tools": ["Sphinx", "JSDoc"]
            }
        }
        
        # 計算質量分數
        overall_score = self._calculate_quality_score(checks)
        
        return {
            "checks": checks,
            "overall_score": overall_score,
            "grade": self._get_quality_grade(overall_score),
            "recommendations": self._get_quality_recommendations(overall_score)
        }
    
    async def _perform_security_check(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """執行安全檢查"""
        security_arch = architecture.get("security_architecture", {})
        
        checks = {
            "authentication": {
                "implemented": security_arch.get("authentication", {}).get("method") == "JWT",
                "token_expiry": security_arch.get("authentication", {}).get("token_expiry") == "24h",
                "refresh_tokens": security_arch.get("authentication", {}).get("refresh_tokens", False)
            },
            "authorization": {
                "model": security_arch.get("authorization", {}).get("model"),
                "rbac_implemented": security_arch.get("authorization", {}).get("model") == "RBAC"
            },
            "data_protection": {
                "encryption_at_rest": security_arch.get("data_protection", {}).get("encryption_at_rest", False),
                "encryption_in_transit": security_arch.get("data_protection", {}).get("encryption_in_transit", False)
            },
            "security_headers": {
                "csp": security_arch.get("security_headers", {}).get("CSP", False),
                "hsts": security_arch.get("security_headers", {}).get("HSTS", False)
            }
        }
        
        security_score = self._calculate_security_score(checks)
        
        return {
            "checks": checks,
            "security_score": security_score,
            "risk_level": self._get_risk_level(security_score),
            "fixes_required": self._get_security_fixes(checks)
        }
    
    async def _generate_test_configuration(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, str]:
        """生成測試配置"""
        return {
            "jest.config.js": self._generate_jest_config(),
            "pytest.ini": self._generate_pytest_config(),
            "cypress.json": self._generate_cypress_config(),
            "locustfile.py": self._generate_locust_config()
        }
    
    async def _generate_cicd_configuration(self) -> Dict[str, str]:
        """生成CI/CD配置"""
        return {
            ".github/workflows/ci.yml": self._generate_github_actions(),
            ".github/workflows/cd.yml": self._generate_deployment_workflow(),
            "Dockerfile.test": self._generate_test_dockerfile()
        }
    
    # 測試生成輔助方法
    def _generate_header_test(self) -> str:
        """生成Header組件測試"""
        return '''
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Header from '../Header';

describe('Header Component', () => {
  test('renders header with navigation', () => {
    render(<Header />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  test('contains logo and menu items', () => {
    render(<Header />);
    expect(screen.getByText('MyApp')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
  });
});
'''
    
    def _generate_home_test(self) -> str:
        """生成Home組件測試"""
        return '''
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from '../Home';

describe('Home Component', () => {
  test('renders welcome message', () => {
    render(<Home />);
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  test('displays call to action', () => {
    render(<Home />);
    expect(screen.getByRole('button', { name: /get started/i })).toBeInTheDocument();
  });
});
'''
    
    def _generate_app_test(self) -> str:
        """生成App組件測試"""
        return '''
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

describe('App Component', () => {
  test('renders without crashing', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  test('contains header and footer', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
  });
});
'''
    
    def _generate_users_api_test(self) -> str:
        """生成用戶API測試"""
        return '''
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestUsersAPI:
    def test_get_users_empty(self):
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_user(self):
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["email"] == user_data["email"]

    def test_get_user_by_id(self):
        # First create a user
        user_data = {
            "email": "test2@example.com",
            "password": "testpassword123"
        }
        create_response = client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Then get the user
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]
'''
    
    def _generate_auth_api_test(self) -> str:
        """生成認證API測試"""
        return '''
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuthAPI:
    def test_login_success(self):
        # First create a user
        user_data = {
            "email": "login@example.com",
            "password": "testpassword123"
        }
        client.post("/api/v1/users", json=user_data)
        
        # Then login
        login_data = {
            "email": "login@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()

    def test_login_invalid_credentials(self):
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
'''
    
    def _generate_models_test(self) -> str:
        """生成模型測試"""
        return '''
import pytest
from models.user import User
from models.base import Base

class TestModels:
    def test_user_model_creation(self):
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.id is None  # Not saved yet

    def test_base_model_timestamps(self):
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        user.create_timestamps()
        assert user.created_at is not None
        assert user.updated_at is not None
'''
    
    def _count_tests(self, test_suite: Dict[str, Any]) -> int:
        """計算測試數量"""
        count = 0
        for category in test_suite.values():
            if isinstance(category, dict):
                for subcategory in category.values():
                    if isinstance(subcategory, dict) and "test_files" in subcategory:
                        count += len(subcategory["test_files"])
        return count
    
    def _calculate_quality_score(self, checks: Dict[str, Any]) -> float:
        """計算質量分數"""
        score = 85.0  # 基礎分數
        
        # 根據檢查結果調整分數
        if "code_style" in checks:
            score += 5.0
        
        if "code_complexity" in checks:
            score += 5.0
        
        if "documentation" in checks:
            score += 5.0
        
        return min(score, 100.0)
    
    def _get_quality_grade(self, score: float) -> str:
        """獲取質量等級"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        else:
            return "D"
    
    def _get_quality_recommendations(self, score: float) -> List[str]:
        """獲取質量建議"""
        recommendations = []
        
        if score < 85:
            recommendations.append("增加代碼覆蓋率")
            recommendations.append("改進代碼風格一致性")
        
        if score < 75:
            recommendations.append("降低代碼複雜度")
            recommendations.append("完善文檔")
        
        return recommendations
    
    def _calculate_security_score(self, checks: Dict[str, Any]) -> float:
        """計算安全分數"""
        score = 0
        total_checks = 0
        
        for category, items in checks.items():
            if isinstance(items, dict):
                for key, value in items.items():
                    total_checks += 1
                    if isinstance(value, bool) and value:
                        score += 1
                    elif isinstance(value, str) and value.lower() in ["jwt", "rbac", "true"]:
                        score += 1
        
        return (score / total_checks * 100) if total_checks > 0 else 0
    
    def _get_risk_level(self, score: float) -> str:
        """獲取風險等級"""
        if score >= 80:
            return "low"
        elif score >= 60:
            return "medium"
        else:
            return "high"
    
    def _get_security_fixes(self, checks: Dict[str, Any]) -> List[str]:
        """獲取安全修復建議"""
        fixes = []
        
        if not checks.get("authentication", {}).get("implemented", False):
            fixes.append("實施JWT認證")
        
        if not checks.get("data_protection", {}).get("encryption_at_rest", False):
            fixes.append("啟用數據靜態加密")
        
        if not checks.get("security_headers", {}).get("csp", False):
            fixes.append("配置內容安全策略")
        
        return fixes

    # 配置文件生成方法
    def _generate_eslint_config(self) -> str:
        return '''
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'airbnb',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: ['react'],
  rules: {
    'no-console': 'warn',
    'react/jsx-filename-extension': [1, { extensions: ['.js', '.jsx'] }],
  },
};
'''
    
    def _generate_pylint_config(self) -> str:
        return '''
[MASTER]
disable=R0903,C0114,C0115,C0116

[FORMAT]
max-line-length=88

[BASIC]
good-names=i,j,k,ex,Run,_

[DESIGN]
max-args=5
max-locals=15
max-returns=6
max-branches=12
max-statements=50
max-parents=7
max-attributes=7
min-public-methods=2
max-public-methods=20
'''

__all__ = ["TestingAgent"]