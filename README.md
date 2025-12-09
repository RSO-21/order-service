# 🛒 Order Service

The Order Service is a microservice responsible for creating and managing customer orders.  
It communicates with the Payment Service to process payments and updates order status accordingly.

---

## ✨ Features
- Create and retrieve orders
- Communicate with Payment Service for payment processing
- Update order status (pending, paid, failed)
- Auto-generated API documentation via FastAPI

---

## 📚 API Documentation
Plain FastAPI docs:

- **Swagger UI:** http://localhost:8002/docs  

---

## ▶️ Running Locally (without Docker)

### 1. Install dependencies
We suggest you create a virtual environment and activate it. Then install dependencies:
```bash
pip install -r requirements.txt
```
### 2. Start the service
```bash
uvicorn app.main:app --reload --port 8002
```

## 🐳 Running with Docker
### 1. Build the image
```bash
docker build -t order-service:latest .
```
### 2. Run the container
```bash
docker run -p 8002:8000 order-service:latest
```
