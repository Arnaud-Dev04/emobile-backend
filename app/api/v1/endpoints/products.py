from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Product])
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search in title and description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    sort_by: Optional[str] = Query(None, description="Sort: price_asc, price_desc, newest, popular"),
) -> Any:
    """
    Retrieve products with optional search and filters.
    """
    query = db.query(models.Product)
    
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Product.title.ilike(search_term),
                models.Product.description.ilike(search_term)
            )
        )
    
    # Price filters
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    
    # Category filter
    if category:
        query = query.filter(models.Product.category == category)
    
    # Sorting
    if sort_by == "price_asc":
        query = query.order_by(models.Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(models.Product.price.desc())
    elif sort_by == "newest":
        query = query.order_by(models.Product.created_at.desc())
    elif sort_by == "popular":
        # Could be based on order count or views
        query = query.order_by(models.Product.id.desc())
    else:
        query = query.order_by(models.Product.created_at.desc())
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=schemas.Product)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    product_in: schemas.ProductCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new product.
    """
    if not current_user.is_vendor:
        raise HTTPException(
            status_code=400,
            detail="Only vendors can create products.",
        )
    
    db_product = models.Product(
        **product_in.model_dump(),
        seller_id=current_user.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: int,
) -> Any:
    """
    Get product by ID.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    *,
    db: Session = Depends(deps.get_db),
    product_id: int,
    product_in: schemas.ProductUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a product.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Permission check: Superuser or Owner
    if not current_user.is_superuser and (product.seller_id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to edit this product",
        )
        
    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
        
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
