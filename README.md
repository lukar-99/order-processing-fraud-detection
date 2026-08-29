# Event-Driven Order Processing & Fraud Engine

A high-throughput checkout engine designed to ingest flash-sale traffic spikes without dropping HTTP requests. 

FastAPI accepts incoming orders in milliseconds (`202 Accepted`) and offloads them to **Apache Kafka**. Independent Python consumer workers pull events to execute simulated fraud checks. **KEDA** monitors consumer group lag to scale worker pods from **0 to 10 and back to 0**, while **ArgoCD** manages deployments via GitOps.

---

## Data Flow

```text
[ Client ] ──POST /order──► [ FastAPI Producer ] ──Publish──► [ Kafka ('order-events') ]
                                                                      │
                                                            4. Lag    │ 3. Pull
                                                           Monitor    ▼
[ ArgoCD GitOps ] ────► [ K8s Cluster ] ◄──Scale (0 ↔ 10)── [ KEDA ] ──► [ Python Workers ]
```

1. **FastAPI (Producer):** Ingests orders, pushes `OrderEvent` JSON to Kafka, and returns `202 Accepted` immediately.
2. **Kafka (Queue):** Buffers incoming messages to protect downstream services from traffic spikes.
3. **Python Worker (Consumer):** Asynchronously pulls events and executes fraud/validation checks.
4. **KEDA (Autoscaler):** Scales worker deployment from **0 → 10 pods** during high consumer lag, scaling back to **0 pods** when idle.
5. **ArgoCD (GitOps):** Reconciles Kubernetes cluster state with manifests stored in GitHub.

---

## Tech Stack

* **API & Worker:** Python 3.12, FastAPI, `aiokafka`, Pydantic v2, Poetry
* **Messaging:** Apache Kafka, Kafbat UI
* **Autoscaling & Orchestration:** Kubernetes, KEDA (Kafka ScaledObject)
* **Continuous Delivery:** ArgoCD

---

## Quickstart (Docker Compose)

Run the full local stack (Kafka, Kafka UI, API, and Consumer):

```bash
docker compose up --build
```

* **FastAPI Swagger:** `http://localhost:8000/docs`
* **Kafka UI:** `http://localhost:8080`

---

## GitOps & KEDA Deployment

### 1. Build & Push Docker Images

```bash
docker build -f Dockerfile.api -t <DOCKER_USER>/order-api:v1 .
docker build -f Dockerfile.consumer -t <DOCKER_USER>/order-consumer:v1 .

docker push <DOCKER_USER>/order-api:v1
docker push <DOCKER_USER>/order-consumer:v1
```

### 2. Initialize Kubernetes Cluster & Operators

```bash
minikube start --cpus=4 --memory=8192

# Install KEDA Operator
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace

# Install ArgoCD Controller
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 3. Deploy App via ArgoCD

Commit your K8s manifests (`api-deployment.yaml`, `consumer-deployment.yaml`, `keda-scaledobject.yaml`) to GitHub under `k8s/`, then apply the ArgoCD application:

```bash
kubectl apply -f argocd/application.yaml
```

### 4. Flash Sale Load Test

```bash
# Terminal 1: Watch worker pods auto-scale live (0 -> 10 -> 0)
kubectl get pods -l app=order-consumer -w

# Terminal 2: Send 500 burst requests
for i in {1..500}; do 
  curl -X POST http://localhost:8000/order \
       -H "Content-Type: application/json" \
       -d '{"item_id": 1, "quantity": 1, "price": 10.0}' & 
done
```