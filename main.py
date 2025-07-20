from fastapi import FastAPI
from .routers import products, orders



app = FastAPI(
    title="E-commerce API",
    version="1.0.0",
    docs_url="/docs",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application. See /docs for documentation."}

app.include_router(products.router)
app.include_router(orders.router)
