from order_models import Coupon, CustomerProfile, OrderBreakdown, OrderItem


VIP_DISCOUNT_BY_TIER = {
    "silver": 0.02,
    "gold": 0.05,
    "platinum": 0.1,
}

ZONE_TAX_RATE = {
    "domestic": 0.06,
    "reduced": 0.03,
    "international": 0.0,
}


def calculate_subtotal(items: list[OrderItem], customer: CustomerProfile) -> tuple[float, list[str]]:
    subtotal = 0.0
    rules: list[str] = []

    for item in items:
        line_total = item.unit_price * item.quantity
        if item.category == "subscription" and customer.is_corporate:
            line_total *= 0.9
            rules.append(f"corporate_subscription_discount:{item.sku}")
        subtotal += line_total

    tier_discount = VIP_DISCOUNT_BY_TIER.get(customer.tier, 0.0)
    if tier_discount:
        subtotal *= 1 - tier_discount
        rules.append(f"tier_discount:{customer.tier}")

    return round(subtotal, 2), rules


def calculate_coupon_discount(
    subtotal: float,
    items: list[OrderItem],
    customer: CustomerProfile,
    coupon: Coupon | None,
    is_first_order: bool,
) -> tuple[float, list[str]]:
    if coupon is None:
        return 0.0, []
    if subtotal < coupon.min_subtotal:
        return 0.0, ["coupon_rejected:min_subtotal"]
    if coupon.allowed_tiers and customer.tier not in coupon.allowed_tiers:
        return 0.0, ["coupon_rejected:tier_not_allowed"]
    if coupon.first_order_only and not is_first_order:
        return 0.0, ["coupon_rejected:not_first_order"]

    scoped_subtotal = subtotal
    if coupon.category_scope:
        scoped_subtotal = sum(
            item.unit_price * item.quantity for item in items if item.category == coupon.category_scope
        )
        if scoped_subtotal <= 0:
            return 0.0, ["coupon_rejected:category_scope_empty"]

    if coupon.discount_type == "percent":
        return round(scoped_subtotal * coupon.value, 2), [f"coupon_applied:{coupon.code}"]
    if coupon.discount_type == "fixed":
        return round(min(coupon.value, scoped_subtotal), 2), [f"coupon_applied:{coupon.code}"]

    return 0.0, ["coupon_rejected:unknown_type"]


def calculate_points_credit(customer: CustomerProfile, requested_points: int, subtotal: float) -> tuple[float, list[str]]:
    if requested_points <= 0 or customer.loyalty_points <= 0:
        return 0.0, []

    usable_points = min(requested_points, customer.loyalty_points, int(subtotal * 100))
    credit = round(usable_points / 100, 2)
    return credit, [f"points_redeemed:{usable_points}"]


def calculate_shipping_fee(items: list[OrderItem], zone: str, subtotal_after_discount: float) -> tuple[float, list[str]]:
    if all(item.is_digital for item in items):
        return 0.0, ["shipping_waived:digital_only"]
    if subtotal_after_discount >= 120:
        return 0.0, ["shipping_waived:threshold"]

    base = 8.0 if zone == "domestic" else 18.0
    bulky_count = sum(item.quantity for item in items if item.category in {"hardware", "appliance"})
    surcharge = bulky_count * 2.5
    return round(base + surcharge, 2), ["shipping_charged:standard"]


def calculate_tax_amount(taxable_amount: float, zone: str, tax_exempt: bool) -> tuple[float, list[str]]:
    if tax_exempt or zone == "international":
        return 0.0, ["tax_skipped"]
    rate = ZONE_TAX_RATE.get(zone, 0.06)
    return round(taxable_amount * rate, 2), [f"tax_rate:{rate}"]


def build_breakdown(
    items: list[OrderItem],
    customer: CustomerProfile,
    coupon: Coupon | None,
    points_to_redeem: int,
    destination_zone: str,
    is_first_order: bool,
) -> OrderBreakdown:
    subtotal, rules = calculate_subtotal(items, customer)

    discount_total, discount_rules = calculate_coupon_discount(
        subtotal=subtotal,
        items=items,
        customer=customer,
        coupon=coupon,
        is_first_order=is_first_order,
    )
    rules.extend(discount_rules)

    points_credit, point_rules = calculate_points_credit(customer, points_to_redeem, subtotal - discount_total)
    rules.extend(point_rules)

    discounted_subtotal = max(subtotal - discount_total - points_credit, 0.0)
    shipping_fee, shipping_rules = calculate_shipping_fee(items, destination_zone, discounted_subtotal)
    rules.extend(shipping_rules)

    tax_total, tax_rules = calculate_tax_amount(discounted_subtotal + shipping_fee, destination_zone, customer.tax_exempt)
    rules.extend(tax_rules)

    grand_total = round(discounted_subtotal + shipping_fee + tax_total, 2)
    return OrderBreakdown(
        subtotal=subtotal,
        discount_total=discount_total,
        points_credit=points_credit,
        shipping_fee=shipping_fee,
        tax_total=tax_total,
        grand_total=grand_total,
        applied_rules=rules,
    )
