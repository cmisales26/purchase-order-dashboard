import streamlit as st
from fpdf import FPDF
import pandas as pd
from num2words import num2words
import datetime
import io
from PIL import Image
import os
import textwrap

# --- Global Data and Configuration ---
PRODUCT_CATALOG = {
    "Creative cloud pro plus for Teams": {"basic": 114560.0, "gst_percent": 18.0},
    "Creative cloud Pro for Teams": {"basic": 104560.0, "gst_percent": 18.0},
    "Adobe Creative Cloud All Apps": {"basic": 95000.0, "gst_percent": 18.0},
    "Adobe Acrobat Pro DC": {"basic": 25000.0, "gst_percent": 18.0},
    "Adobe Substance 3D Collection": {"basic": 85000.0, "gst_percent": 18.0},
    "Autodesk Commercial Software License": {"basic": 27500.0, "gst_percent": 18.0},
    "Solidworks Premium": {"basic": 50000.0, "gst_percent": 18.0},
    "Catia License": {"basic": 75000.0, "gst_percent": 18.0},
    "Mastercam Module": {"basic": 30000.0, "gst_percent": 18.0},
    "Siemens NX": {"basic": 65000.0, "gst_percent": 18.0},
}

# Sales Person Mapping - ONLY ONE DEFINITION
SALES_PERSON_MAPPING = {
    "SD": {"name": "Sakshi Darji", "email": "sakshi@cminfotech.com", "mobile": "+91 74051 15721"},
    "CP": {"name": "Chirag Prajapati", "email": "chirag@cminfotech.com", "mobile": "+91 87339 15721"},
    "HP": {"name": "Hiral Patel", "email": "hiral@cminfotech.com", "mobile": "+91 95581 15721"},
    "KP": {"name": "Khushi Patel", "email": "khushi@cminfotech.com", "mobile": "+91 97241 15721"}
}

# --- Helper Functions for Quotation and PO ---
def get_current_quarter():
    """Get current quarter (Q1, Q2, Q3, Q4) based on current month"""
    month = datetime.datetime.now().month
    if month in [4, 5, 6]:
        return "Q1"
    elif month in [7, 8, 9]:
        return "Q2"
    elif month in [10, 11, 12]:
        return "Q3"
    else:
        return "Q4"

def parse_po_number(po_number):
    """Parse PO number to extract components"""
    try:
        parts = po_number.split('/')
        if len(parts) >= 4:
            prefix = parts[0]  # C
            sales_person = parts[1]  # CP, SD, HP, KP
            year = parts[2]  # 2025
            quarter_sequence = parts[3]  # Q4_001
            quarter = quarter_sequence.split('_')[0]  # Q4
            sequence = quarter_sequence.split('_')[1] if '_' in quarter_sequence else "001"  # 001, 002, etc.
            return prefix, sales_person, year, quarter, sequence
    except:
        pass
    return "CMI", "CP", str(datetime.datetime.now().year), get_current_quarter(), "001"

def generate_po_number(sales_person, sequence_number):
    """Generate PO number with current quarter and sequence"""
    current_date = datetime.datetime.now()
    quarter = get_current_quarter()
    year = str(current_date.year)
    sequence = f"{sequence_number:03d}"
    
    return f"CMI/{sales_person}/{year}/{quarter}_{sequence}"

def get_next_sequence_number_po(po_number):
    """Extract and increment sequence number from PO number"""
    try:
        parts = po_number.split('_')
        if len(parts) > 1:
            sequence = parts[-1]
            return int(sequence) + 1
    except:
        pass
    return 1

def parse_quotation_number(quotation_number):
    """Parse quotation number to extract components"""
    try:
        parts = quotation_number.split('/')
        if len(parts) >= 5:
            prefix = parts[0]  # CMI
            sales_person = parts[1]  # SD, CP, HP, KP
            quarter = parts[2]  # Q1, Q2, Q3, Q4
            date_part = parts[3]  # DD-MM-YYYY
            year_range = parts[4].split('_')[0]  # 2025-2026
            sequence = parts[4].split('_')[1] if '_' in parts[4] else "001"  # 001, 002, etc.
            return prefix, sales_person, quarter, date_part, year_range, sequence
    except:
        pass
    return "CMI", sales_person(), get_current_quarter(), datetime.datetime.now().strftime("%d-%m-%Y"), f"{datetime.datetime.now().year}-{datetime.datetime.now().year+1}", "001"

def generate_quotation_number(sales_person, sequence_number):
    """Generate quotation number with current quarter and sequence"""
    current_date = datetime.datetime.now()
    quarter = get_current_quarter()
    year_range = f"{current_date.year}-{current_date.year+1}"
    sequence = f"{sequence_number:03d}"
    
    return f"CMI/{sales_person}/{quarter}/{current_date.strftime('%d-%m-%Y')}/{year_range}_{sequence}"

def get_next_sequence_number(quotation_number):
    """Extract and increment sequence number from quotation number"""
    try:
        parts = quotation_number.split('_')
        if len(parts) > 1:
            sequence = parts[-1]
            return int(sequence) + 1
    except:
        pass
    return 1

# --- PDF Class for Two-Page Quotation (Matching Demo Format) ---
class QUOTATION_PDF(FPDF):
    def __init__(self, quotation_number="Q-N/A", quotation_date="Date N/A", sales_person_code="CP"):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_left_margin(15)
        self.set_right_margin(15)
        self.quotation_number = quotation_number
        self.quotation_date = quotation_date
        self.sales_person_code = sales_person_code
        
    def sanitize_text(self, text):
        try:
            return text.encode('latin-1', 'ignore').decode('latin-1')
        except:
            return text

    def header(self):
        # Logo placement (top right) - FIXED
        if hasattr(self, 'logo_path') and self.logo_path and os.path.exists(self.logo_path):
            try:
                self.image(self.logo_path, x=155, y=8, w=50)
            except:
                # If image fails, show placeholder
                self.set_font("Helvetica", "B", 10)
                self.set_xy(150, 8)
                self.cell(40, 5, "[LOGO]", border=0, align="C")
            
        # Main Title (Centered)
        self.set_font("Helvetica", "B", 16)
        self.set_y(15)
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
        # Make footer emails and phone clickable - FIXED OVERLAP
        self.set_text_color(0, 0, 255)  # Blue color for links
        
        # Website link
        # self.cell(0, 4, "www.cminfotech.com", ln=True, align="C", link="https://www.cminfotech.com/")
        
        # Email and phone on same line - FIXED
        email_text = " info@cminfotech.com "
        phone_text = " +91 873 391 5721"
        
        # Calculate positions for proper alignment
        page_width = self.w - 2 * self.l_margin
        email_width = self.get_string_width(email_text)
        phone_width = self.get_string_width(phone_text)
        separator_width = self.get_string_width(" | ")
        
        total_width = email_width + separator_width + phone_width
        start_x = (page_width - total_width) / 2 + self.l_margin
        
        self.set_x(start_x)
        self.cell(email_width, 4, email_text, ln=0, link=f"mailto:{email_text}")
        self.cell(separator_width, 4, " | ", ln=0)
        self.cell(phone_width, 4, phone_text, ln=True, link=f"tel:{phone_text.replace(' ', '').replace('+', '')}")

        self.cell(0, 4, "www.cminfotech.com", ln=True, align="C", link="https://www.cminfotech.com/")
        
        self.set_text_color(0, 0, 0)  # Reset to black
        self.set_y(-8)
        self.set_font("Helvetica", "I", 7)
        self.cell(0, 4, f"Page {self.page_no()}", 0, 0, 'C')

# --- Page Content Generation Helpers ---

def add_clickable_email(pdf, email, label="Email: "):
    """Add clickable email with label - FIXED OVERLAP"""
    pdf.set_font("Helvetica", "B", 10)
    label_width = pdf.get_string_width(label)
    pdf.cell(label_width, 4, label, ln=0)
    
    pdf.set_text_color(0, 0, 255)  # Blue for clickable
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 4, email, ln=True, link=f"mailto:{email}")
    pdf.set_text_color(0, 0, 0)  # Reset to black

def add_clickable_phone(pdf, phone, label="Mobile: "):
    """Add clickable phone number with label - FIXED OVERLAP"""
    pdf.set_font("Helvetica", "B", 10)
    label_width = pdf.get_string_width(label)
    pdf.cell(label_width, 4, label, ln=0)
    
    pdf.set_text_color(0, 0, 255)  # Blue for clickable
    pdf.set_font("Helvetica", "", 10)
    # Remove spaces and + for tel link
    tel_number = phone.replace(' ', '').replace('+', '')
    pdf.cell(0, 4, phone, ln=True, link=f"tel:{tel_number}")
    pdf.set_text_color(0, 0, 0)  # Reset to black

def add_page_one_intro(pdf, data):
    # Reference Number & Date (Top Right) - FIXED ALIGNMENT
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_y(25)
    pdf.cell(0, 5, f"REF NO.: {data['quotation_number']}", ln=True, align="L")
    pdf.cell(0, 5, f"Date: {data['quotation_date']}", ln=True, align="L")
    pdf.ln(10)

    # Recipient Details (Left Aligned) - FIXED ALIGNMENT
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "To,", ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 6, pdf.sanitize_text(data['vendor_name']), ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    # Address handling
    pdf.multi_cell(0, 4, pdf.sanitize_text(data['vendor_address']))
    
    pdf.ln(3)
    
    # Clickable Email - FIXED
    if data.get('vendor_email'):
        add_clickable_email(pdf, data['vendor_email'])
    
    # Clickable Mobile - FIXED
    if data.get('vendor_mobile'):
        add_clickable_phone(pdf, data['vendor_mobile'])
    
    pdf.set_font("Helvetica", "BU", 10)
    pdf.cell(0, 5, f"Kind Attention :- {pdf.sanitize_text(data['vendor_contact'])}",align="C", ln=True)
    pdf.ln(8)

    # Subject Line (from user input)
    pdf.set_font("Helvetica", "BU", 12)
    pdf.cell(0, 6, f"Subject :- {pdf.sanitize_text(data['subject'])}", ln=True)
    pdf.ln(5)

    # Introductory Paragraph (from user input)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, pdf.sanitize_text(data['intro_paragraph']))
    pdf.ln(5)

    # Contact Information - FIXED ALIGNMENT with clickable elements - FIXED OVERLAP
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    # Normal text
    pdf.write(5, "Please revert back to us, if you need any clarification / information "
                "at the below mentioned address or email at ")

    # Email clickable
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Helvetica", "U", 10)  # underline
    pdf.write(5, "chirag@cminfotech.com", link="mailto:chirag@cminfotech.com")

    # Back to normal for separator + Mobile:
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.write(5, "  Mobile: ")

    # First mobile
    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Helvetica", "U", 10)
    pdf.write(5, "+91 740 511 5721 ", link="tel:+91 740 511 5721")

    # Separator + second mobile
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.write(5, ", ")

    pdf.set_text_color(0, 0, 255)
    pdf.set_font("Helvetica", "U", 10)
    pdf.write(5, "+91 873 391 5721", link="tel:+91 873 391 5721")

    # Reset back to normal for anything after
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(10)  # move cursor down for next section
    
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 4, "For more information, please visit our web site & Social Media :-", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    # Clickable website
    pdf.set_font("Helvetica", "U", 10)
    pdf.set_text_color(0, 0, 255)
    pdf.cell(0, 4, "https://www.cminfotech.com/", ln=True, link="https://www.cminfotech.com/")
    pdf.cell(0, 4, "https://www.linkedin.com/", ln=True, link="https://www.linkedin.com/")
    pdf.cell(0, 4, "https://wa.me/message/8733915721", ln=True, link="https://wa.me/message/8733915721")
    pdf.cell(0, 4, "https://www.facebook.com/", ln=True, link="https://www.facebook.com/")
    pdf.cell(0, 4, "https://www.instagram.com/", ln=True, link="https://www.instagram.com/")
    pdf.set_text_color(0, 0, 0)
    
def add_quotation_header(pdf, annexure_text, quotation_text):
    """Add dynamic quotation header with both annexure and title"""
    pdf.set_font("Helvetica", "BU", 14)
    pdf.cell(0, 8, annexure_text, ln=True, align="C")
    pdf.set_font("Helvetica", "BU", 12)
    pdf.cell(0, 6, quotation_text, ln=True, align="C")
    pdf.ln(8)

def add_page_two_commercials(pdf, data):
    pdf.add_page()
    
    # Use dynamic header function
    annexure_text = data.get('annexure_text', 'Annexure I - Commercials')
    quotation_title = data.get('quotation_title', 'Quotation for Adobe Software')
    
    add_quotation_header(pdf, annexure_text, quotation_title)

    # pdf.set_font("Helvetica", "B", 14)
    # pdf.cell(0, 8, "Annexure I - Commercials", ln=True, align="C")
    # pdf.set_font("Helvetica", "B", 12)
    # pdf.cell(0, 6, quotation_title, ln=True, align="C")
    # pdf.ln(8)
    # pdf.set_font("Helvetica", "B", 14)
    # pdf.cell(0, 8, "Annexure I - Commercials", ln=True, align="C")
    # pdf.set_font("Helvetica", "B", 12)
    # pdf.cell(0, 6, "Quotation for Adobe Software", ln=True, align="C")
    # pdf.ln(8)

    # --- Products Table - FIXED COLUMN WIDTHS ---
    col_widths = [70, 25, 25, 25, 15, 25]  # Adjusted for better fit
    headers = ["Description", "Basic Price", "GST Tax @ 18%", "Per Unit Price", "Qty.", "Total"]
    
    # Table Header
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 9)
    for width, header in zip(col_widths, headers):
        pdf.cell(width, 7, header, border=1, align="C", fill=True)
    pdf.ln()

    # Table Rows
    pdf.set_font("Helvetica", "", 9)
    grand_total = 0.0
    
    for product in data["products"]:
        basic_price = product["basic"]
        qty = product["qty"]
        gst_amount = basic_price * 0.18
        per_unit_price = basic_price + gst_amount
        total = per_unit_price * qty
        grand_total += total
        
        # Description (wrap long text)
        desc = product["name"]
        if len(desc) > 35:
            desc = desc[:32] + "..."
        
        pdf.cell(col_widths[0], 6, pdf.sanitize_text(desc), border=1)
        pdf.cell(col_widths[1], 6, f"{basic_price:,.2f}", border=1, align="R")
        pdf.cell(col_widths[2], 6, f"{gst_amount:,.2f}", border=1, align="R")
        pdf.cell(col_widths[3], 6, f"{per_unit_price:,.2f}", border=1, align="R")
        pdf.cell(col_widths[4], 6, f"{qty:.0f}", border=1, align="C")
        pdf.cell(col_widths[5], 6, f"{total:,.2f}", border=1, align="R")
        pdf.ln()

    # Grand Total Row - FIXED ALIGNMENT
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(sum(col_widths[:-1]), 7, "Grand Total", border=1, align="R")
    pdf.cell(col_widths[5], 7, f"{grand_total:,.2f}", border=1, align="R")
    pdf.ln(15)

    pdf.set_font("Helvetica", "B", 9)

    # Terms & Conditions with partial bold formatting
    terms_y = pdf.get_y()

    # Regular terms (1-6)
    terms = [
        "Above charges are Inclusive of GST.",
        "Any changes in Govt. duties, Taxes & Forex rate at the time of dispatch shall be applicable.",
        "TDS should not be deducted at the time of payment as per Govt. NOTIFICATION NO. 21/2012 [F.No.142/10/2012-SO (TPL)] S.O. 1323(E), DATED 13-6-2012.",
        "ELD licenses are paper licenses that do not contain media.",
        "An Internet connection is required to access cloud services.",
        "Training will be charged at extra cost depending on no. of participants.",
    ]

    for i, term in enumerate(terms):
        pdf.set_xy(x_start + padding, terms_y)
        pdf.multi_cell(col1_width - 2*padding, line_height, f"{i+1}. {term}")
        terms_y = pdf.get_y()

    # Special terms with partial bold (7-11)
    pdf.set_xy(x_start + padding, terms_y)
    pdf.multi_cell(col1_width - 2*padding, line_height, "7. Price Validity: ")
    pdf.set_x(x_start + padding + pdf.get_string_width("7. Price Validity: "))
    pdf.set_font("Helvetica", "B", 9)
    pdf.multi_cell(col1_width - 2*padding - pdf.get_string_width("7. Price Validity: "), line_height, "10 days from Quotation date")
    terms_y = pdf.get_y()

    pdf.set_xy(x_start + padding, terms_y)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(col1_width - 2*padding, line_height, "8. Payment: ")
    pdf.set_x(x_start + padding + pdf.get_string_width("8. Payment: "))
    pdf.set_font("Helvetica", "B", 9)
    pdf.multi_cell(col1_width - 2*padding - pdf.get_string_width("8. Payment: "), line_height, "100% Advance along with purchase order")
    terms_y = pdf.get_y()

    pdf.set_xy(x_start + padding, terms_y)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(col1_width - 2*padding, line_height, "9. Delivery period: ")
    pdf.set_x(x_start + padding + pdf.get_string_width("9. Delivery period: "))
    pdf.set_font("Helvetica", "B", 9)
    pdf.multi_cell(col1_width - 2*padding - pdf.get_string_width("9. Delivery period: "), line_height, "License will be delivered electronically within 2-3 working days after payment confirmation. Includes 12 months of technical support and software updates from OEM.")
    terms_y = pdf.get_y()

    pdf.set_xy(x_start + padding, terms_y)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(col1_width - 2*padding, line_height, "10. Dispatched Through: ")
    pdf.set_x(x_start + padding + pdf.get_string_width("10. Dispatched Through: "))
    pdf.set_font("Helvetica", "B", 9)
    pdf.multi_cell(col1_width - 2*padding - pdf.get_string_width("10. Dispatched Through: "), line_height, "Online")
    terms_y = pdf.get_y()

    pdf.set_xy(x_start + padding, terms_y)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(col1_width - 2*padding, line_height, '11. Cheque to be issued on name of: ')
    pdf.set_x(x_start + padding + pdf.get_string_width('11. Cheque to be issued on name of: '))
    pdf.set_font("Helvetica", "B", 9)
    pdf.multi_cell(col1_width - 2*padding - pdf.get_string_width('11. Cheque to be issued on name of: '), line_height, '"CM INFOTECH"')
    terms_y = pdf.get_y()

    # Bank Details (UPDATED TO MATCH SECOND VERSION)
    bank_info = [
        ("Name", "CM INFOTECH"),
        ("Account Number", "88130420182"),
        ("IFSC Code", "IDFB0040335"),
        ("SWIFT Code","IDFBINBBMUM"),
        ("Bank Name", "IDFC FIRST"),
        ("Branch", "AHMEDABAD - SHYAMAL BRANCH"),
        ("MSME", "UDYAM-GJ-01-0117646"),
        ("GSTIN", "24ANMPP4891R1ZX"),
        ("PAN No", "ANMPP4891R")
    ]

    # Box dimensions and styling
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    page_width = pdf.w - 1.6 * pdf.l_margin
    col1_width = page_width * 0.6  # 60% for Terms
    col2_width = page_width * 0.4  # 40% for Bank Details
    padding = 4
    line_height = 4.5
    section_spacing = 2

    # Calculate required height for both columns
    def calculate_column_height(items, col_width):
        height = 0
        for item in items:
            lines = pdf.multi_cell(col_width - 2*padding, line_height, item, split_only=True)
            height += len(lines) * line_height + section_spacing
        return height + 3*padding  # Add padding

    terms_height = calculate_column_height(terms, col1_width)
    
    # Calculate bank details height including signature section
    bank_items_height = calculate_column_height([f"{label}: {value}" for label, value in bank_info], col2_width)
    signature_height = 35  # Estimated height for signature section
    bank_height = bank_items_height + signature_height + padding
    
    # Use the maximum height
    box_height = max(terms_height, bank_height) + padding

    # Draw the main box
    pdf.rect(x_start, y_start, page_width, box_height)
    
    # Draw vertical separator line
    pdf.line(x_start + col1_width, y_start, x_start + col1_width, y_start + box_height)

    # Add section headers
    pdf.set_font("Helvetica", "B", 10)
    
    # Terms & Conditions header
    pdf.set_xy(x_start + padding, y_start + padding)
    pdf.cell(col1_width - 2*padding, 5, "Terms & Conditions:", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    
    # Terms content
    terms_y = pdf.get_y()
    for i, term in enumerate(terms):
        pdf.set_xy(x_start + padding, terms_y)
        pdf.multi_cell(col1_width - 2*padding, line_height, f"{i+1}. {term}")
        terms_y = pdf.get_y()

    # Bank Details header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(x_start + col1_width + padding, y_start + padding)
    pdf.cell(col2_width - 2*padding, 5, "Bank Details:", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    
    # Bank details content
    bank_y = pdf.get_y()
    for label, value in bank_info:
        pdf.set_xy(x_start + col1_width + padding, bank_y)
        pdf.multi_cell(col2_width - 2*padding, line_height, f"{label}: {value}")
        bank_y = pdf.get_y()
    
    # --- Signature Block INSIDE BANK DETAILS BOX ---
    signature_start_y = bank_y + 5
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(x_start + col1_width + padding, signature_start_y)
    pdf.cell(col2_width - 2*padding, 5, "Yours Truly,", ln=True)
    
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    pdf.cell(col2_width - 2*padding, 5, "For CM INFOTECH", ln=True)
    
        # --- Signature Block INSIDE BANK DETAILS BOX ---
    signature_start_y = bank_y + 5
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_xy(x_start + col1_width + padding, signature_start_y)
    pdf.cell(col2_width - 2*padding, 5, "Yours Truly,", ln=True)
    
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    pdf.cell(col2_width - 2*padding, 5, "For CM INFOTECH", ln=True)
    
    # --- Signature Block with Dynamic Sales Person ---
    sales_person_code = data.get('sales_person_code', 'SD')
    sales_person_info = SALES_PERSON_MAPPING.get(sales_person_code, SALES_PERSON_MAPPING['SD'])
    
    # Add stamp between "For CM INFOTECH" and sales person name
    if data.get('stamp_path') and os.path.exists(data['stamp_path']):
        try:
            # Position stamp centered between "For CM INFOTECH" and sales person name
            stamp_y = pdf.get_y() + 2  # Small space after "For CM INFOTECH"
            stamp_x = x_start + col1_width + padding# + (col2_width - 2*padding - 20) / 2  # Center the stamp
            pdf.image(data['stamp_path'], x=stamp_x, y=stamp_y, w=20)
            # Move cursor down after stamp
            pdf.set_y(stamp_y + 25)  # Space for stamp + some padding
        except:
            pdf.set_y(pdf.get_y() + 8)  # If stamp fails, add some space
    else:
        pdf.set_y(pdf.get_y() + 8)  # Space if no stamp
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    pdf.cell(col2_width - 2*padding, 4, sales_person_info["name"], ln=True)
    
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    pdf.cell(col2_width - 2*padding, 4, "Inside Sales Executive", ln=True)
    
    # Clickable email in signature
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    label = "Email: "
    pdf.cell(pdf.get_string_width(label), 4, label, ln=0)
    pdf.set_text_color(0, 0, 255)
    pdf.cell(col2_width - 2*padding - pdf.get_string_width(label), 4, sales_person_info["email"], 
             ln=True, link=f"mailto:{sales_person_info['email']}")
    
    # Clickable phone in signature
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    label = "Mobile: "
    pdf.cell(pdf.get_string_width(label), 4, label, ln=0)
    pdf.set_text_color(0, 0, 255)
    pdf.cell(col2_width - 2*padding - pdf.get_string_width(label), 4, sales_person_info["mobile"], 
             ln=True, link=f"tel:{sales_person_info['mobile'].replace(' ', '').replace('+', '')}")
    pdf.set_text_color(0, 0, 0)         

    # Move cursor below the box
    pdf.set_xy(x_start, y_start + box_height + 10)

def create_quotation_pdf(quotation_data, logo_path=None, stamp_path=None):
    """Orchestrates the creation of the two-page PDF."""
    sales_person_code = quotation_data.get('sales_person_code', 'SD')
    pdf = QUOTATION_PDF(quotation_number=quotation_data['quotation_number'], 
                        quotation_date=quotation_data['quotation_date'],
                        sales_person_code=sales_person_code)
    
    # Set logo path for header
    if logo_path and os.path.exists(logo_path):
        pdf.logo_path = logo_path
    
    quotation_data['stamp_path'] = stamp_path

    pdf.add_page()
    
    # 1. Add Page 1 (Introduction Letter)
    add_page_one_intro(pdf, quotation_data)

    # 2. Add Page 2 (Commercials, Terms, Bank Details)
    add_page_two_commercials(pdf, quotation_data)
    
    # Handle PDF output properly
    try:
        pdf_output = pdf.output(dest='S')
        
        if isinstance(pdf_output, str):
            return pdf_output.encode('latin-1')
        elif isinstance(pdf_output, bytearray):
            return bytes(pdf_output)
        elif isinstance(pdf_output, bytes):
            return pdf_output
        else:
            return str(pdf_output).encode('latin-1')
            
    except Exception:
        # Fallback method
        try:
            buffer = io.BytesIO()
            pdf.output(dest=buffer)
            return buffer.getvalue()
        except Exception as e:
            st.error(f"PDF generation failed: {e}")
            return b""

from fpdf import FPDF

# --- PDF Class for Tax Invoice ---
from fpdf import FPDF

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


# --- Function to Create Invoice PDF ---
def create_invoice_pdf(invoice_data, logo_file="logo_final.jpg", stamp_file="stamp.jpg"):
    pdf = PDF()
    pdf.set_auto_page_break(auto=False, margin=10)
    pdf.add_page()

        # --- Logo on top right ---
    if logo_file:
        try:
            pdf.image(logo_file, x=170, y=2.5, w=35)
        except Exception as e:
            st.warning(f"Could not add logo: {e}")

    # === HEADER (Vendor + Invoice Details) ===
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 8, "CM Infotech.", border=1, ln=0)
    pdf.cell(47, 8, "Invoice No.", border=1, ln=0, align="C")
    pdf.cell(47, 8, "Invoice Date", border=1, ln=1, align="C")

    y_left_start = pdf.get_y()

    # --- Left Side (Vendor Details) ---
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(95, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur,\nChenpur Road, Jagatpur Village, Ahmedabad - 382481", border="LB")
    
    # Vendor details lines
    vendor_lines = [
        ("GST No.:", invoice_data['vendor']['gst']),
        ("MSME Registration No.:", invoice_data['vendor']['msme']),
        ("E-Mail:", "cm.infotech2014@gmail.com"),
        ("Mobile No.:", "8733915721"),
    ]
    
    for i, (label, value) in enumerate(vendor_lines):
        pdf.set_x(15)
        pdf.set_font("Helvetica", "B", 8)
        label_width = pdf.get_string_width(label)
        pdf.cell(label_width, 6, label, border="LB", ln=0)
        pdf.set_font("Helvetica", "", 8)
        border = "RB" if i < len(vendor_lines) - 1 else "RB"
        pdf.cell(95 - label_width, 6, value, border=border, ln=1)

    y_left_end = pdf.get_y()

    # --- Right Side (Invoice Details) ---
    pdf.set_xy(110, y_left_start)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(47, 8, invoice_data['invoice']['invoice_no'], border="LR", ln=0, align="C")
    pdf.cell(47, 8, invoice_data['invoice']['date'], border="R", ln=1, align="C")

    # Payment terms
    pdf.set_x(110)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(47, 8, "Mode/Terms of Payment:", border="LRT", ln=0)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(47, 8, "100% Advance with Purchase", border="RT", ln=1)

    # Supplier's reference
    pdf.set_x(110)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(47, 8, "Supplier's Reference:", border="LRT", ln=0)
    pdf.set_font("Helvetica", "", 8)
    other_ref_value = invoice_data['Reference']['Suppliers_Reference']
    pdf.cell(47, 8, other_ref_value, border="RTB", ln=1)

    # Other's reference
    pdf.set_x(110)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(47, 8, "Other's Reference:", border="LRTB", ln=0)
    pdf.set_font("Helvetica", "", 8)
    other_ref_value = invoice_data['Reference']['Other']
    pdf.cell(47, 8, other_ref_value, border="LRTB", ln=1)

    # # Empty closing row
    # pdf.set_x(110)
    # pdf.cell(94, 6, "", border="LRB", ln=1)

    pdf.ln(6)

    # === BUYER SECTION ===
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 8, "Buyer", border=1, ln=0)
    pdf.cell(47, 8, "Buyer's Order No.", border=1, ln=0, align="C")
    pdf.cell(47, 8, "Buyer's Order Date", border=1, ln=1, align="C")

    y_buyer_start = pdf.get_y()

    # --- Buyer Left Details ---
    # Store starting position for left buyer block
    y_left_buyer_start = pdf.get_y()
    
    # Buyer name and address
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(95, 5, invoice_data['buyer']['name'], border="LR", ln=1)
    
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(95, 4, invoice_data['buyer']['address'], border="LRB")
    
    # Buyer contact details
    buyer_lines = [
        ("Email:", "dmistry@baseengr.com"),
        ("Tel No.:", "98987 91813"),
        ("GST No.:", invoice_data['buyer']['gst']),
    ]
    
    for i, (label, value) in enumerate(buyer_lines):
        pdf.set_x(15)
        pdf.set_font("Helvetica", "B", 8)
        label_width = pdf.get_string_width(label)
        pdf.cell(label_width, 6, label, border="LBT", ln=0)
        pdf.set_font("Helvetica", "", 8)
        border = "RB" if i < len(buyer_lines) - 1 else "RB"
        pdf.cell(95 - label_width, 6, value, border=border, ln=1)

    y_buyer_left_end = pdf.get_y()
    
    # Calculate total height of left buyer block
    total_left_buyer_height = y_buyer_left_end - y_left_buyer_start

    # --- Buyer Right Details ---
    pdf.set_xy(110, y_buyer_start)
    
    # Row 1: Buyer's Order No/Date - FIXED POSITION (doesn't stretch with address)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(47, 4, invoice_data['invoice_details']['buyers_order_no'], border="RB", ln=0, align="C")
    pdf.cell(47, 4, invoice_data['invoice_details']['buyers_order_date'], border="RB", ln=1, align="C")

    # Calculate remaining height needed for address space
    name_height = 5  # Height of buyer name
    contact_lines_height = 18  # Height of 3 contact lines (6mm each)
    remaining_height_for_address = total_left_buyer_height - name_height - contact_lines_height
    
    # Add empty space for address if needed
    if remaining_height_for_address > 0:
        pdf.set_x(110)
        pdf.cell(94, remaining_height_for_address, "", border="R", ln=1)

    # Row 2: Dispatched Through
    pdf.set_x(110)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(47, 6, "Dispatched Through", border="LRT", ln=0)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(47, 6, invoice_data['invoice_details']['dispatched_through'], border="RT", ln=1)

    # Row 3: Destination
    pdf.set_x(110)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(47, 6, "Destination", border="LRT", ln=0)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(47, 6, invoice_data['invoice_details']['destination'], border="RT", ln=1)

    # Row 4: Terms of delivery
    pdf.set_x(110)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(47, 6, "Terms of delivery", border="LRT", ln=0)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(47, 6, invoice_data['invoice_details']['terms_of_delivery'], border="RT", ln=1)

    # Closing row
    pdf.set_x(110)
    pdf.cell(94, 1, "", border="LRB", ln=1)

    # --- Item Table Header ---
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(10, 5, "Sr. No.", border=1, align="C")
    pdf.cell(80, 5, "Description of Goods", border=1, align="C")
    pdf.cell(20, 5, "HSN/SAC", border=1, align="C")
    pdf.cell(20, 5, "Quantity", border=1, align="C")
    pdf.cell(25, 5, "Unit Rate", border=1, align="C")
    pdf.cell(34, 5, "Amount", border=1, ln=True, align="C")

    # --- Items ---
    pdf.set_font("Helvetica", "", 8)
    col_widths = [10, 80, 20, 20, 25, 34]
    line_height = 4

    for i, item in enumerate(invoice_data["items"], start=1):
        x_start = pdf.get_x()
        y_start = pdf.get_y()

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
    pdf.cell(sum(col_widths[:5]), 5, "Basic Amount", border=1, align="L")
    pdf.cell(34, 5, f"{invoice_data['totals']['basic_amount']:.2f}", border=1, ln=True, align="R")
    
    pdf.cell(sum(col_widths[:5]), 5, "SGST @ 9%", border=1, align="L")
    pdf.cell(34, 5, f"{invoice_data['totals']['sgst']:.2f}", border=1, ln=True, align="R")
    
    pdf.cell(sum(col_widths[:5]), 5, "CGST @ 9%", border=1, align="L")
    pdf.cell(34, 5, f"{invoice_data['totals']['cgst']:.2f}", border=1, ln=True, align="R")

    pdf.cell(sum(col_widths[:5]), 5, "Final Amount to be Paid", border=1, align="L")
    pdf.cell(34, 5, f"{invoice_data['totals']['final_amount']:.2f}", border=1, ln=True, align="R")
    
    # --- Amount in Words ---
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(189, 5, f"Amount Chargeable (in words): {invoice_data['totals']['amount_in_words']}", ln=True, border=1)

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
    pdf.cell(190, 5, f"Tax Amount (in words): {invoice_data['totals']['tax_in_words']}", ln=True, border=1)

    # --- Reserve footer space ---
    needed_space = 70
    if pdf.get_y() + needed_space > pdf.h - pdf.b_margin:
        pdf.set_y(pdf.h - pdf.b_margin - needed_space)

    # --- Bank Details ---
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "Company's Bank Details", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(0, 4,
            f"Bank Nmae : IDFC FIRST\n"
            "Branch        : AHMEDABAD Shyamal Branch\n"
            "Account No : 88130420182\n"
            "IFS Code    : IDFB0040335")
    #     f"Bank Name: {invoice_data['bank']['name']}\n"
    #     f"Branch: {invoice_data['bank']['branch']}\n"
    #     f"Account No.: {invoice_data['bank']['account_no']}\n"
    #     f"IFS Code: {invoice_data['bank']['ifsc']}"
    # )

    # --- Declaration ---
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "Declaration:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(0, 4, invoice_data['declaration'])
    
    # --- Signature ---
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, "For CM Infotech.", ln=True, align="R")

    if stamp_file:
        try:
            stamp_width = 25
            stamp_x = pdf.w - pdf.r_margin - stamp_width
            stamp_y = pdf.get_y()
            pdf.image(stamp_file, x=stamp_x, y=stamp_y, w=stamp_width)
            pdf.ln(25)
        except Exception as e:
            st.warning(f"Could not add stamp: {e}")
    else:
        pdf.ln(15)
        
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Authorized Signatory", ln=True, align="R")
    
    # --- Footer with clickable email and mobile ---
    pdf.set_y(-24)
    pdf.set_font("Helvetica", "U", 8)
    pdf.cell(0, 4, "This is a Computer Generated Invoice", ln=True, align="C")
    
    # Company address
    pdf.set_y(-18)
    pdf.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
    
    # Clickable email and mobile
    pdf.set_text_color(0, 0, 255)
    email1 = "info@cminfotech.com "
    phone_number = " +91 873 391 5721"
    pdf.cell(0, 4, f"{email1} | {phone_number}", ln=True, align="C", link=f"mailto:{email1}")
    pdf.cell(0, 4, "www.cminfotech.com", ln=True, align="C", link="https://www.cminfotech.com/")
    pdf.set_x((pdf.w - 80) / 2)
    pdf.cell(0, 0, "", link=f"tel:{phone_number}")
    pdf.set_text_color(0, 0, 0)

    pdf_bytes = pdf.output(dest="S").encode('latin-1') if isinstance(pdf.output(dest="S"), str) else pdf.output(dest="S")
    return pdf_bytes









# --- PDF Class ---
class PO_PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False, margin=10)
        self.set_left_margin(15)
        self.set_right_margin(15)
        self.logo_path = os.path.join(os.path.dirname(__file__),"logo_final.jpg")
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        # Comment out font loading to avoid errors if fonts don't exist
        # self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
        # self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
        # self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
        # self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
        self.website_url = "https://cminfotech.com/"
    def header(self):
        if self.page_no() == 1:
            # Logo (if available)
            if self.logo_path and os.path.exists(self.logo_path):
                self.image(self.logo_path, x=162.5, y=2.5, w=45,link=self.website_url)
                # self.image(self.logo_path, x=150, y=10, w=40)

            
            # Title
            self.set_font("Helvetica", "B", 15)
            self.cell(0, 15, "PURCHASE ORDER", ln=True, align="C")
            self.ln(1)

            # PO info
            self.set_font("Helvetica", "", 12)
            # PO Number (right aligned)
            self.set_xy(140,25)
            self.multi_cell(60,4,
                            f"PO No: {self.sanitize_text(st.session_state.po_number)}\n"
                            f"Date: {self.sanitize_text(st.session_state.po_date)}")
            # self.cell(0, 8, f"PO No: {self.sanitize_text(st.session_state.po_number)}", ln=1, align='R')
            # # Date (right aligned, under PO Number)
            # self.cell(0, 8, f"Date: {self.sanitize_text(st.session_state.po_date)}", ln=0, align='R')
            # self.ln(4)

    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", "U", 10)
        self.multi_cell(0, 4, "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n", align="C")
        self.set_text_color(0, 0, 255)
        # email1 = "cad@cmi.com"
        email1 = "info@cminfotech.com "
        phone_number =" +91 873 391 5721"
        self.set_text_color(0, 0, 255)
        self.cell(0, 4, f"{email1} | {phone_number}", ln=True, align="C", link=f"mailto:{email1}")
        self.set_x((self.w - 80) / 2)
        self.cell(0, 0, "", link=f"tel:{phone_number}")
        self.set_x((self.w - 60) / 2)
        website ="www.cminfotech.com"
        self.set_text_color(0, 0, 255)
        self.cell(60, 4, f"{website}", ln=True, align="C", link=website)
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 6, self.sanitize_text(title), ln=True)
        self.ln(1)

    def sanitize_text(self, text):
        return text.encode('ascii', 'ignore').decode('ascii')

def create_po_pdf(po_data, logo_path = "logo_final.jpg"):
    pdf = PO_PDF()
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
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(95, 5, f"{sanitized_vendor_name}\n{sanitized_vendor_address}\nKind Attend: {sanitized_vendor_contact}\nMobile: {sanitized_vendor_mobile}")
    pdf.ln(7)
    # pdf.set_xy(110, pdf.get_y() - 20)
    pdf.multi_cell(95, 5, f"Bill To: \n{sanitized_bill_to_company}\n{sanitized_bill_to_address}")
    pdf.set_xy(120, pdf.get_y() - 20)
    pdf.multi_cell(0, 5, f"Ship To: \n{sanitized_ship_to_company}\n{sanitized_ship_to_address}")
    # pdf.ln(2)
    pdf.multi_cell(0, 5, f"GST NO: {sanitized_gst_no}\nPAN NO: {sanitized_pan_no}\nMSME Registration No: {sanitized_msme_no}")
    pdf.ln(2)

    # --- Products Table ---
    pdf.section_title("Products & Services")
    col_widths = [65, 22, 30, 25, 15, 22]
    headers = ["Product", "Basic", "GST TAX @ 18%", "Per Unit Price", "Qty", "Total"]
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 10)
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
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(sum(col_widths[:-1]), 6, "Grand Total", border=1, align="R")
    pdf.cell(col_widths[5], 6, f"{po_data['grand_total']:.2f}", border=1, align="R")
    pdf.ln(4)

    # --- Amount in Words ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, "Amount in Words:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, pdf.sanitize_text(po_data['amount_words']))
    pdf.ln(4)

    # # --- Terms ---
    # pdf.section_title("Terms & Conditions")
    # pdf.set_font("Helvetica", "", 10)
    # pdf.multi_cell(0, 4, f"Taxes            : As specified above\nPayment                     : {sanitized_payment_terms}\nDelivery                      : {sanitized_delivery_terms}")
    # pdf.ln(2)

    # # --- End User ---
    # pdf.section_title("End User Details")
    # pdf.set_font("Helvetica", "", 10)
    # pdf.multi_cell(0, 4, f"Company Name         :{sanitized_end_company}\nCompany Address   :{sanitized_end_address}\nContact                       : {sanitized_end_person} | {sanitized_end_contact}\nEmail                           : {sanitized_end_email}")
    # pdf.ln(2)


    # --- Terms & Conditions ---
    pdf.section_title("Terms & Conditions")
    pdf.set_font("Helvetica", "", 10)

    # Taxes
    pdf.cell(45, 4, "Taxes")
    pdf.cell(5, 4, ":")
    pdf.multi_cell(0, 4, f"As specified above")

    # Payment
    pdf.cell(45, 4, "Payment")
    pdf.cell(5, 4, ":")
    pdf.multi_cell(0, 4, f"{sanitized_payment_terms}")

    # Delivery
    pdf.cell(45, 4, "Delivery")
    pdf.cell(5, 4, ":")
    pdf.multi_cell(0, 4, f"{sanitized_delivery_terms}")

    pdf.ln(2)

    # --- End User ---
    pdf.section_title("End User Details")
    pdf.set_font("Helvetica", "", 10)

    # Company Name
    pdf.cell(45, 4, "Company Name")
    pdf.cell(5, 4, ":")
    pdf.multi_cell(0, 4, f"{sanitized_end_company}")

    # Company Address
    pdf.cell(45, 4, "Company Address")
    pdf.cell(5, 4, ":")
    pdf.multi_cell(0, 4, f"{sanitized_end_address}")

    # Contact
    pdf.cell(45, 4, "Contact")
    pdf.cell(5, 4, ":")
    pdf.multi_cell(0, 4, f"{sanitized_end_person} | {sanitized_end_contact}")

    # Email
    pdf.cell(45, 4, "Email")
    pdf.cell(5, 4, ":")
    pdf.multi_cell(0, 4, f"{sanitized_end_email}")

    pdf.ln(2)
    # Authorization Section
    # pdf.set_font("Helvetica", "", 10)
    # pdf.set_x(pdf.l_margin)
    # pdf.cell(0, 5, f"Prepared By: {sanitized_prepared_by}", ln=1, border=0)

    # pdf.set_x(pdf.l_margin)
    # pdf.cell(0, 5, f"Authorized By: {sanitized_authorized_by}", ln=1, border=0)

    # --- Footer (Company Name + Stamp) that floats) ---
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"For, {sanitized_company_name}", ln=True, border=0, align="L")
    stamp_path = os.path.join(os.path.dirname(__file__), "stamp.jpg")
    if os.path.exists(stamp_path):
        pdf.ln(2)
        pdf.image(stamp_path, x=pdf.get_x(), y=pdf.get_y(), w=30)
        pdf.ln(15)

    pdf_bytes = pdf.output(dest="S").encode('latin-1')
    return pdf_bytes

# --- Utility to safely get string from session_state ---
def safe_str_state(key, default=""):
    """Ensure session_state value exists and is always a string."""
    if key not in st.session_state or not isinstance(st.session_state[key], str):
        st.session_state[key] = str(default)
    return st.session_state[key] 

# --- The main function with FIXED Quotation Tab ---
def main():
    st.set_page_config(page_title="Document Generator", page_icon="📑", layout="wide")
    st.title("📑 Document Generator - Invoice, PO & Quotation")

    # --- Initialize Session State ---
    if "quotation_seq" not in st.session_state:
        st.session_state.quotation_seq = 1
    if "quotation_products" not in st.session_state:
        st.session_state.quotation_products = []
    if "last_quotation_number" not in st.session_state:
        st.session_state.last_quotation_number = ""
    if "po_seq" not in st.session_state:
        st.session_state.po_seq = 1
    if "products" not in st.session_state:
        st.session_state.products = []
    if "company_name" not in st.session_state:
        st.session_state.company_name = "CM Infotech"
    if "po_number" not in st.session_state:
        st.session_state.po_number = generate_po_number("CP", st.session_state.po_seq)
    if "po_date" not in st.session_state:
        st.session_state.po_date = datetime.date.today().strftime("%d-%m-%Y")
    if "last_po_number" not in st.session_state:
        st.session_state.last_po_number = ""
    if "quotation_number" not in st.session_state:
        st.session_state.quotation_number = generate_quotation_number("SD", st.session_state.quotation_seq)
    if "current_quote_sales_person" not in st.session_state:
        st.session_state.current_quote_sales_person = "SD"
    if "current_po_sales_person" not in st.session_state:  # NEW
        st.session_state.current_po_sales_person = "CP"
    if "current_po_quarter" not in st.session_state:  # NEW
        st.session_state.current_po_quarter = get_current_quarter()

    # --- Upload Excel and Load Vendor/End User ---
    uploaded_excel = st.file_uploader("📂 Upload Vendor & End User Excel", type=["xlsx"])

    if uploaded_excel:
        vendors_df = pd.read_excel(uploaded_excel, sheet_name="Vendors", dtype={"Mobile": str})
        endusers_df = pd.read_excel(uploaded_excel, sheet_name="EndUsers")

        st.success("✅ Excel loaded successfully!")

        # --- Select Vendor ---
        vendor_name = st.selectbox("Select Vendor", vendors_df["Vendor Name"].unique())
        vendor = vendors_df[vendors_df["Vendor Name"] == vendor_name].iloc[0]

        # --- Select End User ---
        end_user_name = st.selectbox("Select End User", endusers_df["End User Company"].unique())
        end_user = endusers_df[endusers_df["End User Company"] == end_user_name].iloc[0]

        # --- Clean and Convert Mobile (avoid float or NaN issues) ---
        vendor_mobile = str(vendor.get("Mobile", "")).split(".")[0].strip()

        # Save to session_state (so Invoice & PO can use)
        st.session_state.po_vendor_name = vendor["Vendor Name"]
        st.session_state.po_vendor_address = vendor["Vendor Address"]
        st.session_state.po_vendor_contact = vendor["Contact Person"]
        st.session_state.po_vendor_mobile = vendor_mobile
        st.session_state.po_end_company = end_user["End User Company"]
        st.session_state.po_end_address = end_user["End User Address"]
        st.session_state.po_end_person = end_user["End User Contact"]
        st.session_state.po_end_contact = end_user["End User Phone"]
        st.session_state.po_end_email = end_user["End User Email"]
        st.session_state.po_end_gst_no = end_user["GST NO"]

        st.info("Vendor & End User details auto-filled from Excel ✅")
    

    # Create tabs for different document types
    tab1, tab2, tab3 = st.tabs(["Tax Invoice Generator", "Purchase Order Generator", "Quotation Generator"])

    # --- Tab 1: Tax Invoice Generator ---
    with tab1:
        st.header("Tax Invoice Generator")
        col1, col2 = st.columns([1,1])
        with col1:
            st.subheader("Invoice Details")
            invoice_no = st.text_input("Invoice No", "CMI/25-26/Q1/010")
            invoice_date = st.text_input("Invoice Date", "28 April 2025")
            Suppliers_Reference = st.text_input("Supplier's Reference", "NA")
            Others_Reference = st.text_input("Other's Reference", "NA")
            buyers_order_no = st.text_input("Buyer's Order No.", "Online")
            buyers_order_date = st.text_input("Buyer's Order Date", "17 April 2025")
            dispatched_through = st.text_input("Dispatched Through", "Online")
            terms_of_delivery = st.text_input("Terms of delivery", "Within Month")
            destination = st.text_input("Destination", "Vadodara")
            
            st.subheader("Seller Details")
            vendor_name = st.text_input("Seller Name", "CM Infotech")
            vendor_address = st.text_area("Seller Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur, Chenpur Road, Jagatpur Village, Ahmedabad - 382481")
            vendor_gst = st.text_input("Seller GST No.", "24ANMPP4891R1ZX")
            vendor_msme = st.text_input("Seller MSME Registration No.", "UDYAM-GJ-01-0117646")

            st.subheader("Buyer Details")
            buyer_name = st.text_input(
                "Buyer Name",
                value = st.session_state.get("po_end_company","Baldridge Pvt Ltd.")
            )
            buyer_address = st.text_area(
                "Buyer Address",
                value=st.session_state.get("po_end_address","406, Sakar East,...")
            )
            buyer_gst = st.text_input(
                "Buyer GST No.",
                value=st.session_state.get("po_end_gst_no","24AAHCB9")
            )

            
            st.subheader("Products")
            items = []
            num_items = st.number_input("Number of Products", 1, 10, 1)
            for i in range(num_items):
                with st.expander(f"Product {i+1}"):
                    desc = st.text_area(f"Description {i+1}", "Autodesk BIM Collaborate Pro - Single-user\nCLOUD Commercial New Annual Subscription\nSerial #575-26831580\nContract #110004988191\nEnd Date: 17/04/2026")
                    hsn = st.text_input(f"HSN/SAC {i+1}", "997331")
                    qty = st.number_input(f"Quantity {i+1}", 1.00, 100.00, 1.00)
                    rate = st.number_input(f"Unit Rate {i+1}", 0.00, 100000.00, 36500.00)
                    items.append({"description": desc, "hsn": hsn, "quantity": qty, "unit_rate":rate})

            # st.subheader("Bank Details")
            # bank_name = st.text_input("Bank Name", "XYZ bank")
            # bank_branch = st.text_input("Branch", "AHMED")
            # account_no = st.text_input("Account No.", "881304")
            # ifsc = st.text_input("IFS Code", "IDFB004")

            st.subheader("Declaration")
            declaration = st.text_area("Declaration", "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN\nDEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF\nNOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED\nFROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE")
            
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
                tax_in_words = num2words(sgst + cgst, to="cardinal").title()+"Only/-"

                invoice_data = {
                    "invoice": {"invoice_no": invoice_no, "date": invoice_date},
                    "Reference": {"Suppliers_Reference":Suppliers_Reference, "Other": Others_Reference},
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
                    # "bank": {"name": bank_name, "branch": bank_branch, "account_no": account_no, "ifsc": ifsc},
                    "declaration": declaration
                }

                pdf_file = create_invoice_pdf(invoice_data)

                st.download_button(
                    "⬇ Download Invoice PDF",
                    data=pdf_file,
                    file_name=f"Invoice_{invoice_no.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    key="invoice_download_button")
                
    # --- Tab 2: Purchase Order Generator ---
    with tab2:
        st.header("Purchase Order Generator")
        
        today = datetime.date.today()
        current_quarter = get_current_quarter()
        
        # PO Settings in sidebar for this tab
        st.sidebar.header("PO Settings")
        
        # Sales Person Selection for PO - JUST LIKE QUOTATION
        po_sales_person = st.sidebar.selectbox("Select Sales Person", 
                                            options=list(SALES_PERSON_MAPPING.keys()), 
                                            format_func=lambda x: f"{x} - {SALES_PERSON_MAPPING[x]['name']}",
                                            key="po_sales_person_select")
        
        # Get current sales person info
        current_sales_person_info = SALES_PERSON_MAPPING.get(po_sales_person, SALES_PERSON_MAPPING['CP'])
        
        # Generate PO number based on selected sales person - JUST LIKE QUOTATION
        def get_po_number():
            # Check if we need to increment sequence
            if st.session_state.last_po_number:
                try:
                    last_prefix, last_sales_person, last_year, last_quarter, last_sequence = parse_po_number(st.session_state.last_po_number)
                    
                    if last_sales_person == po_sales_person and last_quarter == current_quarter:
                        # Same sales person and same quarter, increment sequence
                        next_sequence = get_next_sequence_number_po(st.session_state.last_po_number)
                        return generate_po_number(po_sales_person, next_sequence)
                    else:
                        # Different sales person or new quarter, start from sequence 1
                        return generate_po_number(po_sales_person, 1)
                except:
                    # If parsing fails, use current sequence
                    return generate_po_number(po_sales_person, st.session_state.po_seq)
            else:
                # No previous PO, start from current sequence
                return generate_po_number(po_sales_person, st.session_state.po_seq)
        
        # Initialize or update PO number when sales person changes
        if "current_po_sales_person" not in st.session_state:
            st.session_state.current_po_sales_person = po_sales_person
            st.session_state.po_number = get_po_number()
        
        # Update PO number if sales person changes or quarter changes
        if (st.session_state.current_po_sales_person != po_sales_person or 
            st.session_state.get('current_po_quarter', '') != current_quarter):
            st.session_state.current_po_sales_person = po_sales_person
            st.session_state.current_po_quarter = current_quarter
            st.session_state.po_number = get_po_number()
        
        # Display current sales person info
        st.sidebar.info(f"**Current Sales Person:** {current_sales_person_info['name']}")
        st.sidebar.info(f"**Current Quarter:** {current_quarter}")
        
        # Show auto-generated breakdown
        try:
            prefix, current_sp, year, quarter, sequence = parse_po_number(st.session_state.po_number)
            st.sidebar.success(f"**Auto-generated PO Number**")
            st.sidebar.info(f"**Format:** {current_sp}/{year}/{quarter}_{sequence}")
        except:
            st.sidebar.warning("Could not parse PO number")
        
        # Editable PO number WITH sales person selection
        st.sidebar.subheader("PO Number Editor")
        
        # Parse current PO number for editing
        try:
            current_prefix, current_sp, current_year, current_q, current_seq = parse_po_number(st.session_state.po_number)
            
            # Create editable components
            col1, col2, col3, col4 = st.sidebar.columns([1, 2, 2, 1])
            
            with col1:
                # Show current sales person (read-only)
                st.text_input("Sales Person", value=current_sp, key="po_sp_display", disabled=True)
            
            with col2:
                new_year = st.text_input("Year", value=current_year, key="po_year_edit")
            
            with col3:
                new_quarter = st.text_input("Quarter", value=current_q, key="po_quarter_edit")
            
            with col4:
                new_sequence = st.number_input("Sequence", 
                                            min_value=1, 
                                            value=int(current_seq), 
                                            step=1,
                                            key="po_seq_edit")
            
            # Construct new PO number using the SELECTED sales person, not the edited one
            new_po_number = f"CMI/{po_sales_person}/{new_year}/{new_quarter}_{new_sequence:03d}"
            
            # Update if changed
            if new_po_number != st.session_state.po_number:
                st.session_state.po_number = new_po_number
                
        except Exception as e:
            st.sidebar.error(f"Error parsing PO number: {e}")
            # Fallback to default
            st.session_state.po_number = generate_po_number(po_sales_person, st.session_state.po_seq)
        
        # Display final PO number
        st.sidebar.code(st.session_state.po_number)
        
        po_auto_increment = st.sidebar.checkbox("Auto-increment Sequence", value=True, key="po_auto_increment_checkbox")
        
        # FIXED: Added unique key to the reset button
        if st.sidebar.button("Reset to Auto-generate", use_container_width=True, key="po_reset_auto_generate"):
            st.session_state.po_seq = 1
            st.session_state.last_po_number = ""
            st.session_state.po_number = get_po_number()
            st.sidebar.success("PO number reset to auto-generated")
            st.rerun()
        
        tab_vendor, tab_products, tab_terms, tab_preview = st.tabs(["Vendor Details", "Products", "Terms", "Preview & Generate"])
        
        with tab_vendor:
            col1, col2 = st.columns(2)
            with col1:
                vendor_name = st.text_input(
                    "Vendor Name",
                    value=safe_str_state("po_vendor_name", "Arkance IN Pvt. Ltd."),
                    key="po_vendor_name_input"
                )
                vendor_address = st.text_area(
                    "Vendor Address",
                    value=safe_str_state("po_vendor_address", "Unit 801-802, 8th Floor, Tower 1..."),
                    key="po_vendor_address_input"
                )
                vendor_contact = st.text_input(
                    "Contact Person",
                    value=safe_str_state("po_vendor_contact", "Ms/Mr"),
                    key="po_vendor_contact_input"
                )
                vendor_mobile = st.text_input(
                    "Mobile",
                    value=safe_str_state("po_vendor_mobile", "+91 1234567890"),
                    key="po_vendor_mobile_input"
                )
                end_company = st.text_input(
                    "End User Company",
                    value=safe_str_state("po_end_company", "Baldridge & Associates Pvt Ltd."),
                    key="po_end_company_input"
                )
                end_address = st.text_area(
                    "End User Address",
                    value=safe_str_state("po_end_address", "406 Sakar East, Vadodara 390009"),
                    key="po_end_address_input"
                )
                end_person = st.text_input(
                    "End User Contact",
                    value=safe_str_state("po_end_person", "Mr. Dev"),
                    key="po_end_person_input"
                )
                end_contact = st.text_input(
                    "End User Phone",
                    value=safe_str_state("po_end_contact", "+91 9876543210"),
                    key="po_end_contact_input"
                )
                end_email = st.text_input(
                    "End User Email",
                    value=safe_str_state("po_end_email", "info@company.com"),
                    key="po_end_email_input"
                )
            with col2:
                bill_to_company = st.text_input(
                    "Bill To",
                    value=safe_str_state("po_bill_to_company", "CM INFOTECH"),
                    key="po_bill_to_company_input"
                )
                bill_to_address = st.text_area(
                    "Bill To Address",
                    value=safe_str_state("po_bill_to_address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481"),
                    key="po_bill_to_address_input"
                )
                ship_to_company = st.text_input(
                    "Ship To",
                    value=safe_str_state("po_ship_to_company", "CM INFOTECH"),
                    key="po_ship_to_company_input"
                )
                ship_to_address = st.text_area(
                    "Ship To Address",
                    value=safe_str_state("po_ship_to_address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481"),
                    key="po_ship_to_address_input"
                )
                gst_no = st.text_input(
                    "GST No",
                    value=safe_str_state("po_gst_no", "24ANMPP4891R1ZX"),
                    key="po_gst_no_input"
                )
                pan_no = st.text_input(
                    "PAN No",
                    value=safe_str_state("po_pan_no", "ANMPP4891R"),
                    key="po_pan_no_input"
                )
                msme_no = st.text_input(
                    "MSME No",
                    value=safe_str_state("po_msme_no", "UDYAM-GJ-01-0117646"),
                    key="po_msme_no_input"
                )

        with tab_products:
            st.header("Products")
            selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="po_product_select_catalog")
            
            # FIXED: Added unique key to the add product button
            if st.button("➕ Add Selected Product", key="po_add_selected_product"):
                if selected_product:
                    details = PRODUCT_CATALOG[selected_product]
                    st.session_state.products.append({
                        "name": selected_product,
                        "basic": details["basic"],
                        "gst_percent": details["gst_percent"],
                        "qty": 1.0,
                    })
                    st.success(f"{selected_product} added!")
            
            # FIXED: Added unique key to the add empty product button
            if st.button("➕ Add Empty Product", key="po_add_empty_product"):
                st.session_state.products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

            for i, p in enumerate(st.session_state.products):
                with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
                    st.session_state.products[i]["name"] = st.text_input("Name", p["name"], key=f"po_name_{i}")
                    st.session_state.products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"po_basic_{i}")
                    st.session_state.products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"po_gst_{i}")
                    st.session_state.products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"po_qty_{i}")
                    # FIXED: Added unique key to the remove button
                    if st.button("Remove", key=f"po_remove_{i}"):
                        st.session_state.products.pop(i)
                        st.rerun()
                        
        with tab_terms:
            st.header("Terms & Authorization")
            col1, col2 = st.columns(2)
            with col1:
                payment_terms = st.text_input("Payment Terms", "30 Days from Invoice date", key="po_payment_terms_input")
                delivery_days = st.number_input("Delivery (Days)", min_value=1, value=2, key="po_delivery_days_input")
                delivery_terms = st.text_input("Delivery Terms", f"Within {delivery_days} Days", key="po_delivery_terms_input")
            with col2:
                prepared_by = st.text_input("Prepared By", "Finance Department", key="po_prepared_by_input")
                authorized_by = st.text_input("Authorized By", "CM INFOTECH", key="po_authorized_by_input")
        
        with tab_preview:
            st.header("Preview & Generate")
            
            # Show the current PO number prominently with sales person info - JUST LIKE QUOTATION
            st.info(f"**PO Number:** {st.session_state.po_number}")
            st.info(f"**Sales Person:** {current_sales_person_info['name']} ({po_sales_person}) - {current_sales_person_info['email']}")
            
            total_base = sum(p["basic"] * p["qty"] for p in st.session_state.products)
            total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.products)
            grand_total = total_base + total_gst
            amount_words = num2words(grand_total, to="currency", currency="INR").title()
            st.metric("Grand Total", f"₹{grand_total:,.2f}")

            logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"], key="po_logo_uploader")
            logo_path = None
            if logo_file:
                logo_path = "logo_final.jpg"
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
            
            # FIXED: Added unique key to the generate PO button
            if st.button("Generate PO", type="primary", key="po_generate_button"):
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
                    "end_address":end_address,
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

                # Store the last PO number for sequence tracking
                st.session_state.last_po_number = st.session_state.po_number
                
                # Auto-increment for next PO
                if po_auto_increment:
                    try:
                        next_sequence = get_next_sequence_number_po(st.session_state.po_number)
                        # Update the sequence in session state for next time
                        st.session_state.po_seq = next_sequence
                    except:
                        st.session_state.po_seq += 1

                st.success("Purchase Order generated!")
                st.info(f"📧 Sales Person: {current_sales_person_info['name']}")
                
                st.download_button(
                    "⬇ Download Purchase Order",
                    data=pdf_bytes,
                    file_name=f"PO_{st.session_state.po_number.replace('/', '_')}.pdf",
                    mime="application/pdf"
                )

    # --- Tab 3: Quotation Generator (SINGLE SALES PERSON SELECTION) ---
    with tab3:
        st.header("📑 Adobe Software Quotation Generator")
        
        today = datetime.date.today()
        current_quarter = get_current_quarter()
        
        # Sales Person Selection - ONLY ONE SELECTION
        st.sidebar.header("Quotation Settings")
        sales_person = st.sidebar.selectbox("Select Sales Person", 
                                        options=list(SALES_PERSON_MAPPING.keys()), 
                                        format_func=lambda x: f"{x} - {SALES_PERSON_MAPPING[x]['name']}",
                                        key="quote_sales_person")
        
        # Get current sales person info
        current_sales_person_info = SALES_PERSON_MAPPING.get(sales_person, SALES_PERSON_MAPPING['SD'])
        
        # Generate quotation number based on selected sales person
        def get_quotation_number():
            # Check if we need to increment sequence
            if st.session_state.last_quotation_number:
                try:
                    last_prefix, last_sales_person, last_quarter, last_date, last_year_range, last_sequence = parse_quotation_number(st.session_state.last_quotation_number)
                    
                    if last_sales_person == sales_person and last_quarter == current_quarter:
                        # Same sales person and same quarter, increment sequence
                        next_sequence = get_next_sequence_number(st.session_state.last_quotation_number)
                        return generate_quotation_number(sales_person, next_sequence)
                    else:
                        # Different sales person or new quarter, start from sequence 1
                        return generate_quotation_number(sales_person, 1)
                except:
                    # If parsing fails, use current sequence
                    return generate_quotation_number(sales_person, st.session_state.quotation_seq)
            else:
                # No previous quotation, start from current sequence
                return generate_quotation_number(sales_person, st.session_state.quotation_seq)
        
        # Initialize or update quotation number when sales person changes
        if "current_quote_sales_person" not in st.session_state:
            st.session_state.current_quote_sales_person = sales_person
            st.session_state.quotation_number = get_quotation_number()
        
        # Update quotation number if sales person changes or quarter changes
        if (st.session_state.current_quote_sales_person != sales_person or 
            st.session_state.get('current_quarter', '') != current_quarter):
            st.session_state.current_quote_sales_person = sales_person
            st.session_state.current_quarter = current_quarter
            st.session_state.quotation_number = get_quotation_number()
        
        # Display current sales person info
        st.sidebar.info(f"**Current Sales Person:** {current_sales_person_info['name']}")
        st.sidebar.info(f"**Current Quarter:** {current_quarter}")
        
        # Show auto-generated breakdown
        try:
            prefix, current_sp, quarter, date_part, year_range, sequence = parse_quotation_number(st.session_state.quotation_number)
            st.sidebar.success(f"**Auto-generated Quotation Number**")
            st.sidebar.info(f"**Format:** {current_sp}/{quarter}/{date_part}/{year_range}_{sequence}")
        except:
            st.sidebar.warning("Could not parse quotation number")
        
        # Editable quotation number WITHOUT sales person selection
        st.sidebar.subheader("Quotation Number Editor")
        
        # Parse current quotation number for editing
        try:
            current_prefix, current_sp, current_q, current_date, current_year_range, current_seq = parse_quotation_number(st.session_state.quotation_number)
            
            # Create editable components (NO SALES PERSON SELECTION)
            col1, col2, col3, col4 = st.sidebar.columns([1, 2, 2, 1])
            
            with col1:
                # Show current sales person (read-only)
                st.text_input("Sales Person", value=current_sp, key="quote_sp_display", disabled=True)
            
            with col2:
                new_date = st.text_input("Date", value=current_date, key="quote_date_edit")
            
            with col3:
                new_year_range = st.text_input("Year Range", value=current_year_range, key="quote_year_edit")
            
            with col4:
                new_sequence = st.number_input("Sequence", 
                                            min_value=1, 
                                            value=int(current_seq), 
                                            step=1,
                                            key="quote_seq_edit")
            
            # Construct new quotation number using the SELECTED sales person, not the edited one
            new_quotation_number = f"CMI/{sales_person}/{current_q}/{new_date}/{new_year_range}_{new_sequence:03d}"
            
            # Update if changed
            if new_quotation_number != st.session_state.quotation_number:
                st.session_state.quotation_number = new_quotation_number
                
        except Exception as e:
            st.sidebar.error(f"Error parsing quotation number: {e}")
            # Fallback to default
            st.session_state.quotation_number = generate_quotation_number(sales_person, st.session_state.quotation_seq)
        
        # Display final quotation number
        st.sidebar.code(st.session_state.quotation_number)
        
        quotation_auto_increment = st.sidebar.checkbox("Auto-increment Sequence", value=True, key="quote_auto_increment")
        
        if st.sidebar.button("Reset to Auto-generate", use_container_width=True):
            st.session_state.quotation_seq = 1
            st.session_state.last_quotation_number = ""
            st.session_state.quotation_number = get_quotation_number()
            st.sidebar.success("Quotation number reset to auto-generated")
            st.rerun()
        
        # Main form
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("Recipient Details")
            vendor_name = st.text_input("Company Name", "Creation Studio", key="quote_vendor_name")
            vendor_address = st.text_area("Company Address", "Al-Habtula Apartment, Swk Society,\nSid, Dah, Guja 389", key="quote_vendor_address")
            vendor_email = st.text_input("Email", "info@dreamcreationstudio.com", key="quote_vendor_email")
            vendor_contact = st.text_input("Contact Person (Kind Attention)", "Mr. Musta", key="quote_vendor_contact")
            vendor_mobile = st.text_input("Mobile", "+91 9876543210", key="quote_vendor_mobile")

            st.header("Quotation Details")
            price_validity = st.text_input("Price Validity", "September 29, 2025", key="quote_price_validity")
            subject_line = st.text_input("Subject", "Proposal for Adobe Commercial Software Licenses", key="quote_subject")
            intro_paragraphs = st.text_area("Introduction Paragraphs",
            """This is with reference to your requirement for Adobe Software. It gives us great pleasure to know that we are being considered by you and are invited to fulfill the requirements of your organization.
            
Enclosed please find our Quotation for your information and necessary action. You're electing CM Infotech's proposal; your company is assured of our pledge to provide immediate and long-term operational advantages.
            
CMI (CM INFOTECH) is now one of the leading IT solution providers in India, serving more than 1,000 subscribers across the India in Architecture, Construction, Geospatial, Infrastructure, Manufacturing, Multimedia and Graphic Solutions.
            
Our partnership with Autodesk, GstarCAD, Grabert, RuleBuddy, CMS Intellicad, ZWCAD, Etabs, Trimble, Bentley, Solidworks, Solid Edge, Bluebeam, Adobe, Microsoft, Corel, Chaos, Nitro, Tally Quick Heal and many more brings in India the best solutions for design, construction and manufacturing. We are committed to making each of our clients successful with their design technology.
            
As one of our privileged customers, we look forward to having you take part in our journey as we keep our eye on the future, where we will unleash ideas to create a better world!""",
            key="quote_intro"
            )
        
        with col2:
            st.header("Products & Services")
            
            # Add input fields for both annexure and quotation title
            col_annexure, col_title = st.columns(2)
            
            with col_annexure:
                annexure_text = st.text_input(
                    "Annexure Text", 
                    "Annexure I - Commercials", 
                    key="quote_annexure_input",
                    help="Enter annexure text (e.g., Annexure I - Commercials, Annexure II - Terms)"
                )
            
            with col_title:
                quotation_title = st.text_input(
                    "Quotation Title", 
                    "Quotation for Adobe Software", 
                    key="quote_title_input",
                    help="Enter the main title that will appear below annexure"
                )
            
            # Product selection from catalog
            selected_product = st.selectbox("Select from Product Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="quote_product_select")
            if st.button("➕ Add Selected Product", key="add_selected_quote"):
                if selected_product:
                    details = PRODUCT_CATALOG[selected_product]
                    st.session_state.quotation_products.append({
                        "name": selected_product,
                        "basic": details["basic"],
                        "gst_percent": details["gst_percent"],
                        "qty": 1.0,
                    })
                    st.success(f"{selected_product} added!")
            
            # Custom product addition
            with st.expander("➕ Add Custom Product"):
                custom_name = st.text_input("Product Name", key="quote_custom_name")
                custom_basic = st.number_input("Basic Price (₹)", min_value=0.0, value=0.0, format="%.2f", key="quote_custom_basic")
                custom_gst = st.number_input("GST %", min_value=0.0, max_value=100.0, value=18.0, format="%.1f", key="quote_custom_gst")
                custom_qty = st.number_input("Quantity", min_value=1.0, value=1.0, format="%.0f", key="quote_custom_qty")
                
                if st.button("Add Custom Product", key="add_custom_quote"):
                    if custom_name:
                        st.session_state.quotation_products.append({
                            "name": custom_name,
                            "basic": custom_basic,
                            "gst_percent": custom_gst,
                            "qty": custom_qty,
                        })
                        st.success(f"Custom product '{custom_name}' added!")
            
            # Display current products
            st.subheader("Current Products")
            if not st.session_state.quotation_products:
                st.info("No products added yet.")
            else:
                for i, product in enumerate(st.session_state.quotation_products):
                    with st.expander(f"Product {i+1}: {product['name']}", expanded=True):
                        col_a, col_b, col_c = st.columns([3, 1, 1])
                        with col_a:
                            st.text_input("Name", product["name"], key=f"quote_name_{i}", disabled=True)
                        with col_b:
                            st.number_input("Basic Price", value=product["basic"], format="%.2f", key=f"quote_basic_{i}", disabled=True)
                        with col_c:
                            st.number_input("Qty", value=product["qty"], format="%.0f", key=f"quote_qty_{i}", disabled=True)
                        
                        if st.button("Remove", key=f"quote_remove_{i}"):
                            st.session_state.quotation_products.pop(i)
                            st.rerun()
        
        # Preview and Generate Section
        st.header("Preview & Generate Quotation")
        
        # Show the current quotation number prominently with sales person info
        st.info(f"**Quotation Number:** {st.session_state.quotation_number}")
        st.info(f"**Sales Person:** {current_sales_person_info['name']} ({sales_person}) - {current_sales_person_info['email']}")
        
        # Calculate totals
        total_base = sum(p["basic"] * p["qty"] for p in st.session_state.quotation_products)
        total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.quotation_products)
        grand_total = total_base + total_gst
        
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("Total Base Amount", f"₹{total_base:,.2f}")
        with col4:
            st.metric("Total GST (18%)", f"₹{total_gst:,.2f}")
        with col5:
            st.metric("Grand Total", f"₹{grand_total:,.2f}")
        
        # File uploaders
        st.subheader("Upload Images")
        logo_file = st.file_uploader("Company Logo (PNG, JPG)", type=["png", "jpg", "jpeg"], key="quote_logo")
        stamp_file = st.file_uploader("Company Stamp/Signature (PNG, JPG)", type=["png", "jpg", "jpeg"], key="quote_stamp")
        
        logo_path = None
        stamp_path = None
        
        # Process uploaded files
        if logo_file:
            logo_path = "temp_logo_quote.jpg"
            try:
                image_bytes = io.BytesIO(logo_file.getbuffer())
                img = Image.open(image_bytes)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(logo_path, format="JPEG", quality=95)
                st.success("✓ Logo uploaded successfully")
            except Exception as e:
                st.warning(f"Could not process logo: {e}")
                logo_path = None
        
        if stamp_file:
            stamp_path = "temp_stamp_quote.jpg"
            try:
                image_bytes = io.BytesIO(stamp_file.getbuffer())
                img = Image.open(image_bytes)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(stamp_path, format="JPEG", quality=95)
                st.success("✓ Stamp uploaded successfully")
            except Exception as e:
                st.warning(f"Could not process stamp: {e}")
                stamp_path = None
        
        if st.button("Generate Quotation PDF", type="primary", use_container_width=True, key="generate_quote"):
            if not st.session_state.quotation_products:
                st.error("Please add at least one product to generate the quotation.")
            else:
                quotation_data = {
                    "quotation_number": st.session_state.quotation_number,
                    "quotation_date": today.strftime("%d-%m-%Y"),
                    "vendor_name": vendor_name,
                    "vendor_address": vendor_address,
                    "vendor_email": vendor_email,
                    "vendor_contact": vendor_contact,
                    "vendor_mobile": vendor_mobile,
                    "products": st.session_state.quotation_products,
                    "price_validity": price_validity,
                    "grand_total": grand_total,
                    "subject": subject_line,
                    "intro_paragraph": intro_paragraphs,
                    "sales_person_code": sales_person,  
                    "annexure_text": annexure_text,  
                    "quotation_title": quotation_title
                }
                
                try:
                    pdf_bytes = create_quotation_pdf(quotation_data, logo_path, stamp_path)
                    
                    # Store the last quotation number for sequence tracking
                    st.session_state.last_quotation_number = st.session_state.quotation_number
                    
                    # Auto-increment for next quotation
                    if quotation_auto_increment:
                        try:
                            next_sequence = get_next_sequence_number(st.session_state.quotation_number)
                            # Update the sequence in session state for next time
                            st.session_state.quotation_seq = next_sequence
                        except:
                            st.session_state.quotation_seq += 1
                    
                    st.success("✅ Quotation generated successfully!")
                    st.info(f"📧 Sales Person: {current_sales_person_info['name']}")
                    
                    # Download button
                    st.download_button(
                        "⬇ Download Quotation PDF",
                        data=pdf_bytes,
                        file_name=f"Quotation_{st.session_state.quotation_number.replace('/', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")

    # Clean up temporary files
    for path in ["temp_logo.jpg", "temp_stamp.jpg", "temp_logo_quote.jpg", "temp_stamp_quote.jpg"]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
    
    st.divider()
    st.caption("© 2025 Document Generator - CM Infotech")

if __name__ == "__main__":
    main()
