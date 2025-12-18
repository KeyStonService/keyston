"""
Tests for TaskExecutor
測試任務執行器
"""

import pytest
from agents.task_executor import TaskExecutor


@pytest.fixture
def executor():
    """Create TaskExecutor instance for testing"""
    return TaskExecutor()


def test_executor_initialization(executor):
    """Test TaskExecutor initialization"""
    assert executor is not None
    assert executor.problem_content == ""
    assert executor.editor_code == ""
    assert executor.context_history == []


def test_set_problem_content(executor):
    """Test setting problem content"""
    content = "Test problem description"
    executor.set_problem_content(content)
    assert executor.problem_content == content


def test_set_editor_code(executor):
    """Test setting editor code"""
    code = "def test(): pass"
    executor.set_editor_code(code)
    assert executor.editor_code == code


def test_reset_context(executor):
    """Test context reset"""
    executor.context_history = ["item1", "item2"]
    executor.reset_context()
    assert executor.context_history == []


@pytest.mark.asyncio
async def test_analyze_code_security(executor):
    """Test security analysis"""
    unsafe_code = """
def unsafe_function(user_input):
    result = eval(user_input)
    password = "hardcoded123"
    return result
"""
    
    result = await executor.analyze_code(unsafe_code, "security")
    
    assert result is not None
    assert "issues" in result
    assert len(result["issues"]) > 0
    
    # Check for security issues detected
    security_issues = [i for i in result["issues"] if i["type"] == "security"]
    assert len(security_issues) > 0


@pytest.mark.asyncio
async def test_analyze_code_performance(executor):
    """Test performance analysis"""
    slow_code = """
def slow_function(data):
    for i in range(len(data)):
        for j in range(len(data)):
            for k in range(len(data)):
                process(i, j, k)
"""
    
    result = await executor.analyze_code(slow_code, "performance")
    
    assert result is not None
    assert "issues" in result


@pytest.mark.asyncio
async def test_execute_auto_fix(executor):
    """Test automated fixing"""
    code_with_eval = "result = eval(user_input)"
    
    issue = {
        "type": "security",
        "severity": "critical",
        "automated": True
    }
    
    fixed_code = await executor.execute_auto_fix(code_with_eval, issue)
    
    # Should remove or comment out eval
    assert fixed_code is not None
    assert "REMOVED_eval" in fixed_code or "eval" not in fixed_code


@pytest.mark.asyncio
async def test_stream_analysis(executor):
    """Test streaming analysis"""
    test_code = "def test(): pass"
    
    chunks = []
    async for chunk in executor.stream_analysis(test_code):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    assert chunks[0]["status"] == "started"
    assert chunks[-1]["status"] == "completed"


@pytest.mark.asyncio
async def test_comprehensive_analysis(executor):
    """Test comprehensive analysis"""
    complex_code = """
def complex_function(user_input):
    # Security issue
    result = eval(user_input)
    password = "secret123"
    
    # Performance issue
    for i in range(100):
        for j in range(100):
            for k in range(100):
                process(i, j, k)
    
    return result
"""
    
    result = await executor.analyze_code(complex_code, "comprehensive")
    
    assert result is not None
    assert "issues" in result
    assert "recommendations" in result
    
    # Should detect both security and performance issues
    issue_types = set(issue["type"] for issue in result["issues"])
    assert len(issue_types) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
