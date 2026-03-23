from checkout import CheckoutService, evaluate_refund
from inventory import InventoryGateway
from order_models import Coupon, CustomerProfile, OrderItem, OrderRequest, RefundRequest


def run_checkout_demo() -> None:
    inventory = InventoryGateway(
        {
            "LAPTOP-15": 5,
            "MOUSE-01": 20,
            "LICENSE-PRO": 999,
        }
    )
    service = CheckoutService(inventory=inventory)

    customer = CustomerProfile(
        customer_id="cust-100",
        tier="gold",
        country="CN",
        loyalty_points=1800,
        failed_attempts_24h=1,
    )
    items = [
        OrderItem("LAPTOP-15", "hardware", 899.0, 1),
        OrderItem("MOUSE-01", "hardware", 49.0, 2),
        OrderItem("LICENSE-PRO", "subscription", 199.0, 1, is_digital=True),
    ]
    coupon = Coupon(
        code="WELCOME10",
        discount_type="percent",
        value=0.10,
        min_subtotal=300.0,
        allowed_tiers=("gold", "platinum"),
        first_order_only=True,
    )
    request = OrderRequest(
        customer=customer,
        items=items,
        coupon=coupon,
        points_to_redeem=1200,
        destination_zone="domestic",
        is_first_order=True,
    )

    decision = service.submit_order(request)
    print("ORDER ACCEPTED:", decision.accepted)
    print("ORDER STATUS:", decision.status)
    print("ORDER REASON:", decision.reason)
    if decision.breakdown:
        print("TOTAL:", decision.breakdown.grand_total)
        print("RULES:", ", ".join(decision.breakdown.applied_rules))


def run_refund_demo() -> None:
    refund = evaluate_refund(
        RefundRequest(
            order_id="order-001",
            paid_amount=1399.0,
            shipped=True,
            delivered=False,
            has_digital_items=True,
            hours_since_payment=6,
        )
    )
    print("REFUND APPROVED:", refund.approved)
    print("REFUND AMOUNT:", refund.refund_amount)
    print("REFUND REASON:", refund.reason)


if __name__ == "__main__":
    run_checkout_demo()
    run_refund_demo()
