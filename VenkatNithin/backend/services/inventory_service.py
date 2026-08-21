"""
backend/services/inventory_service.py
-------------------------------------
Business logic for auditing material stock levels and raising low-stock alarms.
"""
from sqlalchemy.orm import Session
from backend.models.inventory import MaterialStock
from backend.models.dashboard import SystemNotification


def check_low_stock_alerts(db: Session, stock: MaterialStock):
    """
    Checks if a material's stock level has breached its safety threshold.
    Sets low-stock alarm flag and dispatches system notifications in real-time.
    """
    if stock.quantity <= stock.min_threshold:
        # Stock dips below or equal to threshold
        if not stock.low_stock_alert:
            stock.low_stock_alert = True
            
            # Create a System Notification
            notification = SystemNotification(
                title="🚨 Material Stock Low Alert",
                message=(
                    f"Material '{stock.material_name}' has fallen below the safety threshold. "
                    f"Current level: {stock.quantity} {stock.unit} (Min: {stock.min_threshold} {stock.unit})."
                )
            )
            db.add(notification)
    else:
        # Stock restored
        stock.low_stock_alert = False
