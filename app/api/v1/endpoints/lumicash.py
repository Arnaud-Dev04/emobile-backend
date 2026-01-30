from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import models, schemas
from app.api import deps
from app.services.lumicash_service import create_payment, verify_payment

router = APIRouter()

class LumicashPaymentRequest(BaseModel):
    phone_number: str

@router.post('/orders/{order_id}/pay/lumicash', response_model=schemas.Order)
def pay_order_lumicash(
    *,
    db: Session = Depends(deps.get_db),
    order_id: int,
    payment_data: LumicashPaymentRequest = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Initiate LUMICASH payment for an order.
    Returns the updated order with payment details.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    # Only buyer can pay
    if order.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail='Only the buyer can pay for this order')
    if order.status != models.OrderStatus.CREATED:
        raise HTTPException(status_code=400, detail='Order cannot be paid in its current status')
    # Create LUMICASH payment request with phone number
    payment_info = create_payment(
        order_id=order.id,
        amount=order.total_price,
        phone_number=payment_data.phone_number
    )
    # Store payment reference (mock) in order fields if needed
    order.payment_method = models.PaymentMethod.LUMICASH
    order.transaction_hash = payment_info['payment_ref']
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
