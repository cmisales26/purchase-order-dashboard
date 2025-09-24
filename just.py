# import streamlit as st
# from fpdf import FPDF
# from num2words import num2words
# from datetime import datetime
# from io import BytesIO

# # --- PDF Class ---
# class PDF(FPDF):
#     def __init__(self):
#         super().__init__()
#         self.set_auto_page_break(auto=True, margin=15)
#         self.set_left_margin(15)
#         self.set_right_margin(15)
#         self.set_font("Arial", "", 10)

#     def header(self):
#         self.set_font("Arial", "B", 18)
#         self.cell(0, 15, "TAX INVOICE", ln=True, align="C")
#         self.set_font("Arial", "", 10)
#         self.cell(0, 5, "CM Infotech | We aim for the best", ln=True, align="R")
#         self.ln(5)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font("Arial", "I", 8)
#         self.cell(0, 5, "This is a Computer Generated Invoice", ln=True, align="C")

#     def section_title(self, title):
#         self.set_font("Arial", "B", 12)
#         self.set_fill_color(220, 220, 220)
#         self.cell(0, 7, title, border=1, ln=1, fill=True)
#         self.set_font("Arial", "", 10)

# # --- Generate PDF ---
# def create_invoice_pdf(invoice_data):
#     pdf = PDF()
#     pdf.add_page()

#     # --- Supplier & Buyer ---
#     pdf.set_font("Arial", "B", 10)
#     pdf.cell(95, 5, "Supplier", border=1)
#     pdf.cell(0, 5, "Buyer", border=1, ln=1)

#     y_start = pdf.get_y()
#     # Supplier details
#     pdf.set_font("Arial", "", 10)
#     pdf.multi_cell(95, 5, f"{invoice_data['supplier']['name']}\n{invoice_data['supplier']['address']}\nGST: {invoice_data['supplier']['gst_no']}\nMSME: {invoice_data['supplier']['msme_reg_no']}\nEmail: {invoice_data['supplier']['email']}\nMobile: {invoice_data['supplier']['mobile_no']}", border=1)

#     # Buyer details
#     pdf.set_xy(110, y_start)
#     pdf.multi_cell(0, 5, f"{invoice_data['buyer']['name']}\n{invoice_data['buyer']['address']}\nGST: {invoice_data['buyer']['gst_no']}\nEmail: {invoice_data['buyer']['email']}\nTel: {invoice_data['buyer']['tel_no']}\nDestination: {invoice_data['buyer']['destination']}", border=1)
#     pdf.ln(5)

#     # --- Invoice Details Table ---
#     pdf.set_font("Arial", "B", 10)
#     col1, col2, col3, col4 = 45, 50, 45, 50
#     details = invoice_data["invoice"]
#     pdf.cell(col1, 7, "Invoice No.", border=1)
#     pdf.cell(col2, 7, details["invoice_no"], border=1)
#     pdf.cell(col3, 7, "Invoice Date", border=1)
#     pdf.cell(col4, 7, details["invoice_date"], border=1, ln=1)

#     pdf.cell(col1, 7, "Buyer's Order No.", border=1)
#     pdf.cell(col2, 7, details["buyers_order_no"], border=1)
#     pdf.cell(col3, 7, "Buyer's Order Date", border=1)
#     pdf.cell(col4, 7, details["buyers_order_date"], border=1, ln=1)

#     pdf.cell(col1, 7, "Payment Terms", border=1)
#     pdf.cell(col2, 7, details["terms_of_payment"], border=1)
#     pdf.cell(col3, 7, "Dispatch Doc No.", border=1)
#     pdf.cell(col4, 7, details["dispatch_doc_no"], border=1, ln=1)
#     pdf.cell(col1, 7, "Dispatched Through", border=1)
#     pdf.cell(col2, 7, details["dispatched_through"], border=1)
#     pdf.cell(col3, 7, "Delivery Note Date", border=1)
#     pdf.cell(col4, 7, details["delivery_note_date"], border=1, ln=1)
#     pdf.cell(col1, 7, "Terms of Delivery", border=1)
#     pdf.cell(col2, 7, details["terms_of_delivery"], border=1)
#     pdf.cell(col3, 7, "", border=1)
#     pdf.cell(col4, 7, "", border=1, ln=1)
#     pdf.ln(5)

#     # --- Products Table ---
#     pdf.section_title("Product Details")
#     pdf.set_font("Arial", "B", 10)
#     headers = ["Sr. No.", "Description", "HSN/SAC", "Qty", "Unit Rate", "Amount"]
#     widths = [10, 80, 20, 20, 20, 20]
#     for h, w in zip(headers, widths):
#         pdf.cell(w, 7, h, border=1, align="C")
#     pdf.ln()
#     pdf.set_font("Arial", "", 10)

#     total_basic = 0
#     for i, item in enumerate(invoice_data["items"], 1):
#         amount = item["quantity"] * item["unit_rate"]
#         total_basic += amount
#         pdf.cell(widths[0], 7, str(i), border=1, align="C")
#         pdf.cell(widths[1], 7, item["description"][:50], border=1)  # truncate for row height
#         pdf.cell(widths[2], 7, item["hsn_sac"], border=1, align="C")
#         pdf.cell(widths[3], 7, f"{item['quantity']:.2f}", border=1, align="R")
#         pdf.cell(widths[4], 7, f"{item['unit_rate']:.2f}", border=1, align="R")
#         pdf.cell(widths[5], 7, f"{amount:.2f}", border=1, align="R")
#         pdf.ln()

#     # Totals
#     totals = invoice_data["totals"]
#     pdf.set_font("Arial", "B", 10)
#     pdf.cell(sum(widths[:-1]), 7, "Basic Amount", border=1, align="R")
#     pdf.cell(widths[-1], 7, f"{totals['basic_amount']:.2f}", border=1, align="R", ln=1)
#     pdf.cell(sum(widths[:-1]), 7, "SGST @ 9%", border=1, align="R")
#     pdf.cell(widths[-1], 7, f"{totals['sgst']:.2f}", border=1, align="R", ln=1)
#     pdf.cell(sum(widths[:-1]), 7, "CGST @ 9%", border=1, align="R")
#     pdf.cell(widths[-1], 7, f"{totals['cgst']:.2f}", border=1, align="R", ln=1)
#     pdf.cell(sum(widths[:-1]), 7, "Final Amount", border=1, align="R")
#     pdf.cell(widths[-1], 7, f"{totals['final_amount']:.2f}", border=1, align="R", ln=1)
#     pdf.ln(5)

#     # Amount in words
#     pdf.set_font("Arial", "B", 10)
#     pdf.cell(0, 7, "Amount in Words:", ln=1)
#     pdf.set_font("Arial", "", 10)
#     pdf.multi_cell(0, 7, totals["amount_in_words"])
#     pdf.ln(5)

#     # Bank Details
#     pdf.section_title("Bank Details")
#     bank = invoice_data["bank_details"]
#     pdf.set_font("Arial", "B", 10)
#     pdf.cell(50, 7, "Bank Name:", border=1)
#     pdf.set_font("Arial", "", 10)
#     pdf.cell(0, 7, bank["bank_name"], border=1, ln=1)
#     pdf.set_font("Arial", "B", 10)
#     pdf.cell(50, 7, "Branch:", border=1)
#     pdf.set_font("Arial", "", 10)
#     pdf.cell(0, 7, bank["branch"], border=1, ln=1)
#     pdf.set_font("Arial", "B", 10)
#     pdf.cell(50, 7, "Account No.:", border=1)
#     pdf.set_font("Arial", "", 10)
#     pdf.cell(0, 7, bank["account_no"], border=1, ln=1)
#     pdf.set_font("Arial", "B", 10)
#     pdf.cell(50, 7, "IFS Code:", border=1)
#     pdf.set_font("Arial", "", 10)
#     pdf.cell(0, 7, bank["ifs_code"], border=1, ln=1)
#     pdf.ln(5)

#     # Declaration & Signature
#     pdf.set_font("Arial", "", 8)
#     pdf.multi_cell(0, 5, invoice_data["declaration"])
#     pdf.ln(10)
#     pdf.set_font("Arial", "I", 10)
#     pdf.cell(0, 7, "Authorized Signatory", align="R")

#     # Return as bytes for Streamlit
#     return pdf.output(dest="S").encode("latin-1")


# # --- Streamlit UI ---
# st.set_page_config(page_title="Tax Invoice Generator", layout="wide")
# st.title("📄 Tax Invoice Generator")

# # Dummy invoice data
# invoice_data = {
#     "supplier": {
#         "name": "CM Infotech",
#         "address": "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Village, Ahmedabad - 382481",
#         "gst_no": "24ANMPP4",
#         "msme_reg_no": "UDYAM-",
#         "email": "cm.infot@example.com",
#         "mobile_no": "873391",
#     },
#     "buyer": {
#         "name": "Baldridge Pvt Ltd.",
#         "address": "406, Sakar East, Vadodara 390009",
#         "gst_no": "24AAHCB9",
#         "email": "dmistry@example.com",
#         "tel_no": "98987",
#         "destination": "Vadodara",
#     },
#     "invoice": {
#         "invoice_no": "CMI/25-26/Q1/010",
#         "invoice_date": "28 April 2025",
#         "buyers_order_no": "",
#         "buyers_order_date": "17 April 2025",
#         "terms_of_payment": "100% Advance",
#         "dispatch_doc_no": "",
#         "dispatched_through": "Online",
#         "delivery_note_date": "",
#         "terms_of_delivery": "Within Month",
#     },
#     "items": [
#         {
#             "description": "Autodesk BIM Collaborate Pro - Single-user CLOUD Commercial New Annual Subscription",
#             "hsn_sac": "997331",
#             "quantity": 1,
#             "unit_rate": 36500,
#         }
#     ],
#     "totals": {
#         "basic_amount": 36500,
#         "sgst": 3285,
#         "cgst": 3285,
#         "final_amount": 43070,
#         "amount_in_words": "Rs. Forty Three Thousand And Seventy Only/-",
#     },
#     "bank_details": {
#         "bank_name": "XYZ Bank",
#         "branch": "AHMED",
#         "account_no": "881304",
#         "ifs_code": "IDFB004",
#     },
#     "declaration": "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITHHOLDING TAX..."
# }

# # Generate PDF button
# if st.button("Generate Tax Invoice"):
#     pdf_bytes = create_invoice_pdf(invoice_data)
#     st.download_button("⬇ Download Tax Invoice", pdf_bytes, "tax_invoice.pdf", "application/pdf")













import streamlit as st
from fpdf import FPDF
from num2words import num2words

# ------------------- PDF Class -------------------
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_left_margin(15)
        self.set_right_margin(15)
        self.set_font("Arial", "", 10)

    def header(self):
        self.set_font("Arial", "B", 18)
        self.cell(0, 15, "TAX INVOICE", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "CM Infotech | We aim for the best", ln=True, align="R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 5, "This is a Computer Generated Invoice", ln=True, align="C")

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="Tax Invoice Generator", page_icon="📄", layout="wide")
st.title("📄 Tax Invoice Generator")

# Supplier Details
st.subheader("Supplier Details")
supplier_name = st.text_input("Name", "CM Infotech")
supplier_address = st.text_area("Address", "E/402, Ganesh Glory, Ahmedabad")
supplier_gst = st.text_input("GST No.", "24ANMPP4")
supplier_msme = st.text_input("MSME No.", "UDYAM-")
supplier_email = st.text_input("Email", "cm.infot@example.com")
supplier_mobile = st.text_input("Mobile No.", "873391")

# Buyer Details
st.subheader("Buyer Details")
buyer_name = st.text_input("Name", "Baldridge Pvt Ltd.")
buyer_address = st.text_area("Address", "406, Sakar East, Vadodara")
buyer_gst = st.text_input("GST No.", "24AAHCB9")
buyer_email = st.text_input("Email", "dmistry@example.com")
buyer_tel = st.text_input("Tel No.", "98987")
buyer_dest = st.text_input("Destination", "Vadodara")

# Invoice Details
st.subheader("Invoice Details")
invoice_no = st.text_input("Invoice No.", "CMI/25-26/Q1/010")
invoice_date = st.text_input("Invoice Date", "28 April 2025")

# Bank Details
st.subheader("Bank Details")
bank_name = st.text_input("Bank Name", "XYZ Bank")
bank_branch = st.text_input("Branch", "AHMED")
bank_account = st.text_input("Account No.", "881304")
bank_ifsc = st.text_input("IFS Code", "IDFB004")

# Products
st.subheader("Products")
if "products" not in st.session_state:
    st.session_state.products = []

if st.button("➕ Add Product"):
    st.session_state.products.append({"desc": "", "hsn": "", "qty": 1.0, "rate": 0.0})

for i, prod in enumerate(st.session_state.products):
    with st.expander(f"Product {i+1}", expanded=True):
        prod["desc"] = st.text_area("Description", prod["desc"], key=f"desc_{i}")
        prod["hsn"] = st.text_input("HSN/SAC", prod["hsn"], key=f"hsn_{i}")
        prod["qty"] = st.number_input("Quantity", value=prod["qty"], format="%.2f", key=f"qty_{i}")
        prod["rate"] = st.number_input("Unit Rate", value=prod["rate"], format="%.2f", key=f"rate_{i}")
        if st.button("Remove Product", key=f"remove_{i}"):
            st.session_state.products.pop(i)
            st.experimental_rerun()

# ------------------- Generate PDF -------------------
if st.button("Generate Invoice"):
    pdf = PDF()
    pdf.add_page()

    # Supplier & Buyer
    y_start = pdf.get_y()
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 5, "Supplier", border=1)
    pdf.cell(0, 5, "Buyer", border=1, ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(95, 5, f"{supplier_name}\n{supplier_address}\nGST: {supplier_gst}\nMSME: {supplier_msme}\nEmail: {supplier_email}\nMobile: {supplier_mobile}", border=1)
    pdf.set_xy(110, y_start)
    pdf.multi_cell(0, 5, f"{buyer_name}\n{buyer_address}\nGST: {buyer_gst}\nEmail: {buyer_email}\nTel: {buyer_tel}\nDestination: {buyer_dest}", border=1)
    pdf.ln(5)

    # Invoice Info
    pdf.set_font("Arial", "B", 10)
    pdf.cell(45, 7, "Invoice No.", border=1)
    pdf.cell(50, 7, invoice_no, border=1)
    pdf.cell(45, 7, "Invoice Date", border=1)
    pdf.cell(0, 7, invoice_date, border=1, ln=1)
    pdf.ln(5)

    # Products Table Header
    pdf.set_font("Arial", "B", 10)
    col_widths = [10, 80, 20, 20, 20, 20]
    headers = ["Sr. No.", "Description", "HSN/SAC", "Qty", "Unit Rate", "Amount"]
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, align="C")
    pdf.ln()

    # Products Table Rows
    pdf.set_font("Arial", "", 10)
    total_basic = 0.0
    hsn_summary = {}
    for idx, p in enumerate(st.session_state.products):
        amount = p["qty"] * p["rate"]
        total_basic += amount
        pdf.cell(col_widths[0], 7, str(idx+1), border=1, align="C")
        pdf.cell(col_widths[1], 7, p["desc"], border=1)
        pdf.cell(col_widths[2], 7, p["hsn"], border=1, align="C")
        pdf.cell(col_widths[3], 7, f"{p['qty']:.2f}", border=1, align="R")
        pdf.cell(col_widths[4], 7, f"{p['rate']:.2f}", border=1, align="R")
        pdf.cell(col_widths[5], 7, f"{amount:.2f}", border=1, align="R")
        pdf.ln()
        # HSN summary
        if p["hsn"] not in hsn_summary:
            hsn_summary[p["hsn"]] = 0.0
        hsn_summary[p["hsn"]] += amount

    # Tax Calculation
    sgst = total_basic * 0.09
    cgst = total_basic * 0.09
    final_amount = total_basic + sgst + cgst
    amount_words = num2words(final_amount, to="currency", lang='en_IN').title() + " Only/-"

    # Totals
    pdf.set_font("Arial", "B", 10)
    pdf.cell(sum(col_widths[:-1]), 7, "Basic Amount", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{total_basic:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "SGST @ 9%", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{sgst:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "CGST @ 9%", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{cgst:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "Final Amount to be Paid", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{final_amount:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # Amount in Words
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Amount in Words:", ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, amount_words)
    pdf.ln(5)

    # HSN/SAC Tax Details
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "HSN/SAC Tax Details", ln=1)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 7, "HSN/SAC", border=1)
    pdf.cell(40, 7, "Taxable Value", border=1)
    pdf.cell(30, 7, "CGST 9%", border=1)
    pdf.cell(30, 7, "SGST 9%", border=1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    for hsn, val in hsn_summary.items():
        pdf.cell(30, 7, hsn, border=1, align="C")
        pdf.cell(40, 7, f"{val:.2f}", border=1, align="R")
        pdf.cell(30, 7, f"{val*0.09:.2f}", border=1, align="R")
        pdf.cell(30, 7, f"{val*0.09:.2f}", border=1, align="R")
        pdf.ln()
    pdf.ln(5)

    # Bank Details
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Bank Details", ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 7, "Bank Name:", border=0)
    pdf.cell(0, 7, bank_name, ln=1)
    pdf.cell(50, 7, "Branch:", border=0)
    pdf.cell(0, 7, bank_branch, ln=1)
    pdf.cell(50, 7, "Account No.:", border=0)
    pdf.cell(0, 7, bank_account, ln=1)
    pdf.cell(50, 7, "IFS Code:", border=0)
    pdf.cell(0, 7, bank_ifsc, ln=1)
    pdf.ln(10)

    # Signature
    pdf.cell(100, 7, "Customer's Seal and Signature", ln=0)
    pdf.cell(0, 7, "For, CM Infotech", ln=1, align="R")
    pdf.ln(15)
    pdf.cell(100, 7, "", ln=0)
    pdf.cell(0, 7, "Authorized Signatory", ln=1, align="R")

    # Output PDF
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    st.download_button("⬇ Download Tax Invoice", pdf_bytes, "tax_invoice.pdf", "application/pdf")
