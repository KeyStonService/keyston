#!/usr/bin/env python3
"""
網路策略測試
Network Policy Tests

測試 Kubernetes 網路策略的有效性和配置驗證。
Tests for validating Kubernetes NetworkPolicy effectiveness and configuration.
"""

import json
import subprocess
import time
from typing import Optional

import pytest

# 測試配置
TEST_NAMESPACE_PREFIX = "test-netpol"
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


def get_network_policies(namespace: str) -> list:
    """獲取命名空間中的網路策略"""
    output = run_kubectl(["get", "networkpolicy", "-n", namespace, "-o", "json"])
    result = json.loads(output)
    return result.get("items", [])


def create_test_pod(namespace: str, name: str, labels: Optional[dict] = None) -> None:
    """創建測試 Pod"""
    manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": name, "namespace": namespace, "labels": labels or {}},
        "spec": {
            "containers": [
                {
                    "name": "test",
                    "image": "busybox:latest",
                    "command": ["sleep", "3600"],
                }
            ]
        },
    }
    apply_manifest(manifest)


@pytest.fixture
def test_namespace():
    """創建測試用命名空間 fixture"""
    name = f"{TEST_NAMESPACE_PREFIX}-{int(time.time())}"
    create_namespace(name, labels={"purpose": "network-policy-test"})
    yield name
    delete_namespace(name)


@pytest.fixture
def two_namespaces():
    """創建兩個測試用命名空間 fixture"""
    timestamp = int(time.time())
    ns1 = f"{TEST_NAMESPACE_PREFIX}-source-{timestamp}"
    ns2 = f"{TEST_NAMESPACE_PREFIX}-target-{timestamp}"

    create_namespace(ns1, labels={"role": "source"})
    create_namespace(ns2, labels={"role": "target"})

    yield ns1, ns2

    delete_namespace(ns1)
    delete_namespace(ns2)


class TestNetworkPolicyCreation:
    """網路策略創建測試"""

    

    def test_create_deny_all_ingress_policy(self, test_namespace):
        """測試創建拒絕所有入站流量的策略"""
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "deny-all-ingress", "namespace": test_namespace},
            "spec": {"podSelector": {}, "policyTypes": ["Ingress"], "ingress": []},
        }

        apply_manifest(policy)

        # 驗證策略已創建
        policies = get_network_policies(test_namespace)
        assert len(policies) == 1
        assert policies[0]["metadata"]["name"] == "deny-all-ingress"
        assert policies[0]["spec"]["policyTypes"] == ["Ingress"]

    

    def test_create_deny_all_egress_policy(self, test_namespace):
        """測試創建拒絕所有出站流量的策略"""
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "deny-all-egress", "namespace": test_namespace},
            "spec": {"podSelector": {}, "policyTypes": ["Egress"], "egress": []},
        }

        apply_manifest(policy)

        policies = get_network_policies(test_namespace)
        policy_names = [p["metadata"]["name"] for p in policies]
        assert "deny-all-egress" in policy_names

    

    def test_create_allow_same_namespace_policy(self, test_namespace):
        """測試創建允許同命名空間通訊的策略"""
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "allow-same-namespace",
                "namespace": test_namespace,
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "kubernetes.io/metadata.name": test_namespace
                                    }
                                }
                            }
                        ]
                    }
                ],
            },
        }

        apply_manifest(policy)

        policies = get_network_policies(test_namespace)
        assert any(p["metadata"]["name"] == "allow-same-namespace" for p in policies)


class TestNetworkPolicyRules:
    """網路策略規則測試"""

    

    def test_pod_selector_policy(self, test_namespace):
        """測試 Pod 選擇器策略"""
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "backend-policy", "namespace": test_namespace},
            "spec": {
                "podSelector": {"matchLabels": {"app": "backend"}},
                "policyTypes": ["Ingress"],
                "ingress": [
                    {
                        "from": [{"podSelector": {"matchLabels": {"app": "frontend"}}}],
                        "ports": [{"protocol": "TCP", "port": 8080}],
                    }
                ],
            },
        }

        apply_manifest(policy)

        policies = get_network_policies(test_namespace)
        backend_policy = next(
            (p for p in policies if p["metadata"]["name"] == "backend-policy"), None
        )

        assert backend_policy is not None
        assert backend_policy["spec"]["podSelector"]["matchLabels"]["app"] == "backend"
        assert backend_policy["spec"]["ingress"][0]["ports"][0]["port"] == 8080

    

    def test_namespace_selector_policy(self, two_namespaces):
        """測試命名空間選擇器策略"""
        source_ns, target_ns = two_namespaces

        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "allow-from-source", "namespace": target_ns},
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress"],
                "ingress": [
                    {
                        "from": [
                            {"namespaceSelector": {"matchLabels": {"role": "source"}}}
                        ]
                    }
                ],
            },
        }

        apply_manifest(policy)

        policies = get_network_policies(target_ns)
        assert len(policies) >= 1

        allow_policy = next(
            (p for p in policies if p["metadata"]["name"] == "allow-from-source"), None
        )
        assert allow_policy is not None

    

    def test_port_specific_policy(self, test_namespace):
        """測試端口特定策略"""
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "allow-http-https", "namespace": test_namespace},
            "spec": {
                "podSelector": {"matchLabels": {"app": "web"}},
                "policyTypes": ["Ingress"],
                "ingress": [
                    {
                        "ports": [
                            {"protocol": "TCP", "port": 80},
                            {"protocol": "TCP", "port": 443},
                        ]
                    }
                ],
            },
        }

        apply_manifest(policy)

        policies = get_network_policies(test_namespace)
        http_policy = next(
            (p for p in policies if p["metadata"]["name"] == "allow-http-https"), None
        )

        assert http_policy is not None
        ports = http_policy["spec"]["ingress"][0]["ports"]
        assert any(p["port"] == 80 for p in ports)
        assert any(p["port"] == 443 for p in ports)


class TestNetworkPolicyValidation:
    """網路策略驗證測試"""

    

    def test_policy_with_cidr_block(self, test_namespace):
        """測試 CIDR 區塊策略"""
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "allow-external", "namespace": test_namespace},
            "spec": {
                "podSelector": {},
                "policyTypes": ["Egress"],
                "egress": [
                    {
                        "to": [{"ipBlock": {"cidr": "10.0.0.0/8", "except": ["10.0.0.0/24"]}}],
                        "ports": [{"protocol": "TCP", "port": 443}],
                    }
                ],
            },
        }

        apply_manifest(policy)

        policies = get_network_policies(test_namespace)
        cidr_policy = next(
            (p for p in policies if p["metadata"]["name"] == "allow-external"), None
        )

        assert cidr_policy is not None
        ip_block = cidr_policy["spec"]["egress"][0]["to"][0]["ipBlock"]
        assert ip_block["cidr"] == "10.0.0.0/8"
        assert "10.0.0.0/24" in ip_block["except"]

    

    def test_multiple_policies_same_namespace(self, test_namespace):
        """測試同一命名空間多個策略"""
        policies = [
            {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {"name": f"policy-{i}", "namespace": test_namespace},
                "spec": {
                    "podSelector": {"matchLabels": {"policy": str(i)}},
                    "policyTypes": ["Ingress"],
                    "ingress": [],
                },
            }
            for i in range(3)
        ]

        for policy in policies:
            apply_manifest(policy)

        result = get_network_policies(test_namespace)
        assert len(result) >= 3


class TestDNSPolicy:
    """DNS 策略測試"""

    

    def test_allow_dns_egress(self, test_namespace):
        """測試允許 DNS 出站流量"""
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "allow-dns", "namespace": test_namespace},
            "spec": {
                "podSelector": {},
                "policyTypes": ["Egress"],
                "egress": [
                    {
                        "to": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "kubernetes.io/metadata.name": "kube-system"
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 53},
                        ],
                    }
                ],
            },
        }

        apply_manifest(policy)

        policies = get_network_policies(test_namespace)
        dns_policy = next(
            (p for p in policies if p["metadata"]["name"] == "allow-dns"), None
        )

        assert dns_policy is not None
        egress_ports = dns_policy["spec"]["egress"][0]["ports"]
        assert any(p["port"] == 53 and p["protocol"] == "UDP" for p in egress_ports)
        assert any(p["port"] == 53 and p["protocol"] == "TCP" for p in egress_ports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
