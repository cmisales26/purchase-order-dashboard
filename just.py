import streamlit as st
from fpdf import FPDF
from num2words import num2words
from datetime import datetime
from io import BytesIO

# --- PDF Class ---
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

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 7, title, border=1, ln=1, fill=True)
        self.set_font("Arial", "", 10)

# --- Generate PDF ---
def create_invoice_pdf(invoice_data):
    pdf = PDF()
    pdf.add_page()

    # --- Supplier & Buyer ---
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 5, "Supplier", border=1)
    pdf.cell(0, 5, "Buyer", border=1, ln=1)

    y_start = pdf.get_y()
    # Supplier details
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(95, 5, f"{invoice_data['supplier']['name']}\n{invoice_data['supplier']['address']}\nGST: {invoice_data['supplier']['gst_no']}\nMSME: {invoice_data['supplier']['msme_reg_no']}\nEmail: {invoice_data['supplier']['email']}\nMobile: {invoice_data['supplier']['mobile_no']}", border=1)

    # Buyer details
    pdf.set_xy(110, y_start)
    pdf.multi_cell(0, 5, f"{invoice_data['buyer']['name']}\n{invoice_data['buyer']['address']}\nGST: {invoice_data['buyer']['gst_no']}\nEmail: {invoice_data['buyer']['email']}\nTel: {invoice_data['buyer']['tel_no']}\nDestination: {invoice_data['buyer']['destination']}", border=1)
    pdf.ln(5)

    # --- Invoice Details Table ---
    pdf.set_font("Arial", "B", 10)
    col1, col2, col3, col4 = 45, 50, 45, 50
    details = invoice_data["invoice"]
    pdf.cell(col1, 7, "Invoice No.", border=1)
    pdf.cell(col2, 7, details["invoice_no"], border=1)
    pdf.cell(col3, 7, "Invoice Date", border=1)
    pdf.cell(col4, 7, details["invoice_date"], border=1, ln=1)

    pdf.cell(col1, 7, "Buyer's Order No.", border=1)
    pdf.cell(col2, 7, details["buyers_order_no"], border=1)
    pdf.cell(col3, 7, "Buyer's Order Date", border=1)
    pdf.cell(col4, 7, details["buyers_order_date"], border=1, ln=1)

    pdf.cell(col1, 7, "Payment Terms", border=1)
    pdf.cell(col2, 7, details["terms_of_payment"], border=1)
    pdf.cell(col3, 7, "Dispatch Doc No.", border=1)
    pdf.cell(col4, 7, details["dispatch_doc_no"], border=1, ln=1)
    pdf.cell(col1, 7, "Dispatched Through", border=1)
    pdf.cell(col2, 7, details["dispatched_through"], border=1)
    pdf.cell(col3, 7, "Delivery Note Date", border=1)
    pdf.cell(col4, 7, details["delivery_note_date"], border=1, ln=1)
    pdf.cell(col1, 7, "Terms of Delivery", border=1)
    pdf.cell(col2, 7, details["terms_of_delivery"], border=1)
    pdf.cell(col3, 7, "", border=1)
    pdf.cell(col4, 7, "", border=1, ln=1)
    pdf.ln(5)

    # --- Products Table ---
    pdf.section_title("Product Details")
    pdf.set_font("Arial", "B", 10)
    headers = ["Sr. No.", "Description", "HSN/SAC", "Qty", "Unit Rate", "Amount"]
    widths = [10, 80, 20, 20, 20, 20]
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, align="C")
    pdf.ln()
    pdf.set_font("Arial", "", 10)

    total_basic = 0
    for i, item in enumerate(invoice_data["items"], 1):
        amount = item["quantity"] * item["unit_rate"]
        total_basic += amount
        pdf.cell(widths[0], 7, str(i), border=1, align="C")
        pdf.cell(widths[1], 7, item["description"][:50], border=1)  # truncate for row height
        pdf.cell(widths[2], 7, item["hsn_sac"], border=1, align="C")
        pdf.cell(widths[3], 7, f"{item['quantity']:.2f}", border=1, align="R")
        pdf.cell(widths[4], 7, f"{item['unit_rate']:.2f}", border=1, align="R")
        pdf.cell(widths[5], 7, f"{amount:.2f}", border=1, align="R")
        pdf.ln()

    # Totals
    totals = invoice_data["totals"]
    pdf.set_font("Arial", "B", 10)
    pdf.cell(sum(widths[:-1]), 7, "Basic Amount", border=1, align="R")
    pdf.cell(widths[-1], 7, f"{totals['basic_amount']:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(widths[:-1]), 7, "SGST @ 9%", border=1, align="R")
    pdf.cell(widths[-1], 7, f"{totals['sgst']:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(widths[:-1]), 7, "CGST @ 9%", border=1, align="R")
    pdf.cell(widths[-1], 7, f"{totals['cgst']:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(widths[:-1]), 7, "Final Amount", border=1, align="R")
    pdf.cell(widths[-1], 7, f"{totals['final_amount']:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # Amount in words
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Amount in Words:", ln=1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, totals["amount_in_words"])
    pdf.ln(5)

    # Bank Details
    pdf.section_title("Bank Details")
    bank = invoice_data["bank_details"]
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 7, "Bank Name:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, bank["bank_name"], border=1, ln=1)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 7, "Branch:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, bank["branch"], border=1, ln=1)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 7, "Account No.:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, bank["account_no"], border=1, ln=1)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 7, "IFS Code:", border=1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, bank["ifs_code"], border=1, ln=1)
    pdf.ln(5)

    # Declaration & Signature
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, invoice_data["declaration"])
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 7, "Authorized Signatory", align="R")

    # Return as bytes for Streamlit
    return pdf.output(dest="S").encode("latin-1")


# --- Streamlit UI ---
st.set_page_config(page_title="Tax Invoice Generator", layout="wide")
st.title("📄 Tax Invoice Generator")

# Dummy invoice data
invoice_data = {
    "supplier": {
        "name": "CM Infotech",
        "address": "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Village, Ahmedabad - 382481",
        "gst_no": "24ANMPP4",
        "msme_reg_no": "UDYAM-",
        "email": "cm.infot@example.com",
        "mobile_no": "873391",
    },
    "buyer": {
        "name": "Baldridge Pvt Ltd.",
        "address": "406, Sakar East, Vadodara 390009",
        "gst_no": "24AAHCB9",
        "email": "dmistry@example.com",
        "tel_no": "98987",
        "destination": "Vadodara",
    },
    "invoice": {
        "invoice_no": "CMI/25-26/Q1/010",
        "invoice_date": "28 April 2025",
        "buyers_order_no": "",
        "buyers_order_date": "17 April 2025",
        "terms_of_payment": "100% Advance",
        "dispatch_doc_no": "",
        "dispatched_through": "Online",
        "delivery_note_date": "",
        "terms_of_delivery": "Within Month",
    },
    "items": [
        {
            "description": "Autodesk BIM Collaborate Pro - Single-user CLOUD Commercial New Annual Subscription",
            "hsn_sac": "997331",
            "quantity": 1,
            "unit_rate": 36500,
        }
    ],
    "totals": {
        "basic_amount": 36500,
        "sgst": 3285,
        "cgst": 3285,
        "final_amount": 43070,
        "amount_in_words": "Rs. Forty Three Thousand And Seventy Only/-",
    },
    "bank_details": {
        "bank_name": "XYZ Bank",
        "branch": "AHMED",
        "account_no": "881304",
        "ifs_code": "IDFB004",
    },
    "declaration": "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITHHOLDING TAX..."
}

# Generate PDF button
if st.button("Generate Tax Invoice"):
    pdf_bytes = create_invoice_pdf(invoice_data)
    st.download_button("⬇ Download Tax Invoice", pdf_bytes, "tax_invoice.pdf", "application/pdf")
