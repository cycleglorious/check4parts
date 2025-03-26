from dotenv import load_dotenv
from fastapi import FastAPI

from app.adapters.bm_parts_adapter import BMPartsAdapter
from app.api import auth

load_dotenv()

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


@app.get("/")
async def root():
    return {"message": "Check4Parts API adapter is running"}


@app.get("/bm_parts/profile/")
async def get_bm_parts_profile():
    """Отримує інформацію про профіль користувача у BM Parts."""
    adapter = BMPartsAdapter()
    return await adapter.get_profile()


@app.get("/bm_parts/aggregations/advertisements/")
async def get_aggregations_advertisements():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_advertisements()


@app.get("/bm_parts/aggregations/end_nodes/")
async def get_aggregations_end_nodes():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_end_nodes()


@app.get("/bm_parts/aggregations/brands/")
async def get_aggregations_brands():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_brands()


@app.get("/bm_parts/aggregations/nodes/")
async def get_aggregations_nodes():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_nodes()


@app.get("/bm_parts/aggregations/cars/")
async def get_aggregations_cars():
    adapter = BMPartsAdapter()
    return await adapter.get_aggregations_cars()


@app.get("/bm_parts/search/history/")
async def get_search_history():
    adapter = BMPartsAdapter()
    return await adapter.get_search_history()


@app.get("/bm_parts/search/suggest/")
async def get_search_suggestions(q: str, products_as: str = "obj"):
    adapter = BMPartsAdapter()
    return await adapter.get_search_suggestions(q, products_as)


@app.get("/bm_parts/search/groups/")
async def get_product_groups():
    adapter = BMPartsAdapter()
    return await adapter.get_product_groups()


@app.get("/bm_parts/search/")
async def search_products(q: str, **filters):
    adapter = BMPartsAdapter()
    return await adapter.search_products(q, **filters)


@app.get("/bm_parts/search/suggests/")
async def search_suggestions(query: str, products_as: str = "obj"):
    adapter = BMPartsAdapter()
    return await adapter.search_suggestions(query, products_as)


@app.get("/bm_parts/models_by_brand/{car_name}")
async def get_models_by_brand(car_name: str):
    adapter = BMPartsAdapter()
    return await adapter.get_models_by_brand(car_name)


@app.get("/bm_parts/engines_by_model/{car_name}/{model_name}")
async def get_engines_by_model(car_name: str, model_name: str):
    adapter = BMPartsAdapter()
    return await adapter.get_engines_by_model(car_name, model_name)


@app.get("/bm_parts/group_filters/{group_path}")
async def get_group_filters(group_path: str):
    adapter = BMPartsAdapter()
    return await adapter.get_group_filters(group_path)


@app.post("/bm_parts/reserved_products_detailed/")
async def get_reserved_products_detailed(reserves_uuid: list):
    adapter = BMPartsAdapter()
    return await adapter.get_reserved_products_detailed(reserves_uuid)


@app.get("/bm_parts/unreserved_products_excel/")
async def get_unreserved_products_excel():
    adapter = BMPartsAdapter()
    return await adapter.get_unreserved_products_excel()


@app.post("/bm_parts/reserved_products/")
async def get_reserved_products(reserves_uuid: list):
    adapter = BMPartsAdapter()
    return await adapter.get_reserved_products(reserves_uuid)


@app.post("/bm_parts/reserve_order/")
async def reserve_order(order_uuid: str, comment: str, warehouse_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.reserve_order(order_uuid, comment, warehouse_uuid)


@app.post("/bm_parts/save_unshipped_products_in_cart/")
async def save_unshipped_products_in_cart(products: list, cart_name: str = None):
    adapter = BMPartsAdapter()
    return await adapter.save_unshipped_products_in_cart(products, cart_name)


@app.get("/bm_parts/carts/count/")
async def get_bm_parts_carts_count():
    adapter = BMPartsAdapter()
    return await adapter.get_carts_count()


@app.post("/bm_parts/carts/union/")
async def post_bm_parts_union_carts(carts_array: list):
    adapter = BMPartsAdapter()
    return await adapter.union_carts(carts_array)


@app.post("/bm_parts/change_product/")
async def post_bm_parts_change_product_in_cart(
    cart_uuid: str, from_product_uuid: str, to_product_uuid: str
):
    adapter = BMPartsAdapter()
    return await adapter.change_product_in_cart(
        cart_uuid, from_product_uuid, to_product_uuid
    )


@app.get("/bm_parts/cart_products/")
async def get_bm_parts_cart_products(cart_uuid: str, warehouse: list):
    adapter = BMPartsAdapter()
    return await adapter.get_cart_products(cart_uuid, warehouse)


@app.post("/bm_parts/change_owner/")
async def post_bm_parts_change_cart_owner(cart_uuid: str, client_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.change_cart_owner(cart_uuid, client_uuid)


@app.get("/bm_parts/reserves/")
async def get_bm_parts_reserves(response_fields: str = "all"):
    adapter = BMPartsAdapter()
    return await adapter.get_reserves(response_fields)


@app.delete("/bm_parts/reserves/")
async def delete_bm_parts_reserves(orders: list):
    """Видаляє резерви за переданими ID."""
    adapter = BMPartsAdapter()
    return await adapter.delete_reserves(orders)


@app.get("/bm_parts/shopping/carts/")
async def get_bm_parts_carts():
    """Отримує список корзин."""
    adapter = BMPartsAdapter()
    return await adapter.get_carts()


@app.post("/bm_parts/shopping/carts/")
async def create_bm_parts_cart(name: str, products: list = None):
    """Створює нову корзину."""
    adapter = BMPartsAdapter()
    return await adapter.create_cart(name, products)


@app.post("/bm_parts/shopping/cart/{cart_uuid}/product/{product_uuid}/{quantity}")
async def add_product_to_bm_parts_cart(
    cart_uuid: str, product_uuid: str, quantity: int
):
    """Додає товар в корзину."""
    adapter = BMPartsAdapter()
    return await adapter.add_product_to_cart(cart_uuid, product_uuid, quantity)


@app.put("/bm_parts/shopping/cart/{cart_uuid}/product/{product_uuid}/{quantity}")
async def update_product_in_bm_parts_cart(
    cart_uuid: str, product_uuid: str, quantity: int
):
    adapter = BMPartsAdapter()
    return await adapter.update_product_quantity_in_cart(
        cart_uuid, product_uuid, quantity
    )


@app.delete("/bm_parts/shopping/cart/{cart_uuid}/product/{product_uuid}")
async def delete_product_from_bm_parts_cart(cart_uuid: str, product_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.delete_product_from_cart(cart_uuid, product_uuid)


@app.delete("/bm_parts/shopping/cart/{cart_uuid}")
async def delete_bm_parts_cart(cart_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.delete_cart(cart_uuid)


@app.get("/bm_parts/shopping/cart/{cart_uuid}")
async def get_bm_parts_cart(cart_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.get_cart(cart_uuid)


@app.post("/bm_parts/shopping/cart/{cart_uuid}")
async def update_bm_parts_cart(
    cart_uuid: str, name: str = None, owner_uuid: str = None
):
    adapter = BMPartsAdapter()
    return await adapter.update_cart(cart_uuid, name, owner_uuid)


@app.get("/bm_parts/product/{product_uuid}/in_waiting/")
async def get_in_waiting(product_uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.get_in_waiting(product_uuid)


@app.get("/bm_parts/product/{product_uuid}/in_stocks/")
async def get_in_stocks(product_uuid: str, id_type: str = "id"):
    adapter = BMPartsAdapter()
    return await adapter.get_in_stocks(product_uuid, id_type)


@app.get("/bm_parts/product/{product_uuid}/prices/")
async def get_prices(product_uuid: str, id_type: str = "id"):
    adapter = BMPartsAdapter()
    return await adapter.get_prices(product_uuid, id_type)


@app.get("/bm_parts/product/{product_uuid}/price/")
async def get_price(product_uuid: str, currency: str = "UAH", id_type: str = "id"):
    adapter = BMPartsAdapter()
    return await adapter.get_price(product_uuid, currency, id_type)


@app.get("/bm_parts/product/{product_uuid}/")
async def get_product_info(
    product_uuid: str,
    warehouses: str = "all",
    currency: str = "UAH",
    id_type: str = "id",
    products_as: str = "obj",
):
    adapter = BMPartsAdapter()
    return await adapter.get_product_info(
        product_uuid, warehouses, currency, id_type, products_as
    )


@app.get("/bm_parts/detection_cases/")
async def get_detection_cases():
    adapter = BMPartsAdapter()
    return await adapter.get_detection_cases()


@app.get("/bm_parts/reclamations/")
async def get_reclamations(page: int = 1, per_page: int = 10, direction: str = "desc"):
    adapter = BMPartsAdapter()
    return await adapter.get_reclamations(page, per_page, direction)


@app.post("/bm_parts/reclamation/")
async def create_reclamation(data: dict):
    adapter = BMPartsAdapter()
    return await adapter.create_reclamation(data)


@app.get("/bm_parts/returns/")
async def get_returns(page: int = 1, per_page: int = 10, direction: str = "desc"):
    adapter = BMPartsAdapter()
    return await adapter.get_returns(page, per_page, direction)


@app.get("/bm_parts/sold_products/")
async def get_sold_products(
    page: int = 1,
    per_page: int = 10,
    direction: str = "desc",
    reason: str = "returns",
    q: str = None,
):
    adapter = BMPartsAdapter()
    return await adapter.get_sold_products(page, per_page, direction, reason, q)


@app.delete("/bm_parts/returns/products/{uuid}")
async def delete_product_return(uuid: str):
    adapter = BMPartsAdapter()
    return await adapter.delete_product_return(uuid)


@app.get("/bm_parts/returns/products/")
async def get_return_products():
    adapter = BMPartsAdapter()
    return await adapter.get_return_products()


@app.post("/bm_parts/returns/request/")
async def create_return_request(request_data: dict):
    adapter = BMPartsAdapter()
    return await adapter.create_return_request(request_data)


@app.get("/bm_parts/returns/causes/")
async def get_return_causes():
    adapter = BMPartsAdapter()
    return await adapter.get_return_causes()


@app.post("/bm_parts/returns/notify/")
async def notify_return(text: str):
    adapter = BMPartsAdapter()
    return await adapter.notify_return(text)
