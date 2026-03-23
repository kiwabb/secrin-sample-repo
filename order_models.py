from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CustomerProfile:
    customer_id: str
    tier: str
    country: str
    tax_exempt: bool = False
    loyalty_points: int = 0
    failed_attempts_24h: int = 0
    is_corporate: bool = False


@dataclass
class OrderItem:
    sku: str
    category: str
    unit_price: float
    quantity: int
    is_digital: bool = False
    restricted_region_only: bool = False


@dataclass
class Coupon:
    code: str
    discount_type: str
    value: float
    min_subtotal: float = 0.0
    allowed_tiers: tuple[str, ...] = ()
    category_scope: Optional[str] = None
    first_order_only: bool = False


@dataclass
class OrderRequest:
    customer: CustomerProfile
    items: list[OrderItem]
    coupon: Optional[Coupon] = None
    points_to_redeem: int = 0
    destination_zone: str = "domestic"
    is_first_order: bool = False


@dataclass
class PaymentAuthorization:
    approved: bool
    reason: str
    risk_level: str
    auth_code: str = ""


@dataclass
class OrderBreakdown:
    subtotal: float
    discount_total: float
    points_credit: float
    shipping_fee: float
    tax_total: float
    grand_total: float
    applied_rules: list[str] = field(default_factory=list)


@dataclass
class OrderDecision:
    accepted: bool
    status: str
    reason: str
    payment: PaymentAuthorization
    breakdown: Optional[OrderBreakdown] = None


@dataclass
class RefundRequest:
    order_id: str
    paid_amount: float
    shipped: bool
    delivered: bool
    has_digital_items: bool
    hours_since_payment: int
    requested_by_support: bool = False


@dataclass
class RefundDecision:
    approved: bool
    refund_amount: float
    restocking_fee: float
    reason: str
