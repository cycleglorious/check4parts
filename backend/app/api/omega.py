import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.adapters.omega_adapter import OmegaAdapter, OmegaAPIError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/omega", tags=["omega"])


class BasketProductItem(BaseModel):
    product_id: int = Field(..., description="Product ID")
    count: int = Field(..., gt=0, description="Product count must be positive")


class AddProductRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    count: int = Field(..., description="Product count (can be negative to reduce)")


class AddProductListRequest(BaseModel):
    product_list: List[BasketProductItem] = Field(
        ..., min_items=1, description="List of products to add"
    )


class RemoveProductRequest(BaseModel):
    product_id: int = Field(..., description="Product ID to remove")


class ClaimProductBase(BaseModel):
    product_id: str = Field(..., description="Product ID")
    doc_id: str = Field(..., description="Document ID")
    kind_id: str = Field(..., description="Kind of claim")
    text: Optional[str] = Field(None, description="Claim text")
    quantity: Optional[str] = Field(None, description="Quantity")
    sum_claim: Optional[float] = Field(None, ge=0, description="Claim sum")
    vin: Optional[str] = Field(None, description="VIN number for hidden defects")
    car_mark: Optional[str] = Field(None, description="Car mark for hidden defects")
    car_model: Optional[str] = Field(None, description="Car model for hidden defects")
    year_vehicle: Optional[int] = Field(
        None, ge=1000, le=9999, description="Vehicle year for hidden defects"
    )
    ready_for_discount: Optional[int] = Field(
        None, ge=0, le=1, description="Ready for discount (0 or 1)"
    )


class CreateClaimRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    comment: Optional[str] = Field(None, description="Claim comment")
    contact_id: Optional[str] = Field(None, description="Contact ID")
    phone_id: Optional[str] = Field(None, description="Phone ID")
    address_key: Optional[str] = Field(None, description="Address key")
    products: List[ClaimProductBase] = Field(
        ..., min_items=1, description="List of products for claim"
    )
    photos: Optional[List[str]] = Field(
        None, description="List of photo reference keys"
    )


class UploadPhotoRequest(BaseModel):
    product_id: Optional[str] = Field(None, description="Product ID")
    data: str = Field(..., description="Base64 encoded image data")
    file_name: str = Field(..., description="File name with .jpg extension")

    @field_validator("file_name")
    def validate_file_extension(cls, v):
        if not v.lower().endswith(".jpg"):
            raise ValueError("File name must end with .jpg extension")
        return v


class GetKindClaimsRequest(BaseModel):
    product_id: str = Field(..., description="Product ID")
    doc_id: str = Field(..., description="Document ID")


class CheckClaimKindRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    kind_id: str = Field(..., description="Kind ID")
    product_id: str = Field(..., description="Product ID")


class GetDiscountRequest(BaseModel):
    product_id: str = Field(..., description="Product ID")
    doc_id: str = Field(..., description="Document ID")
    type_id: str = Field(..., description="Type ID")


class GetAddressesRequest(BaseModel):
    kind: int = Field(..., description="Address kind")


class GetContactListRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")


class AddContactRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    first_name: str = Field(..., description="First name")
    second_name: str = Field(..., description="Second name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")


class EditContactRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    first_name: str = Field(..., description="First name")
    second_name: str = Field(..., description="Second name")
    last_name: str = Field(..., description="Last name")


class RemoveContactRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")


class AddContactPhoneRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    phone: str = Field(..., description="Phone number")


class RemoveContactPhoneRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")
    phone: str = Field(..., description="Phone number")


class GetContactDetailsRequest(BaseModel):
    contact_id: str = Field(..., description="Contact ID")


class GetExpenseDocumentRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


class GetExpenseDocumentListRequest(BaseModel):
    start_date: str = Field(..., description="Start date in DD.MM.YYYY format")
    end_date: str = Field(..., description="End date in DD.MM.YYYY format")

    @field_validator("start_date", "end_date")
    def validate_date_format(cls, v):
        from datetime import datetime

        try:
            datetime.strptime(v, "%d.%m.%Y")
            return v
        except ValueError:
            raise ValueError("Date must be in DD.MM.YYYY format")


class GetExpenseDocumentDetailsRequest(BaseModel):
    doc_id: str = Field(..., description="Document ID")


async def handle_api_errors(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except OmegaAPIError as e:
        logger.error(f"Omega API error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in Omega adapter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/profile/account")
async def get_account():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_account)


@router.post("/basket/add-product")
async def add_product_to_basket(request: AddProductRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_product_to_basket, request.product_id, request.count
        )


@router.post("/basket/add-product-list")
async def add_product_list_to_basket(request: AddProductListRequest):
    async with OmegaAdapter() as adapter:
        products_data = [
            {"ProductId": item.product_id, "Count": item.count}
            for item in request.product_list
        ]
        return await handle_api_errors(
            adapter.add_product_list_to_basket, products_data
        )


@router.post("/basket/remove-product")
async def remove_product_from_basket(request: RemoveProductRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.remove_product_from_basket, request.product_id
        )


@router.post("/basket/get")
async def get_basket():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_basket)


@router.post("/basket/clear")
async def clear_basket():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.clear_basket)


@router.post("/claims/kind-claims")
async def get_kind_claims(request: GetKindClaimsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_kind_claims, request.product_id, request.doc_id
        )


@router.post("/claims/check-claim-kind")
async def check_claim_kind(request: CheckClaimKindRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.check_claim_kind,
            request.doc_id,
            request.kind_id,
            request.product_id,
        )


@router.post("/claims/discount")
async def get_discount(request: GetDiscountRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_discount, request.product_id, request.doc_id, request.type_id
        )


@router.post("/claims/contacts")
async def get_contacts():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contacts)


@router.post("/claims/upload-photo")
async def upload_photo(request: UploadPhotoRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.upload_photo, request.product_id, request.data, request.file_name
        )


@router.post("/claims/addresses")
async def get_addresses(request: GetAddressesRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_addresses, request.kind)


@router.post("/claims/create")
async def create_claim(request: CreateClaimRequest):
    async with OmegaAdapter() as adapter:
        products_data = []
        for product in request.products:
            product_dict = {
                "ProductId": product.product_id,
                "DocId": product.doc_id,
                "KindId": product.kind_id,
            }

            if product.text:
                product_dict["Text"] = product.text
            if product.quantity:
                product_dict["Quantity"] = product.quantity
            if product.sum_claim is not None:
                product_dict["SumClaim"] = product.sum_claim

            if product.vin:
                product_dict["Vin"] = product.vin
            if product.car_mark:
                product_dict["CarMark"] = product.car_mark
            if product.car_model:
                product_dict["CarModel"] = product.car_model
            if product.year_vehicle:
                product_dict["YearVehicle"] = product.year_vehicle
            if product.ready_for_discount is not None:
                product_dict["ReadyForDiscount"] = product.ready_for_discount

            products_data.append(product_dict)

        return await handle_api_errors(
            adapter.create_claim,
            request.doc_id,
            products_data,
            request.comment,
            request.contact_id,
            request.phone_id,
            request.address_key,
            request.photos,
        )


@router.post("/claims/list")
async def get_claims_list():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_claims_list)


@router.post("/claims/download-refund-documents")
async def download_refund_documents():
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.download_refund_documents)


# Contact endpoints
@router.post("/contact/get-contacts")
async def get_contact_list(request: GetContactListRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_list, request.customer_id)


@router.post("/contact/add-contact")
async def add_contact(request: AddContactRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_contact,
            request.customer_id,
            request.first_name,
            request.second_name,
            request.last_name,
            request.phone,
        )


@router.post("/contact/edit-contact")
async def edit_contact(request: EditContactRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.edit_contact,
            request.contact_id,
            request.first_name,
            request.second_name,
            request.last_name,
        )


@router.post("/contact/remove-contact")
async def remove_contact(request: RemoveContactRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.remove_contact, request.contact_id)


@router.post("/contact/add-contact-phone")
async def add_contact_phone(request: AddContactPhoneRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.add_contact_phone, request.contact_id, request.phone
        )


@router.post("/contact/remove-contact-phone")
async def remove_contact_phone(request: RemoveContactPhoneRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.remove_contact_phone, request.contact_id, request.phone
        )


@router.post("/contact/get-contact-details")
async def get_contact_details(request: GetContactDetailsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_details, request.contact_id)


# Expense document endpoints
@router.post("/expense/get-expense-document")
async def get_expense_document(request: GetExpenseDocumentRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_expense_document, request.doc_id)


@router.post("/expense/get-expense-document-list")
async def get_expense_document_list(request: GetExpenseDocumentListRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_expense_document_list, request.start_date, request.end_date
        )


@router.post("/expense/get-expense-document-details")
async def get_expense_document_details(request: GetExpenseDocumentDetailsRequest):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_expense_document_details, request.doc_id
        )


# GET endpoints (existing ones kept for backward compatibility)
@router.get("/basket/add-product")
async def add_product_to_basket_query(
    product_id: int = Query(..., description="Product ID"),
    count: int = Query(..., gt=0, description="Product count must be positive"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.add_product_to_basket, product_id, count)


@router.get("/basket/remove-product")
async def remove_product_from_basket_query(
    product_id: int = Query(..., description="Product ID to remove"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.remove_product_from_basket, product_id)


@router.get("/claims/kind-claims")
async def get_kind_claims_query(
    product_id: str = Query(..., description="Product ID"),
    doc_id: str = Query(..., description="Document ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_kind_claims, product_id, doc_id)


@router.get("/claims/discount")
async def get_discount_query(
    product_id: str = Query(..., description="Product ID"),
    doc_id: str = Query(..., description="Document ID"),
    type_id: str = Query(..., description="Type ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_discount, product_id, doc_id, type_id
        )


@router.get("/claims/addresses")
async def get_addresses_query(
    kind: int = Query(..., description="Address kind"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_addresses, kind)


@router.get("/contact/get-contacts")
async def get_contact_list_query(
    customer_id: str = Query(..., description="Customer ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_list, customer_id)


@router.get("/contact/get-contact-details")
async def get_contact_details_query(
    contact_id: str = Query(..., description="Contact ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_contact_details, contact_id)


@router.get("/expense/get-expense-document")
async def get_expense_document_query(
    doc_id: str = Query(..., description="Document ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_expense_document, doc_id)


@router.get("/expense/get-expense-document-list")
async def get_expense_document_list_query(
    start_date: str = Query(..., description="Start date in DD.MM.YYYY format"),
    end_date: str = Query(..., description="End date in DD.MM.YYYY format"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(
            adapter.get_expense_document_list, start_date, end_date
        )


@router.get("/expense/get-expense-document-details")
async def get_expense_document_details_query(
    doc_id: str = Query(..., description="Document ID"),
):
    async with OmegaAdapter() as adapter:
        return await handle_api_errors(adapter.get_expense_document_details, doc_id)
