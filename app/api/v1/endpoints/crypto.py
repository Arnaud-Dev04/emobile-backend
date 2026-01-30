from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user, get_db
from app.models import User, CryptoWallet, CryptoTransaction, Order
from app.schemas.crypto import (
    WalletCreate, WalletResponse,
    TransactionCreate, TransactionVerify, TransactionResponse,
    PaymentInitRequest, PaymentInitResponse
)
from app.services.crypto_service import CryptoService

router = APIRouter()


# ============ WALLET ENDPOINTS ============

@router.post("/wallet", response_model=WalletResponse)
async def register_wallet(
    wallet: WalletCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new cryptocurrency wallet address"""
    # Check if wallet already exists
    existing = db.query(CryptoWallet).filter(
        CryptoWallet.user_id == current_user.id,
        CryptoWallet.wallet_address == wallet.wallet_address
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet already registered"
        )
    
    # Set all other wallets as non-primary
    db.query(CryptoWallet).filter(
        CryptoWallet.user_id == current_user.id
    ).update({"is_primary": False})
    
    # Create new wallet
    db_wallet = CryptoWallet(
        user_id=current_user.id,
        wallet_address=wallet.wallet_address,
        wallet_type=wallet.wallet_type,
        network=wallet.network,
        is_primary=True
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    
    return db_wallet


@router.get("/wallet", response_model=WalletResponse)
async def get_my_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's primary wallet"""
    wallet = db.query(CryptoWallet).filter(
        CryptoWallet.user_id == current_user.id,
        CryptoWallet.is_primary == True
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No wallet registered"
        )
    
    return wallet


@router.get("/wallets", response_model=List[WalletResponse])
async def get_all_wallets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all wallets for current user"""
    return db.query(CryptoWallet).filter(
        CryptoWallet.user_id == current_user.id
    ).all()


# ============ PAYMENT ENDPOINTS ============

@router.post("/payment/init", response_model=PaymentInitResponse)
async def init_crypto_payment(
    request: PaymentInitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialize a cryptocurrency payment for an order
    Returns seller's wallet address and deep link for payment
    """
    # Get the order
    order = db.query(Order).filter(Order.id == request.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Ensure user is the buyer
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this order"
        )
    
    # Get seller's wallet
    seller_wallet = db.query(CryptoWallet).filter(
        CryptoWallet.user_id == order.seller_id,
        CryptoWallet.is_primary == True
    ).first()
    
    if not seller_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seller has no crypto wallet configured"
        )
    
    # Convert price to crypto (USDT = 1:1 with USD)
    crypto_amount = CryptoService.usd_to_crypto(order.total_price, "USDT")
    
    # Create pending transaction record
    transaction = CryptoTransaction(
        order_id=order.id,
        from_address="",  # Will be filled when verified
        to_address=seller_wallet.wallet_address,
        amount=crypto_amount,
        currency="USDT",
        network=seller_wallet.network,
        status="pending"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Generate deep link
    deep_link = CryptoService.generate_safepal_deep_link(
        to_address=seller_wallet.wallet_address,
        amount=crypto_amount,
        currency="USDT",
        network=seller_wallet.network
    )
    
    return PaymentInitResponse(
        transaction_id=transaction.id,
        seller_wallet=seller_wallet.wallet_address,
        amount=crypto_amount,
        currency="USDT",
        network=seller_wallet.network,
        deep_link=deep_link
    )


@router.post("/payment/verify", response_model=TransactionResponse)
async def verify_crypto_payment(
    request: TransactionVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify a cryptocurrency payment using transaction hash
    """
    # Find pending transaction by hash or create verification
    transaction = db.query(CryptoTransaction).filter(
        CryptoTransaction.tx_hash == request.tx_hash
    ).first()
    
    if transaction and transaction.status == "confirmed":
        return transaction
    
    # Verify on blockchain
    result = await CryptoService.verify_bsc_transaction(request.tx_hash)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Transaction verification failed")
        )
    
    if transaction:
        # Update existing transaction
        transaction.tx_hash = request.tx_hash
        transaction.status = result["status"]
        transaction.from_address = result.get("from_address", "")
        transaction.block_number = result.get("block_number", 0)
        transaction.confirmations = result.get("confirmations", 0)
        
        if result["status"] == "confirmed":
            from datetime import datetime
            transaction.confirmed_at = datetime.utcnow()
            
            # Update order status
            order = db.query(Order).filter(Order.id == transaction.order_id).first()
            if order:
                order.status = "paid"
        
        db.commit()
        db.refresh(transaction)
        return transaction
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No pending transaction found for this order"
    )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all crypto transactions for current user's orders"""
    # Get user's orders (as buyer or seller)
    from sqlalchemy import or_
    
    transactions = db.query(CryptoTransaction).join(Order).filter(
        or_(
            Order.buyer_id == current_user.id,
            Order.seller_id == current_user.id
        )
    ).order_by(CryptoTransaction.created_at.desc()).all()
    
    return transactions
