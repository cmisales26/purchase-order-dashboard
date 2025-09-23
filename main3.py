# import streamlit as st
# from fpdf import FPDF
# from num2words import num2words
# import datetime
# from io import BytesIO
# import os

# # --- Product Catalog (Dropdown Options) ---
# PRODUCT_CATALOG = {
#     "Autodesk Commercial Software License": {"basic": 2000.0, "gst_percent": 18.0},
#     "Solidworks Premium": {"basic": 50000.0, "gst_percent": 18.0},
#     "Catia License": {"basic": 75000.0, "gst_percent": 18.0},
#     "Mastercam Module": {"basic": 30000.0, "gst_percent": 18.0},
#     "Siemens NX": {"basic": 65000.0, "gst_percent": 18.0},
# }

# # --- PDF Class ---
# class PDF(FPDF):
#     def __init__(self, logo_path=None):
#         super().__init__()
#         self.set_auto_page_break(auto=False, margin=0)
#         self.set_left_margin(15)
#         self.set_right_margin(15)
#         self.logo_path = logo_path

#     def header(self):
#         if self.page_no() == 1:
#             # Logo (if available)
#             if self.logo_path and os.path.exists(self.logo_path):
#                 self.image(self.logo_path, x=15, y=8, w=25)

#             # Company name (right side)
#             self.set_font("Arial", "B", 16)
#             self.cell(0, 10, st.session_state.company_name, ln=True, align="R")

#             # Title
#             self.set_font("Arial", "B", 14)
#             self.cell(0, 10, "PURCHASE ORDER", ln=True, align="C")
#             self.ln(2)

#             # PO info
#             self.set_font("Arial", "", 10)
#             self.cell(95, 8, f"PO No: {st.session_state.po_number}", ln=0)
#             self.cell(95, 8, f"Date: {st.session_state.po_date}", ln=1)
#             self.ln(3)

#     def footer(self):
#         self.set_y(-20)
#         self.set_font("Arial", "I", 8)
#         self.multi_cell(
#             0,
#             5,
#             "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n"
#             "Email: cad@cmi.com | support@cmi.com | +91 879 815 9721",
#             align="C"
#         )

#     def section_title(self, title):
#         self.set_font("Arial", "B", 11)
#         self.cell(0, 7, title, ln=True)
#         self.ln(1)


# # --- Initialize Session ---
# if "po_seq" not in st.session_state:
#     st.session_state.po_seq = 1
# if "products" not in st.session_state:
#     st.session_state.products = []
# if "company_name" not in st.session_state:
#     st.session_state.company_name = "CM Infotech"

# today = datetime.date.today()
# st.session_state.po_date = today.strftime("%d-%m-%Y")
# st.session_state.po_number = f"C/CP/{today.year}/Q{(today.month-1)//3+1}/{st.session_state.po_seq:03d}"

# # --- UI ---
# st.set_page_config(page_title="Purchase Order Generator", page_icon="📄", layout="wide")
# st.title("📄 One-Page Purchase Order Generator with Logo & Dropdown")

# with st.sidebar:
#     st.header("Company Info")
#     st.session_state.company_name = st.text_input("Company Name", st.session_state.company_name)
#     logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])
#     logo_path = None
#     if logo_file:
#         logo_path = "logo_temp.png"
#         with open(logo_path, "wb") as f:
#             f.write(logo_file.getbuffer())

#     st.divider()
#     auto_increment = st.checkbox("Auto-increment PO Number", value=True)
#     if st.button("Reset PO Sequence"):
#         st.session_state.po_seq = 1
#         st.success("PO sequence reset to 1")

# tab1, tab2, tab3, tab4 = st.tabs(["Vendor Details", "Products", "Terms", "Preview & Generate"])

# with tab1:
#     col1, col2 = st.columns(2)
#     with col1:
#         vendor_name = st.text_input("Vendor Name", "Arkance IN Pvt. Ltd.")
#         vendor_address = st.text_area("Vendor Address", "Unit 801-802, 8th Floor, Tower 1...")
#         vendor_contact = st.text_input("Contact Person", "Ms/Mr")
#         vendor_mobile = st.text_input("Mobile", "+91 1234567890")
#         gst_no = st.text_input("GST No", "GSTIN123456789")
#         pan_no = st.text_input("PAN No", "ABCDE1234F")
#         msme_no = st.text_input("MSME No", "MSME000000123")
#     with col2:
#         bill_to_company = st.text_input("Bill To", "CM INFOTECH")
#         bill_to_address = st.text_area("Bill To Address", "E/402, Ganesh Glory 11, Ahmedabad")
#         ship_to_company = st.text_input("Ship To", "CM INFOTECH")
#         ship_to_address = st.text_area("Ship To Address", "E/402, Ganesh Glory 11, Ahmedabad")
#         end_company = st.text_input("End User Company", "Baldridge & Associates Pvt Ltd.")
#         end_address = st.text_area("End User Address", "406 Sakar East, Vadodara 390009")
#         end_person = st.text_input("End User Contact", "Mr. Dev")
#         end_contact = st.text_input("End User Phone", "+91 9876543210")
#         end_email = st.text_input("End User Email", "info@company.com")

# with tab2:
#     st.header("Products")
#     # --- Dropdown for quick add ---
#     selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()))
#     if st.button("➕ Add Selected Product"):
#         if selected_product:
#             details = PRODUCT_CATALOG[selected_product]
#             st.session_state.products.append({
#                 "name": selected_product,
#                 "basic": details["basic"],
#                 "gst_percent": details["gst_percent"],
#                 "qty": 1.0,
#             })
#             st.success(f"{selected_product} added!")

#     # Manual add
#     if st.button("➕ Add Empty Product"):
#         st.session_state.products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

#     # Product list
#     for i, p in enumerate(st.session_state.products):
#         with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
#             col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
#             st.session_state.products[i]["name"] = st.text_input("Name", p["name"], key=f"name_{i}")
#             st.session_state.products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"basic_{i}")
#             st.session_state.products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"gst_{i}")
#             st.session_state.products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"qty_{i}")
#             if st.button("Remove", key=f"remove_{i}"):
#                 st.session_state.products.pop(i)
#                 st.rerun()

# with tab3:
#     st.header("Terms & Authorization")
#     col1, col2 = st.columns(2)
#     with col1:
#         payment_terms = st.text_input("Payment Terms", "30 Days from Invoice date")
#         delivery_days = st.number_input("Delivery (Days)", min_value=1, value=2)
#         delivery_terms = st.text_input("Delivery Terms", f"Within {delivery_days} Days")
#         additional_terms = st.text_area("Additional Terms", "")
#     with col2:
#         prepared_by = st.text_input("Prepared By", "Finance Department")
#         authorized_by = st.text_input("Authorized By", "CM INFOTECH")

# with tab4:
#     st.header("Preview & Generate")
#     # Totals
#     total_base = sum(p["basic"] * p["qty"] for p in st.session_state.products)
#     total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.products)
#     grand_total = total_base + total_gst
#     amount_words = num2words(grand_total, to="currency", currency="INR").title()
#     st.metric("Grand Total", f"₹{grand_total:,.2f}")

#     if st.button("Generate PO", type="primary"):
#         pdf = PDF(logo_path=logo_path)
#         pdf.add_page()

#         # Vendor & Bill/Ship
#         pdf.section_title("Vendor & Addresses")
#         pdf.set_font("Arial", "", 8)
#         pdf.multi_cell(95, 5, f"{vendor_name}\n{vendor_address}\nAttn: {vendor_contact}\nMobile: {vendor_mobile}")
#         pdf.set_xy(110, pdf.get_y() - 20)
#         pdf.multi_cell(90, 5, f"{bill_to_company}\n{bill_to_address}\nShip: {ship_to_company}\n{ship_to_address}")
#         pdf.ln(2)
#         pdf.cell(0, 5, f"GST: {gst_no} | PAN: {pan_no} | MSME: {msme_no}", ln=True)
#         pdf.ln(2)

#         # Products Table
#         pdf.section_title("Products & Services")
#         col_widths = [65, 22, 15, 22, 15, 22]
#         headers = ["Product", "Basic", "GST%", "GST Amt", "Qty", "Total"]
#         pdf.set_fill_color(200, 200, 200)
#         pdf.set_font("Arial", "B", 8)
#         for h, w in zip(headers, col_widths):
#             pdf.cell(w, 6, h, border=1, align="C", fill=True)
#         pdf.ln()
#         pdf.set_font("Arial", "", 8)
#         for p in st.session_state.products:
#             gst_amt = p["basic"] * p["gst_percent"] / 100
#             total = (p["basic"] + gst_amt) * p["qty"]
#             name = p["name"] if len(p["name"]) <= 25 else p["name"][:25] + "..."
#             pdf.cell(col_widths[0], 6, name, border=1)
#             pdf.cell(col_widths[1], 6, f"{p['basic']:.2f}", border=1, align="R")
#             pdf.cell(col_widths[2], 6, f"{p['gst_percent']}%", border=1, align="C")
#             pdf.cell(col_widths[3], 6, f"{gst_amt:.2f}", border=1, align="R")
#             pdf.cell(col_widths[4], 6, f"{p['qty']:.2f}", border=1, align="C")
#             pdf.cell(col_widths[5], 6, f"{total:.2f}", border=1, align="R")
#             pdf.ln()
#         pdf.set_font("Arial", "B", 8)
#         pdf.cell(sum(col_widths[:-1]), 6, "Grand Total", border=1, align="R")
#         pdf.cell(col_widths[5], 6, f"{grand_total:.2f}", border=1, align="R")
#         pdf.ln(4)

#         # Amount in Words
#         pdf.set_font("Arial", "B", 8)
#         pdf.cell(0, 5, "Amount in Words:", ln=True)
#         pdf.set_font("Arial", "", 8)
#         pdf.multi_cell(0, 5, amount_words)
#         pdf.ln(2)

#         # Terms
#         pdf.section_title("Terms & Conditions")
#         pdf.set_font("Arial", "", 8)
#         pdf.multi_cell(0, 4, f"Taxes: As specified above\nPayment: {payment_terms}\nDelivery: {delivery_terms}")
#         if additional_terms:
#             pdf.multi_cell(0, 4, f"Additional: {additional_terms}")
#         pdf.ln(2)

#         # End User
#         pdf.section_title("End User Details")
#         pdf.set_font("Arial", "", 8)
#         pdf.multi_cell(0, 4, f"{end_company}\n{end_address}\nContact: {end_person} | {end_contact}\nEmail: {end_email}")
#         pdf.ln(2)

#         # Authorization
#         pdf.set_font("Arial", "", 8)
#         pdf.cell(95, 5, f"Prepared By: {prepared_by}", ln=0)
#         pdf.cell(95, 5, f"Authorized By: {authorized_by}", ln=1)
#         pdf.cell(0, 5, f"For, {st.session_state.company_name}", ln=True, align="R")

#         # Save in memory
#         buffer = BytesIO()
#         pdf.output(buffer)
#         pdf_data = buffer.getvalue()

#         if auto_increment:
#             st.session_state.po_seq += 1

#         st.success("Purchase Order generated!")
#         st.download_button(
#             "⬇️ Download Purchase Order",
#             pdf_data,
#             f"PO_{st.session_state.po_number.replace('/', '_')}.pdf",
#             "application/pdf"
#         )







import streamlit as st
from fpdf import FPDF
from num2words import num2words
import datetime
from io import BytesIO
from PIL import Image
import os

# --- Product Catalog (Dropdown Options) ---
PRODUCT_CATALOG = {
    "Autodesk Commercial Software License": {"basic": 2000.0, "gst_percent": 18.0},
    "Solidworks Premium": {"basic": 50000.0, "gst_percent": 18.0},
    "Catia License": {"basic": 75000.0, "gst_percent": 18.0},
    "Mastercam Module": {"basic": 30000.0, "gst_percent": 18.0},
    "Siemens NX": {"basic": 65000.0, "gst_percent": 18.0},
}

# --- PDF Class ---
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False, margin=0)
        self.set_left_margin(15)
        self.set_right_margin(15)
        # self.logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        self.logo_path = os.path.join(os.path.dirname(__file__),"assets","logo_safe.png")
        # # Register Calibri fonts (regular + bold)
        # font_dir = os.path.join(os.path.dirname(__file__),"calibri.ttf","calibrib.ttf","calibrii.ttf","calibril.ttf","calibrili.ttf","calibriz.ttf")  # folder where your ttf files are
        # self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
        # self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
        # self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
        # self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)

        font_dir = os.path.join(os.path.dirname(__file__), "fonts")

        self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
        self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
        self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
        self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)

    def header(self):
        if self.page_no() == 1:
            # Logo (if available)
            if self.logo_path and os.path.exists(self.logo_path):
                try:
                    # self.image(self.logo_path, x=162.5, y=2.5, w=45)
                    self.image(self.logo_path, x=150, y=10, w=40)
                except RuntimeError:
                    pass

            # Company name (right side)
            # self.set_font("Arial", "B", 16)
            # self.cell(0, 10, self.sanitize_text(st.session_state.company_name), ln=True, align="R")

            # Title
            self.set_font("Calibri", "B", 15)
            self.cell(0, 15, "PURCHASE ORDER", ln=True, align="C")
            self.ln(2)

            # PO info
            self.set_font("Calibri", "", 12)
            self.cell(95, 8, f"PO No: {self.sanitize_text(st.session_state.po_number)}", ln=0)
            self.cell(95, 8, f"Date: {self.sanitize_text(st.session_state.po_date)}", ln=1)
            self.ln(2)

    def footer(self):
        self.set_y(-18)
        self.set_font("Calibri", "I", 10)

        # # Address
        self.multi_cell(0, 4,
            "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n",
        #     "Email: cad@cmi.com | support@cmi.com",
            align="C"
        )

        # Emails (clickable)
        self.set_text_color(0, 0, 255)
        email1 = "cad@cmi.com"
        email2 = "support@cmi.com"
        self.cell(0, 4, f"{email1} | {email2}", ln=True, align="C", link=f"mailto:{email1}")
        # Add second link separately (on same text)
        self.set_x((self.w - 80) / 2)
        self.cell(0, 0, "", link=f"mailto:{email2}")


        # Clickable Phone Number
        self.set_x((self.w - 60) / 2)
        phone_number = "+918798159721"
        self.set_text_color(0, 0, 255)  # blue
        self.cell(60, 4, f"Call: {phone_number}", ln=True, align="C", link=f"tel:{phone_number}")
        self.set_text_color(0, 0, 0)

    # def footer(self):
    #     self.set_y(-18)
    #     self.set_font("Arial", "I", 8)
    #     # Sanitize the hardcoded footer text
    #     footer_text = self.sanitize_text(
    #         "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n"
    #         "Email: cad@cmi.com | support@cmi.com | ‪+91 879 815 9721‬"
    #     )
    #     self.multi_cell(
    #         0,
    #         4,
    #         footer_text,
    #         align="C"
    #     )

    def section_title(self, title):
        self.set_font("Calibri", "B", 12)
        self.cell(0, 6, self.sanitize_text(title), ln=True)
        self.ln(1)

    def sanitize_text(self, text):
        """Removes non-ASCII characters that can cause FPDF to fail."""
        return text.encode('ascii', 'ignore').decode('ascii')


# --- Initialize Session ---
if "po_seq" not in st.session_state:
    st.session_state.po_seq = 1
if "products" not in st.session_state:
    st.session_state.products = []
if "company_name" not in st.session_state:
    st.session_state.company_name = "CM Infotech"

today = datetime.date.today()
st.session_state.po_date = today.strftime("%d-%m-%Y")
st.session_state.po_number = f"C/CP/{today.year}/Q{(today.month-1)//3+1}/{st.session_state.po_seq:03d}"

# --- UI ---
st.set_page_config(page_title="Purchase Order Generator", page_icon="📄", layout="wide")
st.title("📄 Purchase Order Generator")

with st.sidebar:
    st.header("Company Info")
    # st.session_state.company_name = st.text_input("Company Name", st.session_state.company_name)
    logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])
    logo_path = None
    if logo_file:
        logo_path = "logo_temp.png"
        with open(logo_path, "wb") as f:
            f.write(logo_file.getbuffer())

    st.divider()
    auto_increment = st.checkbox("Auto-increment PO Number", value=True)
    if st.button("Reset PO Sequence"):
        st.session_state.po_seq = 1
        st.success("PO sequence reset to 1")

tab1, tab2, tab3, tab4 = st.tabs(["Vendor Details", "Products", "Terms", "Preview & Generate"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        vendor_name = st.text_input("Vendor Name", "Arkance IN Pvt. Ltd.")
        vendor_address = st.text_area("Vendor Address", "Unit 801-802, 8th Floor, Tower 1...")
        vendor_contact = st.text_input("Contact Person", "Ms/Mr")
        vendor_mobile = st.text_input("Mobile", "‪+91 1234567890‬")
        gst_no = st.text_input("GST No", "24ANMPP4891R1ZX")
        pan_no = st.text_input("PAN No", "ANMPP4891R")
        msme_no = st.text_input("MSME No", "UDYAM-GJ-01-0117646")
    with col2:
        bill_to_company = st.text_input("Bill To", "CM INFOTECH")
        bill_to_address = st.text_area("Bill To Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481")
        ship_to_company = st.text_input("Ship To", "CM INFOTECH")
        ship_to_address = st.text_area("Ship To Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481")
        end_company = st.text_input("End User Company", "Baldridge & Associates Pvt Ltd.")
        end_address = st.text_area("End User Address", "406 Sakar East, Vadodara 390009")
        end_person = st.text_input("End User Contact", "Mr. Dev")
        end_contact = st.text_input("End User Phone", "+91 9876543210")
        end_email = st.text_input("End User Email", "info@company.com")

with tab2:
    st.header("Products")
    selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()))
    if st.button("➕ Add Selected Product"):
        if selected_product:
            details = PRODUCT_CATALOG[selected_product]
            st.session_state.products.append({
                "name": selected_product,
                "basic": details["basic"],
                "gst_percent": details["gst_percent"],
                "qty": 1.0,
            })
            st.success(f"{selected_product} added!")

    if st.button("➕ Add Empty Product"):
        st.session_state.products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

    for i, p in enumerate(st.session_state.products):
        with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            st.session_state.products[i]["name"] = st.text_input("Name", p["name"], key=f"name_{i}")
            st.session_state.products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"basic_{i}")
            st.session_state.products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"gst_{i}")
            st.session_state.products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"qty_{i}")
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.products.pop(i)
                st.rerun()

with tab3:
    st.header("Terms & Authorization")
    col1, col2 = st.columns(2)
    with col1:
        payment_terms = st.text_input("Payment Terms", "30 Days from Invoice date")
        delivery_days = st.number_input("Delivery (Days)", min_value=1, value=2)
        delivery_terms = st.text_input("Delivery Terms", f"Within {delivery_days} Days")
        # additional_terms = st.text_area("Additional Terms", "")
    with col2:
        prepared_by = st.text_input("Prepared By", "Finance Department")
        authorized_by = st.text_input("Authorized By", "CM INFOTECH")

with tab4:
    st.header("Preview & Generate")
    total_base = sum(p["basic"] * p["qty"] for p in st.session_state.products)
    total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.products)
    grand_total = total_base + total_gst
    amount_words = num2words(grand_total, to="currency", currency="INR").title()
    st.metric("Grand Total", f"₹{grand_total:,.2f}")

    if st.button("Generate PO", type="primary"):
        pdf = PDF()
        if logo_file:
            pdf.logo_path = logo_path
        pdf.add_page()
        
        # Sanitize all input strings
        sanitized_vendor_name = pdf.sanitize_text(vendor_name)
        sanitized_vendor_address = pdf.sanitize_text(vendor_address)
        sanitized_vendor_contact = pdf.sanitize_text(vendor_contact)
        sanitized_vendor_mobile = pdf.sanitize_text(vendor_mobile)
        sanitized_gst_no = pdf.sanitize_text(gst_no)
        sanitized_pan_no = pdf.sanitize_text(pan_no)
        sanitized_msme_no = pdf.sanitize_text(msme_no)
        sanitized_bill_to_company = pdf.sanitize_text(bill_to_company)
        sanitized_bill_to_address = pdf.sanitize_text(bill_to_address)
        sanitized_ship_to_company = pdf.sanitize_text(ship_to_company)
        sanitized_ship_to_address = pdf.sanitize_text(ship_to_address)
        sanitized_end_company = pdf.sanitize_text(end_company)
        sanitized_end_address = pdf.sanitize_text(end_address)
        sanitized_end_person = pdf.sanitize_text(end_person)
        sanitized_end_contact = pdf.sanitize_text(end_contact)
        sanitized_end_email = pdf.sanitize_text(end_email)
        sanitized_payment_terms = pdf.sanitize_text(payment_terms)
        sanitized_delivery_terms = pdf.sanitize_text(delivery_terms)
        # sanitized_additional_terms = pdf.sanitize_text(additional_terms)
        sanitized_prepared_by = pdf.sanitize_text(prepared_by)
        sanitized_authorized_by = pdf.sanitize_text(authorized_by)
        
        # # Vendor & Bill/Ship
        # pdf.section_title("Vendor & Addresses")
        # pdf.set_font("Arial", "", 8)
        # pdf.multi_cell(95, 5, f"{sanitized_vendor_name}\n{sanitized_vendor_address}\nAttn: {sanitized_vendor_contact}\nMobile: {sanitized_vendor_mobile}")
        # pdf.set_xy(110, pdf.get_y() - 20)
        # pdf.multi_cell(90, 5, f"Bill: {sanitized_bill_to_company}\n{sanitized_bill_to_address}\nShip: {sanitized_ship_to_company}\n{sanitized_ship_to_address}")
        # pdf.ln(1)
        # pdf.multi_cell(0, 5, f"GST: {sanitized_gst_no}\nPAN: {sanitized_pan_no}\nMSME: {sanitized_msme_no}")

        # pdf.ln(2)

        # --- Vendor & Bill/Ship ---
        pdf.section_title("Vendor & Addresses")
        pdf.set_font("Calibri", "", 10)
        pdf.multi_cell(95, 5, f"{sanitized_vendor_name}\n{sanitized_vendor_address}\nAttn: {sanitized_vendor_contact}\nMobile: {sanitized_vendor_mobile}")
        pdf.set_xy(110, pdf.get_y() - 20)
        pdf.multi_cell(90, 5, f"Bill: {sanitized_bill_to_company}\n{sanitized_bill_to_address}\nShip: {sanitized_ship_to_company}\n{sanitized_ship_to_address}")
        pdf.ln(1)
        pdf.multi_cell(0, 5, f"GST: {sanitized_gst_no}\nPAN: {sanitized_pan_no}\nMSME: {sanitized_msme_no}")
        pdf.ln(2)


        # # Products Table
        # pdf.section_title("Products & Services")
        # col_widths = [65, 22, 25, 25, 15, 22]
        # headers = ["Product", "Basic", "GST TAX @ 18%","Per Unit Price", "Qty", "Total"]
        # pdf.set_fill_color(220, 220, 220)
        # pdf.set_font("Arial", "B", 8)
        # for h, w in zip(headers, col_widths):
        #     pdf.cell(w, 6, pdf.sanitize_text(h), border=1, align="C", fill=True)
        # pdf.ln()
        # pdf.set_font("Arial", "", 8)
        # for p in st.session_state.products:
        #     gst_amt = p["basic"] * p["gst_percent"] / 100
        #     per_unit_price = (p["basic"] + gst_amt) 
        #     total = (p["basic"] + gst_amt) * p["qty"]
        #     name = pdf.sanitize_text(p["name"])
        #     name = name if len(name) <= 25 else name[:25] + "..."
        #     pdf.cell(col_widths[0], 6, name, border=1)
        #     pdf.cell(col_widths[1], 6, f"{p['basic']:.2f}", border=1, align="R")
        #     # pdf.cell(col_widths[2], 6, f"{p['gst_percent']}%", border=1, align="C")
        #     pdf.cell(col_widths[2], 6, f"{gst_amt:.2f}", border=1, align="R")
        #     pdf.cell(col_widths[3], 6, f"{per_unit_price:.2f}",border=1,align="R")
        #     pdf.cell(col_widths[4], 6, f"{p['qty']:.2f}", border=1, align="C")
        #     pdf.cell(col_widths[5], 6, f"{total:.2f}", border=1, align="R")
        #     pdf.ln()
        # pdf.set_font("Arial", "B", 8)
        # pdf.cell(sum(col_widths[:-1]), 6, "Grand Total", border=1, align="R")
        # pdf.cell(col_widths[5], 6, f"{grand_total:.2f}", border=1, align="R")
        # pdf.ln(4)

        # --- Products Table ---
        pdf.section_title("Products & Services")
        col_widths = [65, 22, 25, 25, 15, 22]
        headers = ["Product", "Basic", "GST TAX @ 18%", "Per Unit Price", "Qty", "Total"]
        pdf.set_fill_color(220, 220, 220)
        pdf.set_font("Calibri", "B", 10)
        for h, w in zip(headers, col_widths):
            pdf.cell(w, 6, pdf.sanitize_text(h), border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_font("Calibri", "", 10)
        for p in st.session_state.products:
            gst_amt = p["basic"] * p["gst_percent"] / 100
            per_unit_price = p["basic"] + gst_amt
            total = (p["basic"] + gst_amt) * p["qty"]
            name = pdf.sanitize_text(p["name"])
            name = name if len(name) <= 25 else name[:25] + "..."
            pdf.cell(col_widths[0], 6, name, border=1)
            pdf.cell(col_widths[1], 6, f"{p['basic']:.2f}", border=1, align="R")
            pdf.cell(col_widths[2], 6, f"{gst_amt:.2f}", border=1, align="R")
            pdf.cell(col_widths[3], 6, f"{per_unit_price:.2f}", border=1, align="R")
            pdf.cell(col_widths[4], 6, f"{p['qty']:.2f}", border=1, align="C")
            pdf.cell(col_widths[5], 6, f"{total:.2f}", border=1, align="R")
            pdf.ln()
        pdf.set_font("Calibri", "B", 10)
        pdf.cell(sum(col_widths[:-1]), 6, "Grand Total", border=1, align="R")
        pdf.cell(col_widths[5], 6, f"{grand_total:.2f}", border=1, align="R")
        pdf.ln(4)

        # --- Amount in Words ---
        pdf.set_font("Calibri", "B", 10)
        pdf.cell(0, 8, "Amount in Words:", ln=True)
        pdf.set_font("Calibri", "", 10)
        pdf.multi_cell(0, 5, pdf.sanitize_text(amount_words))
        pdf.ln(4)


        # # Amount in Words
        # pdf.set_font("Arial", "B", 8)
        # pdf.cell(0, 8, "Amount in Words:", ln=True)
        # pdf.set_font("Arial", "", 8)
        # pdf.multi_cell(0, 5, pdf.sanitize_text(amount_words))
        # pdf.ln(4)

        # # --- Amount in Words ---
        # pdf.set_font("Calibri", "B", 10)
        # pdf.cell(0, 8, "Amount in Words:", ln=True)
        # pdf.set_font("Calibri", "", 10)
        # pdf.multi_cell(0, 5, pdf.sanitize_text(amount_words))
        # pdf.ln(4)

        # # Terms
        # pdf.section_title("Terms & Conditions")
        # pdf.set_font("Arial", "", 8)
        # pdf.multi_cell(0, 4, f"Taxes: As specified above\nPayment: {sanitized_payment_terms}\nDelivery: {sanitized_delivery_terms}")
        # if sanitized_additional_terms:
        #     pdf.multi_cell(0, 4, f"Additional: {sanitized_additional_terms}")
        # pdf.ln(2)

        # # --- Terms ---
        pdf.section_title("Terms & Conditions")
        pdf.set_font("Calibri", "", 10)
        pdf.multi_cell(0, 4, f"Taxes: As specified above\nPayment: {sanitized_payment_terms}\nDelivery: {sanitized_delivery_terms}")
        # if sanitized_additional_terms:
        #     pdf.multi_cell(0, 4, f"Additional: {sanitized_additional_terms}")
        pdf.ln(2)

        # --- Terms ---
    # pdf.section_title("Terms & Conditions")
    # pdf.set_font("Calibri", "", 10)

    # # Main terms
    # safe_terms = (
    #     f"Taxes: As specified above\n"
    #     f"Payment: {sanitized_payment_terms}\n"
    #     f"Delivery: {sanitized_delivery_terms}"
    # )
    # usable_width = pdf.w - 2 * pdf.l_margin
    # pdf.multi_cell(usable_width, 4, safe_terms)

    # # Additional terms, if any
    # if sanitized_additional_terms:
    #     pdf.set_font("Calibri", "", 10)  # reset font in case changed
    #     # Use usable width for safety
    #     try:
    #         pdf.multi_cell(usable_width, 4, f"Additional: {sanitized_additional_terms}")
    #     except Exception:
    #         # fallback: reduce font if text too wide
    #         pdf.set_font("Calibri", "", 8)
    #         pdf.multi_cell(usable_width, 4, f"Additional: {sanitized_additional_terms}")

    # pdf.ln(2)


        # # End User
        # pdf.section_title("End User Details")
        # pdf.set_font("Arial", "", 8)
        # pdf.multi_cell(0, 4, f"{sanitized_end_company}\n{sanitized_end_address}\nContact: {sanitized_end_person} | {sanitized_end_contact}\nEmail: {sanitized_end_email}")
        # pdf.ln(2)

            # --- End User ---
        pdf.section_title("End User Details")
        pdf.set_font("Calibri", "", 10)
        pdf.multi_cell(0, 4, f"{sanitized_end_company}\n{sanitized_end_address}\nContact: {sanitized_end_person} | {sanitized_end_contact}\nEmail: {sanitized_end_email}")
        pdf.ln(2)

        # # Authorization
        # pdf.set_font("Calibri", "", 10)
        # pdf.multi_cell(65, 5, f"Prepared By: {sanitized_prepared_by}", border=0)
        # pdf.multi_cell(65, 5, f"Authorized By: {sanitized_authorized_by}", border=0)
        # pdf.multi_cell(0, 5, f"For, {pdf.sanitize_text(st.session_state.company_name)}", ln=1, align="R")


        # Authorization Section
        pdf.set_font("Calibri", "", 10)

        # Move to left margin
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 5, f"Prepared By: {sanitized_prepared_by}", ln=1, border=0)

        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 5, f"Authorized By: {sanitized_authorized_by}", ln=1, border=0)

        # pdf.set_font("Calibri","",10)
        # pdf.set_x(pdf.l_margin)
        # pdf.cell(0, 5, f"For, {pdf.sanitize_text(st.session_state.company_name)}", ln=2, border=0, align="L")


        # Path to your uploaded image
        pdf.set_y(-110)
        pdf.cell(0, 5, f"For, {pdf.sanitize_text(st.session_state.company_name)}", ln=2, border=0, align="L")
        stamp_path = os.path.join(os.path.dirname(__file__), "stamp.jpg")

        # Position the stamp above the footer
        pdf.set_y(-105)  # 50 mm from bottom, adjust as needed
        pdf.set_x(15)  # center the stamp, assuming width 40
        pdf.image(stamp_path, w=30)  # width 40 mm, height auto


        # Save in memory
        # buffer = BytesIO()
        # pdf.output(buffer)
        # pdf_data = buffer.getvalue()

        # if auto_increment:
        #     st.session_state.po_seq += 1

        # st.success("Purchase Order generated!")
        # st.download_button(
        #     "⬇ Download Purchase Order",
        #     pdf_data,
        #     f"PO_{st.session_state.po_number.replace('/', '_')}.pdf",
        #     "application/pdf"
        # )

        #     # --- Authorization ---
        # pdf.set_font("Arial", "", 8)
        # pdf.cell(65, 5, f"Prepared By: {sanitized_prepared_by}", border=0)
        # pdf.cell(65, 5, f"Authorized By: {sanitized_authorized_by}", border=0)
        # pdf.cell(0, 5, f"For, {pdf.sanitize_text(st.session_state.company_name)}", ln=1, align="R")

        # --- Save in memory for Streamlit ---
        pdf_bytes = pdf.output(dest="S").encode('latin-1')

        if auto_increment:
            st.session_state.po_seq += 1

        st.success("Purchase Order generated!")
        st.download_button(
            "⬇ Download Purchase Order",
            pdf_bytes,
            f"PO_{st.session_state.po_number.replace('/', '_')}.pdf",
            "application/pdf"
        )

st.divider()
st.caption("© 2025 Purchase Order Generator")
