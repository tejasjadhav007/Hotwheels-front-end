from sqlalchemy.orm import Session

from .models import Category, Product, User


CATEGORIES = [
    {
        "id": "1",
        "name": "Cars",
        "slug": "cars",
        "description": "Individual Hot Wheels die-cast cars",
        "image_url": "https://images.pexels.com/photos/35967/mini-cooper-auto-model-vehicle.jpg?auto=compress&cs=tinysrgb&w=800",
    },
    {
        "id": "2",
        "name": "Track Sets",
        "slug": "track-sets",
        "description": "Complete track sets for racing",
        "image_url": "https://images.pexels.com/photos/163742/car-race-ferrari-racing-car-163742.jpeg?auto=compress&cs=tinysrgb&w=800",
    },
]

PRODUCTS = [
    {
        "id": "1",
        "category_id": "1",
        "name": "Fast & Furious Nissan Skyline GT-R",
        "slug": "fast-furious-skyline-gtr",
        "description": "Iconic blue Nissan Skyline GT-R from Fast & Furious franchise.",
        "price": 5.99,
        "stock": 50,
        "image_url": "https://images.pexels.com/photos/3729464/pexels-photo-3729464.jpeg?auto=compress&cs=tinysrgb&w=800",
        "featured": 1,
    },
    {
        "id": "2",
        "category_id": "1",
        "name": "Tesla Cybertruck",
        "slug": "tesla-cybertruck",
        "description": "Futuristic Tesla Cybertruck in silver finish.",
        "price": 6.99,
        "stock": 30,
        "image_url": "https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg?auto=compress&cs=tinysrgb&w=800",
        "featured": 1,
    },
    {
        "id": "3",
        "category_id": "2",
        "name": "Super Speed Blastway Track Set",
        "slug": "super-speed-blastway",
        "description": "Epic track set with loops, jumps, and high-speed launcher.",
        "price": 49.99,
        "stock": 15,
        "image_url": "https://images.pexels.com/photos/163582/toy-car-motor-vehicle-red-163582.jpeg?auto=compress&cs=tinysrgb&w=800",
        "featured": 1,
    },
]

USERS = [
    {
        "id": "admin-1",
        "email": "admin@hotwheels.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin",
    },
    {
        "id": "customer-1",
        "email": "customer@example.com",
        "password": "customer123",
        "full_name": "John Customer",
        "role": "customer",
    },
]


def seed_database(db: Session) -> None:
    if not db.query(Category).first():
        db.add_all(Category(**category) for category in CATEGORIES)

    if not db.query(Product).first():
        db.add_all(Product(**product) for product in PRODUCTS)

    if not db.query(User).first():
        db.add_all(User(**user) for user in USERS)

    db.commit()
