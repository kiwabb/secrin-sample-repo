from inventory import InventoryGateway
from order_models import OrderDecision, OrderRequest, RefundDecision, RefundRequest
from pricing import build_breakdown
from risk import RiskEngine


class CheckoutService:
    def __init__(self, inventory: InventoryGateway, risk_engine: RiskEngine | None = None):
        self.inventory = inventory
        self.risk_engine = risk_engine or RiskEngine()

    def submit_order(self, request: OrderRequest) -> OrderDecision:
        if not request.items:
            denied = self.risk_engine.evaluate(request.customer, request.items, 0.0)
            denied.reason = "empty_order"
            return OrderDecision(False, "rejected", "empty_order", denied)

        stock_ok, stock_reason = self.inventory.check_availability(request.items)
        if not stock_ok:
            denied = self.risk_engine.evaluate(request.customer, request.items, 0.0)
            denied.reason = stock_reason
            return OrderDecision(False, "rejected", stock_reason, denied)

        breakdown = build_breakdown(
            items=request.items,
            customer=request.customer,
            coupon=request.coupon,
            points_to_redeem=request.points_to_redeem,
            destination_zone=request.destination_zone,
            is_first_order=request.is_first_order,
        )

        payment = self.risk_engine.evaluate(
            customer=request.customer,
            items=request.items,
            order_total=breakdown.grand_total,
        )
        if not payment.approved:
            return OrderDecision(False, "manual_review", payment.reason, payment, breakdown)

        reserved, reserve_reason = self.inventory.reserve(request.items)
        if not reserved:
            payment.reason = reserve_reason
            return OrderDecision(False, "rejected", reserve_reason, payment, breakdown)

        return OrderDecision(True, "accepted", "order_confirmed", payment, breakdown)


def evaluate_refund(request: RefundRequest) -> RefundDecision:
    if request.has_digital_items and request.hours_since_payment > 24 and not request.requested_by_support:
        return RefundDecision(False, 0.0, 0.0, "digital_items_past_refund_window")

    if request.delivered:
        restocking_fee = round(request.paid_amount * 0.08, 2)
        refund_amount = round(max(request.paid_amount - restocking_fee, 0.0), 2)
        return RefundDecision(True, refund_amount, restocking_fee, "delivered_return")

    if request.shipped and not request.delivered:
        restocking_fee = round(request.paid_amount * 0.03, 2)
        refund_amount = round(max(request.paid_amount - restocking_fee, 0.0), 2)
        return RefundDecision(True, refund_amount, restocking_fee, "in_transit_cancellation")

    return RefundDecision(True, request.paid_amount, 0.0, "pre_shipment_cancellation")
