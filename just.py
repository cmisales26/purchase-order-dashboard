import streamlit as st
from fpdf import FPDF
from num2words import num2words
import datetime
import os
from io import BytesIO

# --- PDF Class for Tax Invoice ---
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False, margin=0)
        self.set_left_margin(15)
        self.set_right_margin(15)
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        # Ensure these fonts exist in your 'fonts' directory
        self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
        self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
        self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
        self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
        self.website_url = "https://cminfotech.com/"

    def header(self):
        # Supplier details
        self.set_font("Calibri", "", 10)
        self.cell(0, 5, "CM Infotech", ln=1, align='R')
        self.cell(0, 5, "We aim for the best", ln=1, align='R')
        self.ln(2)

        # Main Invoice Title
        self.set_font("Calibri", "B", 18)
        self.cell(0, 15, "TAX INVOICE", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Calibri", "I", 8)
        self.cell(0, 5, "This is a Computer Generated Invoice", ln=1, align="C")

    def section_title(self, title):
        self.set_font("Calibri", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 7, self.sanitize_text(title), border='T,L,R', ln=1, fill=True)
        self.set_font("Calibri", "", 10)

    def sanitize_text(self, text):
        return text.encode('latin-1', 'ignore').decode('latin-1')

# --- Streamlit UI ---
st.set_page_config(page_title="Tax Invoice Generator", page_icon="📄", layout="wide")
st.title("📄 Tax Invoice Generator")

# --- Initialize Session State (simplified for this invoice) ---
if "products" not in st.session_state:
    st.session_state.products = [{
        "name": "Autodesk BIM Collaborate Pro - Single-user CLOUD Commercial New Annual Subscription Serial #575-26831580 Contract #110004988191 End Date: 17/04/2026",
        "hsn_sac": "997331",
        "basic": 36500.00,
        "qty": 1.0,
        "gst_percent": 18.0
    }]
if "invoice_data" not in st.session_state:
    st.session_state.invoice_data = {
        "invoice_no": "CMI/25-26/Q1/010",
        "invoice_date": "28 April 2025",
        "buyers_order_no": "",
        "buyers_order_date": "17 April 2025",
        "terms_of_payment": "100% Advance with Purchase Order",
        "dispatch_doc_no": "",
        "dispatched_through": "Online",
        "delivery_note_date": "",
        "terms_of_delivery": "Within Month",
        "supplier": {
            "name": "CM Infotech",
            "address": "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur, Chenpur Road, Jagatpur Village, Ahmedabad - 382481",
            "gst_no": "24ANMPP4",
            "msme_reg_no": "UDYAM-",
            "email": "cm.infot",
            "mobile_no": "873391"
        },
        "buyer": {
            "name": "Baldridge Pvt Ltd.",
            "address": "406, Sakar East, 40mt Tarsali - Danteshwar Ring Road, Vadodara 390009",
            "email": "dmistry@b",
            "tel_no": "98987",
            "gst_no": "24AAHCB9",
            "destination": "Vadodara"
        },
        "bank": {
            "bank_name": "XYZ bank",
            "branch": "AHMED",
            "account_no": "881304",
            "ifs_code": "IDFB004"
        }
    }

st.subheader("Invoice Details")
st.session_state.invoice_data["invoice_no"] = st.text_input("Invoice No.", value=st.session_state.invoice_data["invoice_no"])
st.session_state.invoice_data["invoice_date"] = st.text_input("Invoice Date", value=st.session_state.invoice_data["invoice_date"])

st.subheader("Products")
if st.button("➕ Add New Product"):
    st.session_state.products.append({"name": "New Product", "hsn_sac": "", "basic": 0.0, "qty": 1.0, "gst_percent": 18.0})

for i, p in enumerate(st.session_state.products):
    with st.expander(f"Product {i+1}", expanded=i==0):
        st.session_state.products[i]["name"] = st.text_area("Name & Description", p["name"], key=f"name_{i}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.session_state.products[i]["hsn_sac"] = st.text_input("HSN/SAC", p["hsn_sac"], key=f"hsn_{i}")
        with col2:
            st.session_state.products[i]["basic"] = st.number_input("Unit Rate", p["basic"], format="%.2f", key=f"basic_{i}")
        with col3:
            st.session_state.products[i]["qty"] = st.number_input("Quantity", p["qty"], format="%.2f", key=f"qty_{i}")
        with col4:
            st.session_state.products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"gst_{i}")
        if st.button("Remove", key=f"remove_{i}"):
            st.session_state.products.pop(i)
            st.rerun()

st.subheader("Generate Invoice")
if st.button("Generate Tax Invoice", type="primary"):
    pdf = PDF()
    pdf.add_page()
    invoice_data = st.session_state.invoice_data
    products = st.session_state.products

    # --- Supplier & Buyer Info ---
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(100, 5, "Supplier", border='T,L,R', ln=0)
    pdf.cell(0, 5, "Buyer", border='T,L,R', ln=1)
    
    pdf.set_font("Calibri", "", 10)
    pdf.cell(100, 5, pdf.sanitize_text(invoice_data["supplier"]["name"]), border='L,R', ln=0)
    pdf.cell(0, 5, pdf.sanitize_text(invoice_data["buyer"]["name"]), border='L,R', ln=1)

    # Address
    x_pos = pdf.get_x()
    y_pos = pdf.get_y()
    pdf.set_font("Calibri", "", 8)
    pdf.multi_cell(100, 4, pdf.sanitize_text(invoice_data["supplier"]["address"]), border='L,R', align='L')
    pdf.set_xy(x_pos + 100, y_pos)
    pdf.multi_cell(0, 4, pdf.sanitize_text(invoice_data["buyer"]["address"]), border='L,R', align='L')
    
    # GST No.
    pdf.set_font("Calibri", "", 10)
    pdf.cell(100, 5, f"GST No.: {pdf.sanitize_text(invoice_data['supplier']['gst_no'])}", border='L,R', ln=0)
    pdf.cell(0, 5, f"GST No.: {pdf.sanitize_text(invoice_data['buyer']['gst_no'])}", border='L,R', ln=1)
    
    # MSME, Email, etc.
    pdf.cell(100, 5, f"MSME Registration No.: {pdf.sanitize_text(invoice_data['supplier']['msme_reg_no'])}", border='L,R', ln=0)
    pdf.cell(0, 5, f"Email: {pdf.sanitize_text(invoice_data['buyer']['email'])}", border='L,R', ln=1)

    pdf.cell(100, 5, f"E-Mail: {pdf.sanitize_text(invoice_data['supplier']['email'])}", border='L,R', ln=0)
    pdf.cell(0, 5, f"Tel No.: {pdf.sanitize_text(invoice_data['buyer']['tel_no'])}", border='L,R', ln=1)

    pdf.cell(100, 5, f"Mobile No.: {pdf.sanitize_text(invoice_data['supplier']['mobile_no'])}", border='L,R,B', ln=0)
    pdf.cell(0, 5, f"Destination: {pdf.sanitize_text(invoice_data['buyer']['destination'])}", border='L,R,B', ln=1)
    pdf.ln(5)

    # --- Invoice Details Table ---
    pdf.set_font("Calibri", "B", 10)
    col1_width, col2_width, col3_width, col4_width = 45, 50, 45, 50
    # Row 1
    pdf.cell(col1_width, 7, "Invoice No.", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["invoice_no"]), border=1)
    pdf.cell(col3_width, 7, "Invoice Date", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["invoice_date"]), border=1, ln=1)
    # Row 2
    pdf.cell(col1_width, 7, "Buyer's Order No.", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["buyers_order_no"]), border=1)
    pdf.cell(col3_width, 7, "Buyer's Order Date", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["buyers_order_date"]), border=1, ln=1)
    # Row 3
    pdf.cell(col1_width, 7, "Mode/Terms of Payment", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["terms_of_payment"]), border=1)
    pdf.cell(col3_width, 7, "Dispatch Document No.", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["dispatch_doc_no"]), border=1, ln=1)
    # Row 4
    pdf.cell(col1_width, 7, "Dispatched Through", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["dispatched_through"]), border=1)
    pdf.cell(col3_width, 7, "Delivery Note Date", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["delivery_note_date"]), border=1, ln=1)
    # Row 5
    pdf.cell(col1_width, 7, "Terms of Delivery", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["terms_of_delivery"]), border=1)
    pdf.cell(col3_width, 7, "", border=1)
    pdf.cell(col4_width, 7, "", border=1, ln=1)
    pdf.ln(5)

    # --- Product Details Table ---
    pdf.set_font("Calibri", "B", 10)
    col_widths = [10, 80, 20, 20, 20, 20]
    headers = ["Sr. No.", "Description of Goods", "HSN/SAC", "Quantity", "Unit Rate", "Amount"]
    pdf.set_fill_color(220, 220, 220)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("Calibri", "", 10)
    total_basic = 0.0
    total_sgst = 0.0
    total_cgst = 0.0
    for i, p in enumerate(products):
        amount = p["basic"] * p["qty"]
        sgst_amt = amount * (p["gst_percent"] / 200)
        cgst_amt = amount * (p["gst_percent"] / 200)
        final_amount = amount + sgst_amt + cgst_amt
        total_basic += amount
        total_sgst += sgst_amt
        total_cgst += cgst_amt
        
        y_before = pdf.get_y()
        pdf.cell(col_widths[0], 7, str(i + 1), border='L,R', align="C")
        pdf.set_x(pdf.get_x())
        pdf.multi_cell(col_widths[1], 7, pdf.sanitize_text(p["name"]), border=0)
        y_after = pdf.get_y()
        row_height = y_after - y_before
        pdf.set_xy(15, y_before)
        pdf.cell(col_widths[0], row_height, str(i+1), border='L,B,T', align="C")
        pdf.set_xy(15 + col_widths[0], y_before)
        pdf.multi_cell(col_widths[1], row_height, pdf.sanitize_text(p["name"]), border='L,R,B,T')
        pdf.set_xy(15 + col_widths[0] + col_widths[1], y_before)
        pdf.cell(col_widths[2], row_height, pdf.sanitize_text(p['hsn_sac']), border='L,R,B,T', align="C")
        pdf.cell(col_widths[3], row_height, f"{p['qty']:.2f}", border='L,R,B,T', align="R")
        pdf.cell(col_widths[4], row_height, f"{p['basic']:.2f}", border='L,R,B,T', align="R")
        pdf.cell(col_widths[5], row_height, f"{amount:.2f}", border='L,R,B,T', align="R", ln=1)

    # Totals
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(sum(col_widths[:-1]), 7, "Basic Amount", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{total_basic:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "SGST @ 9%", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{total_sgst:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "CGST @ 9%", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{total_cgst:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "Final Amount to be Paid", border=1, align="R")
    grand_total = total_basic + total_sgst + total_cgst
    pdf.cell(col_widths[-1], 7, f"{grand_total:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # --- Amount in Words ---
    amount_in_words = num2words(grand_total, to="currency", currency="INR").title() + " Only/-"
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(0, 7, "Amount Chargeable (in words):", ln=1)
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(0, 7, pdf.sanitize_text(amount_in_words))
    pdf.ln(5)

    # --- Tax Details Table ---
    pdf.section_title("HSN/SAC Tax Details")
    col_widths = [20, 40, 20, 30, 20, 30]
    headers = ["HSN/SAC", "Taxable Value", "Central Tax Rate", "Central Tax Amount", "State Tax Rate", "State Tax Amount"]
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Calibri", "B", 10)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Calibri", "", 10)
    for p in products:
        taxable_value = p["basic"] * p["qty"]
        cgst_amt = taxable_value * (p["gst_percent"] / 200)
        sgst_amt = taxable_value * (p["gst_percent"] / 200)
        pdf.cell(col_widths[0], 7, p["hsn_sac"], border=1, align="C")
        pdf.cell(col_widths[1], 7, f"{taxable_value:.2f}", border=1, align="R")
        pdf.cell(col_widths[2], 7, f"{p['gst_percent']/2:.1f}%", border=1, align="C")
        pdf.cell(col_widths[3], 7, f"{cgst_amt:.2f}", border=1, align="R")
        pdf.cell(col_widths[4], 7, f"{p['gst_percent']/2:.1f}%", border=1, align="C")
        pdf.cell(col_widths[5], 7, f"{sgst_amt:.2f}", border=1, align="R", ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(col_widths[0], 7, "Total", border=1, align="C")
    pdf.cell(col_widths[1], 7, f"{total_basic:.2f}", border=1, align="R")
    pdf.cell(col_widths[2], 7, "", border=1)
    pdf.cell(col_widths[3], 7, f"{total_cgst:.2f}", border=1, align="R")
    pdf.cell(col_widths[4], 7, "", border=1)
    pdf.cell(col_widths[5], 7, f"{total_sgst:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # --- Bank Details ---
    pdf.section_title("Company's Bank Details")
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "Bank Name:", border='L', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank"]["bank_name"]), border='R', ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "Branch:", border='L', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank"]["branch"]), border='R', ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "Account No.:", border='L', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank"]["account_no"]), border='R', ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "IFS Code:", border='L,B', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank"]["ifs_code"]), border='R,B', ln=1)
    pdf.ln(5)

    # --- Declaration and Signature ---
    pdf.set_font("Calibri", "", 8)
    pdf.multi_cell(0, 4, "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF NOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED FROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE")
    pdf.ln(5)

    pdf.set_font("Calibri", "", 10)
    pdf.cell(100, 7, "Customer's Seal and Signature", ln=0)
    pdf.cell(0, 7, "For, CM Infotech", ln=1, align="R")
    pdf.ln(15)
    pdf.cell(100, 7, "", ln=0)
    pdf.set_font("Calibri", "I", 10)
    pdf.cell(0, 7, "Authorized Signatory", ln=1, align="R")

    pdf_bytes = pdf.output(dest="S").encode('latin-1')
    st.success("Tax Invoice generated!")
    st.download_button("⬇ Download Tax Invoice", pdf_bytes, "tax_invoice.pdf", "application/pdf")
