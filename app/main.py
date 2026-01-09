from fastapi import FastAPI, Depends
from app.routes import router as orders_router
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db_session, engine, Base
from prometheus_fastapi_instrumentator import Instrumentator
from app.grpc.orders_server import serve_grpc
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Microservice", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(orders_router, prefix="/orders")

# Expose /metrics compatible with Prometheus scraping
Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health_check(db: Session = Depends(get_db_session)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return {"status": "error", "db": "error", "detail": str(e)}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Orders Microservice"}

grpc_server = None

@app.on_event("startup")
def start_grpc_server():
    global grpc_server
    grpc_server = serve_grpc(host="0.0.0.0", port=50051)

@app.on_event("shutdown")
def stop_grpc_server():
    global grpc_server
    if grpc_server:
        grpc_server.stop(0)