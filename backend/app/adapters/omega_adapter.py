import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from app.config import OMEGA_KEY

logger = logging.getLogger(__name__)


class OmegaAPIError(Exception):
    def __init__(
            self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"Omega API Error {status_code}: {message}")


class OmegaAdapter:
    BASE_URL = "https://public.omega.page"

    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0

    def __init__(self, key: str = None):
        self._key = key or OMEGA_KEY
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def _handle_response_errors(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        try:
            error_data = response.json()
        except (ValueError, TypeError):
            error_data = {"error": response.text}

        error_message = (
                error_data.get("message")
                or error_data.get("error")
                or error_data.get("detail")
                or "Unknown error"
        )

        raise OmegaAPIError(response.status_code, error_message, error_data)

    async def _validate_omega_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise OmegaAPIError(500, "Invalid response format from Omega API")

        success = data.get("Success")
        if success is False:
            errors = data.get("Errors", [])
            if errors and isinstance(errors, list) and len(errors) > 0:
                first_error = errors[0]
                if isinstance(first_error, dict):
                    error_msg = first_error.get("Description") or first_error.get("Error") or "API returned error"
                else:
                    error_msg = str(first_error)
            else:
                error_msg = "API request failed"
            raise OmegaAPIError(400, error_msg, {"errors": errors})

        return data

    async def _make_request(
            self,
            method: str,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self._key:
            raise OmegaAPIError(401, "Omega API key is required")

        client = await self._get_client()
        url = urljoin(self.BASE_URL, endpoint.lstrip("/"))

        headers = {"Content-Type": "application/json"}

        if json_data is None:
            json_data = {}
        json_data["Key"] = self._key

        for attempt in range(self.MAX_RETRIES):
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(
                        url, params=params, json=json_data, headers=headers
                    )
                else:
                    raise OmegaAPIError(400, f"Unsupported HTTP method: {method}")

                await self._handle_response_errors(response)

                try:
                    response_data = response.json()
                    return await self._validate_omega_response(response_data)
                except (ValueError, TypeError):
                    return {"Success": True, "Data": response.text}

            except OmegaAPIError:
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF * (2 ** attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                raise OmegaAPIError(
                    500, f"Network error after {self.MAX_RETRIES} attempts: {str(e)}"
                )

    async def get_account(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/profile/account")

    async def add_product_to_basket(self, product_id: int, count: int) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")
        if not isinstance(count, int) or count == 0:
            raise OmegaAPIError(400, "Count must be a non-zero integer")

        json_data = {"ProductId": product_id, "Count": count}
        return await self._make_request("POST", "/public/api/v1.0/basket/addProduct", json_data=json_data)

    async def add_product_list_to_basket(self, product_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not product_list:
            raise OmegaAPIError(400, "Product list cannot be empty")

        for i, product in enumerate(product_list):
            if not isinstance(product, dict):
                raise OmegaAPIError(400, f"Product at index {i} must be a dictionary")
            if "ProductId" not in product:
                raise OmegaAPIError(400, f"Product at index {i} must have 'ProductId' field")
            if "Count" not in product:
                raise OmegaAPIError(400, f"Product at index {i} must have 'Count' field")

            try:
                product_id = int(product["ProductId"])
                count = int(product["Count"])
                if count == 0:
                    raise OmegaAPIError(400, f"Product at index {i} count cannot be zero")
            except (ValueError, TypeError):
                raise OmegaAPIError(400, f"Product at index {i} has invalid ProductId or Count")

        json_data = {"ProductList": product_list}
        return await self._make_request("POST", "/public/api/v1.0/basket/addProductList", json_data=json_data)

    async def remove_product_from_basket(self, product_id: int) -> Dict[str, Any]:
        if not isinstance(product_id, int):
            raise OmegaAPIError(400, "Product ID must be an integer")

        json_data = {"ProductId": product_id}
        return await self._make_request("POST", "/public/api/v1.0/basket/removeProductFromBasket", json_data=json_data)

    async def get_basket(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/basket/getBasket")

    async def clear_basket(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/basket/clear")

    async def get_kind_claims(self, product_id: str, doc_id: str) -> Dict[str, Any]:
        if not product_id or not product_id.strip():
            raise OmegaAPIError(400, "Product ID cannot be empty")
        if not doc_id or not doc_id.strip():
            raise OmegaAPIError(400, "Document ID cannot be empty")

        json_data = {"ProductId": product_id.strip(), "DocId": doc_id.strip()}
        return await self._make_request("POST", "/public/api/v1.0/claims/getKindClaims", json_data=json_data)

    async def check_claim_kind(self, doc_id: str, kind_id: str, product_id: str) -> Dict[str, Any]:
        if not doc_id or not doc_id.strip():
            raise OmegaAPIError(400, "Document ID cannot be empty")
        if not kind_id or not kind_id.strip():
            raise OmegaAPIError(400, "Kind ID cannot be empty")
        if not product_id or not product_id.strip():
            raise OmegaAPIError(400, "Product ID cannot be empty")

        json_data = {
            "DocId": doc_id.strip(),
            "KindId": kind_id.strip(),
            "ProductId": product_id.strip(),
        }
        return await self._make_request("POST", "/public/api/v1.0/claims/checkClaimKind", json_data=json_data)

    async def get_discount(self, product_id: str, doc_id: str, type_id: str) -> Dict[str, Any]:
        if not product_id or not product_id.strip():
            raise OmegaAPIError(400, "Product ID cannot be empty")
        if not doc_id or not doc_id.strip():
            raise OmegaAPIError(400, "Document ID cannot be empty")
        if not type_id or not type_id.strip():
            raise OmegaAPIError(400, "Type ID cannot be empty")

        json_data = {
            "ProductId": product_id.strip(),
            "DocId": doc_id.strip(),
            "TypeId": type_id.strip(),
        }
        return await self._make_request("POST", "/public/api/v1.0/claims/getDiscount", json_data=json_data)

    async def get_contacts(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/claims/getContacts")

    async def upload_photo(self, product_id: Optional[str], data: str, file_name: str) -> Dict[str, Any]:
        if not data or not data.strip():
            raise OmegaAPIError(400, "Image data cannot be empty")
        if not file_name or not file_name.strip():
            raise OmegaAPIError(400, "File name cannot be empty")
        if not file_name.lower().endswith('.jpg'):
            raise OmegaAPIError(400, "File must be a JPEG (.jpg) image")

        json_data = {
            "ProductId": product_id.strip() if product_id else "",
            "Data": data.strip(),
            "FileName": file_name.strip(),
        }
        return await self._make_request("POST", "/public/api/v1.0/claims/uploadPhoto", json_data=json_data)

    async def get_addresses(self, kind: int) -> Dict[str, Any]:
        if not isinstance(kind, int):
            raise OmegaAPIError(400, "Kind must be an integer")

        json_data = {"Kind": kind}
        return await self._make_request("POST", "/public/api/v1.0/claims/getAddresses", json_data=json_data)

    async def create_claim(
            self,
            doc_id: str,
            products: List[Dict[str, Any]],
            comment: Optional[str] = None,
            contact_id: Optional[str] = None,
            phone_id: Optional[str] = None,
            address_key: Optional[str] = None,
            photos: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not doc_id or not doc_id.strip():
            raise OmegaAPIError(400, "Document ID cannot be empty")
        if not products:
            raise OmegaAPIError(400, "Products list cannot be empty")

        for i, product in enumerate(products):
            if not isinstance(product, dict):
                raise OmegaAPIError(400, f"Product at index {i} must be a dictionary")

            required_fields = ["ProductId", "DocId", "KindId"]
            for field in required_fields:
                if field not in product or not str(product[field]).strip():
                    raise OmegaAPIError(400, f"Product at index {i} must have non-empty '{field}' field")

            if "YearVehicle" in product:
                try:
                    year = int(product["YearVehicle"])
                    if year < 1000 or year > 9999:
                        raise OmegaAPIError(400, f"Product at index {i} YearVehicle must be between 1000 and 9999")
                except (ValueError, TypeError):
                    raise OmegaAPIError(400, f"Product at index {i} YearVehicle must be a valid integer")

            if "ReadyForDiscount" in product:
                try:
                    discount = int(product["ReadyForDiscount"])
                    if discount not in [0, 1]:
                        raise OmegaAPIError(400, f"Product at index {i} ReadyForDiscount must be 0 or 1")
                except (ValueError, TypeError):
                    raise OmegaAPIError(400, f"Product at index {i} ReadyForDiscount must be 0 or 1")

        json_data = {
            "DocId": doc_id.strip(),
            "Products": products,
        }

        if comment:
            json_data["Comment"] = comment.strip()
        if contact_id:
            json_data["ContactId"] = contact_id.strip()
        if phone_id:
            json_data["PhoneId"] = phone_id.strip()
        if address_key:
            json_data["AddressKey"] = address_key.strip()
        if photos:
            json_data["Photos"] = [photo.strip() for photo in photos if photo and photo.strip()]

        return await self._make_request("POST", "/public/api/v1.0/claims/createClaim", json_data=json_data)

    async def get_claims_list(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/claims/getClaimsList")

    async def download_refund_documents(self) -> Dict[str, Any]:
        return await self._make_request("POST", "/public/api/v1.0/claims/downloadRefundDocuments")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None