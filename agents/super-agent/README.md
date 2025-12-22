# AAPS SuperAgent

SuperAgent is the central orchestrator in the AAPS Multi-Agent MPC architecture. It coordinates all other agents and manages the incident lifecycle state machine.

## 🎯 Purpose

SuperAgent serves as the **control plane core** in the three-layer agent architecture:
- **Control Plane**: Orchestrates and coordinates all agents
- **Message Routing**: Routes messages between agents
- **State Management**: Manages incident lifecycle state machine
- **Decision Making**: Coordinates multi-agent consensus and voting
- **Audit Trail**: Maintains provenance and audit logs

## 🏗️ Architecture

### Core Responsibilities
```
🤖 SuperAgent (Orchestrator)
├── 📥 Message Reception & Validation
├── 🔄 Message Routing & Distribution  
├── 📊 Incident State Management
├── 🎯 Agent Coordination & Consensus
├── 📝 Audit Trail & Provenance
└── 📡 API Endpoints & Monitoring
```

### Incident Lifecycle State Machine
```
OPEN → TRIAGE → RCA → PROPOSE → VERIFY → APPROVE → EXECUTE → VALIDATE → CLOSE → LEARN
                                     ↓
                               ROLLBACK (on failure)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker
- Kubernetes cluster
- kubectl configured

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Test locally (in another terminal)
python test_super_agent.py
```

### Docker Build & Test
```bash
# Build image
docker build -t axiom-system/super-agent:v1.0.0 .

# Run container
docker run -p 8080:8080 axiom-system/super-agent:v1.0.0

# Test container
python test_super_agent.py http://localhost:8080
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
./deploy.sh

# Or manual deployment
kubectl apply -f deployment.yaml

# Port forward for local testing
kubectl port-forward -n axiom-system svc/super-agent 8080:8080

# Test deployed service
python test_super_agent.py http://localhost:8080
```

## 📡 API Endpoints

### Core Endpoints

#### POST /message
Receive and route messages from other agents.

**Request:**
```json
{
  "meta": {
    "trace_id": "axm-20251221-uuid",
    "source_agent": "monitoring-agent",
    "target_agent": "super-agent", 
    "message_type": "IncidentSignal",
    "schema_version": "v1.0.0"
  },
  "context": {
    "namespace": "axiom-system",
    "cluster": "production",
    "urgency": "P1"
  },
  "payload": {
    "incident_type": "config_validation_failed",
    "severity": "high",
    "affected_resources": ["configmap://app-config"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "trace_id": "axm-20251221-uuid",
  "timestamp": "2025-12-21T16:30:00Z",
  "processing_result": {
    "status": "created",
    "incident_id": "axm-20251221-uuid",
    "state": "TRIAGE"
  }
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-21T16:30:00Z",
  "version": "1.0.0",
  "incidents_count": 3
}
```

#### GET /ready
Readiness check endpoint.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-12-21T16:30:00Z",
  "message_handlers": [
    "IncidentSignal",
    "RCAReport", 
    "FixProposal",
    "VerificationReport",
    "ExecutionResult"
  ]
}
```

#### GET /incidents
List all incidents.

**Response:**
```json
{
  "incidents": [
    {
      "incident_id": "axm-20251221-uuid",
      "trace_id": "axm-20251221-uuid",
      "state": "TRIAGE",
      "incident_type": "config_validation_failed",
      "severity": "high",
      "created_at": "2025-12-21T16:25:00Z",
      "updated_at": "2025-12-21T16:30:00Z",
      "affected_resources": ["configmap://app-config"]
    }
  ],
  "count": 1,
  "timestamp": "2025-12-21T16:30:00Z"
}
```

#### GET /incidents/{incident_id}
Get specific incident details.

#### GET /metrics
Get basic metrics and status.

## 📝 Message Types

### Supported Message Types
- **IncidentSignal**: Incoming incident from monitoring systems
- **RCAReport**: Root cause analysis from ProblemSolverAgent
- **FixProposal**: Proposed fixes from ProblemSolverAgent
- **VerificationReport**: Verification results from QualityAssuranceAgent
- **ExecutionResult**: Execution results from MaintenanceAgent
- **EvidenceBundleRef**: Evidence bundle references
- **KnowledgeArtifactPublished**: Knowledge artifacts from LearningAgent

### Message Envelope Structure
All messages must follow the standard envelope format:
```json
{
  "meta": {
    "trace_id": "axm-YYYYMMDD-UUID",
    "source_agent": "agent-name",
    "target_agent": "super-agent",
    "message_type": "MessageType",
    "schema_version": "v1.0.0"
  },
  "context": {
    "namespace": "axiom-system",
    "cluster": "cluster-name",
    "urgency": "P1|P2|P3"
  },
  "payload": {
    // Message-specific payload
  }
}
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python test_super_agent.py

# Run against specific endpoint
python test_super_agent.py http://localhost:8080

# Run against deployed service
python test_super_agent.py http://super-agent.axiom-system.svc.cluster.local:8080
```

### Test Coverage
- ✅ Health and readiness checks
- ✅ Message envelope validation
- ✅ Incident lifecycle management
- ✅ Message routing and processing
- ✅ Invalid message rejection
- ✅ API endpoint functionality
- ✅ Error handling and recovery

## 🔧 Configuration

### Environment Variables
- `NAMESPACE`: Kubernetes namespace (default: from pod spec)
- `POD_NAME`: Pod name (default: from pod spec)
- `POD_IP`: Pod IP (default: from pod spec)
- `AGENT_TYPE`: Agent type (default: "super-agent")
- `LOG_LEVEL`: Logging level (default: "INFO")
- `TRACE_EXPORTER`: Trace exporter (default: "jaeger")

### Kubernetes Resources
- **ServiceAccount**: `super-agent` with minimal required permissions
- **ClusterRole**: Read permissions + limited write permissions
- **Deployment**: 2 replicas with anti-affinity
- **Service**: ClusterIP service for internal communication
- **HPA**: Horizontal pod autoscaling (2-5 replicas)
- **PDB**: Pod disruption budget (minAvailable: 1)

## 📊 Monitoring

### Prometheus Metrics
The service exposes metrics on port 9090:
```bash
# Access metrics
curl http://localhost:9090/metrics

# Or via service
kubectl port-forward -n axiom-system svc/super-agent 9090:9090
curl http://localhost:9090/metrics
```

### Health Monitoring
```bash
# Health check
curl http://localhost:8080/health

# Readiness check
curl http://localhost:8080/ready

# Detailed status
curl http://localhost:8080/metrics
```

### Log Monitoring
```bash
# View pod logs
kubectl logs -n axiom-system -l app=super-agent -f

# View specific pod logs
kubectl logs -n axiom-system deployment/super-agent -c super-agent -f
```

## 🛡️ Security

### RBAC Permissions
SuperAgent operates with minimal required permissions:
- **Read**: pods, services, configmaps, secrets, deployments, events
- **Write**: limited to coordination resources (incident-trace, execution-plans)
- **No access**: network policies, RBAC changes, PVC deletion

### Security Best Practices
- Runs as non-root user (UID 1000)
- Read-only filesystem (except /tmp and /var/log)
- Health checks and readiness probes
- Pod anti-affinity for high availability
- Resource limits and requests
- Network policies (when available)

## 🔍 Troubleshooting

### Common Issues

#### Service Not Responding
```bash
# Check pod status
kubectl get pods -n axiom-system -l app=super-agent

# Check pod logs
kubectl logs -n axiom-system -l app=super-agent

# Check service endpoints
kubectl get endpoints -n axiom-system super-agent

# Port forward and test
kubectl port-forward -n axiom-system svc/super-agent 8080:8080
curl http://localhost:8080/health
```

#### Permission Issues
```bash
# Check service account permissions
kubectl auth can-i --list --as=system:serviceaccount:axiom-system:super-agent -n axiom-system

# Check cluster role binding
kubectl get clusterrolebinding super-agent-binding -o yaml
```

#### Message Processing Issues
```bash
# Check incident processing
curl http://localhost:8080/incidents

# Send test message
python test_super_agent.py

# Check metrics for errors
curl http://localhost:8080/metrics
```

## 📚 Integration

### Other Agents
SuperAgent integrates with:
- **MonitoringAgent**: Receives incident signals
- **ProblemSolverAgent**: Processes RCA and fix proposals
- **QualityAssuranceAgent**: Handles verification reports
- **MaintenanceAgent**: Receives execution results
- **LearningAgent**: Publishes knowledge artifacts

### External Systems
- **Prometheus**: Metrics and monitoring
- **AlertManager**: Alert routing
- **ArgoCD**: GitOps deployments
- **Jaeger**: Distributed tracing
- **Vault**: Secret management

## 🚀 Next Steps

### Phase 1 Enhancements
- [ ] Add distributed tracing
- [ ] Implement retry mechanisms
- [ ] Add circuit breakers
- [ ] Enhance error handling

### Phase 2 Features
- [ ] Add consensus voting algorithms
- [ ] Implement MPC decision making
- [ ] Add audit logging
- [ ] Enhance security controls

### Phase 3 Capabilities
- [ ] Add machine learning insights
- [ ] Implement predictive analytics
- [ ] Add cross-cluster federation
- [ ] Enhance scalability

---

**SuperAgent is the heart of the AAPS Multi-Agent MPC system, enabling truly intelligent, collaborative problem-solving.**

#machine-native-ops #aaps #multi-agent #super-agent #orchestration