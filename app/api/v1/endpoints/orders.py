from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas
from app.api import deps
from app.models.order import OrderStatus

router = APIRouter()

@router.post("/", response_model=schemas.Order)
def create_order(
    *,
    db: Session = Depends(deps.get_db),
    order_in: schemas.OrderCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new order.
    """
    # Get product
    product = db.query(models.Product).filter(models.Product.id == order_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user is trying to buy their own product
    if product.seller_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot buy your own product",
        )
    
    # Calculate total price
    total_price = product.price * order_in.quantity
    
    # Create order
    db_order = models.Order(
        buyer_id=current_user.id,
        seller_id=product.seller_id,
        product_id=order_in.product_id,
        quantity=order_in.quantity,
        total_price=total_price,
        shipping_address=order_in.shipping_address,
        status=OrderStatus.CREATED,
        payment_method=order_in.payment_method,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[schemas.Order])
def read_orders(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve orders for current user (as buyer or seller).
    """
    orders = db.query(models.Order).filter(
        (models.Order.buyer_id == current_user.id) | 
        (models.Order.seller_id == current_user.id)
    ).offset(skip).limit(limit).all()
    return orders

@router.get("/purchases", response_model=List[schemas.Order])
def read_purchases(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve orders where current user is the buyer.
    """
    orders = db.query(models.Order).filter(
        models.Order.buyer_id == current_user.id
    ).offset(skip).limit(limit).all()
    return orders

@router.get("/sales", response_model=List[schemas.Order])
def read_sales(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve orders where current user is the seller.
    """
    orders = db.query(models.Order).filter(
        models.Order.seller_id == current_user.id
    ).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get order by ID.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user is buyer or seller
    if order.buyer_id != current_user.id and order.seller_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this order",
        )
    
    return order

@router.put("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update order status (state machine).
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions based on status transition
    new_status = status_update.status
    
    # Validate state transitions
    if new_status == OrderStatus.PAID_ESCROW:
        # Only buyer can mark as paid (or webhook/admin)
        if order.buyer_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only buyer can confirm payment")
        if order.status != OrderStatus.CREATED:
            raise HTTPException(status_code=400, detail="Can only pay for created orders")
        order.paid_at = datetime.utcnow()
        if status_update.transaction_hash:
            order.transaction_hash = status_update.transaction_hash
    
    elif new_status == OrderStatus.SHIPPED:
        # Only seller can mark as shipped
        if order.seller_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only seller can mark as shipped")
        if order.status != OrderStatus.PAID_ESCROW:
            raise HTTPException(status_code=400, detail="Can only ship paid orders")
        order.shipped_at = datetime.utcnow()
        if status_update.tracking_number:
            order.tracking_number = status_update.tracking_number
    
    elif new_status == OrderStatus.DELIVERED:
        # Only buyer can confirm delivery
        if order.buyer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only buyer can confirm delivery")
        if order.status != OrderStatus.SHIPPED:
            raise HTTPException(status_code=400, detail="Can only confirm delivery of shipped orders")
        order.delivered_at = datetime.utcnow()
    
    elif new_status == OrderStatus.COMPLETED:
        # Auto-completed after delivery confirmation (or admin)
        if order.buyer_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only buyer or admin can complete order")
        if order.status != OrderStatus.DELIVERED:
            raise HTTPException(status_code=400, detail="Can only complete delivered orders")
        order.completed_at = datetime.utcnow()
    
    elif new_status == OrderStatus.CANCELLED:
        # Buyer or seller can cancel if not yet paid
        if order.buyer_id != current_user.id and order.seller_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if order.status not in [OrderStatus.CREATED]:
            raise HTTPException(status_code=400, detail="Can only cancel unpaid orders")
    
    elif new_status == OrderStatus.DISPUTED:
        # Buyer or seller can raise dispute
        if order.buyer_id != current_user.id and order.seller_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update status
    order.status = new_status
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
