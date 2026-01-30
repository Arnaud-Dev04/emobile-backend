from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.schemas.favorite import FavoriteResponse, FavoriteWithProduct
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[FavoriteWithProduct])
def get_favorites(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all favorites for current user.
    """
    favorites = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id
    ).all()
    
    result = []
    for fav in favorites:
        product = db.query(models.Product).filter(models.Product.id == fav.product_id).first()
        result.append(FavoriteWithProduct(
            id=fav.id,
            user_id=fav.user_id,
            product_id=fav.product_id,
            created_at=fav.created_at,
            product_title=product.title if product else None,
            product_price=product.price if product else None,
            product_image=product.images[0] if product and product.images else None,
        ))
    
    return result

@router.post("/{product_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a product to favorites.
    """
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already favorited
    existing = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == product_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Product already in favorites")
    
    favorite = models.Favorite(
        user_id=current_user.id,
        product_id=product_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> None:
    """
    Remove a product from favorites.
    """
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == product_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(favorite)
    db.commit()

@router.get("/check/{product_id}")
def check_favorite(
    product_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Check if a product is in favorites.
    """
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == product_id
    ).first()
    
    return {"is_favorite": favorite is not None}
