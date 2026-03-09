from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import bins
from app.routes.bins import generate_demo_bins

app = FastAPI(title="Smart Waste Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generate demo data on startup
generate_demo_bins()

app.include_router(bins.router)


@app.get("/")
def root():
    return {"message": "Smart Waste Management API is running"}