from order_models import OrderItem


class InventoryGateway:
    def __init__(self, stock_by_sku: dict[str, int] | None = None):
        self.stock_by_sku = stock_by_sku or {}
        self.reservations: dict[str, int] = {}

    def check_availability(self, items: list[OrderItem]) -> tuple[bool, str]:
        for item in items:
            if item.is_digital:
                continue
            available = self.stock_by_sku.get(item.sku, 0) - self.reservations.get(item.sku, 0)
            if available < item.quantity:
                return False, f"insufficient_stock:{item.sku}"
        return True, "stock_ok"

    def reserve(self, items: list[OrderItem]) -> tuple[bool, str]:
        ok, reason = self.check_availability(items)
        if not ok:
            return False, reason

        for item in items:
            if item.is_digital:
                continue
            self.reservations[item.sku] = self.reservations.get(item.sku, 0) + item.quantity
        return True, "reserved"

    def release(self, items: list[OrderItem]) -> None:
        for item in items:
            if item.is_digital:
                continue
            current = self.reservations.get(item.sku, 0)
            remaining = max(current - item.quantity, 0)
            if remaining == 0:
                self.reservations.pop(item.sku, None)
            else:
                self.reservations[item.sku] = remaining
