"""
Real Estate Management System (Streamlit)
All code lives in this one file. Data is stored in st.session_state and persisted
to a local JSON file (real_estate_data.json). Uses Pakistani Rupees (PKR).
"""

import json
import os
from datetime import datetime, date

import pandas as pd
import streamlit as st

DATA_FILE = "real_estate_data.json"

# --- Constants ---
PROPERTY_TYPES = [
    "House",
    "Apartment",
    "Residential Plot",
    "Commercial Plot",
    "Shop",
    "Office",
    "Farmhouse",
]
LISTING_TYPES = ["For Sale", "For Rent"]
PROPERTY_STATUSES = ["Available", "Under Negotiation", "Sold", "Rented"]
AREA_UNITS = ["Marla", "Kanal", "Square Feet"]
CUSTOMER_TYPES = ["Buyer", "Seller", "Tenant", "Landlord"]
AGENT_STATUSES = ["Active", "On Leave", "Resigned"]
INQUIRY_STATUSES = [
    "New",
    "Contacted",
    "Viewing Scheduled",
    "Negotiation",
    "Converted",
    "Closed",
]
TRANSACTION_STATUSES = ["Completed", "Pending", "Cancelled"]
PAYMENT_STATUSES = ["Paid", "Pending", "Partially Paid", "Overdue"]
PAYMENT_TYPES = [
    "Sale Payment",
    "Monthly Rent",
    "Security Deposit",
    "Commission",
    "Other",
]
PAYMENT_METHODS = ["Cash", "Bank Transfer", "Other"]
RENTAL_STATUSES = ["Active", "Expired", "Terminated"]

st.set_page_config(
    page_title="Real Estate Management Dashboard", page_icon="🏢", layout="wide"
)

# --- Modern Styling ---
st.markdown(
    """
<style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border-left: 5px solid #10b981;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #065f46; }
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background-color: #059669;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Default Data Layer ---
def default_db():
    return {
        "properties": [
            {
                "id": "PROP-101",
                "title": "Luxury 1 Kanal Modern House",
                "type": "House",
                "listing_type": "For Sale",
                "price": 45000000.0,
                "city": "Islamabad",
                "area": "F-7/2",
                "address": "House # 42, Street 15",
                "bedrooms": 5,
                "bathrooms": 6,
                "covered_area": 4500.0,
                "area_unit": "Square Feet",
                "owner_name": "Ahmed Khan",
                "owner_contact": "+923001234567",
                "assigned_agent": "AG-01 - Ali Raza",
                "description": "Brand new luxury villa with high-end finishes and lush green lawn.",
                "listing_date": str(date.today()),
                "status": "Available",
                "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
            },
            {
                "id": "PROP-102",
                "title": "Executive Luxury Apartment",
                "type": "Apartment",
                "listing_type": "For Rent",
                "price": 120000.0,
                "city": "Lahore",
                "area": "Gulberg III",
                "address": "Apartment 4B, Eden Heights",
                "bedrooms": 2,
                "bathrooms": 2,
                "covered_area": 1200.0,
                "area_unit": "Square Feet",
                "owner_name": "Usman Malik",
                "owner_contact": "+923219876543",
                "assigned_agent": "AG-02 - Fatima Noor",
                "description": "Fully furnished luxury apartment with backup generator and security.",
                "listing_date": str(date.today()),
                "status": "Available",
                "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00",
            },
        ],
        "customers": [
            {
                "id": "CUST-01",
                "full_name": "Bilal Ahmed",
                "phone": "+923334445566",
                "email": "bilal@example.com",
                "city": "Islamabad",
                "address": "Sector G-8/4",
                "type": "Buyer",
                "reg_date": str(date.today()),
                "notes": "Looking for modern houses in F sectors.",
            },
            {
                "id": "CUST-02",
                "full_name": "Zainab Bibi",
                "phone": "+923125557788",
                "email": "zainab@example.com",
                "city": "Lahore",
                "address": "DHA Phase 5",
                "type": "Tenant",
                "reg_date": str(date.today()),
                "notes": "Interested in 2-bed furnished apartments.",
            },
        ],
        "agents": [
            {
                "id": "AG-01",
                "full_name": "Ali Raza",
                "phone": "+923001112233",
                "email": "ali.raza@realestate.com",
                "office_location": "Blue Area, Islamabad",
                "joining_date": "2024-01-15",
                "commission_pct": 2.0,
                "status": "Active",
            },
            {
                "id": "AG-02",
                "full_name": "Fatima Noor",
                "phone": "+923223334455",
                "email": "fatima.noor@realestate.com",
                "office_location": "Gulberg, Lahore",
                "joining_date": "2024-03-10",
                "commission_pct": 2.5,
                "status": "Active",
            },
        ],
        "inquiries": [],
        "transactions": [],
        "rentals": [],
        "payments": [],
        "counters": {
            "PROP": 102,
            "CUST": 2,
            "AG": 2,
            "INQ": 0,
            "TX": 0,
            "RENT": 0,
            "PAY": 0,
        },
    }


def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default_db()


def save_db():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.db, f, indent=2)
    except OSError:
        st.warning("Could not save to disk; data maintained for this session only.")


if "db" not in st.session_state:
    st.session_state.db = load_db()
db = st.session_state.db


def generate_id(prefix):
    db["counters"][prefix] += 1
    return f"{prefix}-{db['counters'][prefix]:03d}"


def format_pkr(amount):
    try:
        return f"PKR {float(amount):,.0f}"
    except (ValueError, TypeError):
        return "PKR 0"


def fallback_image():
    return "https://images.unsplash.com/photo-1560518883-ce09059eeffa"


# --- Sidebar Navigation ---
st.sidebar.title("🏢 Real Estate Hub")
st.sidebar.markdown("---")
menu_option = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard Overview",
        "Property Management",
        "Customer Management",
        "Agent Management",
        "Inquiries & Viewings",
        "Sales & Transactions",
        "Rental Management",
        "Payment Management",
        "Reports & Analytics",
        "About & Help",
    ],
)
st.sidebar.markdown("---")
if st.sidebar.button("💾 Save Database State"):
    save_db()
    st.sidebar.success("Database state successfully saved!")


# ==========================================
# 1. DASHBOARD OVERVIEW
# ==========================================
if menu_option == "Dashboard Overview":
    st.title("🏢 Real Estate Agency Dashboard")
    st.markdown(
        "Welcome to your professional real estate management control center."
    )

    # Dynamic KPI Calculations
    total_props = len(db["properties"])
    avail_props = len([p for p in db["properties"] if p["status"] == "Available"])
    sold_props = len([p for p in db["properties"] if p["status"] == "Sold"])
    rented_props = len([p for p in db["properties"] if p["status"] == "Rented"])
    negotiation_props = len(
        [p for p in db["properties"] if p["status"] == "Under Negotiation"]
    )

    total_customers = len(db["customers"])
    total_agents = len(db["agents"])

    completed_txs = [
        t for t in db["transactions"] if t["transaction_status"] == "Completed"
    ]
    total_sales_revenue = sum([float(t["sale_price"]) for t in completed_txs])

    completed_rents = [
        r for r in db["rentals"] if r["agreement_status"] == "Active"
    ]
    active_rental_income = sum([float(r["monthly_rent"]) for r in completed_rents])

    pending_payments_amt = sum(
        [
            float(p["amount"])
            for p in db["payments"]
            if p["payment_status"] in ["Pending", "Partially Paid", "Overdue"]
        ]
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Properties", total_props)
        st.metric("Available Properties", avail_props)
    with col2:
        st.metric("Sold Properties", sold_props)
        st.metric("Rented Properties", rented_props)
    with col3:
        st.metric("Under Negotiation", negotiation_props)
        st.metric("Registered Customers", total_customers)
    with col4:
        st.metric("Total Sales Revenue", format_pkr(total_sales_revenue))
        st.metric("Active Monthly Rent", format_pkr(active_rental_income))

    st.markdown("---")
    col_kpi5, col_kpi6 = st.columns(2)
    with col_kpi5:
        st.metric("Registered Agents", total_agents)
    with col_kpi6:
        st.metric("Pending Payments Amount", format_pkr(pending_payments_amt))

    st.markdown("### 📊 Quick Insights & Recent Activity")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Recent Property Listings")
        if db["properties"]:
            df_props = pd.DataFrame(db["properties"])[
                ["id", "title", "type", "listing_type", "price", "status"]
            ]
            st.dataframe(df_props.tail(5), use_container_width=True)
        else:
            st.info("No properties listed yet.")

    with c2:
        st.subheader("Recent Transactions")
        if db["transactions"]:
            df_tx = pd.DataFrame(db["transactions"])[
                [
                    "id",
                    "property_id",
                    "buyer_id",
                    "sale_price",
                    "transaction_status",
                ]
            ]
            st.dataframe(df_tx.tail(5), use_container_width=True)
        else:
            st.info("No sales transactions recorded yet.")


# ==========================================
# 2. PROPERTY MANAGEMENT
# ==========================================
elif menu_option == "Property Management":
    st.title("🏠 Property Management")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["View Properties", "Add Property", "Edit Property", "Delete Property"]
    )

    with tab1:
        st.subheader("Property Catalog & Search")
        search_query = st.text_input(
            "Search by Title, City, Area, or Property ID"
        )
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            f_type = st.selectbox(
                "Filter by Type", ["All"] + PROPERTY_TYPES
            )
        with col_f2:
            f_listing = st.selectbox(
                "Filter by Listing Type", ["All"] + LISTING_TYPES
            )
        with col_f3:
            f_status = st.selectbox("Filter by Status", ["All"] + PROPERTY_STATUSES)

        filtered = db["properties"]
        if search_query:
            q = search_query.lower()
            filtered = [
                p
                for p in filtered
                if q in p["id"].lower()
                or q in p["title"].lower()
                or q in p["city"].lower()
                or q in p["area"].lower()
            ]
        if f_type != "All":
            filtered = [p for p in filtered if p["type"] == f_type]
        if f_listing != "All":
            filtered = [p for p in filtered if p["listing_type"] == f_listing]
        if f_status != "All":
            filtered = [p for p in filtered if p["status"] == f_status]

        if filtered:
            for p in filtered:
                with st.container():
                    col_img, col_det = st.columns([1, 3])
                    with col_img:
                        img = (
                            p["image_url"]
                            if p.get("image_url")
                            else fallback_image()
                        )
                        st.image(img, use_container_width=True)
                    with col_det:
                        st.markdown(f"### {p['title']} (`{p['id']}`)")
                        st.write(
                            f"**Type:** {p['type']} | **Listing:** {p['listing_type']} | **Status:** {p['status']}"
                        )
                        st.write(
                            f"**Location:** {p['area']}, {p['city']} | **Price/Rent:** {format_pkr(p['price'])}"
                        )
                        st.write(
                            f"**Bedrooms:** {p['bedrooms']} | **Bathrooms:** {p['bathrooms']} | **Covered Area:** {p['covered_area']} {p['area_unit']}"
                        )
                        st.write(
                            f"**Owner:** {p['owner_name']} ({p['owner_contact']}) | **Agent:** {p['assigned_agent']}"
                        )
                        with st.expander("View Full Description"):
                            st.write(p["description"])
                    st.markdown("---")
        else:
            st.info("No properties match your filter criteria.")

    with tab2:
        st.subheader("Add New Property")
        with st.form("add_prop_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_id = st.text_input(
                    "Property ID (e.g., PROP-103)",
                    value=generate_id("PROP"),
                )
                title = st.text_input("Property Title")
                p_type = st.selectbox("Property Type", PROPERTY_TYPES)
                listing_type = st.selectbox("Listing Type", LISTING_TYPES)
                price = st.number_input(
                    "Price / Monthly Rent (PKR)", min_value=0.0, step=10000.0
                )
                city = st.text_input("City")
                area = st.text_input("Area / Sector")
                address = st.text_input("Complete Address")
            with c2:
                bedrooms = st.number_input(
                    "Bedrooms", min_value=0, max_value=20, step=1
                )
                bathrooms = st.number_input(
                    "Bathrooms", min_value=0, max_value=20, step=1
                )
                covered_area = st.number_input(
                    "Covered Area", min_value=0.0, step=50.0
                )
                area_unit = st.selectbox("Area Unit", AREA_UNITS)
                owner_name = st.text_input("Owner Name")
                owner_contact = st.text_input("Owner Contact Number")
                agent_list = [
                    f"{a['id']} - {a['full_name']}" for a in db["agents"]
                ]
                assigned_agent = st.selectbox(
                    "Assigned Agent", agent_list if agent_list else ["None"]
                )
                status = st.selectbox("Availability Status", PROPERTY_STATUSES)

            description = st.text_area("Property Description")
            image_url = st.text_input(
                "Optional Image URL",
                placeholder="https://example.com/image.jpg",
            )

            submitted = st.form_submit_button("Save Property")
            if submitted:
                if not title or not city:
                    st.error("Please fill in all required fields (Title, City).")
                elif any(p["id"] == p_id for p in db["properties"]):
                    st.error(
                        f"Property ID '{p_id}' already exists. Please use a unique ID."
                    )
                else:
                    new_prop = {
                        "id": p_id,
                        "title": title,
                        "type": p_type,
                        "listing_type": listing_type,
                        "price": price,
                        "city": city,
                        "area": area,
                        "address": address,
                        "bedrooms": bedrooms,
                        "bathrooms": bathrooms,
                        "covered_area": covered_area,
                        "area_unit": area_unit,
                        "owner_name": owner_name,
                        "owner_contact": owner_contact,
                        "assigned_agent": assigned_agent,
                        "description": description,
                        "listing_date": str(date.today()),
                        "status": status,
                        "image_url": image_url,
                    }
                    db["properties"].append(new_prop)
                    save_db()
                    st.success(
                        f"Property '{title}' added successfully! ID: {p_id}"
                    )

    with tab3:
        st.subheader("Edit Existing Property")
        if not db["properties"]:
            st.info("No properties available to edit.")
        else:
            prop_ids = [p["id"] for p in db["properties"]]
            selected_edit_id = st.selectbox("Select Property to Edit", prop_ids)
            prop_to_edit = next(
                p for p in db["properties"] if p["id"] == selected_edit_id
            )

            with st.form("edit_prop_form"):
                e_title = st.text_input("Property Title", prop_to_edit["title"])
                e_price = st.number_input(
                    "Price / Monthly Rent (PKR)",
                    value=float(prop_to_edit["price"]),
                    step=10000.0,
                )
                e_status = st.selectbox(
                    "Status",
                    PROPERTY_STATUSES,
                    index=PROPERTY_STATUSES.index(prop_to_edit["status"]),
                )
                e_desc = st.text_area(
                    "Description", prop_to_edit["description"]
                )
                e_img = st.text_input("Image URL", prop_to_edit.get("image_url", ""))

                update_sub = st.form_submit_button("Update Property")
                if update_sub:
                    prop_to_edit["title"] = e_title
                    prop_to_edit["price"] = e_price
                    prop_to_edit["status"] = e_status
                    prop_to_edit["description"] = e_desc
                    prop_to_edit["image_url"] = e_img
                    save_db()
                    st.success(
                        f"Property {selected_edit_id} updated successfully!"
                    )

    with tab4:
        st.subheader("Delete Property")
        if not db["properties"]:
            st.info("No properties available to delete.")
        else:
            del_id = st.selectbox(
                "Select Property ID to Delete", [p["id"] for p in db["properties"]]
            )
            confirm_del = st.checkbox("I confirm I want to delete this property.")
            if st.button("Delete Property Record"):
                if confirm_del:
                    db["properties"] = [
                        p for p in db["properties"] if p["id"] != del_id
                    ]
                    save_db()
                    st.success(
                        f"Property {del_id} has been deleted successfully."
                    )
                else:
                    st.warning("Please check the confirmation box before deleting.")


# ==========================================
# 3. CUSTOMER MANAGEMENT
# ==========================================
elif menu_option == "Customer Management":
    st.title("👥 Customer Management")

    tab1, tab2, tab3 = st.tabs(
        ["View / Search Customers", "Register Customer", "Edit / Delete Customer"]
    )

    with tab1:
        st.subheader("Registered Customers Directory")
        cust_search = st.text_input("Search Customer by Name, Phone, or ID")
        filtered_cust = db["customers"]
        if cust_search:
            q = cust_search.lower()
            filtered_cust = [
                c
                for c in filtered_cust
                if q in c["id"].lower()
                or q in c["full_name"].lower()
                or q in c["phone"].lower()
            ]

        if filtered_cust:
            df_c = pd.DataFrame(filtered_cust)
            st.dataframe(df_c, use_container_width=True)

            # Detailed History Inspection
            selected_c_id = st.selectbox(
                "Select Customer ID to view related history & inquiries",
                [c["id"] for c in filtered_cust],
            )
            cust_obj = next(c for c in filtered_cust if c["id"] == selected_c_id)
            st.markdown(
                f"### Profile History for {cust_obj['full_name']} (`{cust_obj['id']}`)"
            )

            c_inquiries = [
                i for i in db["inquiries"] if i["customer_id"] == cust_obj["id"]
            ]
            c_transactions = [
                t for t in db["transactions"] if t["buyer_id"] == cust_obj["id"]
            ]
            c_rentals = [
                r for r in db["rentals"] if r["tenant_id"] == cust_obj["id"]
            ]

            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                st.write(f"**Inquiries:** {len(c_inquiries)}")
            with col_h2:
                st.write(f"**Transactions:** {len(c_transactions)}")
            with col_h3:
                st.write(f"**Rental Agreements:** {len(c_rentals)}")
        else:
            st.info("No customers found.")

    with tab2:
        st.subheader("Register New Customer")
        with st.form("add_cust_form"):
            c_id = st.text_input(
                "Customer ID", value=generate_id("CUST")
            )
            full_name = st.text_input("Full Name")
            phone = st.text_input("Phone Number (+92...)")
            email = st.text_input("Email Address")
            city = st.text_input("City")
            address = st.text_input("Address")
            cust_type = st.selectbox("Customer Type", CUSTOMER_TYPES)
            notes = st.text_area("Notes / Preferences")

            if st.form_submit_button("Register Customer"):
                if not full_name or not phone:
                    st.error("Full Name and Phone are required fields.")
                elif any(c["id"] == c_id for c in db["customers"]):
                    st.error(f"Customer ID '{c_id}' already exists.")
                else:
                    new_c = {
                        "id": c_id,
                        "full_name": full_name,
                        "phone": phone,
                        "email": email,
                        "city": city,
                        "address": address,
                        "type": cust_type,
                        "reg_date": str(date.today()),
                        "notes": notes,
                    }
                    db["customers"].append(new_c)
                    save_db()
                    st.success(
                        f"Customer {full_name} registered successfully! ID: {c_id}"
                    )

    with tab3:
        st.subheader("Edit or Delete Customer")
        if not db["customers"]:
            st.info("No customers available.")
        else:
            edit_cid = st.selectbox(
                "Select Customer ID", [c["id"] for c in db["customers"]]
            )
            cust_item = next(c for c in db["customers"] if c["id"] == edit_cid)

            with st.form("edit_cust_form"):
                up_name = st.text_input("Full Name", cust_item["full_name"])
                up_phone = st.text_input("Phone Number", cust_item["phone"])
                up_email = st.text_input("Email", cust_item["email"])
                up_notes = st.text_area("Notes", cust_item["notes"])

                if st.form_submit_button("Update Customer"):
                    cust_item["full_name"] = up_name
                    cust_item["phone"] = up_phone
                    cust_item["email"] = up_email
                    cust_item["notes"] = up_notes
                    save_db()
                    st.success("Customer details updated successfully!")

            if st.button("Delete Customer Record"):
                db["customers"] = [
                    c for c in db["customers"] if c["id"] != edit_cid
                ]
                save_db()
                st.success(f"Customer {edit_cid} deleted.")


# ==========================================
# 4. REAL ESTATE AGENT MANAGEMENT
# ==========================================
elif menu_option == "Agent Management":
    st.title("👔 Real Estate Agent Management")

    tab1, tab2, tab3 = st.tabs(
        ["View Agents & Stats", "Register Agent", "Update / Delete Agent"]
    )

    with tab1:
        st.subheader("Our Agents & Performance Statistics")
        if db["agents"]:
            agent_rows = []
            for a in db["agents"]:
                assigned_props = len(
                    [
                        p
                        for p in db["properties"]
                        if a["full_name"] in p["assigned_agent"]
                    ]
                )
                completed_txs = len(
                    [
                        t
                        for t in db["transactions"]
                        if t["agent_id"] == a["id"]
                        and t["transaction_status"] == "Completed"
                    ]
                )
                total_comm = sum(
                    [
                        float(t["commission_amount"])
                        for t in db["transactions"]
                        if t["agent_id"] == a["id"]
                        and t["transaction_status"] == "Completed"
                    ]
                )

                agent_rows.append(
                    {
                        "Agent ID": a["id"],
                        "Name": a["full_name"],
                        "Phone": a["phone"],
                        "Office": a["office_location"],
                        "Commission %": f"{a['commission_pct']}%",
                        "Assigned Properties": assigned_props,
                        "Completed Deals": completed_txs,
                        "Total Commission (PKR)": total_comm,
                        "Status": a["status"],
                    }
                )
            st.dataframe(pd.DataFrame(agent_rows), use_container_width=True)
        else:
            st.info("No agents registered.")

    with tab2:
        st.subheader("Register New Agent")
        with st.form("add_agent_form"):
            a_id = st.text_input("Agent ID", value=generate_id("AG"))
            full_name = st.text_input("Full Name")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email Address")
            office_location = st.text_input("Office Location / Branch")
            commission_pct = st.number_input(
                "Commission Percentage (%)", min_value=0.0, max_value=10.0, value=2.0
            )
            status = st.selectbox("Employment Status", AGENT_STATUSES)

            if st.form_submit_button("Register Agent"):
                if not full_name:
                    st.error("Agent full name is required.")
                elif any(ag["id"] == a_id for ag in db["agents"]):
                    st.error(f"Agent ID '{a_id}' already exists.")
                else:
                    new_agent = {
                        "id": a_id,
                        "full_name": full_name,
                        "phone": phone,
                        "email": email,
                        "office_location": office_location,
                        "joining_date": str(date.today()),
                        "commission_pct": commission_pct,
                        "status": status,
                    }
                    db["agents"].append(new_agent)
                    save_db()
                    st.success(f"Agent {full_name} registered successfully!")

    with tab3:
        st.subheader("Update or Delete Agent")
        if not db["agents"]:
            st.info("No agents available.")
        else:
            aid_sel = st.selectbox(
                "Select Agent", [a["id"] for a in db["agents"]]
            )
            ag_item = next(a for a in db["agents"] if a["id"] == aid_sel)

            with st.form("edit_agent_form"):
                up_stat = st.selectbox(
                    "Status",
                    AGENT_STATUSES,
                    index=AGENT_STATUSES.index(ag_item["status"]),
                )
                up_comm = st.number_input(
                    "Commission %", value=float(ag_item["commission_pct"])
                )

                if st.form_submit_button("Update Agent"):
                    ag_item["status"] = up_stat
                    ag_item["commission_pct"] = up_comm
                    save_db()
                    st.success("Agent updated successfully!")


# ==========================================
# 5. PROPERTY INQUIRY & VIEWING MANAGEMENT
# ==========================================
elif menu_option == "Inquiries & Viewings":
    st.title("📋 Property Inquiries & Viewings")

    tab1, tab2, tab3 = st.tabs(
        ["View All Inquiries", "Register Inquiry", "Update Inquiry & Viewing"]
    )

    with tab1:
        st.subheader("Customer Inquiry Tracker")
        if db["inquiries"]:
            st.dataframe(pd.DataFrame(db["inquiries"]), use_container_width=True)
        else:
            st.info("No inquiries recorded yet.")

    with tab2:
        st.subheader("Register New Inquiry")
        if not db["customers"] or not db["properties"] or not db["agents"]:
            st.warning(
                "Please ensure you have registered customers, properties, and agents first."
            )
        else:
            with st.form("inq_form"):
                inq_id = st.text_input("Inquiry ID", value=generate_id("INQ"))
                cust_choice = st.selectbox(
                    "Customer", [c["id"] + " - " + c["full_name"] for c in db["customers"]]
                )
                prop_choice = st.selectbox(
                    "Property", [p["id"] + " - " + p["title"] for p in db["properties"]]
                )
                agent_choice = st.selectbox(
                    "Assigned Agent", [a["id"] + " - " + a["full_name"] for a in db["agents"]]
                )
                contact_method = st.selectbox(
                    "Preferred Contact Method", ["Phone", "Email", "WhatsApp", "Office Visit"]
                )
                status = st.selectbox("Inquiry Status", INQUIRY_STATUSES)
                notes = st.text_area("Inquiry Notes / Requirements")

                if st.form_submit_button("Save Inquiry"):
                    new_inq = {
                        "id": inq_id,
                        "customer_id": cust_choice.split(" - ")[0],
                        "customer_name": cust_choice.split(" - ")[1],
                        "property_id": prop_choice.split(" - ")[0],
                        "property_title": prop_choice.split(" - ")[1],
                        "agent": agent_choice,
                        "date": str(date.today()),
                        "contact_method": contact_method,
                        "status": status,
                        "notes": notes,
                    }
                    db["inquiries"].append(new_inq)
                    save_db()
                    st.success("Inquiry successfully recorded!")

    with tab3:
        st.subheader("Update Inquiry Status & Viewing Schedule")
        if not db["inquiries"]:
            st.info("No inquiries to update.")
        else:
            sel_inq = st.selectbox(
                "Select Inquiry ID", [i["id"] for i in db["inquiries"]]
            )
            inq_obj = next(i for i in db["inquiries"] if i["id"] == sel_inq)

            with st.form("up_inq_form"):
                new_stat = st.selectbox(
                    "Update Status",
                    INQUIRY_STATUSES,
                    index=INQUIRY_STATUSES.index(inq_obj["status"]),
                )
                viewing_date = st.date_input(
                    "Schedule Viewing Date", value=date.today()
                )
                up_notes = st.text_area(
                    "Viewing Notes / Outcome", inq_obj["notes"]
                )

                if st.form_submit_button("Update Inquiry"):
                    inq_obj["status"] = new_stat
                    inq_obj["notes"] = (
                        f"{up_notes} [Viewing Scheduled/Updated for {viewing_date}]"
                    )
                    save_db()
                    st.success("Inquiry status updated successfully!")


# ==========================================
# 6. SALES & TRANSACTION MANAGEMENT
# ==========================================
elif menu_option == "Sales & Transactions":
    st.title("💰 Sales & Transaction Management")

    tab1, tab2 = st.tabs(["View Transactions", "Record Completed Sale"])

    with tab1:
        st.subheader("Transaction History")
        if db["transactions"]:
            st.dataframe(pd.DataFrame(db["transactions"]), use_container_width=True)
        else:
            st.info("No transactions recorded yet.")

    with tab2:
        st.subheader("Record Property Sale Transaction")
        saleable_props = [
            p
            for p in db["properties"]
            if p["listing_type"] == "For Sale" and p["status"] != "Sold"
        ]
        if not saleable_props or not db["customers"] or not db["agents"]:
            st.warning(
                "Ensure there are available 'For Sale' properties, registered buyers, and agents."
            )
        else:
            with st.form("tx_form"):
                tx_id = st.text_input("Transaction ID", value=generate_id("TX"))
                prop_sel = st.selectbox(
                    "Select Property",
                    [p["id"] + " - " + p["title"] for p in saleable_props],
                )
                buyer_sel = st.selectbox(
                    "Select Buyer",
                    [c["id"] + " - " + c["full_name"] for c in db["customers"]],
                )
                agent_sel = st.selectbox(
                    "Select Agent", [a["id"] + " - " + a["full_name"] for a in db["agents"]]
                )
                sale_price = st.number_input(
                    "Final Sale Price (PKR)", min_value=0.0, step=100000.0
                )
                tx_status = st.selectbox("Transaction Status", TRANSACTION_STATUSES)
                pay_status = st.selectbox("Payment Status", PAYMENT_STATUSES)

                if st.form_submit_button("Record Sale & Calculate Commission"):
                    pid = prop_sel.split(" - ")[0]
                    prop_obj = next(p for p in db["properties"] if p["id"] == pid)
                    agent_id_str = agent_sel.split(" - ")[0]
                    agent_obj = next(a for a in db["agents"] if a["id"] == agent_id_str)

                    # Calculate commission automatically
                    comm_amt = sale_price * (agent_obj["commission_pct"] / 100.0)

                    new_tx = {
                        "id": tx_id,
                        "property_id": pid,
                        "property_title": prop_obj["title"],
                        "buyer_id": buyer_sel.split(" - ")[0],
                        "agent_id": agent_obj["id"],
                        "agent_name": agent_obj["full_name"],
                        "sale_price": sale_price,
                        "commission_pct": agent_obj["commission_pct"],
                        "commission_amount": comm_amt,
                        "transaction_date": str(date.today()),
                        "payment_status": pay_status,
                        "transaction_status": tx_status,
                    }

                    db["transactions"].append(new_tx)

                    # Update property status if completed
                    if tx_status == "Completed":
                        prop_obj["status"] = "Sold"

                    save_db()
                    st.success(
                        f"Transaction {tx_id} recorded! Agent Commission: {format_pkr(comm_amt)}"
                    )


# ==========================================
# 7. RENTAL MANAGEMENT
# ==========================================
elif menu_option == "Rental Management":
    st.title("🔑 Rental Agreements Management")

    tab1, tab2 = st.tabs(["Active & Past Rentals", "Create Rental Agreement"])

    with tab1:
        st.subheader("Rental Agreements Directory")
        if db["rentals"]:
            st.dataframe(pd.DataFrame(db["rentals"]), use_container_width=True)
        else:
            st.info("No rental agreements recorded.")

    with tab2:
        st.subheader("Create New Rental Agreement")
        rent_props = [
            p
            for p in db["properties"]
            if p["listing_type"] == "For Rent" and p["status"] != "Rented"
        ]
        if not rent_props or not db["customers"]:
            st.warning("Ensure available 'For Rent' properties and customers exist.")
        else:
            with st.form("rent_form"):
                rent_id = st.text_input(
                    "Rental Agreement ID", value=generate_id("RENT")
                )
                prop_choice = st.selectbox(
                    "Property", [p["id"] + " - " + p["title"] for p in rent_props]
                )
                tenant_choice = st.selectbox(
                    "Tenant", [c["id"] + " - " + c["full_name"] for c in db["customers"]]
                )
                monthly_rent = st.number_input(
                    "Monthly Rent (PKR)", min_value=0.0, step=5000.0
                )
                security_deposit = st.number_input(
                    "Security Deposit (PKR)", min_value=0.0, step=5000.0
                )
                start_date = st.date_input("Agreement Start Date", value=date.today())
                end_date = st.date_input("Agreement End Date", value=date.today())
                due_day = st.number_input(
                    "Rent Payment Due Day of Month", min_value=1, max_value=28, value=5
                )
                notes = st.text_area("Agreement Notes / Terms")

                if st.form_submit_button("Create Rental Agreement"):
                    pid = prop_choice.split(" - ")[0]
                    prop_obj = next(p for p in db["properties"] if p["id"] == pid)

                    new_rental = {
                        "id": rent_id,
                        "property_id": pid,
                        "property_title": prop_obj["title"],
                        "tenant_id": tenant_choice.split(" - ")[0],
                        "tenant_name": tenant_choice.split(" - ")[1],
                        "monthly_rent": monthly_rent,
                        "security_deposit": security_deposit,
                        "start_date": str(start_date),
                        "end_date": str(end_date),
                        "payment_due_day": due_day,
                        "agreement_status": "Active",
                        "notes": notes,
                    }

                    db["rentals"].append(new_rental)
                    prop_obj["status"] = "Rented"
                    save_db()
                    st.success(
                        f"Rental agreement {rent_id} created successfully!"
                    )


# ==========================================
# 8. PAYMENT MANAGEMENT
# ==========================================
elif menu_option == "Payment Management":
    st.title("💳 Payment Management & Tracking")

    tab1, tab2 = st.tabs(["Payment History", "Record New Payment"])

    with tab1:
        st.subheader("All Recorded Payments")
        if db["payments"]:
            st.dataframe(pd.DataFrame(db["payments"]), use_container_width=True)
            total_paid = sum(
                [
                    float(p["amount"])
                    for p in db["payments"]
                    if p["payment_status"] == "Paid"
                ]
            )
            st.metric("Total Received Payments", format_pkr(total_paid))
        else:
            st.info("No payment records found.")

    with tab2:
        st.subheader("Record Payment")
        with st.form("pay_form"):
            pay_id = st.text_input("Payment ID", value=generate_id("PAY"))
            ref_id = st.text_input(
                "Related Transaction / Rental ID (Optional)"
            )
            payer_name = st.text_input("Customer / Tenant Name")
            pay_type = st.selectbox("Payment Type", PAYMENT_TYPES)
            amount = st.number_input(
                "Amount (PKR)", min_value=0.0, step=10000.0
            )
            pay_date = st.date_input("Payment Date", value=date.today())
            method = st.selectbox("Payment Method", PAYMENT_METHODS)
            status = st.selectbox("Payment Status", PAYMENT_STATUSES)
            ref_no = st.text_input("Reference / Receipt Number")
            notes = st.text_area("Payment Notes")

            if st.form_submit_button("Save Payment Record"):
                if not payer_name or amount <= 0:
                    st.error("Payer name and valid amount required.")
                else:
                    new_pay = {
                        "id": pay_id,
                        "reference_id": ref_id,
                        "payer_name": payer_name,
                        "payment_type": pay_type,
                        "amount": amount,
                        "payment_date": str(pay_date),
                        "payment_method": method,
                        "payment_status": status,
                        "reference_number": ref_no,
                        "notes": notes,
                    }
                    db["payments"].append(new_pay)
                    save_db()
                    st.success(f"Payment {pay_id} recorded successfully!")


# ==========================================
# 9. REPORTS & ANALYTICS
# ==========================================
elif menu_option == "Reports & Analytics":
    st.title("📈 Reports & Analytics")
    st.markdown(
        "Comprehensive agency analytics, financial summaries, and data export facilities."
    )

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.subheader("Properties by Type")
        if db["properties"]:
            df_p = pd.DataFrame(db["properties"])
            type_counts = df_p["type"].value_counts()
            st.bar_chart(type_counts)
        else:
            st.info("No property data.")

    with col_r2:
        st.subheader("Properties by City")
        if db["properties"]:
            df_p = pd.DataFrame(db["properties"])
            city_counts = df_p["city"].value_counts()
            st.bar_chart(city_counts)
        else:
            st.info("No property data.")

    st.markdown("---")
    st.subheader("📥 Data Export Center (CSV Downloads)")
    c_dl1, c_dl2, c_dl3 = st.columns(3)

    with c_dl1:
        if db["properties"]:
            csv_p = pd.DataFrame(db["properties"]).to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Properties CSV",
                csv_p,
                "properties_report.csv",
                "text/csv",
            )
    with c_dl2:
        if db["customers"]:
            csv_c = pd.DataFrame(db["customers"]).to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Customers CSV",
                csv_c,
                "customers_report.csv",
                "text/csv",
            )
    with c_dl3:
        if db["transactions"]:
            csv_t = (
                pd.DataFrame(db["transactions"]).to_csv(index=False).encode("utf-8")
            )
            st.download_button(
                "Download Transactions CSV",
                csv_t,
                "transactions_report.csv",
                "text/csv",
            )


# ==========================================
# 10. ABOUT & HELP
# ==========================================
elif menu_option == "About & Help":
    st.title("ℹ️ About & Help")
    st.markdown(
        """
    ### Real Estate Management Dashboard
    A modern, fully interactive university project built using **Python** and **Streamlit**.
    
    #### Key Features Included:
    - **Dynamic Dashboard:** Real-time KPI metrics for properties, sales revenue, rentals, and customer counts.
    - **Full CRUD Property Management:** Complete support for adding, filtering, searching, and managing listings.
    - **Customer & Agent Modules:** Track buyer preferences, agent performance, and commission percentages.
    - **Inquiries & Viewings:** Schedule client visits and track inquiry conversion funnels.
    - **Sales & Rentals:** Manage property ownership transfers and lease agreements in Pakistani Rupees (PKR).
    - **Financial Tracking:** Record payments, pending balances, and generate CSV reports.

    #### Data Persistence Note:
    Data is stored locally in `real_estate_data.json` and maintained via Streamlit session state. Note that on Streamlit Community Cloud, local files may reset upon app restarts or redeployments.
    """
    )
