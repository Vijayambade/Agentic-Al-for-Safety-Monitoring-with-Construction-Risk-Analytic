"""
frontend/pages/inventory_manager.py
-----------------------------------
Standalone page for Smart Site Inventory & Material Management (Feature 9).
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from frontend.utils.api_client import APIClient


def show_inventory_manager_page():
    st.markdown(
        '# <span class="gradient-text">📦 Smart Site Inventory & Material Management</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Monitors real-time material stocks, logs site consumption and wastage, schedules purchase orders, and handles deliveries.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar control
    st.sidebar.markdown("### 🎛️ Data Controls")
    btn_reset = st.sidebar.button("🔄 Reset Inventory Data", use_container_width=True)

    # Handle Reset request
    try:
        if btn_reset:
            with st.spinner("Reverting stocks to baseline and clearing purchase orders..."):
                APIClient.reset_inventory_data()
                st.success("Inventory metrics reset successfully.")
    except Exception as e:
        st.error(f"Inventory system error: {str(e)}")

    # Fetch data
    stocks = []
    orders = []
    try:
        stocks = APIClient.get_inventory_stocks()
        orders = APIClient.get_inventory_orders()
    except Exception as e:
        st.error(f"Failed to fetch inventory records: {str(e)}")

    if stocks:
        stocks = sorted(stocks, key=lambda x: x["id"])
        
        # 2. KPI Metrics Cards
        total_assets = sum(s["quantity"] * s["unit_price"] for s in stocks)
        total_waste = sum(s["waste_quantity"] * s["unit_price"] for s in stocks)
        low_stock_count = sum(1 for s in stocks if s["low_stock_alert"])

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Total Asset Value", f"${round(total_assets, 2):,}")
        with col_metric2:
            st.metric("Low Stock Alerts", f"{low_stock_count} warnings", delta="Critical Alert" if low_stock_count > 0 else "All Clean", delta_color="inverse" if low_stock_count > 0 else "normal")
        with col_metric3:
            st.metric("Cumulative Waste Value", f"${round(total_waste, 2):,}", delta=f"+${round(total_waste, 2):,}" if total_waste > 0 else "0", delta_color="inverse")

        # 3. Main Stocks Table
        st.markdown("### 📋 Current Inventory Stocks")
        
        table_data = []
        for s in stocks:
            status_lbl = "🚨 LOW STOCK" if s["low_stock_alert"] else "🟢 In Stock"
            table_data.append({
                "ID": s["id"],
                "Material Name": s["material_name"],
                "Stock Quantity": f"{s['quantity']} {s['unit']}",
                "Unit Price": f"${s['unit_price']:.2f}",
                "Min Threshold": f"{s['min_threshold']} {s['unit']}",
                "Asset Value": f"${(s['quantity'] * s['unit_price']):,.2f}",
                "Wasted Amount": f"{s['waste_quantity']} {s['unit']}",
                "Status": status_lbl
            })
        
        st.table(pd.DataFrame(table_data))

        # 4. Action forms columns
        st.markdown("---")
        col_consume, col_reorder = st.columns(2)

        # 4a. Log Consumption Form
        with col_consume:
            st.markdown("### 🪵 Log Material Usage")
            mat_options_c = {s["material_name"]: s for s in stocks}
            
            with st.form("consume_form", clear_on_submit=True):
                selected_mat_c = st.selectbox("Select Material to Consume:", options=list(mat_options_c.keys()), key="consume_sel")
                amount_c = st.number_input("Consumed Quantity:", min_value=0.0, step=1.0)
                waste_c = st.number_input("Wastage Quantity:", min_value=0.0, step=1.0)
                btn_submit_c = st.form_submit_button("Submit Material Consumption", type="primary")

            if btn_submit_c:
                mat_obj = mat_options_c[selected_mat_c]
                if amount_c <= 0:
                    st.error("Consumption quantity must be greater than 0.")
                elif mat_obj["quantity"] < amount_c:
                    st.error(f"Insufficient stock of '{selected_mat_c}'. Max remaining: {mat_obj['quantity']} {mat_obj['unit']}.")
                else:
                    try:
                        APIClient.consume_inventory_material(mat_obj["id"], amount_c, waste_c)
                        st.success(f"Successfully logged usage of {amount_c} {mat_obj['unit']} for '{selected_mat_c}'.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # 4b. Reorder Purchase Form
        with col_reorder:
            st.markdown("### 🛒 Generate Purchase Order (PO)")
            mat_options_r = {s["material_name"]: s for s in stocks}
            
            # Form setup
            with st.form("reorder_form", clear_on_submit=True):
                selected_mat_r = st.selectbox("Select Material to Order:", options=list(mat_options_r.keys()), key="reorder_sel")
                
                # Pre-fill recommended quantity based on threshold
                rec_quantity = mat_options_r[selected_mat_r]["min_threshold"] * 2
                order_quantity = st.number_input("Reorder Quantity:", min_value=1.0, value=float(rec_quantity), step=10.0)
                
                btn_submit_r = st.form_submit_button("Generate Purchase Order", type="primary")

            if btn_submit_r:
                mat_obj = mat_options_r[selected_mat_r]
                try:
                    APIClient.reorder_inventory_material(mat_obj["id"], order_quantity)
                    st.success(f"Purchase order for {order_quantity} {mat_obj['unit']} of '{selected_mat_r}' generated successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Purchase Order Tracker
        st.markdown("---")
        st.markdown("### 🚚 Material Delivery & Pipeline Tracker")
        
        if orders:
            for ord_obj in orders:
                eta_str = datetime.fromisoformat(ord_obj["expected_delivery"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
                status_color = "orange"
                if ord_obj["status"] == "Shipped":
                    status_color = "blue"
                elif ord_obj["status"] == "Delivered":
                    status_color = "green"
                
                # Layout order info
                col_info, col_actions = st.columns([3, 2])
                with col_info:
                    st.markdown(
                        f"**Order #{ord_obj['id']}**: {ord_obj['material_name']} ({ord_obj['order_quantity']} units)  \n"
                        f"Total Cost: **${ord_obj['total_cost']:.2f}** | Delivery ETA: **{eta_str}**  \n"
                        f"Current status: :{status_color}[**{ord_obj['status']}**]"
                    )
                
                with col_actions:
                    if ord_obj["status"] == "Ordered":
                        if st.button("🚢 Mark as Shipped", key=f"ship_{ord_obj['id']}", use_container_width=True):
                            try:
                                APIClient.update_order_delivery_status(ord_obj["id"], "Shipped")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                    elif ord_obj["status"] == "Shipped":
                        if st.button("📥 Receive & Restock", key=f"receive_{ord_obj['id']}", use_container_width=True, type="primary"):
                            try:
                                APIClient.update_order_delivery_status(ord_obj["id"], "Delivered")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                    else:
                        st.write("✅ Stock Received")
                st.markdown("---")
        else:
            st.info("No active material purchase orders or shipments in transit.")
