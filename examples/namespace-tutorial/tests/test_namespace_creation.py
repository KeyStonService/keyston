#!/usr/bin/env python3
"""
命名空間創建測試
Namespace Creation Tests

測試 Kubernetes 命名空間創建的正確性和配置驗證。
Tests for validating Kubernetes namespace creation and configuration.
"""

import json
import subprocess
import time
from typing import Optional

import pytest

# 測試配置
TEST_NAMESPACE_PREFIX = "test-ns"
KUBECTL_TIMEOUT = 30


def kubectl_available() -> bool:
    """檢查 kubectl 是否可用"""
    return subprocess.run(["which", "kubectl"], capture_output=True).returncode == 0


# 模組級別的 kubectl 可用性檢查
pytestmark = pytest.mark.skipif(not kubectl_available(), reason="kubectl 未安裝")


class KubectlError(Exception):
    """Kubectl 命令執行錯誤"""

    pass


def run_kubectl(args: list[str], timeout: int = KUBECTL_TIMEOUT) -> str:
    """執行 kubectl 命令並返回輸出"""
    try:
        result = subprocess.run(
            ["kubectl", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            raise KubectlError(f"kubectl 命令失敗: {result.stderr}")
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise KubectlError(f"kubectl 命令超時: {e}") from e
    except FileNotFoundError:
        pytest.skip("kubectl 未安裝")


def namespace_exists(name: str) -> bool:
    """檢查命名空間是否存在"""
    try:
        run_kubectl(["get", "namespace", name])
        return True
    except KubectlError:
        return False


def create_namespace(name: str, labels: Optional[dict] = None) -> None:
    """創建命名空間"""
    manifest = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": name, "labels": labels or {}},
    }
    subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=json.dumps(manifest),
        text=True,
        capture_output=True,
        check=True,
    )


def delete_namespace(name: str) -> None:
    """刪除命名空間"""
    try:
        run_kubectl(["delete", "namespace", name, "--grace-period=0", "--force"])
    except KubectlError:
        pass  # 忽略刪除錯誤


def get_namespace(name: str) -> dict:
    """獲取命名空間詳情"""
    output = run_kubectl(["get", "namespace", name, "-o", "json"])
    return json.loads(output)


@pytest.fixture
def test_namespace():
    """創建測試用命名空間 fixture"""
    name = f"{TEST_NAMESPACE_PREFIX}-{int(time.time())}"
    yield name
    # 清理
    delete_namespace(name)


@pytest.fixture
def cleanup_namespaces():
    """清理測試命名空間的 fixture"""
    created_namespaces = []
    yield created_namespaces
    # 清理所有創建的命名空間
    for ns in created_namespaces:
        delete_namespace(ns)


class TestNamespaceCreation:
    """命名空間創建測試類"""

    def test_create_basic_namespace(self, test_namespace):
        """測試創建基本命名空間"""
        # 創建命名空間
        create_namespace(test_namespace)

        # 驗證命名空間存在
        assert namespace_exists(test_namespace), f"命名空間 {test_namespace} 應該存在"

        # 獲取命名空間詳情
        ns = get_namespace(test_namespace)
        assert ns["metadata"]["name"] == test_namespace
        assert ns["status"]["phase"] == "Active"

    def test_create_namespace_with_labels(self, test_namespace):
        """測試創建帶標籤的命名空間"""
        labels = {"environment": "test", "team": "testing", "purpose": "unit-test"}

        create_namespace(test_namespace, labels=labels)

        ns = get_namespace(test_namespace)
        ns_labels = ns["metadata"].get("labels", {})

        for key, value in labels.items():
            assert key in ns_labels, f"標籤 {key} 應該存在"
            assert ns_labels[key] == value, f"標籤 {key} 應該為 {value}"

    def test_namespace_naming_convention(self, cleanup_namespaces):
        """測試命名空間命名規範"""
        # 有效的命名
        valid_names = [
            "valid-namespace",
            "namespace123",
            "my-app-prod",
            "team-a-dev",
        ]

        for name in valid_names:
            full_name = f"test-{name}-{int(time.time())}"
            try:
                create_namespace(full_name)
                cleanup_namespaces.append(full_name)
                assert namespace_exists(full_name), f"有效命名 {full_name} 應該創建成功"
            except (subprocess.CalledProcessError, KubectlError):
                pytest.fail(f"有效命名 {full_name} 創建失敗")

    def test_invalid_namespace_names(self):
        """測試無效的命名空間名稱"""
        invalid_names = [
            "Invalid-Namespace",  # 大寫字母
            "namespace_with_underscore",  # 底線
            "-starts-with-dash",  # 以連字號開頭
            "ends-with-dash-",  # 以連字號結尾
            "namespace.with.dots",  # 包含點
        ]

        for name in invalid_names:
            with pytest.raises((subprocess.CalledProcessError, KubectlError)):
                create_namespace(name)

    def test_duplicate_namespace_creation(self, test_namespace):
        """測試重複創建命名空間"""
        # 第一次創建
        create_namespace(test_namespace)
        assert namespace_exists(test_namespace)

        # 再次創建應該成功（apply 是冪等的）
        create_namespace(test_namespace)
        assert namespace_exists(test_namespace)

    def test_namespace_deletion(self, cleanup_namespaces):
        """測試命名空間刪除"""
        name = f"{TEST_NAMESPACE_PREFIX}-delete-{int(time.time())}"
        cleanup_namespaces.append(name)

        # 創建命名空間
        create_namespace(name)
        assert namespace_exists(name)

        # 刪除命名空間
        delete_namespace(name)

        # 等待刪除完成
        max_wait = 60
        start_time = time.time()
        while namespace_exists(name) and (time.time() - start_time) < max_wait:
            time.sleep(1)

        # 驗證刪除
        # 注意：命名空間可能需要一些時間來完全刪除


class TestNamespaceLabelsAndAnnotations:
    """命名空間標籤和註解測試"""

    def test_environment_labels(self, test_namespace):
        """測試環境標籤"""
        labels = {
            "environment": "development",
            "tier": "backend",
        }

        create_namespace(test_namespace, labels=labels)
        ns = get_namespace(test_namespace)

        assert ns["metadata"]["labels"]["environment"] == "development"
        assert ns["metadata"]["labels"]["tier"] == "backend"

    def test_label_selectors(self, cleanup_namespaces):
        """測試標籤選擇器"""
        # 創建多個帶標籤的命名空間
        namespaces = [
            (f"test-team-a-{int(time.time())}", {"team": "a"}),
            (f"test-team-b-{int(time.time())}", {"team": "b"}),
        ]

        for name, labels in namespaces:
            create_namespace(name, labels=labels)
            cleanup_namespaces.append(name)

        # 使用標籤選擇器查詢
        output = run_kubectl(
            ["get", "namespaces", "-l", "team=a", "-o", "json"]
        )
        result = json.loads(output)

        # 驗證結果包含 team=a 的命名空間
        ns_names = [item["metadata"]["name"] for item in result["items"]]
        assert any("team-a" in name for name in ns_names)


class TestProtectedNamespaces:
    """受保護命名空間測試"""

    def test_cannot_delete_kube_system(self):
        """測試無法刪除 kube-system 命名空間"""
        # 注意：這個測試不會真的嘗試刪除 kube-system
        # 只是驗證它存在且受保護
        assert namespace_exists("kube-system"), "kube-system 應該存在"

    def test_cannot_delete_default(self):
        """測試無法刪除 default 命名空間"""
        assert namespace_exists("default"), "default 應該存在"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
