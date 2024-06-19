from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (select,
                        update,
                        delete)
from database.models import Product


async def orm_add_product(session: AsyncSession, data: dict, photo_id: str, photo_data: bytes):
    obj = Product(
        product_name=data["product_name"],
        product_description=data["product_description"],
        product_size=str(data["product_size"]),
        product_brand=data["product_brand"],
        product_sex=data["product_sex"],
        product_category=data["product_category"],
        product_price=int(data["product_price"]),
        product_photo=photo_id,
        product_photo_blob=photo_data
    )
    session.add(obj)
    await session.flush()
    await session.commit()


async def orm_get_products(session: AsyncSession):
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.product_id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    product_size = str(data["product_size"])
    query = update(Product).where(Product.product_id == product_id).values(
        product_name=data["product_name"],
        product_description=data["product_description"],
        product_size=str(data["product_size"]),
        product_brand=data["product_brand"],
        product_sex=data["product_sex"],
        product_category=data["product_category"],
        product_price=int(data["product_price"]),
        product_photo=data["product_photo"],
        product_photo_blob=bytes(data["product_photo_blob"])
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.product_id == product_id)
    await session.execute(query)
    await session.commit()
