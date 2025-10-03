# AgentFabric — *weave agents, services, and policy into one stack*

AgentFabric is a modular, cloud-native framework for building **agentic applications** that talk to **domain services** (Orders, Payments, Inventory, Notifications), run in **Kubernetes** (The Kubernetes Authors, n.d.), and are governed by **policy** via **OPA/Rego** (Open Policy Agent, n.d.). It couples **observability** with **OpenTelemetry** (OpenTelemetry Authors, n.d.), an optional **service mesh** such as **Istio** (Istio Authors, n.d.), and a **queue + ETL** lane using **NATS** (Synadia Communications, n.d.). It can expose tools/resources to agents through the **Model Context Protocol (MCP)** (OpenAI, n.d.).

> **Why**: Most agent apps need more than a model—they need **routing, guardrails, approvals, audit, and service contracts**. AgentFabric supplies the fabric.

---

## Highlights
- **Agent layer**: Orchestrator + Reasoning Engine (LLM/SLM), Memory, and Policy checks with OPA (Open Policy Agent, n.d.).
- **Service layer**: REST microservices for Orders, Payments, Inventory, Notifications.
- **Platform layer**: Kubernetes (The Kubernetes Authors, n.d.), Service Mesh e.g., Istio (Istio Authors, n.d.), NATS queue (Synadia Communications, n.d.), Storage, Observability with OpenTelemetry (OpenTelemetry Authors, n.d.).
- **Governance**: Externalized decisions (PDP), obligations such as PII redaction, audit trails (Open Policy Agent, n.d.; OpenTelemetry Authors, n.d.).
- **MCP**: Optional Model Context Protocol server to expose tools/resources to agents (OpenAI, n.d.).

---

## Quick start (Docker Compose)
```bash
# From the repo root
docker compose up -d --build
# Or bring up OPA first:
docker compose up -d opa
```

**Health checks**
- OPA (PowerShell): `curl.exe "http://localhost:8181/health?plugins&bundles"`  
- OPA (CMD): `curl http://localhost:8181/health?plugins^&bundles`

---

## Architecture (System Overview)

```mermaid
flowchart LR
  subgraph A["Agent Layer — Plan · Act · Learn"]
    U["User / Client"]
    ORCH["Orchestrator Agent"]
    LLM["Reasoning Engine (LLM / SLM)"]
    MEM["Memory"]
    POL["Policy Client"]
  end

  subgraph S["Services"]
    ODR["Orders API"]
    PAY["Payments API"]
    INV["Inventory API"]
    NOTI["Notifications API"]
    ETL["Data Service ETL"]
  end

  subgraph P["Platform"]
    MESH["Service Mesh Istio"]
    Q["Queue NATS"]
    OBS["Observability OTel"]
    K8S["Kubernetes"]
    STO["Storage"]
    OPA["OPA PDP"]
  end

  %% Agent edges
  U --> ORCH
  ORCH --> LLM
  ORCH --> MEM
  ORCH --> POL
  POL --> OPA

  %% Service mesh fanout
  ORCH --> MESH
  MESH --> ODR
  MESH --> PAY
  MESH --> INV
  MESH --> NOTI

  %% Queue / ETL
  ORCH --> Q
  Q --> ETL

  %% Storage
  ODR --> STO
  PAY --> STO
  INV --> STO
  ETL --> STO

  %% Telemetry
  ODR -.-> OBS
  PAY -.-> OBS
  INV -.-> OBS
  NOTI -.-> OBS
  ETL -.-> OBS
  ORCH -.-> OBS
  MESH -.-> OBS

  %% Infra ties
  MESH --- K8S
  ODR --- K8S
  PAY --- K8S
  INV --- K8S
  NOTI --- K8S
  ETL --- K8S
  ORCH --- K8S
  OPA --- K8S

  %% Styling
  classDef agent fill:#e8f1ff,stroke:#1b66ff,color:#0b2e6e
  classDef think fill:#fff2cc,stroke:#e6a100,color:#4a3b00
  classDef policy fill:#fde2e2,stroke:#e63b3b,color:#5a0c0c
  classDef svc fill:#eaffea,stroke:#16a34a,color:#064b23
  classDef mesh fill:#e6fcff,stroke:#06b6d4,color:#034752
  classDef queue fill:#f1e8ff,stroke:#7c3aed,color:#2d0d5a
  classDef store fill:#fff0e6,stroke:#fb923c,color:#5a2c00
  classDef obs fill:#f5f3ff,stroke:#6366f1,color:#1f1b6b
  classDef k8s fill:#eef2ff,stroke:#3b82f6,color:#0b255c

  class U,ORCH agent
  class LLM,MEM think
  class POL policy
  class ODR,PAY,INV,NOTI,ETL svc
  class MESH mesh
  class Q queue
  class OBS obs
  class K8S k8s
  class STO store
```

---

## Governance & Policy (OPA/Rego)

```mermaid
flowchart LR
  subgraph Request
    RQ["Action Request: tool + args + actor + context"]
  end

  RQ --> PDPC["Policy Client"]
  PDPC --> OPA["OPA PDP"]
  OPA -->|allow or deny with obligations| PDPC
  PDPC -->|enforce obligations eg redact| EXEC["Executor or Router"]
  EXEC --> SVC["Domain Service"]
  SVC --> AUD["Audit and OTel spans"]

  classDef policy fill:#fde2e2,stroke:#e63b3b,color:#5a0c0c
  classDef svc fill:#eaffea,stroke:#16a34a,color:#064b23
  classDef obs fill:#f5f3ff,stroke:#6366f1,color:#1f1b6b

  class PDPC,OPA policy
  class SVC,AUD obs
```

**Example policy (`policy/policy.rego`)**
```rego
package agent

default allow = false

# Simple allow for smoke tests
allow {
  input.tool == "ping"
}

# Example: payments guard
deny[msg] {
  input.tool == "charge_payment"
  input.args.amount > 1000
  msg := "amount exceeds limit; approval required"
}

requires_approval {
  input.tool == "charge_payment"
  input.args.amount > 1000
}
```

The orchestrator queries: `POST /v1/data/agent/allow` and can also read auxiliary data (e.g., `requires_approval`) (Open Policy Agent, n.d.).

---

## Orchestration Sequence

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant A as Orchestrator
  participant P as OPA PDP
  participant R as Reasoning LLM or SLM
  participant S as Service API
  participant Q as NATS Queue
  participant O as Observability

  U->>A: POST /act (goal, tool, args)
  A->>P: policy input (tool, args, actor, context)
  alt allowed
    P-->>A: allow true, obligations
    A->>R: plan or transform
    A->>S: call service with obligations
    S-->>A: result
  else approval required
    P-->>A: allow false, requires approval
    A-->>U: 202 Accepted (pending)
  end
  A->>Q: publish ETL job optional
  A-->>U: response
  A-)+O: OTel spans and logs
```

---

## Deployment Topology (K8s)

```mermaid
flowchart TB
  subgraph "Kubernetes Cluster"
    subgraph "Namespace: agentfabric"
      subgraph Control
        OPA["OPA Deployment"]
        OTL["OTel Collector"]
      end
      subgraph Apps
        ORCH["Orchestrator Deployment"]
        ODR["Orders"]
        PAY["Payments"]
        INV["Inventory"]
        NOTI["Notifications"]
        ETL["Data Service"]
      end
      Q["NATS"]
      PVC["PersistentVolumeClaim data"]
    end
  end

  ORCH --> OPA
  ORCH --> OTL
  ODR --> OTL
  PAY --> OTL
  INV --> OTL
  NOTI --> OTL
  ETL --> OTL
  ETL --> PVC
```

---

## Configuration

- **OPA endpoint**: `OPA_URL=http://opa:8181/v1/data/agent/allow`  
- **OTel**: `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318`  
- **Service URLs**: `ORDERS_URL`, `PAYMENTS_URL`, `INVENTORY_URL`, `NOTIFY_URL`  
- **Queue**: `NATS_URL=nats://nats:4222`

**Compose OPA snippet**
```yaml
opa:
  image: openpolicyagent/opa:0.67.0
  command: ["run","--server","--addr=:8181","/policy"]
  volumes:
    - ./policy:/policy:ro
  ports:
    - "8181:8181"
```

---

## References (APA)

- Istio Authors. (n.d.). *Istio documentation*. https://istio.io/latest/docs/
- OpenAI. (n.d.). *Model Context Protocol (MCP)*. https://github.com/modelcontextprotocol
- Open Policy Agent. (n.d.). *OPA documentation*. https://www.openpolicyagent.org/docs/latest/
- OpenTelemetry Authors. (n.d.). *OpenTelemetry documentation*. https://opentelemetry.io/docs/
- Synadia Communications, Inc. (n.d.). *NATS documentation*. https://docs.nats.io/
- The Kubernetes Authors. (n.d.). *Kubernetes documentation*. https://kubernetes.io/docs/

---

## Author
**Freeman Augustus Jackson** — Maintainer & original author.  
Issues and contributions welcome at https://github.com/4th/AgenticFabric

## License
Apache-2.0
