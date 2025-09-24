import streamlit as st
from fpdf import FPDF
from num2words import num2words
import io

# --- PDF Class for Tax Invoice ---
class PDF(FPDF):
    def _init_(self):
        super()._init_()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("Helvetica", "", 10)
        self.set_left_margin(15)
        self.set_right_margin(15)

    def header(self):
        self.set_font("Helvetica", "", 10)
        self.cell(0, 5, "CM Infotech", ln=1, align='R')
        self.cell(0, 5, "We aim for the best", ln=1, align='R')
        self.ln(2)
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 15, "TAX INVOICE", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 5, "This is a Computer Generated Invoice", ln=1, align="C")

    def _render_section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 7, title, border='T,L,R', ln=1, fill=True)
        self.set_font("Helvetica", "", 10)

def create_invoice_pdf(invoice_data):
    pdf = PDF()
    pdf.add_page()

    # --- Supplier and Buyer Details Section ---
    y_start = pdf.get_y()
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 5, "Supplier", border='T,L,R', ln=0)
    pdf.set_xy(115, y_start)
    pdf.cell(95, 5, "Buyer", border='T,L,R', ln=1)

    # Supplier details
    pdf.set_xy(15, y_start + 5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 5, invoice_data["supplier"]["name"], border='L,R', ln=1)
    pdf.set_font("Helvetica", "", 10)
    y_before_supplier = pdf.get_y()
    pdf.set_x(15)
    pdf.multi_cell(100, 5, invoice_data["supplier"]["address"], border=0)
    y_after_supplier = pdf.get_y()
    pdf.set_xy(15, y_after_supplier)
    pdf.cell(100, 5, f"GST No.: {invoice_data['supplier']['gst_no']}", border='L,R', ln=1)
    pdf.set_x(15)
    pdf.cell(100, 5, f"MSME Registration No.: {invoice_data['supplier']['msme_reg_no']}", border='L,R', ln=1)
    pdf.set_x(15)
    pdf.cell(100, 5, f"E-Mail: {invoice_data['supplier']['email']}", border='L,R', ln=1)
    pdf.set_x(15)
    pdf.cell(100, 5, f"Mobile No.: {invoice_data['supplier']['mobile_no']}", border='L,R,B', ln=1)
    
    # Buyer details
    pdf.set_xy(115, y_start + 5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 5, invoice_data["buyer"]["name"], border='L,R', ln=1)
    pdf.set_font("Helvetica", "", 10)
    y_before_buyer = pdf.get_y()
    pdf.set_x(115)
    pdf.multi_cell(95, 5, invoice_data["buyer"]["address"], border=0)
    y_after_buyer = pdf.get_y()
    pdf.set_xy(115, y_after_buyer)
    pdf.cell(95, 5, f"GST No.: {invoice_data['buyer']['gst_no']}", border='L,R', ln=1)
    pdf.set_x(115)
    pdf.cell(95, 5, f"Email: {invoice_data['buyer']['email']}", border='L,R', ln=1)
    pdf.set_x(115)
    pdf.cell(95, 5, f"Tel No.: {invoice_data['buyer']['tel_no']}", border='L,R', ln=1)
    pdf.set_x(115)
    pdf.cell(95, 5, f"Destination: {invoice_data['buyer']['destination']}", border='L,R,B', ln=1)
    
    # Sync cursor position
    max_y_after_details = max(y_after_supplier + 20, y_after_buyer + 20)
    pdf.set_y(max_y_after_details)
    pdf.ln(5)

    # --- Invoice Details Section (Modified to match TAX_DEMO__.pdf) ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Invoice No.", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["invoice_no"], border=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Invoice Date", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["invoice_date"], border=1, ln=1)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Buyer's Order No.", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["buyers_order_no"], border=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Buyer's Order Date", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["buyers_order_date"], border=1, ln=1)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Mode/Terms of Payment", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["terms_of_payment"], border=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Dispatch Doc No.", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["dispatch_doc_no"], border=1, ln=1)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Dispatched Through", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["dispatched_through"], border=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Delivery Note Date", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["delivery_note_date"], border=1, ln=1)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Terms of Delivery", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["terms_of_delivery"], border=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Other Reference(s)", border=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 7, invoice_data["invoice"]["other_references"], border=1, ln=1)
    pdf.ln(5)

    # --- Products Table ---
    pdf.set_font("Helvetica", "B", 10)
    col_widths = [10, 80, 20, 20, 20, 20]
    headers = ["Sr. No.", "Description of Goods", "HSN/SAC", "Quantity", "Unit Rate", "Amount"]
    pdf.set_fill_color(220, 220, 220)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    total_basic = 0.0
    for i, p in enumerate(invoice_data["items"]):
        amount = p["unit_rate"] * p["quantity"]
        total_basic += amount
        
        y_start_cell = pdf.get_y()
        x_start_cell = pdf.get_x()
        
        pdf.multi_cell(col_widths[1], 5, p["description"], border=0)
        
        y_after_description = pdf.get_y()
        row_height = y_after_description - y_start_cell
        
        pdf.set_xy(x_start_cell, y_start_cell)
        pdf.cell(col_widths[0], row_height, str(i + 1), border=1, align="C")
        pdf.set_x(x_start_cell + col_widths[0] + col_widths[1])
        pdf.cell(col_widths[2], row_height, p['hsn_sac'], border=1, align="C")
        pdf.cell(col_widths[3], row_height, f"{p['quantity']:.2f}", border=1, align="R")
        pdf.cell(col_widths[4], row_height, f"{p['unit_rate']:.2f}", border=1, align="R")
        pdf.cell(col_widths[5], row_height, f"{amount:.2f}", border=1, align="R")
        pdf.set_xy(x_start_cell + col_widths[0], y_start_cell)
        pdf.cell(col_widths[1], row_height, "", border=1)
        pdf.set_y(y_after_description)
    
    # --- Totals Section (Modified to match TAX_DEMO__.pdf) ---
    pdf.set_font("Helvetica", "B", 10)
    
    # Basic Amount
    pdf.cell(sum(col_widths[:-1]), 7, "Basic Amount", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{total_basic:.2f}", border=1, align="R", ln=1)

    # SGST
    pdf.cell(sum(col_widths[:-1]), 7, "SGST @ 9%", border='L,R', align="R")
    pdf.cell(col_widths[-1], 7, f"{invoice_data['totals']['sgst']:.2f}", border='L,R', align="R", ln=1)

    # CGST and Round Off
    pdf.cell(sum(col_widths[:-2]), 7, "CGST @ 9%", border='L,R', align="R")
    pdf.cell(col_widths[-2] + col_widths[-1], 7, f"{invoice_data['totals']['cgst']:.2f}", border='L,R', align="R", ln=1)

    pdf.cell(sum(col_widths[:-2]), 7, "Round Off", border='L,R,B', align="R")
    pdf.cell(col_widths[-2] + col_widths[-1], 7, "0.00", border='L,R,B', align="R", ln=1)

    # Final Amount
    pdf.cell(sum(col_widths[:-1]), 7, "Final Amount to be Paid", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{invoice_data['totals']['final_amount']:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # --- Amount in Words ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "Amount Chargeable (in words):", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 7, invoice_data["totals"]["amount_in_words"])
    pdf.ln(5)

    # --- Tax Details Table (Modified to match TAX_DEMO__.pdf) ---
    pdf._render_section_title("HSN/SAC Tax Details")
    col_widths_tax = [20, 40, 25, 25, 25, 25]
    
    pdf.set_font("Helvetica", "B", 10)
    y_start_tax_header = pdf.get_y()
    pdf.cell(col_widths_tax[0], 14, "HSN/SAN", border=1, align="C", fill=True)
    pdf.cell(col_widths_tax[1], 14, "Taxable Value", border=1, align="C", fill=True)
    pdf.cell(sum(col_widths_tax[2:4]), 7, "Central Tax", border=1, align="C", fill=True)
    pdf.cell(sum(col_widths_tax[4:6]), 7, "State Tax", border=1, align="C", fill=True, ln=1)
    
    pdf.set_x(15 + col_widths_tax[0] + col_widths_tax[1])
    pdf.cell(col_widths_tax[2], 7, "Rate", border=1, align="C")
    pdf.cell(col_widths_tax[3], 7, "Amount", border=1, align="C")
    pdf.cell(col_widths_tax[4], 7, "Rate", border=1, align="C")
    pdf.cell(col_widths_tax[5], 7, "Amount", border=1, align="C", ln=1)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(col_widths_tax[0], 7, invoice_data["tax_details"]["hsn_sac"], border=1, align="C")
    pdf.cell(col_widths_tax[1], 7, f"{invoice_data['tax_details']['taxable_value']:.2f}", border=1, align="R")
    pdf.cell(col_widths_tax[2], 7, f"{invoice_data['tax_details']['central_rate']}%", border=1, align="C")
    pdf.cell(col_widths_tax[3], 7, f"{invoice_data['tax_details']['central_amount']:.2f}", border=1, align="R")
    pdf.cell(col_widths_tax[4], 7, f"{invoice_data['tax_details']['state_rate']}%", border=1, align="C")
    pdf.cell(col_widths_tax[5], 7, f"{invoice_data['tax_details']['state_amount']:.2f}", border=1, align="R", ln=1)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(col_widths_tax[0], 7, "Total", border=1, align="C")
    pdf.cell(col_widths_tax[1], 7, f"{invoice_data['tax_details']['total_taxable']:.2f}", border=1, align="R")
    pdf.cell(sum(col_widths_tax[2:4]), 7, f"{invoice_data['tax_details']['total_tax'] / 2:.2f}", border=1, align="R")
    pdf.cell(sum(col_widths_tax[4:6]), 7, f"{invoice_data['tax_details']['total_tax'] / 2:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # --- Bank Details ---
    pdf._render_section_title("Company's Bank Details")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, "Bank Name:", border='L', ln=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, invoice_data["bank_details"]["bank_name"], border='R', ln=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, "Branch:", border='L', ln=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, invoice_data["bank_details"]["branch"], border='R', ln=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, "Account No.:", border='L', ln=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, invoice_data["bank_details"]["account_no"], border='R', ln=1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, "IFS Code:", border='L,B', ln=0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, invoice_data["bank_details"]["ifs_code"], border='R,B', ln=1)
    pdf.ln(5)

    # --- Declaration and Signature ---
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(0, 4, invoice_data["declaration"])
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 7, "Customer's Seal and Signature", ln=0)
    pdf.cell(0, 7, "For, CM Infotech", ln=1, align="R")
    pdf.ln(15)
    pdf.cell(100, 7, "", ln=0)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 7, "Authorized Signatory", ln=1, align="R")

    return io.BytesIO(pdf.output())

# --- Main Streamlit Application ---

st.title("Tax Invoice Generator")

# Sample data dictionary to pre-populate the fields
sample_invoice_data = {
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
        "gst_no": "24AAHCB9",
        "email": "dmistry@b",
        "tel_no": "98987",
        "destination": "Vadodara"
    },
    "invoice": {
        "invoice_no": "CMI/25-26/Q1/010",
        "invoice_date": "28 April 2025",
        "buyers_order_no": "",
        "buyers_order_date": "17 April 2025",
        "terms_of_payment": "100% Advance with Purchase Order",
        "dispatch_doc_no": "",
        "dispatched_through": "Online",
        "delivery_note_date": "",
        "terms_of_delivery": "Within Month",
        "other_references": ""
    },
    "items": [
        {
            "description": "Autodesk BIM Collaborate Pro - Single-user CLOUD Commercial New Annual Subscription Serial #575-26831580 Contract #110004988191 End Date: 17/04/2026",
            "hsn_sac": "997331",
            "quantity": 1.00,
            "unit_rate": 36500.00
        }
    ],
    "totals": {
        "sgst": 3285.00,
        "cgst": 3285.00,
        "final_amount": 43070.00,
        "amount_in_words": "Rs. Forty Three Thousand And Seventy Only/-"
    },
    "tax_details": {
        "hsn_sac": "997331",
        "taxable_value": 36500.00,
        "central_rate": 9,
        "central_amount": 3285.00,
        "state_rate": 9,
        "state_amount": 3285.00,
        "total_taxable": 36500.00,
        "total_tax": 6570.00
    },
    "bank_details": {
        "bank_name": "XYZ bank",
        "branch": "AHMED",
        "account_no": "881304",
        "ifs_code": "IDFB004"
    },
    "declaration": "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF NOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED FROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE"
}

# Generate PDF button and download link
if st.button("Generate Invoice PDF"):
    pdf_bytes = create_invoice_pdf(sample_invoice_data)
    
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name="tax_invoice.pdf",
        mime="application/pdf")

# import streamlit as st
# from fpdf import FPDF
# from num2words import num2words
# import io

# # --- PDF Class for Tax Invoice ---
# class PDF(FPDF):
#     def _init_(self):
#         super()._init_()
#         self.set_auto_page_break(auto=True, margin=15)
#         self.set_font("Helvetica", "", 10)
#         self.set_left_margin(15)
#         self.set_right_margin(15)

#     def header(self):
#         self.set_font("Helvetica", "", 10)
#         self.cell(0, 5, "CM Infotech", ln=1, align='R')
#         self.cell(0, 5, "We aim for the best", ln=1, align='R')
#         self.ln(2)
#         self.set_font("Helvetica", "B", 18)
#         self.cell(0, 15, "TAX INVOICE", ln=True, align="C")
#         self.ln(2)

#     def footer(self):
#         self.set_y(-15)
#         self.set_font("Helvetica", "I", 8)
#         self.cell(0, 5, "This is a Computer Generated Invoice", ln=1, align="C")

#     def _render_section_title(self, title):
#         self.set_font("Helvetica", "B", 12)
#         self.set_fill_color(220, 220, 220)
#         self.cell(0, 7, title, border='T,L,R', ln=1, fill=True)
#         self.set_font("Helvetica", "", 10)

# def create_invoice_pdf(invoice_data):
#     pdf = PDF()
#     pdf.add_page()

#     # --- Supplier and Buyer Details Section ---
#     y_start = pdf.get_y()
    
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(100, 5, "Supplier", border='T,L,R', ln=0)
#     pdf.set_xy(115, y_start)
#     pdf.cell(95, 5, "Buyer", border='T,L,R', ln=1)

#     # Supplier details
#     pdf.set_xy(15, y_start + 5)
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(100, 5, invoice_data["supplier"]["name"], border='L,R', ln=1)
#     pdf.set_font("Helvetica", "", 10)
#     y_before_supplier = pdf.get_y()
#     pdf.set_x(15)
#     pdf.multi_cell(100, 5, invoice_data["supplier"]["address"], border=0)
#     y_after_supplier = pdf.get_y()
#     pdf.set_xy(15, y_after_supplier)
#     pdf.cell(100, 5, f"GST No.: {invoice_data['supplier']['gst_no']}", border='L,R', ln=1)
#     pdf.set_x(15)
#     pdf.cell(100, 5, f"MSME Registration No.: {invoice_data['supplier']['msme_reg_no']}", border='L,R', ln=1)
#     pdf.set_x(15)
#     pdf.cell(100, 5, f"E-Mail: {invoice_data['supplier']['email']}", border='L,R', ln=1)
#     pdf.set_x(15)
#     pdf.cell(100, 5, f"Mobile No.: {invoice_data['supplier']['mobile_no']}", border='L,R,B', ln=1)
    
#     # Buyer details
#     pdf.set_xy(115, y_start + 5)
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(95, 5, invoice_data["buyer"]["name"], border='L,R', ln=1)
#     pdf.set_font("Helvetica", "", 10)
#     y_before_buyer = pdf.get_y()
#     pdf.set_x(115)
#     pdf.multi_cell(95, 5, invoice_data["buyer"]["address"], border=0)
#     y_after_buyer = pdf.get_y()
#     pdf.set_xy(115, y_after_buyer)
#     pdf.cell(95, 5, f"GST No.: {invoice_data['buyer']['gst_no']}", border='L,R', ln=1)
#     pdf.set_x(115)
#     pdf.cell(95, 5, f"Email: {invoice_data['buyer']['email']}", border='L,R', ln=1)
#     pdf.set_x(115)
#     pdf.cell(95, 5, f"Tel No.: {invoice_data['buyer']['tel_no']}", border='L,R', ln=1)
#     pdf.set_x(115)
#     pdf.cell(95, 5, f"Destination: {invoice_data['buyer']['destination']}", border='L,R,B', ln=1)
    
#     # Sync cursor position
#     max_y_after_details = max(y_after_supplier + 20, y_after_buyer + 20)
#     pdf.set_y(max_y_after_details)
#     pdf.ln(5)

#     # --- Invoice Details Table ---
#     pdf.set_font("Helvetica", "B", 10)
#     col_widths = [45, 50, 45, 50]
    
#     pdf.cell(col_widths[0], 7, "Invoice No.", border=1)
#     pdf.cell(col_widths[1], 7, invoice_data["invoice"]["invoice_no"], border=1)
#     pdf.cell(col_widths[2], 7, "Invoice Date", border=1)
#     pdf.cell(col_widths[3], 7, invoice_data["invoice"]["invoice_date"], border=1, ln=1)
    
#     pdf.cell(col_widths[0], 7, "Buyer's Order No.", border=1)
#     pdf.cell(col_widths[1], 7, invoice_data["invoice"]["buyers_order_no"], border=1)
#     pdf.cell(col_widths[2], 7, "Buyer's Order Date", border=1)
#     pdf.cell(col_widths[3], 7, invoice_data["invoice"]["buyers_order_date"], border=1, ln=1)
    
#     pdf.cell(col_widths[0], 7, "Mode/Terms of Payment", border=1)
#     pdf.cell(col_widths[1], 7, invoice_data["invoice"]["terms_of_payment"], border=1)
#     pdf.cell(col_widths[2], 7, "Dispatch Doc No.", border=1)
#     pdf.cell(col_widths[3], 7, invoice_data["invoice"]["dispatch_doc_no"], border=1, ln=1)
    
#     pdf.cell(col_widths[0], 7, "Dispatched Through", border=1)
#     pdf.cell(col_widths[1], 7, invoice_data["invoice"]["dispatched_through"], border=1)
#     pdf.cell(col_widths[2], 7, "Delivery Note Date", border=1)
#     pdf.cell(col_widths[3], 7, invoice_data["invoice"]["delivery_note_date"], border=1, ln=1)
    
#     pdf.cell(col_widths[0], 7, "Terms of Delivery", border=1)
#     pdf.cell(col_widths[1], 7, invoice_data["invoice"]["terms_of_delivery"], border=1)
#     pdf.cell(col_widths[2], 7, "", border=1)
#     pdf.cell(col_widths[3], 7, "", border=1, ln=1)
#     pdf.ln(5)

#     # --- Products Table ---
#     pdf.set_font("Helvetica", "B", 10)
#     col_widths = [10, 80, 20, 20, 20, 20]
#     headers = ["Sr. No.", "Description of Goods", "HSN/SAC", "Quantity", "Unit Rate", "Amount"]
#     pdf.set_fill_color(220, 220, 220)
#     for h, w in zip(headers, col_widths):
#         pdf.cell(w, 7, h, border=1, align="C", fill=True)
#     pdf.ln()

#     pdf.set_font("Helvetica", "", 10)
#     total_basic = 0.0
#     for i, p in enumerate(invoice_data["items"]):
#         amount = p["unit_rate"] * p["quantity"]
#         total_basic += amount
        
#         y_start_cell = pdf.get_y()
#         x_start_cell = pdf.get_x()
        
#         pdf.multi_cell(col_widths[1], 5, p["description"], border=0)
        
#         y_after_description = pdf.get_y()
#         row_height = y_after_description - y_start_cell
        
#         pdf.set_xy(x_start_cell, y_start_cell)
#         pdf.cell(col_widths[0], row_height, str(i + 1), border=1, align="C")
#         pdf.set_x(x_start_cell + col_widths[0] + col_widths[1])
#         pdf.cell(col_widths[2], row_height, p['hsn_sac'], border=1, align="C")
#         pdf.cell(col_widths[3], row_height, f"{p['quantity']:.2f}", border=1, align="R")
#         pdf.cell(col_widths[4], row_height, f"{p['unit_rate']:.2f}", border=1, align="R")
#         pdf.cell(col_widths[5], row_height, f"{amount:.2f}", border=1, align="R")
#         pdf.set_xy(x_start_cell + col_widths[0], y_start_cell)
#         pdf.cell(col_widths[1], row_height, "", border=1)
#         pdf.set_y(y_after_description)
    
#     # Totals
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(sum(col_widths[:-1]), 7, "Basic Amount", border=1, align="R")
#     pdf.cell(col_widths[-1], 7, f"{total_basic:.2f}", border=1, align="R", ln=1)
    
#     # New row for SGST and CGST
#     pdf.cell(sum(col_widths[:-2]), 7, "SGST @ 9%", border='L,R', align="R")
#     pdf.cell(col_widths[-2] + col_widths[-1], 7, f"{invoice_data['totals']['sgst']:.2f}", border='L,R', align="R", ln=1)
#     pdf.cell(sum(col_widths[:-2]), 7, "CGST @ 9%", border='L,R,B', align="R")
#     pdf.cell(col_widths[-2] + col_widths[-1], 7, f"{invoice_data['totals']['cgst']:.2f}", border='L,R,B', align="R", ln=1)
    
#     pdf.cell(sum(col_widths[:-1]), 7, "Final Amount to be Paid", border=1, align="R")
#     pdf.cell(col_widths[-1], 7, f"{invoice_data['totals']['final_amount']:.2f}", border=1, align="R", ln=1)
#     pdf.ln(5)

#     # --- Amount in Words ---
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(0, 7, "Amount Chargeable (in words):", ln=1)
#     pdf.set_font("Helvetica", "", 10)
#     pdf.multi_cell(0, 7, invoice_data["totals"]["amount_in_words"])
#     pdf.ln(5)

#     # --- Tax Details Table ---
#     pdf._render_section_title("HSN/SAC Tax Details")
#     col_widths = [20, 40, 20, 30, 20, 30]
    
#     pdf.set_font("Helvetica", "B", 10)
#     y_start_tax_header = pdf.get_y()
#     pdf.cell(col_widths[0], 14, "HSN/SAC", border=1, align="C", fill=True)
#     pdf.cell(col_widths[1], 14, "Taxable Value", border=1, align="C", fill=True)
#     pdf.cell(sum(col_widths[2:4]), 7, "Central Tax", border=1, align="C", fill=True)
#     pdf.cell(sum(col_widths[4:6]), 7, "State Tax", border=1, align="C", fill=True)
#     pdf.ln(7)
#     pdf.set_x(15 + col_widths[0] + col_widths[1])
#     pdf.cell(col_widths[2], 7, "Rate", border=1, align="C")
#     pdf.cell(col_widths[3], 7, "Amount", border=1, align="C")
#     pdf.cell(col_widths[4], 7, "Rate", border=1, align="C")
#     pdf.cell(col_widths[5], 7, "Amount", border=1, align="C")
#     pdf.ln()

#     pdf.set_font("Helvetica", "", 10)
#     pdf.cell(col_widths[0], 7, invoice_data["tax_details"]["hsn_sac"], border=1, align="C")
#     pdf.cell(col_widths[1], 7, f"{invoice_data['tax_details']['taxable_value']:.2f}", border=1, align="R")
#     pdf.cell(col_widths[2], 7, f"{invoice_data['tax_details']['central_rate']}%", border=1, align="C")
#     pdf.cell(col_widths[3], 7, f"{invoice_data['tax_details']['central_amount']:.2f}", border=1, align="R")
#     pdf.cell(col_widths[4], 7, f"{invoice_data['tax_details']['state_rate']}%", border=1, align="C")
#     pdf.cell(col_widths[5], 7, f"{invoice_data['tax_details']['state_amount']:.2f}", border=1, align="R", ln=1)
    
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(col_widths[0], 7, "Total", border=1, align="C")
#     pdf.cell(col_widths[1], 7, f"{invoice_data['tax_details']['total_taxable']:.2f}", border=1, align="R")
#     pdf.cell(sum(col_widths[2:4]), 7, f"{invoice_data['tax_details']['total_tax'] / 2:.2f}", border=1, align="R")
#     pdf.cell(sum(col_widths[4:6]), 7, f"{invoice_data['tax_details']['total_tax'] / 2:.2f}", border=1, align="R", ln=1)
#     pdf.ln(5)

#     # --- Bank Details ---
#     pdf._render_section_title("Company's Bank Details")
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(50, 7, "Bank Name:", border='L', ln=0)
#     pdf.set_font("Helvetica", "", 10)
#     pdf.cell(0, 7, invoice_data["bank_details"]["bank_name"], border='R', ln=1)
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(50, 7, "Branch:", border='L', ln=0)
#     pdf.set_font("Helvetica", "", 10)
#     pdf.cell(0, 7, invoice_data["bank_details"]["branch"], border='R', ln=1)
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(50, 7, "Account No.:", border='L', ln=0)
#     pdf.set_font("Helvetica", "", 10)
#     pdf.cell(0, 7, invoice_data["bank_details"]["account_no"], border='R', ln=1)
#     pdf.set_font("Helvetica", "B", 10)
#     pdf.cell(50, 7, "IFS Code:", border='L,B', ln=0)
#     pdf.set_font("Helvetica", "", 10)
#     pdf.cell(0, 7, invoice_data["bank_details"]["ifs_code"], border='R,B', ln=1)
#     pdf.ln(5)

#     # --- Declaration and Signature ---
#     pdf.set_font("Helvetica", "", 8)
#     pdf.multi_cell(0, 4, invoice_data["declaration"])
#     pdf.ln(5)
    
#     pdf.set_font("Helvetica", "", 10)
#     pdf.cell(100, 7, "Customer's Seal and Signature", ln=0)
#     pdf.cell(0, 7, "For, CM Infotech", ln=1, align="R")
#     pdf.ln(15)
#     pdf.cell(100, 7, "", ln=0)
#     pdf.set_font("Helvetica", "I", 10)
#     pdf.cell(0, 7, "Authorized Signatory", ln=1, align="R")

#     return io.BytesIO(pdf.output())

# # --- Streamlit UI ---
# st.set_page_config(page_title="Tax Invoice Generator", page_icon="📄", layout="wide")
# st.title("📄 Tax Invoice Generator")

# # Initialize Session State
# if "invoice_data" not in st.session_state:
#     st.session_state.invoice_data = {
#         "supplier": {
#             "name": "CM Infotech",
#             "address": "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur, Chenpur Road, Jagatpur Village, Ahmedabad - 382481",
#             "gst_no": "24ANMPP4",
#             "msme_reg_no": "UDYAM-",
#             "email": "cm.infot",
#             "mobile_no": "873391",
#         },
#         "buyer": {
#             "name": "Baldridge Pvt Ltd.",
#             "address": "406, Sakar East, 40mt Tarsali - Danteshwar Ring Road, Vadodara 390009",
#             "email": "dmistry@b",
#             "tel_no": "98987",
#             "gst_no": "24AAHCB9",
#             "destination": "Vadodara",
#         },
#         "invoice": {
#             "invoice_no": "CMI/25-26/Q1/010",
#             "invoice_date": "28 April 2025",
#             "buyers_order_no": "",
#             "buyers_order_date": "17 April 2025",
#             "terms_of_payment": "100% Advance with Purchase Order",
#             "dispatch_doc_no": "",
#             "dispatched_through": "Online",
#             "delivery_note_date": "",
#             "terms_of_delivery": "Within Month",
#         },
#         "items": [
#             {
#                 "description": "Autodesk BIM Collaborate Pro - Single-user CLOUD Commercial New Annual Subscription Serial #575-26831580 Contract #110004988191 End Date: 17/04/2026",
#                 "hsn_sac": "997331",
#                 "quantity": 1.00,
#                 "unit_rate": 36500.00,
#             }
#         ],
#         "totals": {
#             "basic_amount": 36500.00,
#             "sgst": 3285.00,
#             "cgst": 3285.00,
#             "final_amount": 43070.00,
#             "amount_in_words": "Rs. Forty Three Thousand And Seventy Only/-"
#         },
#         "tax_details": {
#             "hsn_sac": "997331",
#             "taxable_value": 36500.00,
#             "central_rate": 9,
#             "central_amount": 3285.00,
#             "state_rate": 9,
#             "state_amount": 3285.00,
#             "total_taxable": 36500.00,
#             "total_tax": 6570.00
#         },
#         "bank_details": {
#             "bank_name": "XYZ bank",
#             "branch": "AHMED",
#             "account_no": "881304",
#             "ifs_code": "IDFB004",
#         },
#         "declaration": "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF NOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED FROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE"
#     }
    
# st.subheader("Invoice Details")
# col1, col2 = st.columns(2)
# with col1:
#     st.session_state.invoice_data["invoice"]["invoice_no"] = st.text_input("Invoice No.", value=st.session_state.invoice_data["invoice"]["invoice_no"])
# with col2:
#     st.session_state.invoice_data["invoice"]["invoice_date"] = st.text_input("Invoice Date", value=st.session_state.invoice_data["invoice"]["invoice_date"])

# st.subheader("Products")
# if st.button("➕ Add New Product"):
#     st.session_state.invoice_data["items"].append({
#         "description": "New Product",
#         "hsn_sac": "",
#         "quantity": 1.0,
#         "unit_rate": 0.0,
#     })

# for i, p in enumerate(st.session_state.invoice_data["items"]):
#     with st.expander(f"Product {i+1}", expanded=i==0):
#         st.session_state.invoice_data["items"][i]["description"] = st.text_area("Name & Description", p["description"], key=f"desc_{i}")
#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.session_state.invoice_data["items"][i]["hsn_sac"] = st.text_input("HSN/SAC", p["hsn_sac"], key=f"hsn_{i}")
#         with col2:
#             st.session_state.invoice_data["items"][i]["unit_rate"] = st.number_input("Unit Rate", p["unit_rate"], format="%.2f", key=f"basic_{i}")
#         with col3:
#             st.session_state.invoice_data["items"][i]["quantity"] = st.number_input("Quantity", p["quantity"], format="%.2f", key=f"qty_{i}")
#         if st.button("Remove", key=f"remove_{i}"):
#             st.session_state.invoice_data["items"].pop(i)
#             st.rerun()

# st.subheader("Generate Invoice")
# if st.button("Generate Tax Invoice", type="primary"):
#     pdf_bytes_io = create_invoice_pdf(st.session_state.invoice_data)
#     st.success("Tax Invoice generated!")
#     st.download_button("⬇ Download Tax Invoice", pdf_bytes_io.getvalue(), "tax_invoice.pdf", "application/pdf")
