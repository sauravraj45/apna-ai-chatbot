
"""
Structured schemas for tool outputs.

Tools never return raw ORM objects or raw dict blobs from the database --
they return one of these typed, minimal-field schemas. This is what
enforces "the LLM should only receive the minimum required information"
from the project spec: sensitive/irrelevant columns are simply never
serialized here.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserProfileResult(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    member_since: Optional[datetime] = None


class AddressResult(BaseModel):
    id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class AddressListResult(BaseModel):
    addresses: List[AddressResult]


class OrderItemResult(BaseModel):
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None


class OrderSummaryResult(BaseModel):
    order_id: int
    status: Optional[str] = None
    payment_method: Optional[str] = None
    total_amount: Optional[float] = None
    tracking_id: Optional[str] = None
    placed_on: Optional[datetime] = None


class OrderDetailResult(OrderSummaryResult):
    items: List[OrderItemResult] = Field(default_factory=list)


class OrderListResult(BaseModel):
    orders: List[OrderSummaryResult]


class DeliveryAddressResult(BaseModel):
    order_id: int
    full_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None


# ===========================
# FAQ
# ===========================

class FAQResult(BaseModel):
    category: str
    topic: str
    answer: str
    next_actions: List[str] = Field(default_factory=list)


# ===========================
# Error
# ===========================

class ToolError(BaseModel):
    """
    Returned by a tool instead of raising an exception so the AI
    service can gracefully inform the user.
    """

    error: str
    
    
