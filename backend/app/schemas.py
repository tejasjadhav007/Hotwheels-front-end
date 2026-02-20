from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=3)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    fullName: str
    role: str


class LoginResponse(BaseModel):
    token: str
    user: UserOut


class CategoryOut(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    imageUrl: str


class ProductOut(BaseModel):
    id: str
    categoryId: str
    name: str
    slug: str
    description: str
    price: float
    stock: int
    imageUrl: str
    featured: bool


class CartItemRequest(BaseModel):
    productId: str
    quantity: int = Field(ge=1, le=99)


class CartItemOut(BaseModel):
    product: ProductOut
    quantity: int


class ShippingAddress(BaseModel):
    fullName: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: str
    zipCode: str
    phone: str


class OrderItemRequest(BaseModel):
    productId: str
    quantity: int = Field(ge=1, le=99)


class OrderCreateRequest(BaseModel):
    userId: str
    paymentMethod: str
    shippingAddress: ShippingAddress
    items: list[OrderItemRequest]


class OrderItemOut(BaseModel):
    id: int
    orderId: str
    productId: str
    productName: str
    quantity: int
    priceAtTime: float


class OrderOut(BaseModel):
    id: str
    userId: str
    status: str
    totalAmount: float
    shippingAddress: ShippingAddress
    paymentStatus: str
    paymentMethod: str
    trackingNumber: Optional[str] = None
    items: list[OrderItemOut]
    createdAt: datetime
    updatedAt: datetime
