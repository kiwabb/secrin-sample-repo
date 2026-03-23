from order_models import CustomerProfile, OrderItem, PaymentAuthorization


BLOCKED_COUNTRIES = {"KP", "IR"}
HIGH_RISK_CATEGORIES = {"gift_card", "crypto_voucher"}


class RiskEngine:
    def evaluate(self, customer: CustomerProfile, items: list[OrderItem], order_total: float) -> PaymentAuthorization:
        if customer.country in BLOCKED_COUNTRIES:
            return PaymentAuthorization(False, "blocked_country", "critical")

        if customer.failed_attempts_24h >= 5:
            return PaymentAuthorization(False, "too_many_failed_attempts", "high")

        risky_quantity = sum(item.quantity for item in items if item.category in HIGH_RISK_CATEGORIES)
        if risky_quantity >= 5 and not customer.is_corporate:
            return PaymentAuthorization(False, "high_risk_quantity", "high")

        contains_region_locked = any(item.restricted_region_only for item in items)
        if contains_region_locked and customer.country != "CN":
            return PaymentAuthorization(False, "restricted_region_item", "high")

        has_mixed_fulfillment = any(item.is_digital for item in items) and any(not item.is_digital for item in items)
        if has_mixed_fulfillment and order_total > 500:
            return PaymentAuthorization(False, "mixed_fulfillment_manual_review", "medium")

        if order_total > 1000 and not customer.is_corporate:
            return PaymentAuthorization(False, "amount_exceeds_personal_limit", "medium")

        return PaymentAuthorization(True, "approved", "low", auth_code="AUTH-OK")
