#!/usr/bin/env python3
"""
資源配額測試
Resource Quota Tests

測試 Kubernetes 資源配額的正確配置和限制功能。
Tests for validating Kubernetes ResourceQuota configuration and enforcement.
"""

import json
import subprocess
import time
from typing import Optional

import pytest

# 測試配置
TEST_NAMESPACE_PREFIX = "test-quota"
KUBECTL_TIMEOUT = 60


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
        run_kubectl(
            ["delete", "namespace", name, "--grace-period=0", "--force", "--wait=false"]
        )
    except KubectlError:
        pass


def apply_manifest(manifest: dict) -> None:
    """應用 Kubernetes 資源配置"""
    subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=json.dumps(manifest),
        text=True,
        capture_output=True,
        check=True,
    )


def get_resource_quotas(namespace: str) -> list:
    """獲取命名空間中的資源配額"""
    output = run_kubectl(["get", "resourcequota", "-n", namespace, "-o", "json"])
    result = json.loads(output)
    return result.get("items", [])


def get_limit_ranges(namespace: str) -> list:
    """獲取命名空間中的限制範圍"""
    output = run_kubectl(["get", "limitrange", "-n", namespace, "-o", "json"])
    result = json.loads(output)
    return result.get("items", [])


@pytest.fixture
def test_namespace():
    """創建測試用命名空間 fixture"""
    name = f"{TEST_NAMESPACE_PREFIX}-{int(time.time())}"
    create_namespace(name, labels={"purpose": "quota-test"})
    yield name
    delete_namespace(name)


class TestResourceQuotaCreation:
    """資源配額創建測試"""

    

    def test_create_compute_resource_quota(self, test_namespace):
        """測試創建計算資源配額"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "compute-quota", "namespace": test_namespace},
            "spec": {
                "hard": {
                    "requests.cpu": "4",
                    "requests.memory": "8Gi",
                    "limits.cpu": "8",
                    "limits.memory": "16Gi",
                }
            },
        }

        apply_manifest(quota)

        quotas = get_resource_quotas(test_namespace)
        assert len(quotas) == 1

        compute_quota = quotas[0]
        assert compute_quota["metadata"]["name"] == "compute-quota"
        assert compute_quota["spec"]["hard"]["requests.cpu"] == "4"
        assert compute_quota["spec"]["hard"]["requests.memory"] == "8Gi"

    

    def test_create_object_count_quota(self, test_namespace):
        """測試創建物件數量配額"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "object-quota", "namespace": test_namespace},
            "spec": {
                "hard": {
                    "pods": "20",
                    "services": "10",
                    "secrets": "20",
                    "configmaps": "20",
                    "persistentvolumeclaims": "10",
                }
            },
        }

        apply_manifest(quota)

        quotas = get_resource_quotas(test_namespace)
        object_quota = next(
            (q for q in quotas if q["metadata"]["name"] == "object-quota"), None
        )

        assert object_quota is not None
        assert object_quota["spec"]["hard"]["pods"] == "20"
        assert object_quota["spec"]["hard"]["services"] == "10"

    

    def test_create_storage_quota(self, test_namespace):
        """測試創建儲存配額"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "storage-quota", "namespace": test_namespace},
            "spec": {
                "hard": {
                    "requests.storage": "100Gi",
                    "persistentvolumeclaims": "10",
                }
            },
        }

        apply_manifest(quota)

        quotas = get_resource_quotas(test_namespace)
        storage_quota = next(
            (q for q in quotas if q["metadata"]["name"] == "storage-quota"), None
        )

        assert storage_quota is not None
        assert storage_quota["spec"]["hard"]["requests.storage"] == "100Gi"


class TestLimitRangeCreation:
    """限制範圍創建測試"""

    

    def test_create_container_limit_range(self, test_namespace):
        """測試創建容器限制範圍"""
        limit_range = {
            "apiVersion": "v1",
            "kind": "LimitRange",
            "metadata": {"name": "container-limits", "namespace": test_namespace},
            "spec": {
                "limits": [
                    {
                        "type": "Container",
                        "default": {"cpu": "500m", "memory": "512Mi"},
                        "defaultRequest": {"cpu": "100m", "memory": "128Mi"},
                        "max": {"cpu": "2", "memory": "4Gi"},
                        "min": {"cpu": "50m", "memory": "64Mi"},
                    }
                ]
            },
        }

        apply_manifest(limit_range)

        limits = get_limit_ranges(test_namespace)
        assert len(limits) == 1

        container_limits = limits[0]
        assert container_limits["metadata"]["name"] == "container-limits"

        limit_spec = container_limits["spec"]["limits"][0]
        assert limit_spec["type"] == "Container"
        assert limit_spec["default"]["cpu"] == "500m"
        assert limit_spec["defaultRequest"]["memory"] == "128Mi"

    

    def test_create_pod_limit_range(self, test_namespace):
        """測試創建 Pod 限制範圍"""
        limit_range = {
            "apiVersion": "v1",
            "kind": "LimitRange",
            "metadata": {"name": "pod-limits", "namespace": test_namespace},
            "spec": {
                "limits": [
                    {
                        "type": "Pod",
                        "max": {"cpu": "4", "memory": "8Gi"},
                        "min": {"cpu": "100m", "memory": "128Mi"},
                    }
                ]
            },
        }

        apply_manifest(limit_range)

        limits = get_limit_ranges(test_namespace)
        pod_limits = next(
            (lr for lr in limits if lr["metadata"]["name"] == "pod-limits"), None
        )

        assert pod_limits is not None
        limit_spec = pod_limits["spec"]["limits"][0]
        assert limit_spec["type"] == "Pod"

    

    def test_create_pvc_limit_range(self, test_namespace):
        """測試創建 PVC 限制範圍"""
        limit_range = {
            "apiVersion": "v1",
            "kind": "LimitRange",
            "metadata": {"name": "pvc-limits", "namespace": test_namespace},
            "spec": {
                "limits": [
                    {
                        "type": "PersistentVolumeClaim",
                        "max": {"storage": "50Gi"},
                        "min": {"storage": "1Gi"},
                    }
                ]
            },
        }

        apply_manifest(limit_range)

        limits = get_limit_ranges(test_namespace)
        pvc_limits = next(
            (lr for lr in limits if lr["metadata"]["name"] == "pvc-limits"), None
        )

        assert pvc_limits is not None


class TestQuotaStatus:
    """配額狀態測試"""

    

    def test_quota_status_shows_usage(self, test_namespace):
        """測試配額狀態顯示使用量"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "test-quota", "namespace": test_namespace},
            "spec": {"hard": {"pods": "10", "services": "5"}},
        }

        apply_manifest(quota)

        # 等待配額狀態更新
        time.sleep(2)

        quotas = get_resource_quotas(test_namespace)
        test_quota = quotas[0]

        # 驗證狀態包含 used 字段
        assert "status" in test_quota
        assert "used" in test_quota["status"]
        assert "hard" in test_quota["status"]

    

    def test_initial_usage_is_zero(self, test_namespace):
        """測試初始使用量為零"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "zero-usage-quota", "namespace": test_namespace},
            "spec": {"hard": {"pods": "10"}},
        }

        apply_manifest(quota)
        time.sleep(2)

        quotas = get_resource_quotas(test_namespace)
        test_quota = quotas[0]

        # 初始狀態下，pods 使用量應該為 0
        used_pods = test_quota.get("status", {}).get("used", {}).get("pods", "0")
        assert used_pods == "0"


class TestQuotaScopes:
    """配額作用域測試"""

    

    def test_best_effort_scope_quota(self, test_namespace):
        """測試 BestEffort 作用域配額"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "best-effort-quota", "namespace": test_namespace},
            "spec": {
                "hard": {"pods": "5"},
                "scopes": ["BestEffort"],
            },
        }

        apply_manifest(quota)

        quotas = get_resource_quotas(test_namespace)
        be_quota = next(
            (q for q in quotas if q["metadata"]["name"] == "best-effort-quota"), None
        )

        assert be_quota is not None
        assert "BestEffort" in be_quota["spec"]["scopes"]

    

    def test_not_best_effort_scope_quota(self, test_namespace):
        """測試 NotBestEffort 作用域配額"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "not-best-effort-quota", "namespace": test_namespace},
            "spec": {
                "hard": {
                    "pods": "10",
                    "requests.cpu": "4",
                    "requests.memory": "8Gi",
                },
                "scopes": ["NotBestEffort"],
            },
        }

        apply_manifest(quota)

        quotas = get_resource_quotas(test_namespace)
        nbe_quota = next(
            (q for q in quotas if q["metadata"]["name"] == "not-best-effort-quota"), None
        )

        assert nbe_quota is not None
        assert "NotBestEffort" in nbe_quota["spec"]["scopes"]


class TestMultipleQuotas:
    """多配額測試"""

    

    def test_multiple_quotas_same_namespace(self, test_namespace):
        """測試同一命名空間多個配額"""
        quotas = [
            {
                "apiVersion": "v1",
                "kind": "ResourceQuota",
                "metadata": {"name": "compute-quota", "namespace": test_namespace},
                "spec": {"hard": {"requests.cpu": "4", "requests.memory": "8Gi"}},
            },
            {
                "apiVersion": "v1",
                "kind": "ResourceQuota",
                "metadata": {"name": "object-quota", "namespace": test_namespace},
                "spec": {"hard": {"pods": "20", "services": "10"}},
            },
            {
                "apiVersion": "v1",
                "kind": "ResourceQuota",
                "metadata": {"name": "storage-quota", "namespace": test_namespace},
                "spec": {"hard": {"requests.storage": "100Gi"}},
            },
        ]

        for quota in quotas:
            apply_manifest(quota)

        result = get_resource_quotas(test_namespace)
        assert len(result) >= 3

        quota_names = [q["metadata"]["name"] for q in result]
        assert "compute-quota" in quota_names
        assert "object-quota" in quota_names
        assert "storage-quota" in quota_names


class TestQuotaValidation:
    """配額驗證測試"""

    

    def test_valid_resource_values(self, test_namespace):
        """測試有效的資源值"""
        quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": "valid-values-quota", "namespace": test_namespace},
            "spec": {
                "hard": {
                    "requests.cpu": "1000m",  # 毫核心
                    "requests.memory": "1Gi",  # GiB
                    "limits.cpu": "2",  # 核心
                    "limits.memory": "2048Mi",  # MiB
                }
            },
        }

        apply_manifest(quota)

        quotas = get_resource_quotas(test_namespace)
        valid_quota = next(
            (q for q in quotas if q["metadata"]["name"] == "valid-values-quota"), None
        )

        assert valid_quota is not None
        assert valid_quota["spec"]["hard"]["requests.cpu"] == "1000m"
        assert valid_quota["spec"]["hard"]["requests.memory"] == "1Gi"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
