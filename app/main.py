from fastapi import FastAPI
from app.database import engine, Base
# import models so they are registered with SQLAlchemy metadata
from app.models import contact  # noqa: F401  (import for side effects)
from app.routers import identify

# create tables defined by models before the application starts
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(identify.router)