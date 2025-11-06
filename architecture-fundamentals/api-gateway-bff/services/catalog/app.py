from fastapi import FastAPI
app = FastAPI(title="Domain Service: Catalog")

CATALOG = [
    {"sku": "SKU-1", "name": "Widget", "price": 9.99},
    {"sku": "SKU-2", "name": "Gizmo", "price": 14.50},
]

@app.get("/catalog")
def get_catalog():
    return {"items": CATALOG, "service": "catalog"}
