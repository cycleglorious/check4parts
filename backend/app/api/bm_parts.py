from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from app.adapters.bm_parts_adapter import BMPartsAdapter

router = APIRouter(prefix="/bm-parts", tags=["BM Parts"])


class ReservedProductsUUIDRequest(BaseModel):
    reserves_uuid: list[str]


class CartsWarehousesRequest(BaseModel):
    cart_uuid: str
    warehouses: list[str]


class ReserveOrderRequest(BaseModel):
    order_uuid: str = Field(..., description="UUID of the order to reserve")
    comment: str = Field(..., description="Additional comment for the reservation")
    warehouse_uuid: str = Field(..., description="UUID of the warehouse handling the reserve")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_uuid": "53b9c4a2-69dc-4d4c-8e9a-51cbf51ef4f5",
                "comment": "Reserve order for VIP client",
                "warehouse_uuid": "8adf5d6e-0a3d-4d23-9fd3-2f8c3512b156",
            }
        }
    )


class UnionCartsRequest(BaseModel):
    carts_array: list[str]


class ChangeProductRequest(BaseModel):
    cart_uuid: str = Field(..., description="UUID of the cart to update")
    from_product_uuid: str = Field(
        ..., description="UUID of the product that should be replaced"
    )
    to_product_uuid: str = Field(
        ..., description="UUID of the product that replaces the original"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cart_uuid": "c4c5429e-188c-4f41-90d5-51f86f5c593b",
                "from_product_uuid": "ed88e3b9-8ba2-4b04-9cc8-25051ff3677f",
                "to_product_uuid": "a73b38ef-3dd4-4bcf-a47b-3e1d18caea64",
            }
        }
    )


class DeleteReservesRequest(BaseModel):
    orders: list[str] = Field(..., description="List of order UUIDs to remove")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "orders": [
                    "97f08e21-41e4-492b-bc7b-4f469d6243a8",
                    "12bbdcce-9f67-4f42-877f-387b0c36d742",
                ]
            }
        }
    )


class CartProductRequest(BaseModel):
    product_uuid: str = Field(..., description="UUID of the product")
    quantity: int = Field(..., gt=0, description="Desired quantity of the product")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_uuid": "665694f0-07bf-4c4a-a45d-511c73403c42",
                "quantity": 2,
            }
        }
    )


class CartProductDeleteRequest(BaseModel):
    product_uuid: str = Field(..., description="UUID of the product to remove")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_uuid": "665694f0-07bf-4c4a-a45d-511c73403c42",
            }
        }
    )


class ChangeOwnerRequest(BaseModel):
    cart_uuid: str
    client_uuid: str


class CreateCartRequest(BaseModel):
    name: str
    products: list[str] | None = None


class UpdateCartRequest(BaseModel):
    name: str | None = None
    owner_uuid: str | None = None


class CreateReclamationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")


class CreateReturnRequest(BaseModel):
    model_config = ConfigDict(extra="allow")


class NotifyReturnRequest(BaseModel):
    text: str


class PartDetail(BaseModel):
    id: str = None
    value: str
    title: str
    name: str = None


class PartCross(BaseModel):
    id: str
    name: str
    code: str
    brand: str
    description: str


class PartAdditional(BaseModel):
    id: str
    name: str
    code: str
    min_quantity: int


class Part(BaseModel):
    id: str
    name: str
    code: str
    description: str
    image: str
    brand: str
    details: list[PartDetail]
    crosses: list[PartCross] = None
    additional: list[PartAdditional] = None


class Provider(BaseModel):
    id: str = None
    name: str
    short_name: str = None


class Warehouse(BaseModel):
    id: str = None
    name: str
    short_name: str = None
    type: str = None  # 'in-stock' | 'in-waiting' | 'in-other'


class Rest(BaseModel):
    id: str = None
    provider: Provider
    warehouse: Warehouse
    quantity: int
    delivery_time: str
    price: float


class SearchProductsResponse(BaseModel):
    part: Part
    rests: list[Rest]


@router.get("/profile/me/")
async def get_bm_parts_profile():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_profile()


@router.get("/aggregations/advertisements/")
async def get_aggregations_advertisements():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_aggregations_advertisements()


@router.get("/aggregations/end_nodes/")
async def get_aggregations_end_nodes():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_aggregations_end_nodes()


@router.get("/aggregations/brands/")
async def get_aggregations_brands():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_aggregations_brands()


@router.get("/aggregations/nodes/")
async def get_aggregations_nodes():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_aggregations_nodes()


@router.get("/aggregations/cars/")
async def get_aggregations_cars():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_aggregations_cars()


@router.get("/search/history/")
async def get_search_history():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_search_history()


@router.get("/search/suggest/")
async def get_search_suggestions(q: str, products_as: str = "obj"):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_search_suggestions(q, products_as)


@router.get("/search/groups/")
async def get_product_groups():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_product_groups()


@router.get("/search/products")
async def search_products(
    q: str,
    request: Request,
    include_crosses: bool = False,
    include_additional: bool = False,
):
    async with BMPartsAdapter() as adapter:
        filters = dict(request.query_params)
        filters.pop("q", None)
        filters.pop("include_crosses", None)
        filters.pop("include_additional", None)

        return await adapter.search_products_enhanced(
            q,
            include_crosses=include_crosses,
            include_additional=include_additional,
            **filters
        )


@router.get("/products/{product_uuid}/additional")
async def get_models_by_brand(product_uuid: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_product_additional(product_uuid)


@router.get("/models_by_brand/{car_name}")
async def get_models_by_brand(car_name: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_models_by_brand(car_name)


@router.get("/engines_by_model/{car_name}/{model_name}")
async def get_engines_by_model(car_name: str, model_name: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_engines_by_model(car_name, model_name)


@router.get("/group_filters/{group_path}")  # TODO: to test
async def get_group_filters(group_path: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_group_filters(group_path)


@router.post("/reserved_products_detailed/")
async def get_reserved_products_detailed(request: ReservedProductsUUIDRequest):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_reserved_products_detailed(request.reserves_uuid)


@router.post("/reserved_products/")
async def get_reserved_products(request: ReservedProductsUUIDRequest):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_reserved_products(request.reserves_uuid)


@router.post("/reserve_order/")
async def reserve_order(request: ReserveOrderRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.reserve_order(**data)


@router.get("/carts/count/")
async def get_bm_parts_carts_count():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_carts_count()


@router.post("/carts/union/")
async def post_bm_parts_union_carts(request: UnionCartsRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.union_carts(**data)


@router.post("/change_product/")
async def post_bm_parts_change_product_in_cart(request: ChangeProductRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.change_product_in_cart(**data)


@router.post("/cart_products/")
async def get_bm_parts_cart_products(request: CartsWarehousesRequest):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_cart_products(request.cart_uuid, request.warehouses)


@router.post("/change_owner/")
async def post_bm_parts_change_cart_owner(request: ChangeOwnerRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.change_cart_owner(**data)


@router.get("/reserves/")
async def get_bm_parts_reserves(response_fields: str = "all"):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_reserves(response_fields)


@router.delete("/reserves/")
async def delete_bm_parts_reserves(request: DeleteReservesRequest):
    async with BMPartsAdapter() as adapter:
        return await adapter.delete_reserves(request.orders)


@router.get("/shopping/carts/")
async def get_bm_parts_carts():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_carts()


@router.post("/shopping/carts/")
async def create_bm_parts_cart(request: CreateCartRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.create_cart(**data)


@router.post("/shopping/cart/{cart_uuid}/product")
async def add_product_to_bm_parts_cart(cart_uuid: str, request: CartProductRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.add_product_to_cart(cart_uuid, **data)


@router.put("/shopping/cart/{cart_uuid}/product")
async def update_product_in_bm_parts_cart(cart_uuid: str, request: CartProductRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.update_product_quantity_in_cart(cart_uuid, **data)


@router.delete("/shopping/cart/{cart_uuid}/product")
async def delete_product_from_bm_parts_cart(
    cart_uuid: str, request: CartProductDeleteRequest
):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.delete_product_from_cart(cart_uuid, **data)


@router.delete("/shopping/cart/")
async def delete_bm_parts_cart(cart_uuid: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.delete_cart(cart_uuid)


@router.get("/shopping/cart/{cart_uuid}")
async def get_bm_parts_cart(cart_uuid: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_cart(cart_uuid)


@router.post("/shopping/cart/{cart_uuid}")
async def update_bm_parts_cart(cart_uuid: str, request: UpdateCartRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.update_cart(cart_uuid, **data)


@router.get("/product/{product_uuid}/in_waiting/")
async def get_in_waiting(product_uuid: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_in_waiting(product_uuid)


@router.get("/product/{product_uuid}/in_stocks/")
async def get_in_stocks(product_uuid: str, id_type: str = None):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_in_stocks(product_uuid, id_type)


@router.get("/product/{product_uuid}/prices/")
async def get_prices(product_uuid: str, id_type: str = None):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_prices(product_uuid, id_type)


@router.get("/product/{product_uuid}/price/")
async def get_price(product_uuid: str, currency: str = "UAH", id_type: str = None):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_price(product_uuid, currency, id_type)


@router.get("/product/{product_uuid}/")
async def get_product_info(
    product_uuid: str,
    warehouses: str = "all",
    currency: str = "UAH",
    id_type: str = None,
    products_as: str = "obj",
):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_product_info(
            product_uuid, warehouses, currency, id_type, products_as
        )


@router.get("/detection_cases/")
async def get_detection_cases():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_detection_cases()


@router.get("/reclamations/")
async def get_reclamations(page: int = 1, per_page: int = 10, direction: str = "desc"):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_reclamations(page, per_page, direction)


@router.post("/reclamation/")
async def create_reclamation(request: CreateReclamationRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.create_reclamation(data)


@router.get("/returns/")
async def get_returns(page: int = 1, per_page: int = 10, direction: str = "desc"):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_returns(page, per_page, direction)


@router.get("/sold_products/")
async def get_sold_products(
    page: int = 1,
    per_page: int = 10,
    direction: str = "desc",
    reason: str = "returns",
    q: str = None,
):
    async with BMPartsAdapter() as adapter:
        return await adapter.get_sold_products(page, per_page, direction, reason, q)


@router.delete("/returns/products/{uuid}")
async def delete_product_return(uuid: str):
    async with BMPartsAdapter() as adapter:
        return await adapter.delete_product_return(uuid)


@router.get("/returns/products/")
async def get_return_products():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_return_products()


@router.post("/returns/request/")
async def create_return_request(request: CreateReturnRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.create_return_request(data)


@router.get("/returns/causes/")
async def get_return_causes():
    async with BMPartsAdapter() as adapter:
        return await adapter.get_return_causes()


@router.post("/returns/notify/")
async def notify_return(request: NotifyReturnRequest):
    async with BMPartsAdapter() as adapter:
        data = request.model_dump()
        return await adapter.notify_return(**data)
