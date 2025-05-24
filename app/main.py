# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db, Base, engine
from app.routes import auth_router, user_router, portfolio_router
from app.routes.feed_router import router as feed_router
from app.routes.prediction_router import router as prediction_router

app = FastAPI(title="Trading LLM App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(portfolio_router.router)
app.include_router(feed_router)
app.include_router(prediction_router)

# On startup: initialize engine/session & create tables
@app.on_event("startup")
def on_startup():
    init_db()

    print("Tables registered:", Base.metadata.tables.keys())

    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to the Trading LLM App!"}
