"""
Example FastAPI application for testing FastDEV
"""

from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Example API", version="1.0.0")


class Item(BaseModel):
    id: int
    name: str
    description: str = None
    price: float
    tax: float = 0.1


# In-memory database
items_db: List[Item] = []


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Example API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "items_count": len(items_db)}


@app.post("/items/", response_model=Item)
def create_item(item: Item):
    """Create a new item"""
    items_db.append(item)
    return item


@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 10):
    """Get all items with pagination"""
    return items_db[skip : skip + limit]


@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    """Update an existing item"""
    for idx, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            items_db[idx] = item
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """Delete an item"""
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            del items_db[idx]
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
