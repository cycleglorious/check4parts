import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, validator

from app.adapters.intercars_adapter import IntercarsAdapter, IntercarsAPIError
from app.dependencies.intercars import get_intercars_adapter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/intercars", tags=["intercars"])


class InventoryLine(BaseModel):
    sku: str = Field(..., min_length=1, description="Product SKU")
    quantity: int = Field(..., gt=0, description="Quantity must be positive")


class InventoryQuoteRequest(BaseModel):
    lines: List[InventoryLine] = Field(
        ..., min_items=1, description="At least one line is required"
    )


class InventoryStockRequest(BaseModel):
    skus: List[str] = Field(
        ..., min_items=1, description="At least one SKU is required"
    )
    location: str = Field(..., min_length=1, description="Location cannot be empty")

    @validator("skus")
    def validate_skus(cls, v):
        if not all(sku.strip() for sku in v):
            raise ValueError("All SKUs must be non-empty strings")
        return [sku.strip() for sku in v]


class DateRangeRequest(BaseModel):
    creation_date_from: str = Field(..., description="Start date in ISO format")
    creation_date_to: str = Field(..., description="End date in ISO format")
    offset: int = Field(1, ge=1, description="Pagination offset")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")


class InvoiceSearchRequest(BaseModel):
    issue_date_from: str = Field(..., description="Start date in ISO format")
    issue_date_to: str = Field(..., description="End date in ISO format")
    offset: int = Field(1, ge=1, description="Pagination offset")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")


class RequisitionLine(BaseModel):
    sku: str = Field(..., min_length=1, description="Product SKU")
    required_quantity: int = Field(..., gt=0, alias="requiredQuantity")
    unit_price_net: float = Field(..., ge=0, alias="unitPriceNet")
    unit_price_gross: float = Field(..., ge=0, alias="unitPriceGross")

    class Config:
        allow_population_by_field_name = True


class SubmitRequisitionRequest(BaseModel):
    lines: List[RequisitionLine] = Field(..., min_items=1)
    custom_number: Optional[str] = Field(None, alias="customNumber")
    delivery_method: Optional[str] = Field(None, alias="deliveryMethod")
    ship_to: Optional[str] = Field(None, alias="shipTo")
    deferred_payment: Optional[bool] = Field(None, alias="deferredPayment")
    comments: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class CancelRequisitionRequest(BaseModel):
    requisition_id: str = Field(..., min_length=1)
    ship_to: Optional[str] = None


class AuthRequest(BaseModel):
    client_id: str = Field(..., min_length=1)
    client_secret: str = Field(..., min_length=1)


class CalculateItemPriceRequest(BaseModel):
    lines: List[InventoryLine] = Field(..., min_items=1)

def _format_error_detail(
    status_code: int, message: str, details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": status_code,
            "message": message,
            "details": details or {},
        },
    }


async def handle_api_errors(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except IntercarsAPIError as e:
        logger.error(f"InterCars API error: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail=_format_error_detail(e.status_code, e.message, e.details),
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in InterCars adapter")
        raise HTTPException(
            status_code=500,
            detail=_format_error_detail(
                500, "Internal server error", {"exception": str(e)}
            ),
        ) from e


@router.post("/authorize")
async def authorize(
    request: AuthRequest,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(
        adapter.authenticate, request.client_id, request.client_secret
    )


@router.post("/inventory/quote")
async def inventory_quote(
    request: InventoryQuoteRequest,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    lines_data = [line.model_dump(by_alias=True) for line in request.lines]
    return await handle_api_errors(adapter.inventory_quote, lines_data)


@router.get("/search/products")
async def get_stock_balance(
    sku: List[str] = Query(..., description="List of SKUs"),
    location: Optional[List[str]] = Query(None, description="List of locations"),
    ship_to: Optional[str] = Query(None, description="Ship to location"),
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    if not sku:
        raise HTTPException(status_code=400, detail="At least one SKU is required")

    return await handle_api_errors(
        adapter.get_stock_balance, skus=sku, locations=location, ship_to=ship_to
    )


@router.post("/inventory/stock")
async def inventory_stock(
    request: InventoryStockRequest,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(
        adapter.inventory_stock, request.skus, request.location
    )


@router.get("/delivery/search")
async def search_deliveries(
    creation_date_from: str = Query(..., description="Start date"),
    creation_date_to: str = Query(..., description="End date"),
    offset: int = Query(1, ge=1, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(
        adapter.search_deliveries,
        creation_date_from,
        creation_date_to,
        offset,
        limit,
    )


@router.get("/delivery/{delivery_id}")
async def get_delivery(
    delivery_id: str,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    if not delivery_id.strip():
        raise HTTPException(status_code=400, detail="Delivery ID cannot be empty")

    return await handle_api_errors(adapter.get_delivery, delivery_id.strip())


@router.get("/invoice/search")
async def search_invoices(
    issue_date_from: str = Query(..., description="Start date"),
    issue_date_to: str = Query(..., description="End date"),
    offset: int = Query(1, ge=1, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(
        adapter.search_invoices, issue_date_from, issue_date_to, offset, limit
    )


@router.get("/invoice/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    if not invoice_id.strip():
        raise HTTPException(status_code=400, detail="Invoice ID cannot be empty")

    return await handle_api_errors(adapter.get_invoice, invoice_id.strip())


@router.get("/requisition/{requisition_id}")
async def get_requisition(
    requisition_id: str,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    if not requisition_id.strip():
        raise HTTPException(status_code=400, detail="Requisition ID cannot be empty")

    return await handle_api_errors(adapter.get_requisition, requisition_id.strip())


@router.post("/sales/requisition")
async def submit_requisition(
    request: SubmitRequisitionRequest,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    requisition_data = request.dict(exclude_none=True, by_alias=True)
    return await handle_api_errors(adapter.submit_requisition, requisition_data)


@router.post("/requisition/cancel")
async def cancel_requisition(
    request: CancelRequisitionRequest,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(
        adapter.cancel_requisition, request.requisition_id, request.ship_to
    )


@router.get("/sales/order/search")
async def search_orders(
    creation_date_from: str = Query(..., description="Start date"),
    creation_date_to: str = Query(..., description="End date"),
    offset: int = Query(1, ge=1, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(
        adapter.search_orders, creation_date_from, creation_date_to, offset, limit
    )


@router.get("/sales/order/{order_id}")
async def get_order(
    order_id: str,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    if not order_id.strip():
        raise HTTPException(status_code=400, detail="Order ID cannot be empty")

    return await handle_api_errors(adapter.get_order, order_id.strip())


@router.get("/customer")
async def get_customer(
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(adapter.get_customer)


@router.get("/customer/finances")
async def get_customer_finances(
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    return await handle_api_errors(adapter.get_customer_finances)


@router.post("/pricing/quote")
async def calculate_item_price(
    request: CalculateItemPriceRequest,
    adapter: IntercarsAdapter = Depends(get_intercars_adapter),
):
    lines_data = [line.model_dump(by_alias=True) for line in request.lines]
    return await handle_api_errors(adapter.calculate_item_price, lines_data)
