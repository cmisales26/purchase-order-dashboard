import streamlit as st
from fpdf import FPDF
import pandas as pd
from num2words import num2words
import datetime
import io
from PIL import Image
import os

# --- Global Data and Configuration ---
PRODUCT_CATALOG = {
    "Autodesk Commercial Software License": {"basic": 2000.0, "gst_percent": 18.0},
    "Solidworks Premium": {"basic": 50000.0, "gst_percent": 18.0},
    "Catia License": {"basic": 75000.0, "gst_percent": 18.0},
    "Mastercam Module": {"basic": 30000.0, "gst_percent": 18.0},
    "Siemens NX": {"basic": 65000.0, "gst_percent": 18.0},
}

# --- PDF Class for Tax Invoice ---
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_font("Helvetica", "", 8)
        self.set_left_margin(15)
        self.set_right_margin(15)

    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 6, "TAX INVOICE", ln=True, align="C")
        self.ln(3)

def create_invoice_pdf(invoice_data,logo_file="logo_final.jpg",stamp_file = "stamp.jpg"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica",size=10)

    # --- Logo on top right ---
    if logo_file:
        try:
            pdf.image(logo_file, x=170, y=2.5, w=35)
        except Exception as e:
            st.warning(f"Could not add logo: {e}")

    # --- Invoice Details (top-right) ---
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(140, 20)
    pdf.multi_cell(60, 4,
        f"Invoice No.: {invoice_data['invoice']['invoice_no']}\n"
        f"Invoice Date: {invoice_data['invoice']['date']}"
    )

    # --- Vendor & Buyer ---
    pdf.set_y(35)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(95, 5, "CM Infotech", ln=False)
    pdf.set_xy(110, 35)
    pdf.cell(95, 5, "Buyer", ln=True)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(15, 40)
    pdf.multi_cell(95, 4, invoice_data['vendor']['address'])
    y_after_vendor = pdf.get_y()

    pdf.set_xy(110, 40)
    pdf.multi_cell(95, 4,
        f"{invoice_data['buyer']['name']}\n"
        f"{invoice_data['buyer']['address']}"
    )
    y_after_buyer = pdf.get_y()
    
    # --- GST, MSME ---
    pdf.set_xy(15, max(y_after_vendor, y_after_buyer) + 2)
    pdf.multi_cell(95, 4,
        f"GST No.: {invoice_data['vendor']['gst']}\n"
        f"MSME Registration No.: {invoice_data['vendor']['msme']}"
    )
    
    pdf.set_xy(110, max(y_after_vendor, y_after_buyer) + 2)
    pdf.multi_cell(95, 4,
        f"GST No.: {invoice_data['buyer']['gst']}"
    )

    # --- Invoice Specifics ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(95, 4, f"Buyer's Order No.: {invoice_data['invoice_details']['buyers_order_no']}")
    pdf.cell(95, 4, f"Buyer's Order Date: {invoice_data['invoice_details']['buyers_order_date']}", ln=True)
    pdf.cell(95, 4, f"Dispatch Through: {invoice_data['invoice_details']['dispatched_through']}")
    pdf.cell(95, 4, f"Terms of delivery: {invoice_data['invoice_details']['terms_of_delivery']}", ln=True)
    pdf.cell(95, 4, f"Destination: {invoice_data['invoice_details']['destination']}", ln=True)

    # --- Item Table Header ---
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(10, 5, "Sr. No.", border=1, align="C")
    pdf.cell(85, 5, "Description of Goods", border=1, align="C")
    pdf.cell(20, 5, "HSN/SAC", border=1, align="C")
    pdf.cell(20, 5, "Quantity", border=1, align="C")
    pdf.cell(25, 5, "Unit Rate", border=1, align="C")
    pdf.cell(30, 5, "Amount", border=1, ln=True, align="C")

    # --- Items ---
    pdf.set_font("Helvetica", "", 8)
    col_widths = [10, 85, 20, 20, 25, 30]
    line_height = 4

    for i, item in enumerate(invoice_data["items"], start=1):
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        pdf.set_font("Helvetica", "", 8)
        
        # Description
        pdf.set_xy(x_start + col_widths[0], y_start)
        pdf.multi_cell(col_widths[1], line_height, item['description'], border=1)
        y_after_desc = pdf.get_y()

        row_height = y_after_desc - y_start
        
        # Other cells for the row
        pdf.set_xy(x_start, y_start)
        pdf.multi_cell(col_widths[0], row_height, str(i), border=1, align="C")
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
        pdf.multi_cell(col_widths[2], row_height, item['hsn'], border=1, align="C")
        
        pdf.set_xy(x_start + sum(col_widths[:3]), y_start)
        pdf.multi_cell(col_widths[3], row_height, str(item['quantity']), border=1, align="C")
        
        pdf.set_xy(x_start + sum(col_widths[:4]), y_start)
        pdf.multi_cell(col_widths[4], row_height, f"{item['unit_rate']:.2f}", border=1, align="R")
        
        amount = item['quantity'] * item['unit_rate']
        pdf.set_xy(x_start + sum(col_widths[:-1]), y_start)
        pdf.multi_cell(col_widths[5], row_height, f"{amount:.2f}", border=1, align="R")

        pdf.set_xy(x_start, y_start + row_height)

    # --- Totals ---
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(sum(col_widths[:5]), 5, "Basic Amount", border=1, align="R")
    pdf.cell(30, 5, f"{invoice_data['totals']['basic_amount']:.2f}", border=1, ln=True, align="R")
    
    pdf.cell(sum(col_widths[:5]), 5, "SGST @ 9%", border=1, align="R")
    pdf.cell(30, 5, f"{invoice_data['totals']['sgst']:.2f}", border=1, ln=True, align="R")
    
    pdf.cell(sum(col_widths[:5]), 5, "CGST @ 9%", border=1, align="R")
    pdf.cell(30, 5, f"{invoice_data['totals']['cgst']:.2f}", border=1, ln=True, align="R")

    pdf.cell(sum(col_widths[:5]), 5, "Final Amount to be Paid", border=1, align="R")
    pdf.cell(30, 5, f"{invoice_data['totals']['final_amount']:.2f}", border=1, ln=True, align="R")
    
    # --- Amount in Words ---
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, f"Amount Chargeable (in words): {invoice_data['totals']['amount_in_words']}", ln=True, border=1)

    # --- Tax Summary Table ---
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(35, 5, "HSN/SAN", border=1, align="C")
    pdf.cell(35, 5, "Taxable Value", border=1, align="C")
    pdf.cell(60, 5, "Central Tax", border=1, align="C")
    pdf.cell(60, 5, "State Tax", border=1, ln=True, align="C")

    pdf.cell(35, 5, "", border="L", ln=False)
    pdf.cell(35, 5, "", border="L", ln=False)
    pdf.cell(30, 5, "Rate", border="L", align="C")
    pdf.cell(30, 5, "Amount", border="LR", align="C")
    pdf.cell(30, 5, "Rate", border="L", align="C")
    pdf.cell(30, 5, "Amount", border="LR", ln=True, align="C")

    pdf.set_font("Helvetica", "", 8)
    hsn_tax_value = sum(item['quantity'] * item['unit_rate'] for item in invoice_data["items"])
    hsn_sgst = hsn_tax_value * 0.09
    hsn_cgst = hsn_tax_value * 0.09
    
    pdf.cell(35, 5, "997331", border=1, align="C")
    pdf.cell(35, 5, f"{hsn_tax_value:.2f}", border=1, align="C")
    pdf.cell(30, 5, "9%", border=1, align="C")
    pdf.cell(30, 5, f"{hsn_sgst:.2f}", border=1, align="C")
    pdf.cell(30, 5, "9%", border=1, align="C")
    pdf.cell(30, 5, f"{hsn_cgst:.2f}", border=1, ln=True, align="C")

    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(35, 5, "Total", border=1, align="C")
    pdf.cell(35, 5, f"{hsn_tax_value:.2f}", border=1, align="C")
    pdf.cell(30, 5, "", border=1, align="C")
    pdf.cell(30, 5, f"{hsn_sgst:.2f}", border=1, align="C")
    pdf.cell(30, 5, "", border=1, align="C")
    pdf.cell(30, 5, f"{hsn_cgst:.2f}", border=1, ln=True, align="C")
    
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, f"Tax Amount (in words): {invoice_data['totals']['tax_in_words']}", ln=True, border=1)

    # --- Bank Details ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "Company's Bank Details", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(0, 4,
        f"Bank Name: {invoice_data['bank']['name']}\n"
        f"Branch: {invoice_data['bank']['branch']}\n"
        f"Account No.: {invoice_data['bank']['account_no']}\n"
        f"IFS Code: {invoice_data['bank']['ifsc']}"
    )

    # --- Declaration ---
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "Declaration:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(0, 4, invoice_data['declaration'])
    
    # --- Signature ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "For CM Infotech.", ln=True, align="R")

    if stamp_file:
        try:
            stamp_width = 25
            pdf.image(stamp_file, x=210 - 15 - stamp_width, y=pdf.get_y(), w=stamp_width)
            pdf.ln(15) 
        except Exception as e:
            st.warning(f"Could not add stamp: {e}")
    else:
        pdf.ln(10) 
        
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Authorized Signatory", ln=True, align="R")
    
    # --- Footer Info ---
    pdf.set_y(-40)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "This is a Computer Generated Invoice", ln=True, align="C")
    pdf.set_y(-30)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
    pdf.set_y(-25)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "Email: info@cminfotech.com Mo.+91 873 391 5721", ln=True, align="C")
    
    # Fix: output directly to bytes
    pdf_bytes = pdf.output(dest="S").encode('latin-1') if isinstance(pdf.output(dest="S"), str) else pdf.output(dest="S")
    return pdf_bytes


# --- PDF Class for Purchase Order (Existing - adapted for robustness) ---
class PO_PDF(FPDF):
    def __init__(self, po_number="PO-N/A", po_date="Date N/A"):
        super().__init__()
        self.set_auto_page_break(auto=False, margin=0)
        self.set_left_margin(15)
        self.set_right_margin(15)
        self.logo_path = os.path.join(os.path.dirname(__file__),"logo_final.jpg")
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
        self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
        self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
        self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
        self.set_font("Helvetica", "", 10) 
        self.website_url = "https://cminfotech.com/"
        self.po_number = po_number
        self.po_date = po_date
    
    def header(self):
        if self.page_no() == 1:
            # Logo (if available)
            if self.logo_path and os.path.exists(self.logo_path):
                self.image(self.logo_path, x=162.5, y=2.5, w=45,link=self.website_url)
                # self.image(self.logo_path, x=150, y=10, w=40)
            # Title
            self.set_font("calibri", "B", 15)
            self.cell(0, 15, "PURCHASE ORDER", ln=True, align="C")
            self.ln(2)

            # PO info
            self.set_font("calibri", "", 12)
            self.cell(95, 8, f"PO No: {self.sanitize_text(self.po_number)}", ln=0)
            self.cell(95, 8, f"Date: {self.sanitize_text(self.po_date)}", ln=1)
            self.ln(2)

    def footer(self):
        self.set_y(-18)
        self.set_font("calibri", "I", 10)
        self.multi_cell(0, 4, "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n", align="C")
        self.set_text_color(0, 0, 255)
        email1 = "cad@cmi.com"
        email2 = "info@cminfotech.com "
        self.cell(0, 4, f"{email1} | {email2}", ln=True, align="C", link=f"mailto:{email1}")
        self.set_x((self.w - 80) / 2)
        self.cell(0, 0, "", link=f"mailto:{email2}")
        self.set_x((self.w - 60) / 2)
        phone_number ="+91 873 391 5721"
        self.set_text_color(0, 0, 255)
        self.cell(60, 4, f"Call: {phone_number}", ln=True, align="C", link=f"tel:{phone_number}")
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.set_font("calibri", "B", 12)
        self.cell(0, 6, self.sanitize_text(title), ln=True)
        self.ln(1)

    def sanitize_text(self, text):
        # Fix for fpdf compatibility
            return text.encode('latin-1', 'ignore').decode('latin-1')
        
def create_po_pdf(po_data, logo_path = "logo_final.jpg"):
    # Pass dynamic data to PDF constructor
    pdf = PO_PDF(po_number=po_data['po_number'], po_date=po_data['po_date'])
    pdf.logo_path = logo_path
    pdf.add_page()
    
    # Sanitize all input strings
    sanitized_vendor_name = pdf.sanitize_text(po_data['vendor_name'])
    sanitized_vendor_address = pdf.sanitize_text(po_data['vendor_address'])
    sanitized_vendor_contact = pdf.sanitize_text(po_data['vendor_contact'])
    sanitized_vendor_mobile = pdf.sanitize_text(po_data['vendor_mobile'])
    sanitized_gst_no = pdf.sanitize_text(po_data['gst_no'])
    sanitized_pan_no = pdf.sanitize_text(po_data['pan_no'])
    sanitized_msme_no = pdf.sanitize_text(po_data['msme_no'])
    sanitized_bill_to_company = pdf.sanitize_text(po_data['bill_to_company'])
    sanitized_bill_to_address = pdf.sanitize_text(po_data['bill_to_address'])
    sanitized_ship_to_company = pdf.sanitize_text(po_data['ship_to_company'])
    sanitized_ship_to_address = pdf.sanitize_text(po_data['ship_to_address'])
    sanitized_end_company = pdf.sanitize_text(po_data['end_company'])
    sanitized_end_address = pdf.sanitize_text(po_data['end_address'])
    sanitized_end_person = pdf.sanitize_text(po_data['end_person'])
    sanitized_end_contact = pdf.sanitize_text(po_data['end_contact'])
    sanitized_end_email = pdf.sanitize_text(po_data['end_email'])
    sanitized_payment_terms = pdf.sanitize_text(po_data['payment_terms'])
    sanitized_delivery_terms = pdf.sanitize_text(po_data['delivery_terms'])
    sanitized_prepared_by = pdf.sanitize_text(po_data['prepared_by'])
    sanitized_authorized_by = pdf.sanitize_text(po_data['authorized_by'])
    sanitized_company_name = pdf.sanitize_text(po_data['company_name'])
    
    # --- Vendor & Bill/Ship ---
    pdf.section_title("Vendor & Addresses")
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(95, 5, f"{sanitized_vendor_name}\n{sanitized_vendor_address}\nAttn: {sanitized_vendor_contact}\nMobile: {sanitized_vendor_mobile}")
    pdf.set_xy(110, pdf.get_y() - 20)
    pdf.multi_cell(90, 5, f"Bill: {sanitized_bill_to_company}\n{sanitized_bill_to_address}\nShip: {sanitized_ship_to_company}\n{sanitized_ship_to_address}")
    pdf.ln(1)
    pdf.multi_cell(0, 5, f"GST: {sanitized_gst_no}\nPAN: {sanitized_pan_no}\nMSME: {sanitized_msme_no}")
    pdf.ln(2)

    # --- Products Table ---
    pdf.section_title("Products & Services")
    col_widths = [65, 22, 25, 25, 15, 22]
    headers = ["Product", "Basic", "GST TAX @ 18%", "Per Unit Price", "Qty", "Total"]
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Calibri", "B", 10)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 6, pdf.sanitize_text(h), border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    line_height = 5
    for p in po_data["products"]:
        gst_amt = p["basic"] * p["gst_percent"] / 100
        per_unit_price = p["basic"] + gst_amt
        total = per_unit_price * p["qty"]
        name = pdf.sanitize_text(p["name"])

        num_lines = pdf.multi_cell(col_widths[0], line_height, name, border=0, split_only=True)
        max_lines = max(len(num_lines), 1)
        row_height = line_height * max_lines

        x_start = pdf.get_x()
        y_start = pdf.get_y()

        pdf.multi_cell(col_widths[0], line_height, name, border=1)
        pdf.set_xy(x_start + col_widths[0], y_start)
        pdf.cell(col_widths[1], row_height, f"{p['basic']:.2f}", border=1, align="R")
        pdf.cell(col_widths[2], row_height, f"{gst_amt:.2f}", border=1, align="R")
        pdf.cell(col_widths[3], row_height, f"{per_unit_price:.2f}", border=1, align="R")
        pdf.cell(col_widths[4], row_height, f"{p['qty']:.2f}", border=1, align="C")
        pdf.cell(col_widths[5], row_height, f"{total:.2f}", border=1, align="R")
        pdf.ln(row_height)

    # Grand Total Row
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(sum(col_widths[:-1]), 6, "Grand Total", border=1, align="R")
    pdf.cell(col_widths[5], 6, f"{po_data['grand_total']:.2f}", border=1, align="R")
    pdf.ln(4)

    # --- Amount in Words ---
    pdf.ln(5)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(0, 5, "Amount in Words:", ln=True)
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(0, 5, pdf.sanitize_text(po_data['amount_words']))
    pdf.ln(4)

    # # --- Terms ---
    pdf.section_title("Terms & Conditions")
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(0, 4, f"Taxes: As specified above\nPayment: {sanitized_payment_terms}\nDelivery: {sanitized_delivery_terms}")
    pdf.ln(2)

    # --- End User ---
    pdf.section_title("End User Details")
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(0, 4, f"{sanitized_end_company}\n{sanitized_end_address}\nContact: {sanitized_end_person} | {sanitized_end_contact}\nEmail: {sanitized_end_email}")
    pdf.ln(2)

    # Authorization Section
    pdf.set_font("Calibri", "", 10)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 5, f"Prepared By: {sanitized_prepared_by}", ln=1, border=0)

    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 5, f"Authorized By: {sanitized_authorized_by}", ln=1, border=0)

    # --- Footer (Company Name + Stamp) that floats) ---
    pdf.ln(5)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 5, f"For, {sanitized_company_name}", ln=True, border=0, align="L")
    stamp_path = os.path.join(os.path.dirname(__file__), "stamp.jpg")
    if os.path.exists(stamp_path):
        pdf.ln(2)
        pdf.image(stamp_path, x=pdf.get_x(), y=pdf.get_y(), w=30)
        pdf.ln(15)

    pdf_bytes = pdf.output(dest="S").encode('latin-1')
    return pdf_bytes

# --- New PDF Class for Quotation ---
class QUOTATION_PDF(FPDF):
    def __init__(self, quotation_number="Q-N/A", quotation_date="Date N/A"):
        super().__init__()
        self.set_auto_page_break(auto=False, margin=0)
        self.set_left_margin(15)
        self.set_right_margin(15)
        self.set_font("Helvetica", "", 10) 
        self.website_url = "https://cminfotech.com/"
        self.quotation_number = quotation_number
        self.quotation_date = quotation_date
    
    def header(self):
        if self.page_no() == 1:
            # Title changed to QUOTATION
            self.set_font("Helvetica", "B", 15)
            self.cell(0, 15, "PROPOSAL / QUOTATION", ln=True, align="C")
            self.ln(2)

            # Quotation info
            self.set_font("Helvetica", "", 12)
            self.cell(95, 8, f"Quotation No: {self.sanitize_text(self.quotation_number)}", ln=0)
            self.cell(95, 8, f"Date: {self.sanitize_text(self.quotation_date)}", ln=1)
            self.ln(2)
            
    # Reusing common methods from PO_PDF
    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", "I", 10)
        self.multi_cell(0, 4, "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n", align="C")
        self.set_text_color(0, 0, 255)
        email1 = "cad@cmi.com"
        email2 = "info@cminfotech.com "
        self.cell(0, 4, f"{email1} | {email2}", ln=True, align="C", link=f"mailto:{email1}")
        self.set_x((self.w - 80) / 2)
        self.cell(0, 0, "", link=f"mailto:{email2}")
        self.set_x((self.w - 60) / 2)
        phone_number ="+91 873 391 5721"
        self.set_text_color(0, 0, 255)
        self.cell(60, 4, f"Call: {phone_number}", ln=True, align="C", link=f"tel:{phone_number}")
        self.set_text_color(0, 0, 0)
        
    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 6, self.sanitize_text(title), ln=True)
        self.ln(1)

    def sanitize_text(self, text):
        try:
            return text.encode('latin-1', 'ignore').decode('latin-1')
        except:
            return text

# Define the new Quotation generation function (identical body to create_po_pdf)
def create_quotation_pdf(quotation_data, logo_path = "logo_final.jpg"):
    pdf = QUOTATION_PDF(quotation_number=quotation_data['quotation_number'], quotation_date=quotation_data['quotation_date'])
    pdf.logo_path = logo_path
    pdf.add_page()
    
    # Sanitize all input strings
    data = quotation_data 

    # --- Vendor & Bill/Ship ---
    pdf.section_title("Vendor & Addresses")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(95, 5, f"{pdf.sanitize_text(data['vendor_name'])}\n{pdf.sanitize_text(data['vendor_address'])}\nAttn: {pdf.sanitize_text(data['vendor_contact'])}\nMobile: {pdf.sanitize_text(data['vendor_mobile'])}")
    pdf.set_xy(110, pdf.get_y() - 20)
    pdf.multi_cell(90, 5, f"Bill: {pdf.sanitize_text(data['bill_to_company'])}\n{pdf.sanitize_text(data['bill_to_address'])}\nShip: {pdf.sanitize_text(data['ship_to_company'])}\n{pdf.sanitize_text(data['ship_to_address'])}")
    pdf.ln(1)
    pdf.multi_cell(0, 5, f"GST: {pdf.sanitize_text(data['gst_no'])}\nPAN: {pdf.sanitize_text(data['pan_no'])}\nMSME: {pdf.sanitize_text(data['msme_no'])}")
    pdf.ln(2)

    # --- Products Table ---
    pdf.section_title("Products & Services")
    col_widths = [65, 22, 25, 25, 15, 22]
    headers = ["Product", "Basic", "GST TAX @ 18%", "Per Unit Price", "Qty", "Total"]
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 10)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 6, pdf.sanitize_text(h), border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    line_height = 5
    for p in data["products"]:
        gst_amt = p["basic"] * p["gst_percent"] / 100
        per_unit_price = p["basic"] + gst_amt
        total = per_unit_price * p["qty"]
        name = pdf.sanitize_text(p["name"])

        num_lines = pdf.multi_cell(col_widths[0], line_height, name, border=0, split_only=True)
        max_lines = max(len(num_lines), 1)
        row_height = line_height * max_lines

        x_start = pdf.get_x()
        y_start = pdf.get_y()

        pdf.multi_cell(col_widths[0], line_height, name, border=1)
        pdf.set_xy(x_start + col_widths[0], y_start)
        pdf.cell(col_widths[1], row_height, f"{p['basic']:.2f}", border=1, align="R")
        pdf.cell(col_widths[2], row_height, f"{gst_amt:.2f}", border=1, align="R")
        pdf.cell(col_widths[3], row_height, f"{per_unit_price:.2f}", border=1, align="R")
        pdf.cell(col_widths[4], row_height, f"{p['qty']:.2f}", border=1, align="C")
        pdf.cell(col_widths[5], row_height, f"{total:.2f}", border=1, align="R")
        pdf.ln(row_height)

    # Grand Total Row
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(sum(col_widths[:-1]), 6, "Grand Total", border=1, align="R")
    pdf.cell(col_widths[5], 6, f"{data['grand_total']:.2f}", border=1, align="R")
    pdf.ln(4)

    # --- Amount in Words ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, "Amount in Words:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, pdf.sanitize_text(data['amount_words']))
    pdf.ln(4)

    # # --- Terms ---
    pdf.section_title("Terms & Conditions")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 4, f"Taxes: As specified above\nPayment: {pdf.sanitize_text(data['payment_terms'])}\nDelivery: {pdf.sanitize_text(data['delivery_terms'])}")
    pdf.ln(2)

    # --- End User ---
    pdf.section_title("End User Details")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 4, f"{pdf.sanitize_text(data['end_company'])}\n{pdf.sanitize_text(data['end_address'])}\nContact: {pdf.sanitize_text(data['end_person'])} | {pdf.sanitize_text(data['end_contact'])}\nEmail: {pdf.sanitize_text(data['end_email'])}")
    pdf.ln(2)

    # Authorization Section
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 5, f"Prepared By: {pdf.sanitize_text(data['prepared_by'])}", ln=1, border=0)

    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 5, f"Authorized By: {pdf.sanitize_text(data['authorized_by'])}", ln=1, border=0)

    # --- Footer (Company Name + Stamp) that floats) ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"For, {pdf.sanitize_text(data['company_name'])}", ln=True, border=0, align="L")
    
    pdf_bytes = pdf.output(dest="S")
    return pdf_bytes

def main():
    st.set_page_config(page_title="Invoice & PO Generator", page_icon="📑", layout="wide")
    st.title("📑 Invoice, PO, & Quotation Generator")

    # --- Initialize Session State ---
    if "po_seq" not in st.session_state:
        st.session_state.po_seq = 1
    if "quotation_seq" not in st.session_state:
        st.session_state.quotation_seq = 1
    if "products" not in st.session_state:
        st.session_state.products = []
    if "quotation_products" not in st.session_state:
        st.session_state.quotation_products = []
    if "company_name" not in st.session_state:
        st.session_state.company_name = "CM Infotech"

    today = datetime.date.today()
    st.session_state.po_date = today.strftime("%d-%m-%Y")
    st.session_state.quotation_date = today.strftime("%d-%m-%Y")
    
    # Generate default numbers
    default_po_number = f"C/CP/{today.year}/Q{(today.month-1)//3+1}/{st.session_state.po_seq:03d}"
    default_quotation_number = f"Q/CP/{today.year}/Q{(today.month-1)//3+1}/{st.session_state.quotation_seq:03d}"

    st.sidebar.header("Global Settings")
    
    st.sidebar.subheader("PO Control")
    st.session_state.po_number = st.sidebar.text_input("Current PO Number", value=default_po_number)
    po_auto_increment = st.sidebar.checkbox("Auto-increment PO", value=True, key="po_inc")

    st.sidebar.subheader("Quotation Control")
    st.session_state.quotation_number = st.sidebar.text_input("Current Quotation No", value=default_quotation_number)
    quotation_auto_increment = st.sidebar.checkbox("Auto-increment Quotation", value=True, key="quotation_inc")
    
    if st.sidebar.button("Reset PO/Quotation Sequences"):
        st.session_state.po_seq = 1
        st.session_state.quotation_seq = 1
        st.sidebar.success("Sequences reset to 1")


    tab1, tab2, tab3 = st.tabs(["Tax Invoice Generator", "Purchase Order Generator", "Quotation Generator"])

    # --- Tab 1: Tax Invoice Generator ---
    with tab1:
        st.header("Tax Invoice Generator")
        # ... (rest of the Tax Invoice UI logic) ...
        col1, col2 = st.columns([1,1])
        with col1:
            st.subheader("Invoice Details")
            invoice_no = st.text_input("Invoice No", "CMI/25-26/Q1/010", key="inv_no")
            invoice_date = st.text_input("Invoice Date", "28 April 2025", key="inv_date")
            buyers_order_no = st.text_input("Buyer's Order No.", "Online", key="inv_buyer_po")
            buyers_order_date = st.text_input("Buyer's Order Date", "17 April 2025", key="inv_buyer_date")
            dispatched_through = st.text_input("Dispatched Through", "Online", key="inv_dispatch")
            terms_of_delivery = st.text_input("Terms of delivery", "Within Month", key="inv_terms")
            destination = st.text_input("Destination", "Vadodara", key="inv_dest")
            
            st.subheader("Vendor Details")
            vendor_name = st.text_input("Vendor Name", "CM Infotech", key="inv_vendor_name")
            vendor_address = st.text_area("Vendor Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur, Chenpur Road, Jagatpur Village, Ahmedabad - 382481", key="inv_vendor_address")
            vendor_gst = st.text_input("Vendor GST No.", "24ANMPP4", key="inv_vendor_gst")
            vendor_msme = st.text_input("Vendor MSME Registration No.", "UDYAM-", key="inv_vendor_msme")

            st.subheader("Buyer Details")
            buyer_name = st.text_input("Buyer Name", "Baldridge Pvt Ltd.", key="inv_buyer_name")
            buyer_address = st.text_area("Buyer Address", "406, Sakar East, 40mt Tarsali - Danteshwar Ring Road, Vadodara 390009", key="inv_buyer_address")
            buyer_gst = st.text_input("Buyer GST No.", "24AAHCB9", key="inv_buyer_gst")
            
            st.subheader("Products")
            items = []
            num_items = st.number_input("Number of Products", 1, 10, 1, key="inv_num_items")
            for i in range(num_items):
                with st.expander(f"Product {i+1}", expanded=i==0):
                    desc = st.text_area(f"Description {i+1}", "Autodesk BIM Collaborate Pro - Single-user\nCLOUD Commercial New Annual Subscription\nSerial #575-26831580\nContract #110004988191\nEnd Date: 17/04/2026", key=f"inv_desc_{i}")
                    hsn = st.text_input(f"HSN/SAC {i+1}", "997331", key=f"inv_hsn_{i}")
                    qty = st.number_input(f"Quantity {i+1}", 1.00, 100.00, 1.00, key=f"inv_qty_{i}")
                    rate = st.number_input(f"Unit Rate {i+1}", 0.00, 100000.00, 36500.00, key=f"inv_rate_{i}")
                    items.append({"description": desc, "hsn": hsn, "quantity": qty, "unit_rate": rate})

            st.subheader("Bank Details")
            bank_name = st.text_input("Bank Name", "XYZ bank", key="inv_bank_name")
            bank_branch = st.text_input("Branch", "AHMED", key="inv_bank_branch")
            account_no = st.text_input("Account No.", "881304", key="inv_bank_acc")
            ifsc = st.text_input("IFS Code", "IDFB004", key="inv_bank_ifsc")

            st.subheader("Declaration")
            declaration = st.text_area("Declaration", "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN\nDEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF\nNOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED\nFROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE", key="inv_declaration")
            
            st.subheader("Company Logo & Stamp")
            logo_file = st.file_uploader("Upload your company logo (PNG, JPG)", type=["png", "jpg", "jpeg"], key="invoice_logo")
            stamp_file = st.file_uploader("Upload your company stamp (PNG, JPG)", type=["png", "jpg", "jpeg"], key="invoice_stamp")

        with col2:
            st.subheader("Invoice Preview & Download")
            if st.button("Generate Invoice"):
                basic_amount = sum(item['quantity'] * item['unit_rate'] for item in items)
                sgst = basic_amount * 0.09
                cgst = basic_amount * 0.09
                final_amount = basic_amount + sgst + cgst
                
                amount_in_words = num2words(final_amount, to="cardinal").title() + " Only/-"
                tax_in_words = num2words(sgst + cgst, to="cardinal").title() + " Only/-"
                
                invoice_data = {
                    "invoice": {"invoice_no": invoice_no, "date": invoice_date},
                    "vendor": {"name": vendor_name, "address": vendor_address, "gst": vendor_gst, "msme": vendor_msme},
                    "buyer": {"name": buyer_name, "address": buyer_address, "gst": buyer_gst},
                    "invoice_details": {
                        "buyers_order_no": buyers_order_no,
                        "buyers_order_date": buyers_order_date,
                        "dispatched_through": dispatched_through,
                        "terms_of_delivery": terms_of_delivery,
                        "destination": destination
                    },
                    "items": items,
                    "totals": {
                        "basic_amount": basic_amount,
                        "sgst": sgst,
                        "cgst": cgst,
                        "final_amount": final_amount,
                        "amount_in_words": amount_in_words,
                        "tax_in_words": tax_in_words
                    },
                    "bank": {"name": bank_name, "branch": bank_branch, "account_no": account_no, "ifsc": ifsc},
                    "declaration": declaration
                }

                pdf_bytes = create_invoice_pdf(invoice_data, logo_file, stamp_file)

                st.download_button(
                    "⬇ Download Invoice PDF",
                    data=pdf_bytes,
                    file_name=f"Invoice_{invoice_no.replace('/', '_')}.pdf",
                    mime="application/pdf"
                )

    # --- Tab 2: Purchase Order Generator ---
    with tab2:
        st.header("Purchase Order Generator")
        
        tab_vendor, tab_products, tab_terms, tab_preview = st.tabs(["Vendor Details", "Products", "Terms", "Preview & Generate"])
        
        # NOTE: The Excel upload logic is currently commented out in the user's main, so we use default values
        with tab_vendor:
            col1, col2 = st.columns(2)
            with col1:
                vendor_name = st.text_input("Vendor Name", "Arkance IN Pvt. Ltd.", key="po_vendor_name")
                vendor_address = st.text_area("Vendor Address", "Unit 801-802, 8th Floor, Tower 1...", key="po_vendor_address")
                vendor_contact = st.text_input("Contact Person", "Ms/Mr", key="po_vendor_contact")
                vendor_mobile = st.text_input("Mobile", "+91 1234567890", key="po_vendor_mobile")
                gst_no = st.text_input("GST No", "24ANMPP4891R1ZX", key="po_gst_no")
                pan_no = st.text_input("PAN No", "ANMPP4891R", key="po_pan_no")
                msme_no = st.text_input("MSME No", "UDYAM-GJ-01-0117646", key="po_msme_no")
            with col2:
                bill_to_company = st.text_input("Bill To", "CM INFOTECH", key="po_bill_to_company")
                bill_to_address = st.text_area("Bill To Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481", key="po_bill_to_address")
                ship_to_company = st.text_input("Ship To", "CM INFOTECH", key="po_ship_to_company")
                ship_to_address = st.text_area("Ship To Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481", key="po_ship_to_address")
                end_company = st.text_input("End User Company", "Baldridge & Associates Pvt Ltd.", key="po_end_company")
                end_address = st.text_area("End User Address", "406 Sakar East, Vadodara 390009", key="po_end_address")
                end_person = st.text_input("End User Contact", "Mr. Dev", key="po_end_person")
                end_contact = st.text_input("End User Phone", "+91 9876543210", key="po_end_contact")
                end_email = st.text_input("End User Email", "info@company.com", key="po_end_email")

        with tab_products:
            st.header("Products for PO")
            selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="po_catalog_select")
            if st.button("➕ Add Selected Product", key="add_selected_po"):
                if selected_product:
                    details = PRODUCT_CATALOG[selected_product]
                    st.session_state.products.append({
                        "name": selected_product,
                        "basic": details["basic"],
                        "gst_percent": details["gst_percent"],
                        "qty": 1.0,
                    })
                    st.success(f"{selected_product} added!")

            if st.button("➕ Add Empty Product", key="add_empty_po"):
                st.session_state.products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

            for i, p in enumerate(st.session_state.products):
                with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
                    st.session_state.products[i]["name"] = st.text_input("Name", p["name"], key=f"po_name_{i}")
                    st.session_state.products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"po_basic_{i}")
                    st.session_state.products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"po_gst_{i}")
                    st.session_state.products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"po_qty_{i}")
                    if st.button("Remove", key=f"po_remove_{i}"):
                        st.session_state.products.pop(i)
                        st.rerun()

        with tab_terms:
            st.header("Terms & Authorization")
            col1, col2 = st.columns(2)
            with col1:
                payment_terms = st.text_input("Payment Terms", "30 Days from Invoice date", key="po_payment_terms")
                delivery_days = st.number_input("Delivery (Days)", min_value=1, value=2, key="po_delivery_days")
                delivery_terms = st.text_input("Delivery Terms", f"Within {delivery_days} Days", key="po_delivery_terms")
            with col2:
                prepared_by = st.text_input("Prepared By", "Finance Department", key="po_prepared_by")
                authorized_by = st.text_input("Authorized By", "CM INFOTECH", key="po_authorized_by")
        
        with tab_preview:
            st.header("Preview & Generate PO")
            total_base = sum(p["basic"] * p["qty"] for p in st.session_state.products)
            total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.products)
            grand_total = total_base + total_gst
            amount_words = num2words(grand_total, to='currency', currency='INR').replace("INR", "Rs.").title()
            
            st.metric("Grand Total", f"₹{grand_total:,.2f}")
            
            logo_file_po = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"], key="po_logo")
            logo_path = None
            if logo_file_po:
                # Mock saving the file to a temp path for FPDF.image access
                logo_path = "po_logo_temp.png"
                try:
                    with open(logo_path, "wb") as f:
                        f.write(logo_file_po.getbuffer())
                except Exception as e:
                    st.error(f"Error saving logo file: {e}")
                    logo_path = None


            if st.button("Generate Purchase Order", type="primary"):
                po_data = {
                    "po_number": st.session_state.po_number,
                    "po_date": st.session_state.po_date,
                    "vendor_name": vendor_name,
                    "vendor_address": vendor_address,
                    "vendor_contact": vendor_contact,
                    "vendor_mobile": vendor_mobile,
                    "gst_no": gst_no,
                    "pan_no": pan_no,
                    "msme_no": msme_no,
                    "bill_to_company": bill_to_company,
                    "bill_to_address": bill_to_address,
                    "ship_to_company": ship_to_company,
                    "ship_to_address": ship_to_address,
                    "end_company": end_company,
                    "end_address": end_address,
                    "end_person": end_person,
                    "end_contact": end_contact,
                    "end_email": end_email,
                    "products": st.session_state.products,
                    "grand_total": grand_total,
                    "amount_words": amount_words,
                    "payment_terms": payment_terms,
                    "delivery_terms": delivery_terms,
                    "prepared_by": prepared_by,
                    "authorized_by": authorized_by,
                    "company_name": st.session_state.company_name
                }
                pdf_bytes = create_po_pdf(po_data, logo_path)

                if po_auto_increment:
                    st.session_state.po_seq += 1

                st.success("Purchase Order generated!")
                st.download_button(
                    "⬇ Download Purchase Order",
                    pdf_bytes,
                    f"PO_{st.session_state.po_number.replace('/', '_')}.pdf",
                    "application/pdf"
                )
            
            if logo_path and os.path.exists(logo_path):
                try:
                    os.remove(logo_path)
                except Exception:
                    pass

    # --- Tab 3: Quotation Generator (New Implementation) ---
    with tab3:
        st.header("Quotation Generator")
        
        tab_vendor_q, tab_products_q, tab_terms_q, tab_preview_q = st.tabs(["Recipient Details", "Products", "Terms", "Preview & Generate"])

        with tab_vendor_q:
            st.info("The Recipient is the potential Buyer (like 'Vendor' in the PO format).")
            col1, col2 = st.columns(2)
            with col1:
                vendor_name_q = st.text_input("Recipient Name", "Creation Studio", key="q_vendor_name")
                vendor_address_q = st.text_area("Recipient Address", "Al-Habtula Apartment, Swk Society, Sid, Dah, Guja 389", key="q_vendor_address")
                vendor_contact_q = st.text_input("Contact Person (Kind Attention)", "Mr. Musta", key="q_vendor_contact")
                vendor_mobile_q = st.text_input("Mobile", "+91 9988776655", key="q_vendor_mobile")
                gst_no_q = st.text_input("Recipient GST No (Optional)", "24AAHCB9", key="q_gst_no")
                pan_no_q = st.text_input("Recipient PAN No (Optional)", "AXXXXX9999X", key="q_pan_no")
                msme_no_q = st.text_input("Recipient MSME No (Optional)", "N/A", key="q_msme_no")
            with col2:
                # CM Infotech details as the 'Seller/Quoter' (acting as Bill/Ship to in this format)
                bill_to_company_q = st.text_input("Quoter (Bill To)", "CM INFOTECH", key="q_bill_to_company")
                bill_to_address_q = st.text_area("Quoter Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Ahmedabad - 382481", key="q_bill_to_address")
                
                ship_to_company_q = st.text_input("Delivery To (Ship To)", "Creation Studio", key="q_ship_to_company")
                ship_to_address_q = st.text_area("Delivery Address", "Al-Habtula Apartment, Swk Society, Sid, Dah, Guja 389", key="q_ship_to_address")
                
                end_company_q = st.text_input("End User Company (Final Destination)", "Creation Studio", key="q_end_company")
                end_address_q = st.text_area("End User Address", "Al-Habtula Apartment, Swk Society, Sid, Dah, Guja 389", key="q_end_address")
                end_person_q = st.text_input("End User Contact", "Mr. Musta", key="q_end_person")
                end_contact_q = st.text_input("End User Phone", "+91 9988776655", key="q_end_contact")
                end_email_q = st.text_input("End User Email", "info@dreamcreationstudio.com", key="q_end_email")

        with tab_products_q:
            st.header("Products for Quotation")
            selected_product_q = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="q_catalog_select")
            if st.button("➕ Add Selected Product", key="add_selected_q"):
                if selected_product_q:
                    details = PRODUCT_CATALOG[selected_product_q]
                    st.session_state.quotation_products.append({
                        "name": selected_product_q,
                        "basic": details["basic"],
                        "gst_percent": details["gst_percent"],
                        "qty": 1.0,
                    })
                    st.success(f"{selected_product_q} added!")

            if st.button("➕ Add Empty Product", key="add_empty_q"):
                st.session_state.quotation_products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

            for i, p in enumerate(st.session_state.quotation_products):
                with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
                    st.session_state.quotation_products[i]["name"] = st.text_input("Name", p["name"], key=f"q_name_{i}")
                    st.session_state.quotation_products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"q_basic_{i}")
                    st.session_state.quotation_products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"q_gst_{i}")
                    st.session_state.quotation_products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"q_qty_{i}")
                    if st.button("Remove", key=f"q_remove_{i}"):
                        st.session_state.quotation_products.pop(i)
                        st.rerun()

        with tab_terms_q:
            st.header("Terms & Authorization")
            col1, col2 = st.columns(2)
            with col1:
                payment_terms_q = st.text_input("Payment Terms", "100% Advance along with purchase order.", key="q_payment_terms")
                delivery_days_q = st.number_input("Delivery (Days)", min_value=1, value=14, key="q_delivery_days")
                delivery_terms_q = st.text_input("Delivery Terms", f"1-2 Weeks from the date of Purchase Order", key="q_delivery_terms")
            with col2:
                prepared_by_q = st.text_input("Prepared By", "Sales Department", key="q_prepared_by")
                authorized_by_q = st.text_input("Authorized By", "CM INFOTECH", key="q_authorized_by")
        
        with tab_preview_q:
            st.header("Preview & Generate Quotation")
            total_base_q = sum(p["basic"] * p["qty"] for p in st.session_state.quotation_products)
            total_gst_q = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.quotation_products)
            grand_total_q = total_base_q + total_gst_q
            amount_words_q = num2words(grand_total_q, to='currency', currency='INR').replace("INR", "Rs.").title()
            
            st.metric("Grand Total", f"₹{grand_total_q:,.2f}")
            
            logo_file_q = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"], key="q_logo")
            logo_path_q = None
            if logo_file_q:
                logo_path_q = "quotation_logo_temp.png"
                try:
                    with open(logo_path_q, "wb") as f:
                        f.write(logo_file_q.getbuffer())
                except Exception as e:
                    st.error(f"Error saving logo file: {e}")
                    logo_path_q = None

            if st.button("Generate Quotation", type="primary", key="generate_quotation_button"):
                quotation_data = {
                    "quotation_number": st.session_state.quotation_number,
                    "quotation_date": st.session_state.quotation_date,
                    "vendor_name": vendor_name_q, # Recipient
                    "vendor_address": vendor_address_q,
                    "vendor_contact": vendor_contact_q,
                    "vendor_mobile": vendor_mobile_q,
                    "gst_no": gst_no_q,
                    "pan_no": pan_no_q,
                    "msme_no": msme_no_q,
                    "bill_to_company": bill_to_company_q,
                    "bill_to_address": bill_to_address_q,
                    "ship_to_company": ship_to_company_q,
                    "ship_to_address": ship_to_address_q,
                    "end_company": end_company_q,
                    "end_address": end_address_q,
                    "end_person": end_person_q,
                    "end_contact": end_contact_q,
                    "end_email": end_email_q,
                    "products": st.session_state.quotation_products,
                    "grand_total": grand_total_q,
                    "amount_words": amount_words_q,
                    "payment_terms": payment_terms_q,
                    "delivery_terms": delivery_terms_q,
                    "prepared_by": prepared_by_q,
                    "authorized_by": authorized_by_q,
                    "company_name": st.session_state.company_name
                }
                pdf_bytes_q = create_quotation_pdf(quotation_data, logo_path_q)

                if quotation_auto_increment:
                    st.session_state.quotation_seq += 1

                st.success("Quotation generated!")
                st.download_button(
                    "⬇ Download Quotation",
                    pdf_bytes_q,
                    f"Quotation_{st.session_state.quotation_number.replace('/', '_')}.pdf",
                    "application/pdf"
                )
            
            if logo_path_q and os.path.exists(logo_path_q):
                try:
                    os.remove(logo_path_q)
                except Exception:
                    pass

    st.divider()
    st.caption("© 2025 Invoice & PO Generator")

if __name__ == "__main__":
    main()


