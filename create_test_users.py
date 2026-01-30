"""
Script to create test users for E-Mobile application
Run this after resetting the database
"""
from app.db.session import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.core.security import get_password_hash

def create_test_data():
    db = SessionLocal()
    
    try:
        # Create vendor user
        vendor = User(
            email='vendeur@test.com',
            hashed_password=get_password_hash('vendeur123'),
            full_name='Vendeur Test',
            is_vendor=True,
            is_active=True,
            rating=4.5,
            rating_count=10
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        print(f'[OK] Vendor created: {vendor.email}')
        
        # Create buyer user
        buyer = User(
            email='acheteur@test.com',
            hashed_password=get_password_hash('acheteur123'),
            full_name='Acheteur Test',
            is_vendor=False,
            is_active=True,
            rating=5.0,
            rating_count=5
        )
        db.add(buyer)
        db.commit()
        db.refresh(buyer)
        print(f'[OK] Buyer created: {buyer.email}')
        
        # Create test user
        test_user = User(
            email='test@test.com',
            hashed_password=get_password_hash('test123'),
            full_name='Test User',
            is_vendor=True,
            is_active=True,
            rating=4.8,
            rating_count=15
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f'[OK] Test user created: {test_user.email}')
        
        # Create sample products
        products = [
            Product(
                title='iPhone 14 Pro',
                description='Latest iPhone with amazing camera',
                price=999.99,
                currency='USD',
                category='Electronics',
                images=['https://via.placeholder.com/400x400?text=iPhone+14+Pro'],
                seller_id=vendor.id
            ),
            Product(
                title='MacBook Pro M2',
                description='Powerful laptop for professionals',
                price=1999.99,
                currency='USD',
                category='Electronics',
                images=['https://via.placeholder.com/400x400?text=MacBook+Pro'],
                seller_id=vendor.id
            ),
            Product(
                title='AirPods Pro',
                description='Wireless earbuds with noise cancellation',
                price=249.99,
                currency='USD',
                category='Electronics',
                images=['https://via.placeholder.com/400x400?text=AirPods+Pro'],
                seller_id=test_user.id
            ),
        ]
        
        for product in products:
            db.add(product)
        
        db.commit()
        print(f'[OK] {len(products)} products created')
        
        print('\n' + '='*50)
        print('SUCCESS: Test data created!')
        print('='*50)
        print('\nTest Accounts:')
        print('  Vendor: vendeur@test.com / vendeur123')
        print('  Buyer:  acheteur@test.com / acheteur123')
        print('  Test:   test@test.com / test123')
        print('='*50)
        
    except Exception as e:
        print(f'[ERROR] {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_test_data()
