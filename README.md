# 🧾 Receipt Intelligence System — MLOps Pipeline

### BTech Final Year Major Project | Naman Sharma | Shobhit Deemed to be University, Meerut

---

## 📌 Overview

A production-ready **MLOps pipeline** built around an OCR-based receipt parsing engine. The system accepts receipt images, preprocesses them using OpenCV, extracts text via Tesseract OCR, parses structured fields (store name, date, items, total) using regular expressions, and returns confidence-annotated JSON output through a REST API.

Beyond the core ML functionality, the project implements a complete DevOps lifecycle — containerized with Docker, monitored with Prometheus and Grafana, deployed to AWS EC2 via Terraform IaC, and continuously delivered through GitHub Actions CI/CD.

---

## 🏗️ Architecture

```
Receipt Image (Upload via Frontend)
        │
        ▼
  FastAPI REST API  (/process)
        │
   ┌────┴────┐
   │OCR Engine│   ← Tesseract + OpenCV
   └────┬────┘
        │  Structured JSON
        ▼
  Docker Container
        │
  GitHub Actions CI/CD
        │
  AWS ECR (Docker Registry)
        │
  AWS EC2 (Terraform provisioned)
        │
  Prometheus + Grafana (Monitoring)
```

---

## 📁 Project Structure

```
receipt-mlops/
├── app/
│   └── api.py                  # FastAPI REST API
├── preprocessing.py            # OpenCV image preprocessing
├── ocr_eng.py                  # Tesseract OCR engine
├── extraction.py               # Regex field extraction
├── confidence.py               # Confidence scoring
├── utils.py                    # JSON utilities
├── summary.py                  # Batch analytics
├── main.py                     # CLI script (local run)
├── index.html                  # Frontend UI
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # API + Prometheus + Grafana
├── requirements.txt            # Python dependencies
├── terraform/
│   └── main.tf                 # AWS EC2 + Security Group + EIP
├── monitoring/
│   └── prometheus.yml          # Prometheus scrape config
└── .github/
    └── workflows/
        └── ci-cd.yml           # GitHub Actions CI/CD pipeline
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| ML / OCR | Tesseract, OpenCV, Python Regex |
| API | FastAPI, Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions, AWS ECR |
| Infrastructure | Terraform, AWS EC2 |
| Monitoring | Prometheus, Grafana |

---

## 🚀 Quick Start

### Option 1 — Run Locally (Python)

```bash
# Clone the repo
git clone https://github.com/namansharma-eng/receipt-mlops.git
cd receipt-mlops

# Install Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.api:app --reload

# Open browser
http://localhost:8000/ui       ← Frontend
http://localhost:8000/docs     ← Swagger API Docs
```

### Option 2 — Run with Docker

```bash
# Build and start all services
docker compose up --build

# Access
http://localhost:8000/ui       ← Frontend
http://localhost:8000/docs     ← API Docs
http://localhost:9090          ← Prometheus
http://localhost:3000          ← Grafana (admin / admin123)
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Root check |
| `/health` | GET | Liveness probe |
| `/ui` | GET | Frontend UI |
| `/process` | POST | Process single receipt image |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | Swagger UI |

### Example Request

```bash
curl -X POST http://localhost:8000/process \
  -F "file=@receipt.jpg"
```

### Example Response

```json
{
  "status": "success",
  "filename": "receipt.jpg",
  "data": {
    "store_name": { "value": "WAL-MART", "confidence": 0.91 },
    "date":       { "value": "10/20/07", "confidence": 0.88 },
    "total_amount":{ "value": "18.75",   "confidence": 0.95 },
    "items": [
      { "name": "MILK", "price": "3.49" }
    ]
  }
}
```

---

## ☁️ AWS Deployment (Terraform)

```bash
# Install Terraform & AWS CLI first
cd terraform

# Initialize
terraform init

# Preview
terraform plan -var="key_pair_name=receipt-key"

# Deploy
terraform apply -var="key_pair_name=receipt-key"
```

**Terraform creates:**
- EC2 t3.micro instance (Ubuntu 24.04)
- Security Group (ports 22, 8000, 3000, 9090)
- Elastic IP (static public IP)
- Auto installs Docker + clones repo + starts services

**Outputs:**
```
api_url     = "http://XX.XX.XX.XX:8000"
grafana_url = "http://XX.XX.XX.XX:3000"
ssh_command = "ssh -i ~/.ssh/receipt-key.pem ubuntu@XX.XX.XX.XX"
```

---

## 🔄 CI/CD — GitHub Actions

Every push to `main` branch triggers:

```
1. Test    → Install dependencies, run checks
2. Build   → Docker image build → push to AWS ECR
3. Deploy  → SSH to EC2 → docker compose up
```

**Required GitHub Secrets:**

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS Access Key |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key |
| `EC2_HOST` | EC2 Public IP |
| `EC2_SSH_KEY` | Contents of .pem file |

---

## 📊 Monitoring

| URL | Service |
|---|---|
| `http://EC2-IP:9090` | Prometheus |
| `http://EC2-IP:3000` | Grafana (admin/admin123) |

**Metrics Tracked:**

| Metric | Description |
|---|---|
| `receipt_requests_total` | Total API requests |
| `receipt_success_total` | Successful extractions |
| `receipt_failure_total` | Failed extractions |
| `receipt_latency_seconds` | Processing time |
| `receipt_confidence_score` | OCR confidence scores |

---

## 👨‍💻 Author

**Naman Sharma**
B.Tech Computer Science & Engineering
Shobhit Deemed to be University, Meerut, UP
📧 namangd456@gmail.com
🔗 [GitHub](https://github.com/namansharma-eng)