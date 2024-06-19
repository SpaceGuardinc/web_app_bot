from typing import List

from sqlalchemy import (String,
                        ForeignKey,
                        Boolean,
                        BIGINT,
                        DateTime,
                        Text,
                        func,
                        LargeBinary)
from sqlalchemy.orm import (declarative_base,
                            Mapped,
                            mapped_column,
                            relationship,
                            DeclarativeBase)


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = 'user'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    first_name: Mapped[str] = mapped_column(String(30), nullable=True)
    second_name: Mapped[str] = mapped_column(String(30), nullable=True)
    address: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(30), nullable=True)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = 'order'

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'), nullable=False)
    fast_order: Mapped[bool] = mapped_column(Boolean, nullable=True)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="order")
    user: Mapped["User"] = relationship("User", back_populates="orders")


class Product(Base):
    __tablename__ = 'product'

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('order.order_id'), nullable=True)

    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_description: Mapped[str] = mapped_column(Text, nullable=False)
    product_size: Mapped[str] = mapped_column(String(30), nullable=False)
    product_brand: Mapped[str] = mapped_column(String(30), nullable=False)
    product_sex: Mapped[str] = mapped_column(String(30), nullable=False)
    product_category: Mapped[str] = mapped_column(String(30), nullable=False)
    product_price: Mapped[int] = mapped_column(nullable=False)
    product_photo: Mapped[str] = mapped_column(String(200), nullable=False)
    product_photo_blob: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="products")
    sizes: Mapped[List["ProductSize"]] = relationship("ProductSize", back_populates="product")



class ProductSize(Base):
    __tablename__ = "product_size"

    size_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.product_id'), nullable=False)

    product_size: Mapped[str] = mapped_column(String(30), nullable=False)
    product_price: Mapped[int] = mapped_column(nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="sizes")


class Admin(Base):
    __tablename__ = 'admin'

    admin_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_telegram_id: Mapped[int] = mapped_column(nullable=False)
