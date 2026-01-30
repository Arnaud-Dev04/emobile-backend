"""Script pour ajouter des produits de démonstration à la base de données"""
from app.db.session import SessionLocal
from app.models import Product, User
from app.core.security import get_password_hash

def seed_products():
    db = SessionLocal()
    
    try:
        # Vérifier s'il y a déjà des produits
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"La base de données contient déjà {existing_products} produits.")
            return
        
        # Créer un utilisateur vendeur si nécessaire
        vendor = db.query(User).filter(User.email == "vendor@example.com").first()
        if not vendor:
            vendor = User(
                email="vendor@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Vendeur Demo",
                is_vendor=True,
                is_active=True
            )
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
            print("Utilisateur vendeur cree")
        
        # Produits de démonstration
        products_data = [
            {
                "title": "Smartphone XYZ",
                "description": "Un smartphone moderne avec toutes les fonctionnalités",
                "price": 599.99,
                "currency": "EUR",
                "category": "Électronique",
                "images": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300"],
            },
            {
                "title": "Laptop Pro",
                "description": "Ordinateur portable haute performance",
                "price": 1299.99,
                "currency": "EUR",
                "category": "Électronique",
                "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300"],
            },
            {
                "title": "Casque Audio",
                "description": "Casque sans fil avec réduction de bruit",
                "price": 249.99,
                "currency": "EUR",
                "category": "Audio",
                "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300"],
            },
            {
                "title": "Montre Connectée",
                "description": "Montre intelligente avec suivi fitness",
                "price": 349.99,
                "currency": "EUR",
                "category": "Accessoires",
                "images": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300"],
            },
            {
                "title": "Tablette HD",
                "description": "Tablette 10 pouces haute définition",
                "price": 449.99,
                "currency": "EUR",
                "category": "Électronique",
                "images": ["https://images.unsplash.com/photo-1561154464-82e9adf32764?w=300"],
            },
            {
                "title": "Appareil Photo",
                "description": "Appareil photo numérique professionnel",
                "price": 899.99,
                "currency": "EUR",
                "category": "Photo",
                "images": ["https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=300"],
            },
        ]
        
        # Ajouter les produits
        for product_data in products_data:
            product = Product(
                **product_data,
                seller_id=vendor.id
            )
            db.add(product)
        
        db.commit()
        print(f"[OK] {len(products_data)} produits ajoutes avec succes!")
        
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'ajout des produits: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_products()
