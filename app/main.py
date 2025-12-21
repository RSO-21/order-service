from fastapi import FastAPI, Depends
from app.routes import router as orders_router
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db_session, engine, Base
from prometheus_fastapi_instrumentator import Instrumentator

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Microservice", version="1.0.0")
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