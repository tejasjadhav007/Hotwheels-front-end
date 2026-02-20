import uuid
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import CartItem, Category, Order, OrderItem, Product, User
from .schemas import (
    CartItemOut,
    CartItemRequest,
    CategoryOut,
    LoginRequest,
    LoginResponse,
    OrderCreateRequest,
    OrderItemOut,
    OrderOut,
    ProductOut,
    ShippingAddress,
    UserOut,
)
from .seed import seed_database

app = FastAPI(title="Hotwheels Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
with next(get_db()) as db:
    seed_database(db)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return LoginResponse(
        token=f"dev-token-{uuid.uuid4()}",
        user=UserOut(
            id=user.id,
            email=user.email,
            fullName=user.full_name,
            role=user.role,
        ),
    )


@app.get("/api/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [
        CategoryOut(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            imageUrl=category.image_url,
        )
        for category in categories
    ]


@app.get("/api/products", response_model=list[ProductOut])
def list_products(
    search: str | None = Query(default=None),
    category_id: str | None = Query(default=None),
    in_stock_only: bool = Query(default=False),
    max_price: float | None = Query(default=None, ge=0),
    sort_by: str = Query(default="featured"),
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if search:
        term = f"%{search.lower()}%"
        query = query.filter((Product.name.ilike(term)) | (Product.description.ilike(term)))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if in_stock_only:
        query = query.filter(Product.stock > 0)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    products = query.all()

    if sort_by == "price-low":
        products.sort(key=lambda p: p.price)
    elif sort_by == "price-high":
        products.sort(key=lambda p: p.price, reverse=True)
    elif sort_by == "name":
        products.sort(key=lambda p: p.name.lower())
    else:
        products.sort(key=lambda p: p.featured, reverse=True)

    return [serialize_product(product) for product in products]


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_product(product)


@app.get("/api/cart/{user_id}", response_model=list[CartItemOut])
def get_cart(user_id: str, db: Session = Depends(get_db)):
    ensure_user_exists(user_id, db)
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    return [CartItemOut(product=serialize_product(item.product), quantity=item.quantity) for item in items]


@app.post("/api/cart/{user_id}/items", response_model=list[CartItemOut])
def add_cart_item(user_id: str, payload: CartItemRequest, db: Session = Depends(get_db)):
    ensure_user_exists(user_id, db)
    product = db.query(Product).filter(Product.id == payload.productId).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == payload.productId)
        .first()
    )
    if existing:
        existing.quantity += payload.quantity
    else:
        db.add(CartItem(user_id=user_id, product_id=payload.productId, quantity=payload.quantity))

    db.commit()
    return get_cart(user_id, db)


@app.patch("/api/cart/{user_id}/items/{product_id}", response_model=list[CartItemOut])
def update_cart_item(user_id: str, product_id: str, payload: CartItemRequest, db: Session = Depends(get_db)):
    ensure_user_exists(user_id, db)
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    item.quantity = payload.quantity
    db.commit()
    return get_cart(user_id, db)


@app.delete("/api/cart/{user_id}/items/{product_id}", response_model=list[CartItemOut])
def delete_cart_item(user_id: str, product_id: str, db: Session = Depends(get_db)):
    ensure_user_exists(user_id, db)
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .first()
    )
    if item:
        db.delete(item)
        db.commit()
    return get_cart(user_id, db)


@app.get("/api/orders/{user_id}", response_model=list[OrderOut])
def list_orders(user_id: str, db: Session = Depends(get_db)):
    ensure_user_exists(user_id, db)
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return [serialize_order(order) for order in orders]


@app.post("/api/orders", response_model=OrderOut)
def create_order(payload: OrderCreateRequest, db: Session = Depends(get_db)):
    ensure_user_exists(payload.userId, db)

    products = {
        product.id: product
        for product in db.scalars(
            select(Product).where(Product.id.in_([item.productId for item in payload.items]))
        )
    }

    if len(products) != len(payload.items):
        raise HTTPException(status_code=400, detail="One or more products are invalid")

    total = 0.0
    order_items: list[OrderItem] = []
    for item in payload.items:
        product = products[item.productId]
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        product.stock -= item.quantity
        line_total = product.price * item.quantity
        total += line_total
        order_items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=item.quantity,
                price_at_time=product.price,
            )
        )

    order = Order(
        id=f"order-{uuid.uuid4().hex[:10]}",
        user_id=payload.userId,
        status="processing",
        total_amount=round(total, 2),
        shipping_full_name=payload.shippingAddress.fullName,
        shipping_address_line1=payload.shippingAddress.addressLine1,
        shipping_address_line2=payload.shippingAddress.addressLine2,
        shipping_city=payload.shippingAddress.city,
        shipping_state=payload.shippingAddress.state,
        shipping_zip_code=payload.shippingAddress.zipCode,
        shipping_phone=payload.shippingAddress.phone,
        payment_status="paid",
        payment_method=payload.paymentMethod,
        tracking_number=f"TRK-{uuid.uuid4().hex[:8].upper()}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        items=order_items,
    )

    db.add(order)
    db.query(CartItem).filter(CartItem.user_id == payload.userId).delete()
    db.commit()
    db.refresh(order)

    return serialize_order(order)


def ensure_user_exists(user_id: str, db: Session) -> None:
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")


def serialize_product(product: Product) -> ProductOut:
    return ProductOut(
        id=product.id,
        categoryId=product.category_id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        price=product.price,
        stock=product.stock,
        imageUrl=product.image_url,
        featured=bool(product.featured),
    )


def serialize_order(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        userId=order.user_id,
        status=order.status,
        totalAmount=order.total_amount,
        shippingAddress=ShippingAddress(
            fullName=order.shipping_full_name,
            addressLine1=order.shipping_address_line1,
            addressLine2=order.shipping_address_line2,
            city=order.shipping_city,
            state=order.shipping_state,
            zipCode=order.shipping_zip_code,
            phone=order.shipping_phone,
        ),
        paymentStatus=order.payment_status,
        paymentMethod=order.payment_method,
        trackingNumber=order.tracking_number,
        items=[
            OrderItemOut(
                id=item.id,
                orderId=order.id,
                productId=item.product_id,
                productName=item.product_name,
                quantity=item.quantity,
                priceAtTime=item.price_at_time,
            )
            for item in order.items
        ],
        createdAt=order.created_at,
        updatedAt=order.updated_at,
    )
