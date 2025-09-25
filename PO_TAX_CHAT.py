import streamlit as st
from fpdf import FPDF
from num2words import num2words
import datetime
import io
import os

# ---------------- Product Catalog ----------------
PRODUCT_CATALOG = {
    "Autodesk Commercial Software License": {"basic": 2000.0, "gst_percent": 18.0},
    "Solidworks Premium": {"basic": 50000.0, "gst_percent": 18.0},
    "Catia License": {"basic": 75000.0, "gst_percent": 18.0},
    "Mastercam Module": {"basic": 30000.0, "gst_percent": 18.0},
    "Siemens NX": {"basic": 65000.0, "gst_percent": 18.0},
}

# ---------------- PDF Class ----------------
class PDF(FPDF):
    def _init_(self):
        super()._init_()
        self.set_auto_page_break(auto=False, margin=0)
        self.set_left_margin(15)
        self.set_right_margin(15)

    def header(self):
        pass

    def footer(self):
        self.set_y(-40)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 5, "This is a computer-generated document.", ln=True, align="C")
        self.set_y(-30)
        self.cell(0, 5, "E/402, Ganesh Glory 11, Near BSNL Office, Ahmedabad - 382481", ln=True, align="C")
        self.set_y(-25)
        self.set_text_color(0, 0, 255)
        self.cell(0, 5, "Email: info@cminfotech.com | Call: +91 8733915721", ln=True, align="C")
        self.set_text_color(0, 0, 0)

    def sanitize_text(self, text):
        return text.encode('ascii', 'ignore').decode('ascii')

# ---------------- Initialize Session ----------------
if "po_seq" not in st.session_state:
    st.session_state.po_seq = 1
if "products" not in st.session_state:
    st.session_state.products = []

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="PO & Invoice Generator", layout="wide")
st.title("📄 Purchase Order / Tax Invoice Generator")

# ---------------- Sidebar: Logo & Stamp ----------------
logo_file = st.sidebar.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])
stamp_file = st.sidebar.file_uploader("Upload Stamp (Optional)", type=["png", "jpg", "jpeg"])

# ---------------- Select Document Type ----------------
doc_type = st.radio("Select Document Type", ["Purchase Order", "Tax Invoice"])

# ---------------- Tabs for Input ----------------
tab1, tab2, tab3, tab4 = st.tabs(["Vendor/Buyer Details", "Products", "Terms & Authorization", "Preview & Generate"])

# ---------------- Tab 1: Vendor / Buyer Details ----------------
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Vendor / Seller")
        vendor_name = st.text_input("Vendor Name", "CM Infotech")
        vendor_address = st.text_area("Vendor Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur...")
        vendor_contact = st.text_input("Contact Person", "Mr. XYZ")
        vendor_mobile = st.text_input("Mobile", "+91 8733915721")
        vendor_gst = st.text_input("GST No.", "24ANMPP4")
        vendor_msme = st.text_input("MSME No.", "UDYAM-GJ-01-0117646")
    with col2:
        st.subheader("Buyer / End User")
        buyer_name = st.text_input("Buyer Name", "Baldridge Pvt Ltd.")
        buyer_address = st.text_area("Buyer Address", "406, Sakar East, Vadodara 390009")
        buyer_gst = st.text_input("Buyer GST No.", "24AAHCB9")
        bill_to_company = st.text_input("Bill To", "CM Infotech")
        bill_to_address = st.text_area("Bill To Address", "E/402, Ganesh Glory 11, Ahmedabad")
        ship_to_company = st.text_input("Ship To", "CM Infotech")
        ship_to_address = st.text_area("Ship To Address", "E/402, Ganesh Glory 11, Ahmedabad")

# ---------------- Tab 2: Products ----------------
with tab2:
    st.header("Products")
    selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()))
    if st.button("➕ Add Selected Product"):
        if selected_product:
            details = PRODUCT_CATALOG[selected_product]
            st.session_state.products.append({"name": selected_product, "basic": details["basic"], "gst_percent": details["gst_percent"], "qty": 1.0})
            st.success(f"{selected_product} added!")
    if st.button("➕ Add Empty Product"):
        st.session_state.products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

    for i, p in enumerate(st.session_state.products):
        with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
            p["name"] = st.text_input("Name", p["name"], key=f"name_{i}")
            p["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"basic_{i}")
            p["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"gst_{i}")
            p["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"qty_{i}")
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.products.pop(i)
                st.experimental_rerun()

# ---------------- Tab 3: Terms & Authorization ----------------
with tab3:
    st.header("Terms & Authorization")
    payment_terms = st.text_input("Payment Terms", "30 Days from Invoice date")
    delivery_terms = st.text_input("Delivery Terms", "Within 2 Days")
    prepared_by = st.text_input("Prepared By", "Finance Dept.")
    authorized_by = st.text_input("Authorized By", "CM Infotech")
    declaration = st.text_area("Declaration", "This is a system-generated document. Taxes as per rules.")

# ---------------- Tab 4: Preview & Generate ----------------
with tab4:
    st.header("Preview & Generate")
    total_base = sum(p["basic"] * p["qty"] for p in st.session_state.products)
    total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.products)
    grand_total = total_base + total_gst
    amount_words = num2words(grand_total, to="currency", currency="INR").title()
    st.metric("Grand Total", f"₹{grand_total:,.2f}")

    if st.button("Generate Document"):
        pdf = PDF()
        pdf.add_page()

        # ---------------- Header: Vendor & Buyer ----------------
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 5, f"Vendor: {pdf.sanitize_text(vendor_name)}\n{pdf.sanitize_text(vendor_address)}\nAttn: {pdf.sanitize_text(vendor_contact)} | Mobile: {pdf.sanitize_text(vendor_mobile)}")
        pdf.ln(1)
        pdf.multi_cell(0, 5, f"Buyer: {pdf.sanitize_text(buyer_name)}\n{pdf.sanitize_text(buyer_address)}\nGST: {pdf.sanitize_text(buyer_gst)}")
        pdf.ln(5)

        # ---------------- Products Table ----------------
        col_widths = [70, 25, 25, 25, 15, 25]
        pdf.set_font("Helvetica", "B", 10)
        headers = ["Product", "Basic", "GST", "Unit Price", "Qty", "Total"]
        for h, w in zip(headers, col_widths):
            pdf.cell(w, 6, h, border=1, align="C")
        pdf.ln()
        pdf.set_font("Helvetica", "", 10)
        for p in st.session_state.products:
            gst_amt = p["basic"] * p["gst_percent"] / 100
            unit_price = p["basic"] + gst_amt
            total = unit_price * p["qty"]
            pdf.cell(col_widths[0], 5, pdf.sanitize_text(p["name"]), border=1)
            pdf.cell(col_widths[1], 5, f"{p['basic']:.2f}", border=1, align="R")
            pdf.cell(col_widths[2], 5, f"{gst_amt:.2f}", border=1, align="R")
            pdf.cell(col_widths[3], 5, f"{unit_price:.2f}", border=1, align="R")
            pdf.cell(col_widths[4], 5, f"{p['qty']:.2f}", border=1, align="C")
            pdf.cell(col_widths[5], 5, f"{total:.2f}", border=1, align="R")
            pdf.ln()
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(sum(col_widths[:-1]), 6, "Grand Total", border=1, align="R")
        pdf.cell(col_widths[-1], 6, f"{grand_total:.2f}", border=1, align="R")
        pdf.ln(5)

        # ---------------- Amount in Words ----------------
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "Amount in Words:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, pdf.sanitize_text(amount_words))
        pdf.ln(5)

        # ---------------- Terms / Declaration ----------------
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, f"Payment Terms: {payment_terms}\nDelivery Terms: {delivery_terms}\nPrepared By: {prepared_by}\nAuthorized By: {authorized_by}\n\nDeclaration:\n{declaration}")
        pdf.ln(5)

        # ---------------- Stamp ----------------
        if stamp_file:
            stamp_path = "stamp_temp.png"
            with open(stamp_path, "wb") as f:
                f.write(stamp_file.getbuffer())
            pdf.image(stamp_path, x=pdf.get_x() + 120, y=pdf.get_y() + 5, w=40)

        # ---------------- Logo ----------------
        if logo_file:
            logo_path = "logo_temp.png"
            with open(logo_path, "wb") as f:
                f.write(logo_file.getbuffer())
            pdf.image(logo_path, x=pdf.l_margin, y=10, w=40)

        # ---------------- Save & Download ----------------
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.download_button("📥 Download PDF", data=pdf_bytes, file_name=f"{doc_type.replace(' ','_')}_{st.session_state.po_seq}.pdf", mime="application/pdf")
        st.session_state.po_seq += 1
