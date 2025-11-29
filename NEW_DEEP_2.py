import streamlit as st
from fpdf import FPDF
import pandas as pd
from num2words import num2words
import datetime
import io
from PIL import Image
import os
from fpdf import FPDF, HTMLMixin
import textwrap
import html as _html 
import json
import requests  # Add this import for downloading from GitHub

# GitHub Configuration - FIXED URLs
LOGO_URL = "https://raw.githubusercontent.com/cmisales26/purchase-order-dashboard/main/logo_final.jpg"
STAMP_URL = "https://raw.githubusercontent.com/cmisales26/purchase-order-dashboard/main/stamp.jpg"

# --- Global Data and Configuration ---
PRODUCT_CATALOG = {
    "GstarCAD STDANDARD 2026 Perpetual": {"basic": 34777.0, "gst_percent": 18.0},
    "GstarCAD STDANDARD 2026 One year upgrade": {"basic": 18303.0, "gst_percent": 18.0},
    "GstarCAD STDANDARD 2026 Two year upgrade": {"basic": 18303.0, "gst_percent": 18.0},
    "GstarCAD STDANDARD 2026 Three + year upgrade": {"basic": 22696.0, "gst_percent": 18.0},

    "GstarCAD PROFESSIONAL 2026 Perpetual": {"basic": 46125.0, "gst_percent": 18.0},
    "GstarCAD PROFESSIONAL 2026 One year upgrade": {"basic": 25625.0, "gst_percent": 18.0},
    "GstarCAD PROFESSIONAL 2026 Two year upgrade": {"basic": 25625.0, "gst_percent": 18.0},
    "GstarCAD PROFESSIONAL 2026 Three + year upgrade": {"basic": 30018.0, "gst_percent": 18.0},

    "GstarCAD PLUS 2026 Perpetual": {"basic": 57107.0, "gst_percent": 18.0},
    "GstarCAD PLUS 2026 One year upgrade": {"basic": 29286.0, "gst_percent": 18.0},
    "GstarCAD PLUS 2026 Two year upgrade": {"basic": 32946.0, "gst_percent": 18.0},
    "GstarCAD PLUS 2026 Three + year upgrade": {"basic": 41000.0, "gst_percent": 18.0},

    "GstarCAD MECHANICAL 2025 Perpetual": {"basic": 92250.0, "gst_percent": 18.0},
    "GstarCAD MECHANICAL 2025 One year upgrade": {"basic": 73214.0, "gst_percent": 18.0},
    "GstarCAD MECHANICAL 2025 Two year upgrade": {"basic": 87857.0, "gst_percent": 18.0},
    "GstarCAD MECHANICAL 2025 Three + year upgrade": {"basic": 105428.0, "gst_percent": 18.0},

    "GstarCAD ARCHITECTURE 2021 Perpetual": {"basic": 92250.0, "gst_percent": 18.0},
    "GstarCAD ARCHITECTURE 2021 One year upgrade": {"basic": 73214.0, "gst_percent": 18.0},
    "GstarCAD ARCHITECTURE 2021 Two year upgrade": {"basic": 87857.0, "gst_percent": 18.0},
    "GstarCAD ARCHITECTURE 2021 Three + year upgrade": {"basic": 105428.0, "gst_percent": 18.0},

    "Archline.XP LT 2025 Perpetual": {"basic": 30450.0, "gst_percent": 18.0},
    "Archline.XP LT Yearly Subscription": {"basic": 26617.0, "gst_percent": 18.0},

    "Archline.XP Interior 2025 Perpetual": {"basic": 94500.0, "gst_percent": 18.0},
    "Archline.XP Interior Yearly Subscription": {"basic": 70875.0, "gst_percent": 18.0},

    "Archline.XP Professional 2025 Perpetual": {"basic": 126000.0, "gst_percent": 18.0},
    "Archline.XP Professional Yearly Subscription": {"basic": 94500.0, "gst_percent": 18.0},

    "Archline.XP MEP Module for LT 2025": {"basic": 30450.0, "gst_percent": 18.0},
    "Archline.XP MEP Module Yearly Subscription": {"basic": 21000.0, "gst_percent": 18.0},

    "Autodesk BIM Collaborate Pro - Single User Commercial Annual Subscription Renewal":{"basic":00.0,"gst_percent": 18.0},

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

# Load data from JSON files
def load_json_data(filename, default_data=None):
    """Load data from JSON file with error handling"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"⚠️ {filename} not found. Using empty database.")
        return default_data or {}
    except json.JSONDecodeError as e:
        st.error(f"❌ Error reading {filename}: {e}. Using empty database.")
        return default_data or {}
    except Exception as e:
        st.error(f"❌ Unexpected error reading {filename}: {e}. Using empty database.")
        return default_data or {}

# Load vendor and end user databases
VENDOR_DATABASE = load_json_data('vendor.json')
END_USER_DATABASE = load_json_data('endusers.json')


# Sales Person Mapping - ONLY ONE DEFINITION
SALES_PERSON_MAPPING = {
    "CP": {"name": "Chirag Prajapati", "email": "chirag@cminfotech.com", "mobile": "+91 87339 15721"},
    "HP": {"name": "Hiral Patel", "email": "hiral@cminfotech.com", "mobile": "+91 95581 15721"},
    "KP": {"name": "Khushi Patel", "email": "khushi@cminfotech.com", "mobile": "+91 97241 15721"},
    "SD": {"name": "Sakshi Darji", "email": "sakshi@cminfotech.com", "mobile": "+91 74051 15721"}
}

# --- Helper Functions for Vendor Management ---
def get_vendor_dropdown_options():
    """Get vendor names for dropdown"""
    return ["Select Vendor"] + list(VENDOR_DATABASE.keys())

def update_vendor_fields(selected_vendor):
    """Update session state with vendor details when vendor is selected"""
    if selected_vendor and selected_vendor != "Select Vendor":
        vendor_data = VENDOR_DATABASE.get(selected_vendor, {})
        st.session_state.po_vendor_name = selected_vendor
        st.session_state.po_vendor_address = vendor_data.get("address", "")
        st.session_state.po_vendor_contact = vendor_data.get("contact", "")
        st.session_state.po_vendor_mobile = vendor_data.get("mobile", "")
        st.session_state.po_gst_no = vendor_data.get("gst_no", "")
        st.session_state.po_pan_no = vendor_data.get("pan_no", "")
        st.session_state.po_msme_no = vendor_data.get("msme_no", "")

# --- Helper Functions for End User Management ---
def get_enduser_dropdown_options():
    """Get end user names for dropdown"""
    return ["Select End User"] + list(END_USER_DATABASE.keys())

def update_enduser_fields(selected_enduser):
    """Update session state with end user details when end user is selected"""
    if selected_enduser and selected_enduser != "Select End User":
        enduser_data = END_USER_DATABASE.get(selected_enduser, {})
        st.session_state.po_end_company = selected_enduser
        st.session_state.po_end_address = enduser_data.get("address", "")
        st.session_state.po_end_person = enduser_data.get("contact", "")
        st.session_state.po_end_mobile = enduser_data.get("mobile", "")
        st.session_state.po_end_email = enduser_data.get("email", "")
        st.session_state.po_end_gst_no = enduser_data.get("gst_no", "")


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

import os

# Simple file-based counter for PO sequence
PO_COUNTER_FILE = "po_counter.txt"

def get_next_po_sequence():
    """Simple file-based PO sequence counter"""
    try:
        # Read current number from file
        if os.path.exists(PO_COUNTER_FILE):
            with open(PO_COUNTER_FILE, 'r') as f:
                current = int(f.read().strip())
        else:
            current = 0
    except:
        current = 0
    
    # Increment
    next_seq = current + 1
    
    # Save the new number back to file
    with open(PO_COUNTER_FILE, 'w') as f:
        f.write(str(next_seq))
    
    return next_seq

def get_current_po_sequence():
    """Get current PO sequence without incrementing"""
    try:
        if os.path.exists(PO_COUNTER_FILE):
            with open(PO_COUNTER_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return 1


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
import os

# Simple file-based counter for quotations
QUOTATION_COUNTER_FILE = "quotation_counter.txt"

def get_next_quotation_sequence():
    """Simple file-based sequence counter"""
    try:
        # Read current number from file
        if os.path.exists(QUOTATION_COUNTER_FILE):
            with open(QUOTATION_COUNTER_FILE, 'r') as f:
                current = int(f.read().strip())
        else:
            current = 0
    except:
        current = 0
    
    # Increment
    next_seq = current + 1
    
    # Save the new number back to file
    with open(QUOTATION_COUNTER_FILE, 'w') as f:
        f.write(str(next_seq))
    
    return next_seq

def get_current_quotation_sequence():
    """Get current sequence without incrementing"""
    try:
        if os.path.exists(QUOTATION_COUNTER_FILE):
            with open(QUOTATION_COUNTER_FILE, 'r') as f:
                return int(f.read().strip())
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
    return "CMI", "SD", get_current_quarter(), datetime.datetime.now().strftime("%d-%m-%Y"), f"{datetime.datetime.now().year}-{datetime.datetime.now().year+1}", "001"

def generate_quotation_number(sales_person, sequence_number):
    """Generate quotation number with current quarter and sequence"""
    current_date = datetime.datetime.now()
    quarter = get_current_quarter()
    year_range = f"{current_date.year}-{current_date.year+1}"
    sequence = f"{sequence_number:03d}"
    
    return f"CMI/{sales_person}/{quarter}/{current_date.strftime('%d-%m-%Y')}/{year_range}_{sequence}"

# --- Add this function with other helper functions ---
def calculate_quotation_totals(products):
    """Calculate quotation totals with round-off like PO generator"""
    products_total = 0
    for p in products:
        gst_amt = p["basic"] * p["gst_percent"] / 100
        per_unit_price = p["basic"] + gst_amt
        total = per_unit_price * p["qty"]
        products_total += total

    # Calculate round off to make final amount whole number (like PO)
    rounded_total = round(products_total)
    round_off = rounded_total - products_total
    
    return {
        "total_base": sum(p["basic"] * p["qty"] for p in products),
        "total_gst": sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in products),
        "grand_total_unrounded": products_total,
        "grand_total": rounded_total,
        "round_off": round_off
    }

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


import os

# Simple file-based counter for Invoice sequence
INVOICE_COUNTER_FILE = "invoice_counter.txt"

def get_next_invoice_sequence():
    """Simple file-based Invoice sequence counter"""
    try:
        # Read current number from file
        if os.path.exists(INVOICE_COUNTER_FILE):
            with open(INVOICE_COUNTER_FILE, 'r') as f:
                current = int(f.read().strip())
        else:
            current = 0
    except:
        current = 0
    
    # Increment
    next_seq = current + 1
    
    # Save the new number back to file
    with open(INVOICE_COUNTER_FILE, 'w') as f:
        f.write(str(next_seq))
    
    return next_seq

def get_current_invoice_sequence():
    """Get current Invoice sequence without incrementing"""
    try:
        if os.path.exists(INVOICE_COUNTER_FILE):
            with open(INVOICE_COUNTER_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return 1



# --- Helper Functions for Invoice ---
# --- Helper Functions for Invoice ---
def parse_invoice_number(invoice_number):
    """Parse invoice number to extract components - COMPATIBLE WITH EXISTING FORMAT"""
    try:
        parts = invoice_number.split('/')
        if len(parts) >= 4:
            prefix = parts[0]  # CMI
            year_range = parts[1]  # 25-26
            quarter = parts[2]  # Q3
            sequence = parts[3]  # 01, 02, etc.
            return prefix, year_range, quarter, sequence
    except:
        pass
    return "CMI", f"{str(datetime.datetime.now().year)[2:]}-{str(datetime.datetime.now().year + 1)[2:]}", get_current_quarter(), "01"

def generate_invoice_number(sequence_number):
    """Generate invoice number - KEEP EXISTING FORMAT"""
    current_date = datetime.datetime.now()
    quarter = get_current_quarter()
    year_range = f"{str(current_date.year)[2:]}-{str(current_date.year + 1)[2:]}"
    sequence = f"{sequence_number:02d}"
    
    return f"CMI/{year_range}/{quarter}/{sequence}"

def get_next_sequence_number_invoice(invoice_number):
    """Extract and increment sequence number from invoice number"""
    try:
        parts = invoice_number.split('/')
        if len(parts) >= 4:
            sequence = parts[3]
            return int(sequence) + 1
    except:
        pass
    return get_next_invoice_sequence()  # Use your existing counter

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
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        try:
            self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
            self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
            self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
            self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
            self.default_font = "Calibri"
        except:
            self.default_font = "Helvetica"
        
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
                self.set_font(self.default_font, "B", 10)
                self.set_xy(150, 8)
                self.cell(40, 5, "[LOGO]", border=0, align="C")
            
        # Main Title (Centered)
        self.set_font(self.default_font, "B", 16)
        self.set_y(15)
        self.ln(5)

    def footer(self):
        # Position from bottom (same as invoice)
        self.set_y(-12)
        
        # Horizontal line
        # self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        # self.ln(2)
        
        # Footer content - Computer generated text
        # self.set_font("Helvetica", "I", 10)
        # self.cell(0, 4, "This is a Computer Generated Quotation", ln=True, align="C")
        
        # Company address
        self.set_font("Helvetica", "", 10)
        self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
        # Clickable contact info (same as invoice)
        self.set_font("Helvetica", "U", 10)
        self.set_text_color(0, 0, 255)  # Blue for links
        
        email1 = "info@cminfotech.com"
        phone_number = "+91 873 391 5721"
        website = "www.cminfotech.com"
        
        # Center the contact information
        contact_text = f"{email1} | {phone_number} | {website}"
        contact_width = self.get_string_width(contact_text)
        x_contact = (self.w - contact_width) / 2
        
        self.set_x(x_contact)
        self.cell(self.get_string_width(email1), 4, email1, link=f"mailto:{email1}")
        self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | "))
        self.cell(self.get_string_width(phone_number), 4, phone_number, link=f"tel:{phone_number}")
        self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | ") + self.get_string_width(phone_number) + self.get_string_width(" | "))
        self.cell(self.get_string_width(website), 4, website, link="https://www.cminfotech.com/")
        
        self.set_text_color(0, 0, 0)

    # def footer(self):
    #     self.set_y(-18)
    #     self.set_font(self.default_font, "", 10)
    #     self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
    #     # Make footer emails and phone clickable - FIXED OVERLAP
    #     self.set_text_color(0, 0, 255)  # Blue color for links
        
    #     # Website link
    #     # self.cell(0, 4, "www.cminfotech.com", ln=True, align="C", link="https://www.cminfotech.com/")
        
    #     # Email and phone on same line - FIXED
    #     self.set_font(self.default_font, "U", 10)
    #     email_text = " info@cminfotech.com "
    #     phone_text = " +91 873 391 5721"
        
    #     # Calculate positions for proper alignment
    #     page_width = self.w - 2 * self.l_margin
    #     email_width = self.get_string_width(email_text)
    #     phone_width = self.get_string_width(phone_text)
    #     separator_width = self.get_string_width(" | ")
        
    #     total_width = email_width + separator_width + phone_width
    #     start_x = (page_width - total_width) / 2 + self.l_margin
        
    #     self.set_x(start_x)
    #     self.cell(email_width, 4, email_text, ln=0, link=f"mailto:{email_text}")
    #     self.cell(separator_width, 4, " | ", ln=0)
    #     self.cell(phone_width, 4, phone_text, ln=True, link=f"tel:{phone_text.replace(' ', '').replace('+', '')}")

    #     self.cell(0, 4, "www.cminfotech.com", ln=True, align="C", link="https://www.cminfotech.com/")
        
    #     self.set_text_color(0, 0, 0)  # Reset to black

def add_clickable_email(pdf, email, label="Email: "):
    """Add clickable email with label - FIXED OVERLAP"""
    pdf.set_font(pdf.default_font, "B", 12)
    label_width = pdf.get_string_width(label)
    pdf.cell(label_width, 4, label, ln=0)
    
    pdf.set_text_color(0, 0, 255)  # Blue for clickable
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(0, 4, email, ln=True, link=f"mailto:{email}")
    pdf.set_text_color(0, 0, 0)  # Reset to black

def add_clickable_phone(pdf, phone, label="Mobile: "):
    """Add clickable phone number with label - FIXED OVERLAP"""
    pdf.set_font(pdf.default_font, "B", 12)
    label_width = pdf.get_string_width(label)
    pdf.cell(label_width, 4, label, ln=0)
    
    pdf.set_text_color(0, 0, 255)  # Blue for clickable
    pdf.set_font(pdf.default_font, "", 12)
    # Remove spaces and + for tel link
    tel_number = phone.replace(' ', '').replace('+', '')
    pdf.cell(0, 4, phone, ln=True, link=f"tel:{tel_number}")
    pdf.set_text_color(0, 0, 0)  # Reset to black

def add_page_one_intro(pdf, data):
    # Reference Number & Date (Top Right)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.set_y(35)
    pdf.cell(0, 5, f"REF NO.: {data['quotation_number']}", ln=True, align="L")
    pdf.cell(0, 5, f"Date: {data['quotation_date']}", ln=True, align="L")
    pdf.ln(5)

    # Recipient Details
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(0, 5, "To,", ln=True)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(0, 6, pdf.sanitize_text(data['vendor_name']), ln=True)
    pdf.set_font(pdf.default_font, "", 12)
    
    # Address handling
    pdf.multi_cell(94, 4, pdf.sanitize_text(data['vendor_address']))
    
    pdf.ln(3)
    
    # Clickable Email
    if data.get('vendor_email'):
        add_clickable_email(pdf, data['vendor_email'])
        
    pdf.ln(1)
    # Clickable Mobile
    if data.get('vendor_mobile'):
        add_clickable_phone(pdf, data['vendor_mobile'])
    
    pdf.set_font(pdf.default_font, "BU", 12)
    pdf.cell(0, 5, f"Kind Attention :- {pdf.sanitize_text(data['vendor_contact'])}", align="C", ln=True)
    pdf.ln(5)

    # Subject Line
    pdf.set_font(pdf.default_font, "BU", 12)
    pdf.cell(0, 6, f"Subject :- {pdf.sanitize_text(data['subject'])}", ln=True)
    pdf.ln(8)  # Increased spacing

    # Write the user's custom intro paragraph
    intro_text = pdf.sanitize_text(data.get("intro_paragraph", ""))
    if intro_text:
        write_simple_justified_paragraph(pdf, intro_text)

    # Fixed company introduction paragraphs - USE THE SIMPLE VERSION
    fixed_paragraphs = [
        "Enclosed please find our Quotation for your information and necessary action. You're electing CM Infotech's proposal; your company is assured of our pledge to provide immediate and long-term operational advantages.",
        
        "CMI (CM INFOTECH) is now one of the leading IT solution providers in India, serving more than 1,000 subscribers across the India in Architecture, Construction, Geospatial, Infrastructure, Manufacturing, Multimedia and Graphic Solutions.",
        
        "Our partnership with Autodesk, GstarCAD, Grabert, CMS Intellicad, ZWCAD, Etabs, Trimble, Bentley, Solidworks, Solid Edge, Bluebeam, Adobe, Microsoft, Corel, Chaos, Nitro, Tally Quick Heal and many more brings in India the best solutions for design, construction and manufacturing. We are committed to making each of our clients successful with their design technology.",
        
        "As one of our privileged customers, we look forward to having you take part in our journey as we keep our eye on the future, where we will unleash ideas to create a better world!"
    ]

    for paragraph in fixed_paragraphs:
        write_simple_justified_paragraph(pdf, paragraph)
        pdf.ln(3)  # Add space between paragraphs

    # Contact Information - MAKE SURE WE HAVE ENOUGH SPACE
    # Check if we need a new page
    if pdf.get_y() > 220:  # If we're too low on the page
        pdf.add_page()
    
    pdf.set_font(pdf.default_font, "", 12)
    pdf.set_text_color(0, 0, 0)

    # Normal text - make sure it's complete
    contact_text = "Please revert back to us, if you need any clarification / information at the below mentioned address or email at "
    pdf.write(5, contact_text)

    # Get sales person info dynamically
    sales_person_code = data.get('sales_person_code', 'SD')
    sales_person_info = SALES_PERSON_MAPPING.get(sales_person_code, SALES_PERSON_MAPPING['SD'])
    
    # Email clickable - DYNAMIC from sales person
    pdf.set_text_color(0, 0, 255)
    pdf.set_font(pdf.default_font, "U", 12)
    pdf.write(5, sales_person_info["email"], link=f"mailto:{sales_person_info['email']}")

    # Back to normal for separator + Mobile:
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.write(5, "  Mobile: ")

    # Mobile clickable - DYNAMIC from sales person
    pdf.set_text_color(0, 0, 255)
    pdf.set_font(pdf.default_font, "U", 12)
    pdf.write(5, sales_person_info["mobile"], link=f"tel:{sales_person_info['mobile'].replace(' ', '').replace('+', '')}")

    pdf.ln(10)  # Add space after contact info
    pdf.set_text_color(0, 0, 0)
    # Continue with the rest of your contact information...
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(0, 4, "For more information, please visit our web site & Social Media :-", ln=True)
    pdf.set_font(pdf.default_font, "", 12)
    
    # Clickable website - RIGHT ALIGNED
    pdf.set_font(pdf.default_font, "U", 12)
    pdf.set_text_color(0, 0, 255)

    # Calculate the width needed for the longest link
    links = [
        "https://www.cminfotech.com/",
        "https://www.linkedin.com/", 
        "https://wa.me/918733915721",
        "https://www.facebook.com/",
        "https://www.instagram.com/"
    ]

    # Get the maximum width
    max_link_width = max(pdf.get_string_width(link) for link in links)

    # Set right margin position
    right_margin = pdf.w - pdf.r_margin

    # Print each link aligned to the right
    for link in links:
        # Calculate x position to right-align
        x_position = right_margin - max_link_width
        pdf.set_x(x_position)
        pdf.cell(max_link_width, 4, link, ln=True, link=link)

    pdf.set_text_color(0, 0, 0)

def write_simple_justified_paragraph(pdf, text):
    """Ultra-simple justified paragraphs using multi_cell"""
    pdf.set_font(pdf.default_font, "", 12)
    pdf.set_text_color(0, 0, 0)
    
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            # Use multi_cell with justification
            pdf.multi_cell(0, 5, paragraph, align='J')
            pdf.ln(3)

def add_quotation_header(pdf, annexure_text, quotation_text):
    """Add dynamic quotation header with both annexure and title"""
    pdf.set_font(pdf.default_font, "BU", 14)
    pdf.cell(0, 8, annexure_text, ln=True, align="C")
    pdf.set_font(pdf.default_font, "BU", 12)
    pdf.cell(0, 6, quotation_text, ln=True, align="C")
    pdf.ln(8)

def add_page_two_commercials(pdf, data):
    pdf.add_page()
    pdf.ln(10)
    # Use dynamic header function
    annexure_text = data.get('annexure_text', 'Annexure I - Commercials')
    quotation_title = data.get('quotation_title', 'Quotation for Adobe Software')
    
    add_quotation_header(pdf, annexure_text, quotation_title)

    # --- Products Table - FIXED COLUMN WIDTHS (Wider Description) ---
    col_widths = [70, 25, 25, 25, 15, 25]  # Increased Description from 70 to 100
    headers = ["Description", "Basic Price", "GST Tax @ 18%", "Per Unit Price", "Qty.", "Total"]
    
    # Table Header
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font(pdf.default_font, "B", 10)
    for width, header in zip(col_widths, headers):
        pdf.cell(width, 6, header, border=1, align="C", fill=True)
    pdf.ln()
    
    # Table Rows
    pdf.set_font(pdf.default_font, "", 12)
    grand_total_unrounded = 0.0
    
    for product in data["products"]:
        basic_price = product["basic"]
        qty = product["qty"]
        gst_amount = basic_price * (product.get("gst_percent", 18.0) / 100)
        per_unit_price = basic_price + gst_amount
        total = per_unit_price * qty
        grand_total_unrounded += total
        
        # Get current position
        start_y = pdf.get_y()
        
        # Description cell (with proper text wrapping)
        desc = product["name"]
        pdf.set_font(pdf.default_font, "", 10)
        
        # Calculate how many lines the description will take
        desc_lines = pdf.multi_cell(col_widths[0], 5, desc, border=0, split_only=True)
        desc_height = len(desc_lines) * 6
        
        # Set position for description
        pdf.set_xy(pdf.l_margin, start_y)
        
        # Draw description cell with proper height
        if len(desc_lines) > 1:
            # Multi-line description
            pdf.multi_cell(col_widths[0], 6, desc, border=1)
            current_y = pdf.get_y()
            
            # Set positions for other cells WITH COMMA FORMATTING
            pdf.set_xy(pdf.l_margin + col_widths[0], start_y)
            pdf.cell(col_widths[1], desc_height, f"{basic_price:,.2f}", border=1, align="R")
            pdf.cell(col_widths[2], desc_height, f"{gst_amount:,.2f}", border=1, align="R")
            pdf.cell(col_widths[3], desc_height, f"{per_unit_price:,.2f}", border=1, align="R")
            pdf.cell(col_widths[4], desc_height, f"{qty:.0f}", border=1, align="C")
            pdf.cell(col_widths[5], desc_height, f"{total:,.2f}", border=1, align="R")
            
            # Move to next row
            pdf.set_y(current_y)
        else:
            # Single line description WITH COMMA FORMATTING
            pdf.cell(col_widths[0], 6, desc, border=1)
            pdf.cell(col_widths[1], 6, f"{basic_price:,.2f}", border=1, align="R")
            pdf.cell(col_widths[2], 6, f"{gst_amount:,.2f}", border=1, align="R")
            pdf.cell(col_widths[3], 6, f"{per_unit_price:,.2f}", border=1, align="R")
            pdf.cell(col_widths[4], 6, f"{qty:.0f}", border=1, align="C")
            pdf.cell(col_widths[5], 6, f"{total:,.2f}", border=1, align="R")
            pdf.ln()

    # Round Off Row (NEW - like PO) WITH COMMA FORMATTING
    round_off = data.get('round_off', 0.0)
    pdf.set_font(pdf.default_font, "B", 10)
    pdf.cell(sum(col_widths[:-1]), 7, "Round Off", border=1, align="R")
    pdf.cell(col_widths[5], 7, f"{round_off:,.2f}", border=1, align="R")
    pdf.ln()

    # Grand Total Row - WITH COMMA FORMATTING
    grand_total = data.get('grand_total', grand_total_unrounded)
    pdf.set_font(pdf.default_font, "B", 10)
    pdf.cell(sum(col_widths[:-1]), 7, "Final Amount to be Paid", border=1, align="R")
    pdf.cell(col_widths[5], 7, f"{grand_total:,.2f}", border=1, align="R")
    pdf.ln(15)

    # --- Enhanced Box for Terms & Conditions and Bank Details ---
    pdf.set_font(pdf.default_font, "", 9)

    # Terms & Conditions with ALL terms in bold
    price_validity = data.get('price_validity', '10 days from Quotation date')
    terms = [
        ("1. Above charges are Inclusive of GST.", ""),
        ("2. Any changes in Govt. duties, Taxes & Forex rate at the time of dispatch shall be applicable.", ""),
        ("3. TDS should not be deducted at the time of payment as per Govt. NOTIFICATION NO. 21/2012 [F.No.142/10/2012-SO (TPL)] S.O. 1323(E), DATED 13-6-2012.", ""),
        ("4. ELD licenses are paper licenses that do not contain media.", ""),
        ("5. An Internet connection is required to access cloud services.", ""),
        ("6. Training will be charged at extra cost depending on no. of participants.", ""),
        ("7. Price Validity: ", price_validity),
        ("8. Payment: ", "100% Advance along with purchase order"),
        ("9. Delivery period: ", "1-2 Weeks from the date of Purchase Order"),
        ("10. Support: ","Includes 12 months of technical support and software updates from OEM."),
        ("11. Installation: ","Online"),
        ("12. Cheque to be issued on name of: ", '"CM INFOTECH"'),
        ("13. Order to be placed on: ", "CM INFOTECH \nE/402, Ganesh Glory 11, Near BSNL Office,Jagatpur - Chenpur Road, \nJagatpur Village,Ahmedabad - 382481")
    ]

    # Bank Details
    bank_info = [
        ("Name", "CM INFOTECH"),
        ("Account Number", "88130420182"),
        ("IFSC Code", "IDFB0040335"),
        ("SWIFT Code", "IDFBINBBMUM"),
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
    col1_width = page_width * 0.62  # 60% for Terms
    col2_width = page_width * 0.38  # 40% for Bank Details
    padding = 2.5
    line_height = 4
    section_spacing = 2

    # Calculate required height for both columns
    def calculate_column_height(items, col_width):
        height = 0
        for label, value in items:
            if value:  # If there's a value part
                text = f"{label}{value}"
            else:
                text = label
            lines = pdf.multi_cell(col_width - 2*padding, line_height, text, split_only=True)
            height += len(lines) * line_height + section_spacing
        return height + 3*padding  # Add padding

    terms_height = calculate_column_height(terms, col1_width)

    # Calculate bank details height WITHOUT signature section
    bank_items_height = calculate_column_height(bank_info, col2_width)
    signature_height = 35  # Estimated height for signature section
    
    # Use the maximum height between terms and bank items + signature
    box_height = max(terms_height, bank_items_height + signature_height)

    # Draw the main box
    pdf.rect(x_start, y_start, page_width, box_height)

    # Draw vertical separator line
    pdf.line(x_start + col1_width, y_start, x_start + col1_width, y_start + box_height)

    # Add section headers
    pdf.set_font(pdf.default_font, "B", 12)

    # Terms & Conditions header
    pdf.set_xy(x_start + padding, y_start + padding)
    pdf.cell(col1_width - 2*padding, 5, "Terms & Conditions:", ln=True)

    # Terms content - INSIDE THE BOX
    terms_y = pdf.get_y()
    for i, (label, value) in enumerate(terms):
        pdf.set_xy(x_start + padding, terms_y)
        
        if i < 6:  # First 6 terms - ALL BOLD
            pdf.set_font(pdf.default_font, "B", 10)
            pdf.multi_cell(col1_width - 2*padding, line_height, label)
            
        elif value:  # Terms 7-13 with mixed formatting (label + bold value)
            # Write the regular font part
            pdf.set_font(pdf.default_font, "", 10)
            pdf.cell(pdf.get_string_width(label), line_height, label, ln=0)
            
            # Write the bold part
            pdf.set_font(pdf.default_font, "B", 10)
            remaining_width = col1_width - 2*padding - pdf.get_string_width(label)
            pdf.multi_cell(remaining_width, line_height, value)
            
            # Reset to regular font
            pdf.set_font(pdf.default_font, "", 10)
        else:
            # Regular terms without special formatting
            pdf.multi_cell(col1_width - 2*padding, line_height, label)
        
        terms_y = pdf.get_y()

    # Bank Details header - INSIDE THE BOX
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.set_xy(x_start + col1_width + padding, y_start + padding)
    pdf.cell(col2_width - 2*padding, 5, "Bank Details:", ln=True)
    pdf.set_font(pdf.default_font, "", 12)  # Set to regular for labels

    # Bank details content - INSIDE THE BOX
    bank_y = pdf.get_y()
    for label, value in bank_info:
        pdf.set_xy(x_start + col1_width + padding, bank_y)
        
        # Write label in regular font
        pdf.set_font(pdf.default_font, "", 10)
        pdf.cell(pdf.get_string_width(f"{label}: "), line_height, f"{label}: ", ln=0)
        
        # Write value in BOLD font
        pdf.set_font(pdf.default_font, "B", 10)
        remaining_width = col2_width - 2*padding - pdf.get_string_width(f"{label}: ")
        pdf.multi_cell(remaining_width, line_height, value)
        
        bank_y = pdf.get_y()

    # --- Signature Block INSIDE BANK DETAILS BOX - POSITIONED NEAR BOTTOM ---
    # Calculate position to place signature near bottom of the box
    signature_start_y = y_start + box_height - signature_height - 15
    
    pdf.set_font(pdf.default_font, "B", 10)
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
            stamp_x = x_start + col1_width + padding  # Center the stamp
            pdf.image(data['stamp_path'], x=stamp_x, y=stamp_y, w=20)
            # Move cursor down after stamp
            pdf.set_y(stamp_y + 20)  # Space for stamp + some padding
        except:
            pdf.set_y(pdf.get_y() + 8)  # If stamp fails, add some space
    else:
        pdf.set_y(pdf.get_y() + 8)  # Space if no stamp
    
    pdf.set_font(pdf.default_font, "", 9)
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    pdf.cell(col2_width - 2*padding, 4, sales_person_info["name"], ln=True)
    
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    pdf.cell(col2_width - 2*padding, 4, "Inside Sales Executive", ln=True)
    
    # Clickable email in signature
    pdf.set_font(pdf.default_font, "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    label = "Email: "
    pdf.cell(pdf.get_string_width(label), 4, label, ln=0)
    pdf.set_font(pdf.default_font, "U", 9)
    pdf.set_text_color(0, 0, 255)
    pdf.cell(col2_width - 2*padding - pdf.get_string_width(label), 4, sales_person_info["email"], 
             ln=True, link=f"mailto:{sales_person_info['email']}")
    
    # Clickable phone in signature
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(pdf.default_font, "", 9)
    pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
    label = "Mobile: "
    pdf.cell(pdf.get_string_width(label), 4, label, ln=0)
    pdf.set_font(pdf.default_font, "U", 9)
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
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        try:
            self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
            self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
            self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
            self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
            self.default_font = "Calibri"
        except:
            self.default_font = "Helvetica"

        self.set_font(self.default_font, "", 8)
        self.set_left_margin(10)
        self.set_right_margin(15)
        
        # Store logo file path for use in header
        self.logo_file = None

    def header(self):
        # Add logo on every page (including second page)
        if self.logo_file and self.page_no() >= 1:  # Show logo on all pages
            try:
                self.image(self.logo_file, x=155, y=8, w=50)
            except Exception as e:
                # You can add a warning here if needed, but don't show in header
                pass
        self.ln(9)
        self.set_font(self.default_font, "B", 15)
        self.cell(0, 6, "TAX INVOICE", ln=True, align="C")
        self.ln(1)
        
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        
        # Footer content
        self.set_font(self.default_font, "I", 10)
        self.cell(0, 4, "This is a Computer Generated Invoice", ln=True, align="C")
        
        self.set_font(self.default_font, "", 10)
        self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
        # Clickable contact info
        self.set_font(self.default_font, "U", 10)
        self.set_text_color(0, 0, 255)
        
        email1 = "info@cminfotech.com"
        phone_number = "+91 873 391 5721"
        website = "www.cminfotech.com"
        
        # Center the contact information
        contact_text = f"{email1} | {phone_number} | {website}"
        contact_width = self.get_string_width(contact_text)
        x_contact = (self.w - contact_width) / 2
        
        self.set_x(x_contact)
        self.cell(self.get_string_width(email1), 4, email1, link=f"mailto:{email1}")
        self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | "))
        self.cell(self.get_string_width(phone_number), 4, phone_number, link=f"tel:{phone_number}")
        self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | ") + self.get_string_width(phone_number) + self.get_string_width(" | "))
        self.cell(self.get_string_width(website), 4, website, link="https://www.cminfotech.com/")
        
        self.set_text_color(0, 0, 0)


# --- Function to Create Invoice PDF ---
def create_invoice_pdf(invoice_data, logo_file="logo_final.jpg", stamp_file="stamp.jpg"):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    # Store logo file path in the PDF instance for use in header
    pdf.logo_file = logo_file
    
    pdf.add_page()

    # --- Logo on top right --- (This will now be handled by header() on all pages)
    # Remove the individual logo placement since it's now in header()

    # === HEADER (Vendor + Invoice Details) ===
    pdf.set_font(pdf.default_font, "B", 13)
    pdf.cell(95, 8, "CM INFOTECH.", border="LRT", ln=0)
    pdf.cell(48, 8, "Invoice No.", border=1, ln=0, align="L")
    pdf.cell(48, 8, "Invoice Date", border=1, ln=1, align="L")

    y_left_start = pdf.get_y()

    # --- Left Side (Vendor Details) ---
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(95, 4, invoice_data['vendor']['address'], border="L")
    
    # Vendor details lines
    vendor_lines = [
        ("GST No. : ", invoice_data['vendor']['gst']),
        ("MSME Registration No. : ", invoice_data['vendor']['msme']),
        ("E-Mail : ", "cm.infotech2014@gmail.com"),
        ("Mobile No. : ", "8733915721"),
    ]
    
    for i, (label, value) in enumerate(vendor_lines):
        pdf.set_x(10)
        pdf.set_font(pdf.default_font, "B", 12)
        label_width = pdf.get_string_width(label) 
        pdf.cell(label_width, 6, label, border="L", ln=0)
        pdf.set_font(pdf.default_font, "", 12)
        border = "R" if i < len(vendor_lines) - 1 else "R"
        pdf.cell(95 - label_width, 6, value, border=border, ln=1)

    y_left_end = pdf.get_y()

    # --- Right Side (Invoice Details) ---
    pdf.set_xy(105, y_left_start)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(48, 8, invoice_data['invoice']['invoice_no'], border="LR", ln=0, align="L")
    pdf.cell(48, 8, invoice_data['invoice']['date'], border="R", ln=1, align="L")

    # Payment terms - NOW AS INPUT
    pdf.set_x(105)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(48, 8, "Mode/Terms of Payment:", border="LRT", ln=0)
    pdf.set_font(pdf.default_font, "", 12)

    # Use multi_cell to wrap text to next line - NOW USING INPUT VALUE
    payment_terms = invoice_data['invoice_details'].get('payment_terms', '100% Advance with Purchase')

    # Get current Y position before adding the cell
    y_before = pdf.get_y()

    # Set position and draw the payment terms cell
    pdf.set_xy(153, y_before)
    pdf.multi_cell(48, 4, payment_terms, border="LRT", align="L")

    # Get Y position after adding the cell
    y_after = pdf.get_y()

    # Calculate the actual height of the content
    actual_height = y_after - y_before

    # If the actual height is less than 8mm, add an empty cell to make up the difference
    if actual_height < 8:
        remaining_height = 8 - actual_height
        pdf.set_xy(153, y_after)
        pdf.cell(48, remaining_height, "", border="LR", ln=True)

    # Supplier's reference
    pdf.set_x(105)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(48, 8, "Supplier's Reference:", border="LRT", ln=0)
    pdf.set_font(pdf.default_font, "", 12)
    other_ref_value = invoice_data['Reference']['Suppliers_Reference']
    pdf.cell(48, 8, other_ref_value, border="LRTB", ln=1)

    # Other's reference
    pdf.set_x(105)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(48, 8, "Other's Reference:", border="LRTB", ln=0)
    pdf.set_font(pdf.default_font, "", 12)
    other_ref_value = invoice_data['Reference']['Other']
    pdf.cell(48, 8, other_ref_value, border="LRTB", ln=1)

    # === BUYER SECTION ===
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(95, 6, "Buyer", border="LT", ln=0)
    pdf.cell(48, 6, "Buyer's Order No.", border=1, ln=0, align="L")
    pdf.cell(48, 6, "Buyer's Order Date", border=1, ln=1, align="L")

    y_buyer_start = pdf.get_y()

    # --- Buyer Left Details ---
    y_left_buyer_start = pdf.get_y()
    
    # Buyer name and address
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.multi_cell(95, 5, invoice_data['buyer']['name'], border="LR")
    
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(95, 4, invoice_data['buyer']['address'], border="LR")
    
    # Buyer contact details
    buyer_lines = [
        ("Email :",invoice_data['buyer']['email']),
        ("Mobile No :",invoice_data['buyer']['mobile']),
        ("GST No. :",invoice_data['buyer']['gst']),
    ]
    
    for i, (label, value) in enumerate(buyer_lines):
        pdf.set_x(10)
        pdf.set_font(pdf.default_font, "B", 12)
        label_width = pdf.get_string_width(label) + 1
        pdf.cell(label_width, 6, label, border="L", ln=0)
        pdf.set_font(pdf.default_font, "", 12)
        border = "R" if i < len(buyer_lines) - 1 else "R"
        pdf.cell(95 - label_width, 6, value, border=border, ln=1)

    y_buyer_left_end = pdf.get_y()
    total_left_height = y_buyer_left_end - y_left_buyer_start

    # --- Buyer Right Details ---
    pdf.set_xy(105, y_buyer_start)
    
    # Calculate right side cell heights to match left side
    num_right_rows = 4
    right_cell_height = total_left_height / num_right_rows
    
    # Row 1: Buyer's Order No/Date
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(48, right_cell_height, invoice_data['invoice_details']['buyers_order_no'], border="LR", ln=0, align="L")
    pdf.cell(48, right_cell_height, invoice_data['invoice_details']['buyers_order_date'], border="R", ln=1, align="L")

    # Row 2: Dispatched Through
    pdf.set_x(105)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(48, right_cell_height, "Dispatched Through", border="LRT", ln=0)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(48, right_cell_height, invoice_data['invoice_details']['dispatched_through'], border="RT", ln=1)

    # Row 3: Destination
    pdf.set_x(105)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(48, right_cell_height, "Destination", border="LRT", ln=0)
    pdf.set_font(pdf.default_font, "", 12)
    destination = invoice_data['invoice_details'].get('destination', 'Vadodara')
    pdf.cell(48, right_cell_height, destination, border="RT", ln=1)

    # Row 4: Terms of delivery
    pdf.set_x(105)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(48, right_cell_height, "Terms of delivery", border="LRT", ln=0)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(48, right_cell_height, invoice_data['invoice_details']['terms_of_delivery'], border="LRT", ln=1)

    # Set Y position to continue from the maximum height
    pdf.set_y(max(y_buyer_left_end, y_buyer_start + total_left_height))
    
    pdf.ln(0.3)
    
    # --- Item Table Header ---
    pdf.set_font(pdf.default_font, "B", 12)
    col_widths = [13, 82, 22, 23, 23, 28]
    
    # Header row
    pdf.cell(col_widths[0], 5, "Sr.No.", border=1, align="C")
    pdf.cell(col_widths[1], 5, "Description of Goods", border=1, align="C")
    pdf.cell(col_widths[2], 5, "HSN/SAC", border=1, align="C")
    pdf.cell(col_widths[3], 5, "Quantity", border=1, align="C")
    pdf.cell(col_widths[4], 5, "Unit Rate", border=1, align="C")
    pdf.cell(col_widths[5], 5, "Amount", border=1, ln=True, align="C")

    # --- Items ---
    pdf.set_font(pdf.default_font, "", 12)
    line_height = 5

    # Store HSN/SAC codes for use in tax summary
    hsn_codes = []
    
    for i, item in enumerate(invoice_data["items"], start=1):
        # Store HSN code for tax summary
        hsn_codes.append(item['hsn'])
        
        # Check if we need a new page before adding each item
        if pdf.get_y() + 25 > pdf.page_break_trigger:
            pdf.add_page()
            # Re-add header for new page
            pdf.set_font(pdf.default_font, "B", 12)
            pdf.cell(col_widths[0], 5, "Sr. No.", border=1, align="C")
            pdf.cell(col_widths[1], 5, "Description of Goods", border=1, align="C")
            pdf.cell(col_widths[2], 5, "HSN/SAC", border=1, align="C")
            pdf.cell(col_widths[3], 5, "Quantity", border=1, align="C")
            pdf.cell(col_widths[4], 5, "Unit Rate", border=1, align="C")
            pdf.cell(col_widths[5], 5, "Amount", border=1, ln=True, align="C")
            pdf.set_font(pdf.default_font, "", 12)
            
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # Description cell (multi-line)
        pdf.set_xy(x_start + col_widths[0], y_start)
        pdf.multi_cell(col_widths[1], line_height, item['description'], border="LRT", align="L")
        y_after_desc = pdf.get_y()
        
        row_height = y_after_desc - y_start
        
        # Other cells for the row WITH COMMA FORMATTING
        pdf.set_xy(x_start, y_start)
        pdf.multi_cell(col_widths[0], row_height, str(i), border="LRT", align="C")
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
        pdf.multi_cell(col_widths[2], row_height, item['hsn'], border="LRT", align="C")
        
        pdf.set_xy(x_start + sum(col_widths[:3]), y_start)
        pdf.multi_cell(col_widths[3], row_height, str(item['quantity']), border="LRT", align="C")
        
        pdf.set_xy(x_start + sum(col_widths[:4]), y_start)
        pdf.multi_cell(col_widths[4], row_height, f"{item['unit_rate']:,.2f}", border="LRT", align="R")  # Added comma formatting
        
        amount = item['quantity'] * item['unit_rate']
        pdf.set_xy(x_start + sum(col_widths[:-1]), y_start)
        pdf.multi_cell(col_widths[5], row_height, f"{amount:,.2f}", border="LRT", align="R")  # Added comma formatting

        pdf.set_xy(x_start, y_start + row_height)

    # --- ADD EMPTY PRODUCT TABLE ROW FOR SPACE ---
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    
    # Create an empty row with the same structure
    empty_row_height = 15  # Height for the empty space row
    
    pdf.set_xy(x_start, y_start)
    pdf.multi_cell(col_widths[0], empty_row_height, "", border="LRB", align="C")
    
    pdf.set_xy(x_start + col_widths[0], y_start)
    pdf.multi_cell(col_widths[1], empty_row_height, "", border="LRB", align="C")
    
    pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
    pdf.multi_cell(col_widths[2], empty_row_height, "", border="LRB", align="C")
    
    pdf.set_xy(x_start + sum(col_widths[:3]), y_start)
    pdf.multi_cell(col_widths[3], empty_row_height, "", border="LRB", align="C")
    
    pdf.set_xy(x_start + sum(col_widths[:4]), y_start)
    pdf.multi_cell(col_widths[4], empty_row_height, "", border="LRB", align="C")
    
    pdf.set_xy(x_start + sum(col_widths[:-1]), y_start)
    pdf.multi_cell(col_widths[5], empty_row_height, "", border="LRB", align="C")
    
    pdf.set_xy(x_start, y_start + empty_row_height)

    # Check if we need a new page before totals
    if pdf.get_y() + 60 > pdf.page_break_trigger:
        pdf.add_page()

# --- Totals WITH COMMA FORMATTING ---
    pdf.set_font(pdf.default_font, "B", 12)
    total_width = sum(col_widths[:5])
    pdf.ln(0.2)
    pdf.cell(total_width, 5, "Basic Amount", border=1, align="L")
    pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['basic_amount']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting
    
    pdf.cell(total_width, 5, "SGST @ 9%", border=1, align="L")
    pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['sgst']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting
    
    pdf.cell(total_width, 5, "CGST @ 9%", border=1, align="L")
    pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['cgst']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting
    
    # Add Round Off row if needed WITH COMMA FORMATTING
    round_off = invoice_data['totals']['final_amount'] - (invoice_data['totals']['basic_amount'] + invoice_data['totals']['sgst'] + invoice_data['totals']['cgst'])
    if round_off != 0:
        pdf.cell(total_width, 5, "Round Off", border=1, align="L")
        pdf.cell(col_widths[5], 5, f"{round_off:,.2f}", border=1, ln=True, align="R")  # Added comma formatting

    pdf.cell(total_width, 5, "Final Amount to be Paid", border=1, align="L")
    pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['final_amount']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting

    
    # --- Amount in Words ---
    # First set the position and draw the border
    pdf.cell(191, 5, "", border=1, ln=True)

    # Now go back and write the text with mixed formatting
    pdf.set_y(pdf.get_y() - 5)  # Move back up to the same line
    pdf.set_x(10)  # Starting X position

    # Write bold label
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(pdf.get_string_width("Amount Chargeable (in words): "), 5, "Amount Chargeable (in words): ", ln=0)

    # Write normal value
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(0, 5, invoice_data['totals']['amount_in_words'], ln=True)

    # Check if we need a new page before tax summary
    if pdf.get_y() + 60 > pdf.page_break_trigger:
        pdf.add_page()

    # --- Tax Summary Table ---
    pdf.set_font(pdf.default_font, "B", 12)
    
    # Main header
    pdf.cell(34, 10, "HSN/SAC", border="LRT", align="C")
    pdf.cell(34, 10, "Taxable Value", border="LRT", align="C")
    pdf.cell(60, 5, "Central Tax", border=1, align="C")
    pdf.cell(63, 5, "State Tax", border=1, ln=True, align="C")

    # Sub-header
    pdf.cell(34, 1, "", border="L", ln=False)
    pdf.cell(34, 1, "", border="L", ln=False)
    pdf.cell(30, 5, "Rate", border="L", align="C")
    pdf.cell(30, 5, "Amount", border="LR", align="C")
    pdf.cell(32, 5, "Rate", border="L", align="C")
    pdf.cell(31, 5, "Amount", border="LR", ln=True, align="C")

    pdf.set_font(pdf.default_font, "", 12)
    
    # Get the HSN code from the first item (assuming all items have same HSN)
    # If you have multiple HSN codes, you might want to aggregate them differently
    primary_hsn = hsn_codes[0] if hsn_codes else ""
    
    hsn_tax_value = sum(item['quantity'] * item['unit_rate'] for item in invoice_data["items"])
    hsn_sgst = hsn_tax_value * 0.09
    hsn_cgst = hsn_tax_value * 0.09
    
    # Data row - using the actual HSN code from products WITH COMMA FORMATTING
    pdf.cell(34, 5, primary_hsn, border=1, align="C")
    pdf.cell(34, 5, f"{hsn_tax_value:,.2f}", border=1, align="C")  # Added comma formatting
    pdf.cell(30, 5, "9%", border=1, align="C")
    pdf.cell(30, 5, f"{hsn_sgst:,.2f}", border=1, align="C")  # Added comma formatting
    pdf.cell(32, 5, "9%", border=1, align="C")
    pdf.cell(31, 5, f"{hsn_cgst:,.2f}", border=1, ln=True, align="C")  # Added comma formatting

    # Total row WITH COMMA FORMATTING
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(34, 5, "Total", border=1, align="C")
    pdf.cell(34, 5, f"{hsn_tax_value:,.2f}", border=1, align="C")  # Added comma formatting
    pdf.cell(30, 5, "", border=1, align="C")
    pdf.cell(30, 5, f"{hsn_sgst:,.2f}", border=1, align="C")  # Added comma formatting
    pdf.cell(32, 5, "", border=1, align="C")
    pdf.cell(31, 5, f"{hsn_cgst:,.2f}", border=1, ln=True, align="C")  # Added comma formatting
    
    # --- Amount in Words ---
    pdf.set_font(pdf.default_font, "B", 12)
    # Write just the label part in bold
    label_part = "Tax Amount (in words): "
    pdf.cell(pdf.get_string_width(label_part), 5, label_part, border="LTB", ln=0)

    pdf.set_font(pdf.default_font, "", 12)
    # Write the value part in normal font and complete the border
    value_part = invoice_data['totals']['tax_in_words']
    remaining_width = 189.7 - pdf.get_string_width(label_part)
    pdf.cell(remaining_width, 5, value_part, border="TRB", ln=True)
    
    # # Tax in words
    # pdf.set_font(pdf.default_font, "B", 10)
    # pdf.cell(191, 5, f"Tax Amount (in words): {invoice_data['totals']['tax_in_words']}", ln=True, border=1)

    # Check if we need a new page before footer content
    if pdf.get_y() + 80 > pdf.page_break_trigger:
        pdf.add_page()

        # --- Bank Details & Declaration (Side by Side) ---
    pdf.set_font(pdf.default_font, "B", 10)
    pdf.cell(95, 5, "Company's Bank Details", ln=0, border=1)
    pdf.cell(96, 5, "Declaration:", ln=1, border=1)

    # Save current Y position
    y_before = pdf.get_y()
    x_left = pdf.get_x()

    # --- Left column (Bank Details) ---
    bank_lines = [
        ("Bank Name", "IDFC FIRST"),
        ("Branch", "AHMEDABAD Shyamal Branch"),
        ("Account No", "88130420182"),
        ("IFS Code", "IDFB0040335")
    ]
    
    pdf.set_font(pdf.default_font, "", 10)
    
    # Fixed positions for perfect alignment
    label_start_x = x_left
    colon_x = label_start_x + 25  # Fixed position for all colons
    value_start_x = colon_x + 5   # Fixed position for values (after colon + space)
    
    # Draw bank details with perfectly aligned colons
    current_y = y_before
    for label, value in bank_lines:
        # Set position for label
        pdf.set_xy(label_start_x, current_y)
        pdf.set_font(pdf.default_font, "B", 10)
        pdf.cell(25, 5, label, border="L", ln=0)  # Fixed width for labels
        
        # Set position for colon (same X for all lines)
        pdf.set_xy(colon_x, current_y)
        pdf.cell(5, 5, ":", ln=0)  # Just the colon
        
        # Set position for value
        pdf.set_xy(value_start_x, current_y)
        pdf.set_font(pdf.default_font, "", 10)
        pdf.cell(50, 5, value, border="", ln=1)  # Remaining width for values
        
        current_y += 5
    
    y_after_left = current_y
    
    # --- Right column (Declaration) ---
    pdf.set_xy(x_left + 95, y_before)
    pdf.set_font(pdf.default_font, "", 10)
    pdf.multi_cell(96, 4, invoice_data['declaration'], border=1)
    y_after_right = pdf.get_y()
    
    # Set Y to the maximum of both columns
    max_y = max(y_after_left, y_after_right)
    pdf.set_y(max_y)

    # --- Signature Boxes (Side by Side) ---
    y_signature_start = pdf.get_y()

    # Left side - Buyer's Company Signature (Blank box for future use)
    pdf.set_font(pdf.default_font, "B", 10)
    pdf.cell(95, 6, "Buyer's Company Signature", border="LRT", ln=0, align="C")

    # Right side - Our Company Signature
    pdf.cell(96, 6, "For CM INFOTECH.", border="LR", ln=1, align="C")

    # Create the signature boxes with DIFFERENT heights
    left_signature_box_height = 33
    right_signature_box_height = 33

    # Left signature box (Buyer - Blank)
    pdf.set_font(pdf.default_font, "I", 10)
    pdf.set_text_color(128, 128, 128)

    # Check if buyer logo is available
    buyer_logo_file = invoice_data.get('buyer', {}).get('logo_file')

    if buyer_logo_file:
        try:
            # Add buyer logo at the top of the left box
            logo_width = 25
            logo_x = 10 + (95 - logo_width) / 2
            logo_y = pdf.get_y() + 4
            
            # Add buyer company logo
            pdf.image(buyer_logo_file, x=logo_x, y=logo_y, w=logo_width)
            
            # Add buyer company name below logo
            pdf.set_xy(10, logo_y + logo_width + 2)
            pdf.set_font(pdf.default_font, "B", 9)
            pdf.cell(95, 4, invoice_data['buyer']['name'], border=0, ln=1, align="C")
            
            # Add signature line and text
            pdf.set_xy(10, pdf.get_y() + 8)
            pdf.set_font(pdf.default_font, "", 9)
            pdf.cell(95, 4, "_________________________", border=0, ln=1, align="C")
            pdf.cell(95, 4, "Authorized Signatory", border=0, ln=1, align="C")
            
            # Draw the border around everything
            pdf.set_xy(10, y_signature_start + 6)
            pdf.cell(95, left_signature_box_height, "", border="LRB")
            
            # Update Y position after left box
            y_after_left_signature = y_signature_start + 6 + left_signature_box_height
            
        except Exception as e:
            st.warning(f"Could not add buyer logo: {e}")
            # Fallback without logo
            pdf.multi_cell(95, left_signature_box_height/5, "\n\n(Space for Buyer's Company\nStamp and Signature)", border="LRB", align="C")
            y_after_left_signature = pdf.get_y()
    else:
        # No buyer logo available, show original placeholder
        pdf.multi_cell(95, left_signature_box_height/5, "\n\n\n(Space for Buyer's Company\nStamp and Signature)", border="LRB", align="C")
        y_after_left_signature = pdf.get_y()

    # Right signature box (Our Company)
    pdf.set_xy(105, y_signature_start + 5)
    pdf.set_text_color(0, 0, 0)

    # Add stamp if available
    if stamp_file:
        try:
            stamp_width = 25
            stamp_x = 105 + (96 - stamp_width) / 2
            stamp_y = pdf.get_y() + 2
            pdf.image(stamp_file, x=stamp_x, y=stamp_y, w=stamp_width)
        except Exception as e:
            st.warning(f"Could not add stamp: {e}")

    # Position for the signature text in right box
    pdf.set_xy(105, y_signature_start + 10 + right_signature_box_height - 10)
    pdf.set_font(pdf.default_font, "B", 10)
    pdf.cell(96, 5, "Authorized Signatory", border=0, ln=True, align="C")

    # Draw border for right signature box
    pdf.set_xy(105, y_signature_start + 6)
    pdf.cell(96, right_signature_box_height, "", border="LRB")

    # Set Y position to continue after both signature boxes
    pdf.set_y(max(y_after_left_signature, y_signature_start + 6 + right_signature_box_height))

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
        try:
            self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
            self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
            self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
            self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
            self.default_font = "Calibri"
        except:
            self.default_font = "Helvetica"

        self.website_url = "https://cminfotech.com/"
    def header(self):
        self.ln(5)
        if self.page_no() == 1:
            # Logo (if available)
            self.ln(1)
            if self.logo_path and os.path.exists(self.logo_path):
                self.image(self.logo_path, x=155, y=8, w=50,link=self.website_url)
                # (self.logo_path, x=155, y=8, w=50)
                # (self.logo_path, x=160, y=5.5, w=45,link=self.website_url)
                # self.image(self.logo_path, x=150, y=10, w=40)
            self.ln(4)
            # Title
            self.set_font(self.default_font, "BU", 15)
            self.cell(0, 15, "PURCHASE ORDER", ln=True, align="C")
            self.ln(1)

            # PO info
            self.set_font(self.default_font, "", 12)
            # PO Number (right aligned)
            self.set_xy(140,33)
            self.multi_cell(60,4,
                            f"PO No: {self.sanitize_text(st.session_state.po_number)}\n"
                            f"Date: {self.sanitize_text(st.session_state.po_date)}")
            # self.cell(0, 8, f"PO No: {self.sanitize_text(st.session_state.po_number)}", ln=1, align='R')
            # # Date (right aligned, under PO Number)
            # self.cell(0, 8, f"Date: {self.sanitize_text(st.session_state.po_date)}", ln=0, align='R')
            # self.ln(4)

    def footer(self):
        # Position from bottom (same as invoice)
        self.set_y(-12)
        
        # Horizontal line
        # self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        # self.ln(2)
        
        # Footer content - Computer generated text
        # self.set_font("Helvetica", "I", 10)
        # self.cell(0, 4, "This is a Computer Generated Quotation", ln=True, align="C")
        
        # Company address
        self.set_font("Helvetica", "", 10)
        self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
        # Clickable contact info (same as invoice)
        self.set_font("Helvetica", "U", 10)
        self.set_text_color(0, 0, 255)  # Blue for links
        
        email1 = "info@cminfotech.com"
        phone_number = "+91 873 391 5721"
        website = "www.cminfotech.com"
        
        # Center the contact information
        contact_text = f"{email1} | {phone_number} | {website}"
        contact_width = self.get_string_width(contact_text)
        x_contact = (self.w - contact_width) / 2
        
        self.set_x(x_contact)
        self.cell(self.get_string_width(email1), 4, email1, link=f"mailto:{email1}")
        self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | "))
        self.cell(self.get_string_width(phone_number), 4, phone_number, link=f"tel:{phone_number}")
        self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | ") + self.get_string_width(phone_number) + self.get_string_width(" | "))
        self.cell(self.get_string_width(website), 4, website, link="https://www.cminfotech.com/")
        
        self.set_text_color(0, 0, 0)


    # def footer(self):
    #     self.set_y(-18)
    #     self.set_font(self.default_font, "", 10)
    #     self.multi_cell(0, 4, "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n", align="C")
    #     self.set_text_color(0, 0, 255)
    #     self.set_font(self.default_font, "U", 10)
    #     # email1 = "cad@cmi.com"
    #     email1 = "info@cminfotech.com "
    #     phone_number =" +91 873 391 5721"
    #     self.set_text_color(0, 0, 255)
    #     self.cell(0, 4, f"{email1} | {phone_number}", ln=True, align="C", link=f"mailto:{email1}")
    #     self.set_x((self.w - 80) / 2)
    #     self.cell(0, 0, "", link=f"tel:{phone_number}")
    #     self.set_x((self.w - 60) / 2)
    #     website ="www.cminfotech.com"
    #     self.set_text_color(0, 0, 255)
    #     self.cell(60, 4, f"{website}", ln=True, align="C", link=website)
    #     self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.set_font(self.default_font, "B", 12)
        self.cell(0, 6, self.sanitize_text(title), ln=True)
        self.ln(1)

    def sanitize_text(self, text):
        return text.encode('ascii', 'ignore').decode('ascii')
def number_to_words(number):
    """Convert number to words"""
    try:
        from num2words import num2words
        return num2words(number, lang='en_IN').title() + " Rupees Only/-"
    except ImportError:
        # Simple fallback if num2words is not available
        words = f"Rupees {number:,.2f} Only/-"
        return words

# If you don't have num2words installed, you can install it with:
# pip install num2words
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
    sanitized_end_mobile = pdf.sanitize_text(po_data['end_mobile'])
    sanitized_end_email = pdf.sanitize_text(po_data['end_email'])
    sanitized_payment_terms = pdf.sanitize_text(po_data['payment_terms'])
    sanitized_delivery_terms = pdf.sanitize_text(po_data['delivery_terms'])
    sanitized_prepared_by = pdf.sanitize_text(po_data['prepared_by'])
    sanitized_authorized_by = pdf.sanitize_text(po_data['authorized_by'])
    sanitized_company_name = pdf.sanitize_text(po_data['company_name'])
    
    # # --- Vendor & Bill/Ship ---
    # pdf.set_font(pdf.default_font, "B", 12)
    # pdf.section_title("To:")
    # pdf.set_font(pdf.default_font, "B", 12)
    # pdf.multi_cell(95, 5, sanitized_vendor_name)
    # pdf.set_font(pdf.default_font, "", 12)
    # pdf.multi_cell(95, 5, f"{sanitized_vendor_address}\nKind Attend: {sanitized_vendor_contact}\nMobile: {sanitized_vendor_mobile}")
    # pdf.ln(5)
    # # pdf.set_xy(110, pdf.get_y() - 20)
    # # pdf.set_font(pdf.default_font, "B", 10)
    # pdf.multi_cell(70, 5, f"Bill To: \n{sanitized_bill_to_company}\n{sanitized_bill_to_address}")
    # pdf.set_xy(125, pdf.get_y() - 25)
    # pdf.multi_cell(0, 5, f"Ship To: \n{sanitized_ship_to_company}\n{sanitized_ship_to_address}")
    # pdf.ln(2)
    # pdf.multi_cell(0, 5, f"GST NO: {sanitized_gst_no}\nPAN NO: {sanitized_pan_no}\nMSME Registration No: {sanitized_msme_no}")
    # pdf.ln(2)
    # --- Vendor & Bill/Ship ---
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.section_title("To:")

    # Vendor Name (Bold)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.multi_cell(90, 5, sanitized_vendor_name)

    # Vendor Address (Normal)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(90, 5, sanitized_vendor_address)

    # Kind Attend: (Bold label + Normal value)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.write(5, "Kind Attend: ")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(95, 5, sanitized_vendor_contact)

    # Mobile: (Bold label + Normal value)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.write(5, "Mobile: ")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(95, 5, sanitized_vendor_mobile)

    pdf.ln(5)

    # Save current Y position
    start_y = pdf.get_y()

    # --- BILL TO (Left Side) ---
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(90, 5, "Bill To:", ln=1)
    # pdf.set_x(10)

    # Bill To - Company Name in Bold
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.multi_cell(90, 5, sanitized_bill_to_company)

    # Bill To - Address in Normal
    # pdf.set_x(10)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(90, 5, sanitized_bill_to_address)

    # Get Y position after Bill To
    y_after_bill = pdf.get_y()

    # --- SHIP TO (Right Side) ---
    pdf.set_xy(110, start_y)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(90, 5, "Ship To:", ln=1)
    pdf.set_x(110)

    # Ship To - Company Name in Bold
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.multi_cell(90, 5, sanitized_ship_to_company)

    # Ship To - Address in Normal
    pdf.set_x(110)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(90, 5, sanitized_ship_to_address)

    # Get Y position after Ship To
    y_after_ship = pdf.get_y()

    # Set to the maximum Y position
    pdf.set_y(max(y_after_bill, y_after_ship))
    pdf.ln(2)
    # GST NO:
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.write(5, "GST NO: ")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, sanitized_gst_no)

    # PAN NO:
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.write(5, "PAN NO: ")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, sanitized_pan_no)

    # MSME Registration No:
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.write(5, "MSME Registration No: ")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, sanitized_msme_no)

    pdf.ln(2)
#  --- Products Table ---
    col_widths = [65, 22, 30, 25, 15, 22]
    headers = ["Product", "Basic", "GST TAX @ 18%", "Per Unit Price", "Qty.", "Total"]
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font(pdf.default_font, "B", 12)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 6, pdf.sanitize_text(h), border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font(pdf.default_font, "", 12)
    line_height = 5

    # Calculate total from all products
    products_total = 0
    for p in po_data["products"]:
        gst_amt = p["basic"] * p["gst_percent"] / 100
        per_unit_price = p["basic"] + gst_amt
        total = per_unit_price * p["qty"]
        products_total += total

    # Calculate round off to make final amount whole number
    rounded_total = round(products_total)
    round_off = rounded_total - products_total

    # Now display the products table WITH COMMA FORMATTING
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
        pdf.cell(col_widths[1], row_height, f"{p['basic']:,.2f}", border=1, align="R")  # Added comma formatting
        pdf.cell(col_widths[2], row_height, f"{gst_amt:,.2f}", border=1, align="R")    # Added comma formatting
        pdf.cell(col_widths[3], row_height, f"{per_unit_price:,.2f}", border=1, align="R")  # Added comma formatting
        pdf.cell(col_widths[4], row_height, f"{p['qty']:.2f}", border=1, align="C")
        pdf.cell(col_widths[5], row_height, f"{total:,.2f}", border=1, align="R")      # Added comma formatting
        pdf.ln(row_height)

    # Round Off Row WITH COMMA FORMATTING
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(sum(col_widths[:-1]), 6, "Round Off", border=1, align="R")
    pdf.cell(col_widths[5], 6, f"{round_off:,.2f}", border=1, align="R")  # Added comma formatting
    pdf.ln()

    # Grand Total Row WITH COMMA FORMATTING
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(sum(col_widths[:-1]), 6, "Final Amount to be Paid", border=1, align="R")
    pdf.cell(col_widths[5], 6, f"{rounded_total:,.2f}", border=1, align="R")  # Added comma formatting
    pdf.ln(4)

    # --- Amount in Words ---
    pdf.ln(5)
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 4, "Amount in Words")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 4, pdf.sanitize_text(po_data['amount_words']))
    # pdf.ln(2)

    # --- Terms & Conditions ---
    # pdf.section_title("Terms & Conditions")
    pdf.set_font(pdf.default_font, "B", 12)

    # Taxes
    pdf.cell(45, 5, "Taxes")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"As specified above")

    # Payment
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 5, "Payment")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"{sanitized_payment_terms}")

    # Delivery
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 5, "Delivery")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"{sanitized_delivery_terms}")

    pdf.ln(2)

    # --- End User ---
    pdf.section_title("End User Details")
    pdf.set_font(pdf.default_font, "", 12)

    # Company Name
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 5, "Company Name")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"{sanitized_end_company}")

    # Company Address
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 5, "Company Address")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"{sanitized_end_address}")
    # Authorization Section

    # Contact
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 5, "Contact")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"{sanitized_end_person}")

    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 5, "Mobile No:")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"{sanitized_end_mobile}")

    # Email
    pdf.set_font(pdf.default_font, "B", 12)
    pdf.cell(45, 5, "Email")
    pdf.cell(5, 4, ":")
    pdf.set_font(pdf.default_font, "", 12)
    pdf.multi_cell(0, 5, f"{sanitized_end_email}")

    # pdf.ln(2)
    # pdf.set_font(pdf.default_font, "B", 12)
    # pdf.cell(45, 5, "Authorized By")
    # pdf.cell(5, 4, ":")
    # pdf.set_font(pdf.default_font, "", 12)
    # pdf.multi_cell(0, 5, f"{sanitized_authorized_by}")
    

    # --- Footer (Company Name + Stamp) that floats) ---
    pdf.ln(5)
    pdf.set_font(pdf.default_font, "", 12)
    pdf.cell(0, 5, f"For, {sanitized_company_name}", ln=True, border=0, align="L")
    stamp_path = os.path.join(os.path.dirname(__file__), "stamp.jpg")
    if os.path.exists(stamp_path):
        pdf.ln(2)
        pdf.image(stamp_path, x=pdf.get_x(), y=pdf.get_y(), w=25)
        pdf.ln(15)

    pdf_bytes = pdf.output(dest="S").encode('latin-1')
    return pdf_bytes

# --- Utility to safely get string from session_state ---
def safe_str_state(key, default=""):
    """Ensure session_state value exists and is always a string."""
    if key not in st.session_state or not isinstance(st.session_state[key], str):
        st.session_state[key] = str(default)
    return st.session_state[key] 

# --- Image Management Functions ---
def safe_image_path(image_path, default_name):
    """Safely handle image paths, return None if file doesn't exist"""
    if image_path and os.path.exists(image_path):
        return image_path
    else:
        st.sidebar.warning(f"⚠ {default_name} not found")
        return None

def load_images_from_github():
    """Download images from GitHub"""
    logo_path = None
    stamp_path = None
    
    try:
        # Download logo
        logo_response = requests.get(LOGO_URL, timeout=10)
        if logo_response.status_code == 200:
            logo_path = "github_logo.jpg"
            with open(logo_path, "wb") as f:
                f.write(logo_response.content)
        else:
            st.sidebar.warning(f"⚠ Could not load logo from GitHub (Status: {logo_response.status_code})")
    except Exception as e:
        st.sidebar.warning(f"⚠ Logo download failed: {str(e)}")
    
    try:
        # Download stamp
        stamp_response = requests.get(STAMP_URL, timeout=10)
        if stamp_response.status_code == 200:
            stamp_path = "github_stamp.jpg"
            with open(stamp_path, "wb") as f:
                f.write(stamp_response.content)
        else:
            st.sidebar.warning(f"⚠ Could not load stamp from GitHub (Status: {stamp_response.status_code})")
    except Exception as e:
        st.sidebar.warning(f"⚠ Stamp download failed: {str(e)}")
    
    return logo_path, stamp_path

def save_uploaded_file(uploaded_file, filename):
    """Save uploaded file to disk"""
    try:
        with open(filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filename
    except Exception as e:
        st.sidebar.error(f"Error saving {filename}: {str(e)}")
        return None

# --- The main function with Logo/Stamp Management ---
def main():
    st.set_page_config(page_title="Document Generator", page_icon="📑", layout="wide")
    st.title("📑 Document Generator - Invoice, PO & Quotation")

    # --- Logo and Stamp Configuration in Sidebar ---
    st.sidebar.header("📷 Company Branding")
    
    # Option 1: Use GitHub images
    use_github = st.sidebar.checkbox("Use GitHub Images", value=True, 
                                   help="Use logo and stamp from GitHub repository")
    
    # Option 2: Upload custom images
    uploaded_logo = None
    uploaded_stamp = None
    
    if not use_github:
        st.sidebar.subheader("Upload Custom Images")
        uploaded_logo = st.sidebar.file_uploader("Upload Company Logo", 
                                               type=["png", "jpg", "jpeg"], 
                                               key="global_logo")
        uploaded_stamp = st.sidebar.file_uploader("Upload Company Stamp", 
                                                type=["png", "jpg", "jpeg"], 
                                                key="global_stamp")
    
    # Load images based on selection
    global_logo_path = None
    global_stamp_path = None
    
    if use_github:
        with st.sidebar.status("Loading images from GitHub..."):
            global_logo_path, global_stamp_path = load_images_from_github()
            
            if global_logo_path:
                st.sidebar.success("✓ GitHub logo loaded")
            else:
                st.sidebar.error("❌ GitHub logo failed")
                
            if global_stamp_path:
                st.sidebar.success("✓ GitHub stamp loaded")
            else:
                st.sidebar.error("❌ GitHub stamp failed")
    else:
        if uploaded_logo:
            global_logo_path = save_uploaded_file(uploaded_logo, "custom_logo.jpg")
            if global_logo_path:
                st.sidebar.success("✓ Custom logo loaded")
        
        if uploaded_stamp:
            global_stamp_path = save_uploaded_file(uploaded_stamp, "custom_stamp.jpg")
            if global_stamp_path:
                st.sidebar.success("✓ Custom stamp loaded")
    
    # Display image status
    st.sidebar.subheader("Image Status")
    if global_logo_path:
        st.sidebar.info("Logo: ✅ Loaded")
    else:
        st.sidebar.error("Logo: ❌ Not available")
    
    if global_stamp_path:
        st.sidebar.info("Stamp: ✅ Loaded")
    else:
        st.sidebar.error("Stamp: ❌ Not available")

    # --- Initialize Session State ---
    # --- Initialize Session State ---
# Quotation session states
    if "quotation_seq" not in st.session_state:
        st.session_state.quotation_seq = get_current_quotation_sequence()
    if "quotation_products" not in st.session_state:
        st.session_state.quotation_products = []
    if "last_quotation_number" not in st.session_state:
        st.session_state.last_quotation_number = ""
    if "quotation_number" not in st.session_state:
        st.session_state.quotation_number = generate_quotation_number("SD", st.session_state.quotation_seq)
    if "current_quote_sales_person" not in st.session_state:
        st.session_state.current_quote_sales_person = "SD"

    # PO session states  
    if "po_seq" not in st.session_state:
        st.session_state.po_seq = get_current_po_sequence()
    if "products" not in st.session_state:
        st.session_state.products = []
    if "company_name" not in st.session_state:
        st.session_state.company_name = "CM INFOTECH"
    if "po_number" not in st.session_state:
        st.session_state.po_number = generate_po_number("CP", st.session_state.po_seq)
    if "po_date" not in st.session_state:
        st.session_state.po_date = datetime.date.today().strftime("%d-%m-%Y")
    if "last_po_number" not in st.session_state:
        st.session_state.last_po_number = ""
    if "current_po_sales_person" not in st.session_state:
        st.session_state.current_po_sales_person = "CP"
    if "current_po_quarter" not in st.session_state:
        st.session_state.current_po_quarter = get_current_quarter()

    # Invoice session states
    if "invoice_seq" not in st.session_state:
        st.session_state.invoice_seq = get_current_invoice_sequence()
    if "invoice_number" not in st.session_state:
        st.session_state.invoice_number = generate_invoice_number(st.session_state.invoice_seq)
    if "last_invoice_number" not in st.session_state:
        st.session_state.last_invoice_number = ""
    if "current_invoice_quarter" not in st.session_state:
        st.session_state.current_invoice_quarter = get_current_quarter()

    # Invoice buyer session states - ADDED
    if "invoice_buyer_company" not in st.session_state:
        st.session_state.invoice_buyer_company = "Baldridge & Associates Pvt Ltd."
    if "invoice_buyer_address" not in st.session_state:
        st.session_state.invoice_buyer_address = "406 Sakar East, Vadodara 390009"
    if "invoice_buyer_gst" not in st.session_state:
        st.session_state.invoice_buyer_gst = "24AAHCB9"
    if "invoice_buyer_mobile" not in st.session_state:
        st.session_state.invoice_buyer_mobile = "98987 91813"
    if "invoice_buyer_email" not in st.session_state:
        st.session_state.invoice_buyer_email = "dmistry@baseengr.com"
    
                #     st.session_state.invoice_buyer_mobile = enduser_data.get("mobile", "")
                # st.session_state.invoice_buyer_email = enduser_data.get("email", "")

    # Vendor session states
    if "po_vendor_name" not in st.session_state:
        st.session_state.po_vendor_name = "Arkance IN Pvt. Ltd."
    if "po_vendor_address" not in st.session_state:
        st.session_state.po_vendor_address = "Unit 801-802, 8th Floor, Tower 1..."
    if "po_vendor_contact" not in st.session_state:
        st.session_state.po_vendor_contact = "Ms/Mr"
    if "po_vendor_mobile" not in st.session_state:
        st.session_state.po_vendor_mobile = "+91 1234567890"
    if "po_gst_no" not in st.session_state:
        st.session_state.po_gst_no = "24ANMPP4891R1ZX"
    if "po_pan_no" not in st.session_state:
        st.session_state.po_pan_no = "ANMPP4891R"
    if "po_msme_no" not in st.session_state:
        st.session_state.po_msme_no = "UDYAM-GJ-01-0117646"

    # Quotation end user session states
    if "quote_end_company" not in st.session_state:
        st.session_state.quote_end_company = "Baldridge & Associates Pvt Ltd."
    if "quote_end_address" not in st.session_state:
        st.session_state.quote_end_address = "406 Sakar East, Vadodara 390009"
    if "quote_end_person" not in st.session_state:
        st.session_state.quote_end_person = "Mr. Dev"
    if "quote_end_mobile" not in st.session_state:
        st.session_state.quote_end_mobile = "1234567891"
    if "quote_end_email" not in st.session_state:
        st.session_state.quote_end_email = "info@company.com"
    if "quote_end_gst_no" not in st.session_state:
        st.session_state.quote_end_gst_no = "24AAHCB9"

    # PO end user session states - ADDED
    if "po_end_company" not in st.session_state:
        st.session_state.po_end_company = "Baldridge & Associates Pvt Ltd."
    if "po_end_address" not in st.session_state:
        st.session_state.po_end_address = "406 Sakar East, Vadodara 390009"
    if "po_end_person" not in st.session_state:
        st.session_state.po_end_person = "Mr. Dev"
    if "po_end_mobile" not in st.session_state:
        st.session_state.po_end_mobile = "1234567891"
    if "po_end_email" not in st.session_state:
        st.session_state.po_end_email = "info@company.com"
    if "po_end_gst_no" not in st.session_state:
        st.session_state.po_end_gst_no = "24AAHCB9"

    # PO bill to/ship to session states - ADDED
    if "po_bill_to_company" not in st.session_state:
        st.session_state.po_bill_to_company = "CM INFOTECH"
    if "po_bill_to_address" not in st.session_state:
        st.session_state.po_bill_to_address = "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481"
    if "po_ship_to_company" not in st.session_state:
        st.session_state.po_ship_to_company = "CM INFOTECH"
    if "po_ship_to_address" not in st.session_state:
        st.session_state.po_ship_to_address = "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481"

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
        def safe_strip(value):
            """Safely convert any value to string and strip whitespace."""
            try:
                if pd.isna(value):
                    return ""
                return str(value).split(".")[0].strip()
            except Exception:
                return ""

        vendor_mobile = safe_strip(vendor.get("Mobile", ""))
        End_user_mobile = safe_strip(end_user.get("End Mobile", ""))

        # Save to session_state (so Invoice & PO can use)
        st.session_state.po_vendor_name = vendor["Vendor Name"]
        st.session_state.po_vendor_address = vendor["Vendor Address"]
        st.session_state.po_vendor_contact = vendor["Contact Person"]
        st.session_state.po_vendor_mobile = vendor_mobile
        st.session_state.po_end_company = end_user["End User Company"]
        st.session_state.po_end_address = end_user["End User Address"]
        st.session_state.po_end_person = end_user["End User Contact"]
        st.session_state.po_end_mobile = End_user_mobile
        st.session_state.po_end_email = end_user["End User Email"]
        st.session_state.po_end_gst_no = end_user["GST NO"]

        st.info("Vendor & End User details auto-filled from Excel ✅")

    # Create tabs for different document types
    tab1, tab2, tab3 = st.tabs(["Quotation Generator", "Purchase Order Generator", "Tax Invoice Generator"])

    # --- Tab 1: Quotation Generator ---
    with tab1:
        st.header("📑 Quotation Generator")
        
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
            if st.session_state.last_quotation_number:
                try:
                    last_prefix, last_sales_person, last_quarter, last_date, last_year_range, last_sequence = parse_quotation_number(st.session_state.last_quotation_number)
                    
                    if last_sales_person == sales_person and last_quarter == current_quarter:
                        next_sequence = get_next_sequence_number(st.session_state.last_quotation_number)
                        return generate_quotation_number(sales_person, next_sequence)
                    else:
                        return generate_quotation_number(sales_person, 1)
                except:
                    return generate_quotation_number(sales_person, st.session_state.quotation_seq)
            else:
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
            
            # REPLACE VENDOR DROPDOWN WITH END USER DROPDOWN
            selected_enduser_quote = st.selectbox(
                "Select Company", 
                options=get_enduser_dropdown_options(),
                key="enduser_dropdown_quote"
            )
            
            # UPDATE END USER FIELDS WHEN DROPDOWN SELECTION CHANGES FOR QUOTATION
            if selected_enduser_quote and selected_enduser_quote != "Select End User":
                enduser_data = END_USER_DATABASE.get(selected_enduser_quote, {})
                st.session_state.quote_end_company = selected_enduser_quote
                st.session_state.quote_end_address = enduser_data.get("address", "")
                st.session_state.quote_end_person = enduser_data.get("contact", "")
                st.session_state.quote_end_mobile = enduser_data.get("mobile", "")
                st.session_state.quote_end_email = enduser_data.get("email", "")
                st.session_state.quote_end_gst_no = enduser_data.get("gst_no", "")
            
            # UPDATE TEXT INPUT FIELDS TO USE END USER DATA INSTEAD OF VENDOR DATA
            vendor_name = st.text_input("Company Name", 
                                    value=st.session_state.get("quote_end_company", "Baldridge & Associates Pvt Ltd."), 
                                    key="quote_end_company")
            vendor_address = st.text_area("Company Address", 
                                        value=st.session_state.get("quote_end_address", "406 Sakar East, Vadodara 390009"), 
                                        key="quote_end_address")
            vendor_email = st.text_input("Email", 
                                    value=st.session_state.get("quote_end_email", "info@company.com"), 
                                    key="quote_end_email")
            vendor_contact = st.text_input("Contact Person (Kind Attention)", 
                                        value=st.session_state.get("quote_end_person", "Mr. Dev"), 
                                        key="quote_end_person")
            vendor_mobile = st.text_input("Mobile", 
                                        value=st.session_state.get("quote_end_mobile", "1234567891"), 
                                        key="quote_end_mobile")
            
            # You can also add GST field if needed
            vendor_gst = st.text_input("GST No (Optional)", 
                                    value=st.session_state.get("quote_end_gst_no", ""), 
                                    key="quote_end_gst_no")

            st.header("Quotation Details")
            price_validity = st.text_input("Price Validity", "10 days from Quotation date", key="quote_price_validity")
            subject_line = st.text_input("Subject", "Proposal for Adobe Commercial Software License", key="quote_subject")
            intro_paragraphs_1 = st.text_area("Introduction Paragraph",
            """This is with reference to your requirement for Adobe Software. It gives us great pleasure to know that we are being considered by you and are invited to fulfill the requirements of your organization. """,
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
            
            # --- SAME PRODUCT SELECTION LOGIC AS PO ---
            st.subheader("Add Products")
            selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="quote_product_select_catalog")
            
            if st.button("➕ Add Selected Product", key="quote_add_selected_product"):
                if selected_product:
                    details = PRODUCT_CATALOG[selected_product]
                    st.session_state.quotation_products.append({
                        "name": selected_product,
                        "basic": details["basic"],
                        "gst_percent": details["gst_percent"],
                        "qty": 1.0,
                    })
                    st.success(f"{selected_product} added!")
            
            if st.button("➕ Add Empty Product", key="quote_add_empty_product"):
                st.session_state.quotation_products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

            # Display current products with EDITABLE fields (same as PO)
            st.subheader("Current Products")
            for i, p in enumerate(st.session_state.quotation_products):
                with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
                    st.session_state.quotation_products[i]["name"] = st.text_input("Name", p["name"], key=f"quote_name_{i}")
                    st.session_state.quotation_products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"quote_basic_{i}")
                    st.session_state.quotation_products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"quote_gst_{i}")
                    st.session_state.quotation_products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"quote_qty_{i}")
                    if st.button("Remove", key=f"quote_remove_{i}"):
                        st.session_state.quotation_products.pop(i)
                        st.rerun()
        
        # Preview and Generate Section
        st.header("Preview & Generate Quotation")
        
        # Show the current quotation number prominently with sales person info
        st.info(f"**Quotation Number:** {st.session_state.quotation_number}")
        st.info(f"**Sales Person:** {current_sales_person_info['name']} ({sales_person}) - {current_sales_person_info['email']}")
        
        # Calculate totals
        totals = calculate_quotation_totals(st.session_state.quotation_products)
        
        # Preview and totals calculation (same as PO)
        total_base = sum(p["basic"] * p["qty"] for p in st.session_state.quotation_products)
        total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.quotation_products)
        grand_total = total_base + total_gst
        amount_words = num2words(grand_total, to="currency", currency="INR").title()
        
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("Total Base Amount", f"₹{total_base:,.2f}")
        with col4:
            st.metric("Total GST", f"₹{total_gst:,.2f}")
        with col5:
            st.metric("Grand Total", f"₹{grand_total:,.2f}")
        
        # Use global images
        st.subheader("Company Branding")
        st.info("Using global logo and stamp from sidebar settings")
        logo_path = global_logo_path
        stamp_path = global_stamp_path

        if not logo_path:
            st.warning("⚠ No company logo available")
        if not stamp_path:
            st.warning("⚠ No company stamp available")
        
        if st.button("Generate Quotation PDF", type="primary", use_container_width=True, key="generate_quote"):
            if not st.session_state.quotation_products:
                st.error("Please add at least one product to generate the quotation.")
            else:
                # Calculate total from all products (same as PO logic)
                products_total = 0
                for p in st.session_state.quotation_products:
                    gst_amt = p["basic"] * p["gst_percent"] / 100
                    per_unit_price = p["basic"] + gst_amt
                    total = per_unit_price * p["qty"]
                    products_total += total

                # Calculate round off to make final amount whole number (same as PO)
                rounded_total = round(products_total)
                round_off = rounded_total - products_total

                # Update grand_total and amount_words with rounded amount
                grand_total = rounded_total
                amount_words = number_to_words(rounded_total)

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
                    "round_off": round_off,
                    "amount_words": amount_words,
                    "subject": subject_line,
                    "intro_paragraph": intro_paragraphs_1,
                    "product_name": selected_product if selected_product else "Software",   
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
                        next_sequence = get_next_quotation_sequence()
                        st.session_state.quotation_seq = next_sequence
                    
                    st.success("✅ Quotation generated successfully!")
                    st.info(f"📧 Sales Person: {current_sales_person_info['name']}")
                    
                    # Download button
                    st.download_button(
                        "⬇ Download Quotation PDF",
                        data=pdf_bytes,
                        file_name=f"{vendor_name}_{st.session_state.quotation_number.replace('/', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")

                
    # --- Tab 2: Purchase Order Generator ---
    with tab2:
        st.header("📑 Purchase Order Generator")
        
        today = datetime.date.today()
        current_quarter = get_current_quarter()
        
        # PO Settings in sidebar for this tab
        st.sidebar.header("PO Settings")
        
        # Sales Person Selection for PO
        po_sales_person = st.sidebar.selectbox("Select Sales Person", 
                                            options=list(SALES_PERSON_MAPPING.keys()), 
                                            format_func=lambda x: f"{x} - {SALES_PERSON_MAPPING[x]['name']}",
                                            key="po_sales_person_select")
        
        # Get current sales person info
        current_sales_person_info = SALES_PERSON_MAPPING.get(po_sales_person, SALES_PERSON_MAPPING['CP'])
        
        # Generate PO number based on selected sales person
        def get_po_number():
            if st.session_state.last_po_number:
                try:
                    last_prefix, last_sales_person, last_year, last_quarter, last_sequence = parse_po_number(st.session_state.last_po_number)
                    
                    if last_sales_person == po_sales_person and last_quarter == current_quarter:
                        next_sequence = get_next_sequence_number_po(st.session_state.last_po_number)
                        return generate_po_number(po_sales_person, next_sequence)
                    else:
                        return generate_po_number(po_sales_person, 1)
                except:
                    return generate_po_number(po_sales_person, st.session_state.po_seq)
            else:
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
            st.session_state.po_number = generate_po_number(po_sales_person, st.session_state.po_seq)
        
        # Display final PO number
        st.sidebar.code(st.session_state.po_number)
        
        po_auto_increment = st.sidebar.checkbox("Auto-increment Sequence", value=True, key="po_auto_increment_checkbox")
        
        if st.sidebar.button("Reset to Auto-generate", use_container_width=True, key="po_reset_auto_generate"):
            st.session_state.po_seq = 1
            st.session_state.last_po_number = ""
            st.session_state.po_number = get_po_number()
            st.sidebar.success("PO number reset to auto-generated")
            st.rerun()
        
        # Single tab with two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vendor & End User Details")
            
            # Vendor Selection
            selected_vendor = st.selectbox(
                "Select Vendor", 
                options=get_vendor_dropdown_options(),
                key="vendor_dropdown_po"
            )
            
            # Update vendor fields when dropdown selection changes
            if selected_vendor and selected_vendor != "Select Vendor":
                update_vendor_fields(selected_vendor)
            
            st.subheader("Vendor Details")
            vendor_name = st.text_input(
                "Vendor Name",
                value=st.session_state.get("po_vendor_name", "Arkance IN Pvt. Ltd."),
                key="po_vendor_name"
            )
            vendor_address = st.text_area(
                "Vendor Address",
                value=st.session_state.get("po_vendor_address", "Unit 801-802, 8th Floor, Tower 1..."),
                key="po_vendor_address"
            )
            vendor_contact = st.text_input(
                "Contact Person",
                value=st.session_state.get("po_vendor_contact", "Ms/Mr"),
                key="po_vendor_contact"
            )
            vendor_mobile = st.text_input(
                "Mobile",
                value=st.session_state.get("po_vendor_mobile", "+91 1234567890"),
                key="po_vendor_mobile"
            )
            
            st.subheader("End User Details")
            
            # End User Dropdown
            selected_enduser = st.selectbox(
                "Select End User", 
                options=get_enduser_dropdown_options(),
                key="enduser_dropdown_po"
            )
            
            # Update end user fields when dropdown selection changes
            if selected_enduser and selected_enduser != "Select End User":
                update_enduser_fields(selected_enduser)
            
            end_company = st.text_input(
                "End User Company",
                value=st.session_state.get("po_end_company", "Baldridge & Associates Pvt Ltd."),
                key="po_end_company"
            )
            end_address = st.text_area(
                "End User Address",
                value=st.session_state.get("po_end_address", "406 Sakar East, Vadodara 390009"),
                key="po_end_address"
            )
            end_person = st.text_input(
                "End User Contact",
                value=st.session_state.get("po_end_person", "Mr. Dev"),
                key="po_end_person"
            )
            end_mobile = st.text_input(
                "End Mobile",
                value=str(st.session_state.get("po_end_mobile", "1234567891") or "").strip(),
                key="po_end_mobile"
            )
            end_email = st.text_input(
                "End User Email",
                value=st.session_state.get("po_end_email", "info@company.com"),
                key="po_end_email"
            )
            
            # Products Section under End User
            st.subheader("Products")
            selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="po_product_select_catalog")
            
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                if st.button("➕ Add Selected Product", key="po_add_selected_product", use_container_width=True):
                    if selected_product:
                        details = PRODUCT_CATALOG[selected_product]
                        st.session_state.products.append({
                            "name": selected_product,
                            "basic": details["basic"],
                            "gst_percent": details["gst_percent"],
                            "qty": 1.0,
                        })
                        st.success(f"{selected_product} added!")
                        st.rerun()
            with col_add2:
                if st.button("➕ Add Empty Product", key="po_add_empty_product", use_container_width=True):
                    st.session_state.products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})
                    st.rerun()

            # Display products
            for i, p in enumerate(st.session_state.products):
                with st.expander(f"Product {i+1}: {p['name']}", expanded=True):
                    col_prod1, col_prod2, col_prod3, col_prod4 = st.columns([3, 2, 2, 1])
                    with col_prod1:
                        st.session_state.products[i]["name"] = st.text_input("Name", p["name"], key=f"po_name_{i}")
                    with col_prod2:
                        st.session_state.products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"po_basic_{i}")
                    with col_prod3:
                        st.session_state.products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"po_gst_{i}")
                    with col_prod4:
                        st.session_state.products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"po_qty_{i}")
                    if st.button("Remove", key=f"po_remove_{i}", use_container_width=True):
                        st.session_state.products.pop(i)
                        st.rerun()

        with col2:
            st.subheader("Company & Tax Details")
            
            # Company Details
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
                value=st.session_state.get("po_gst_no", "24ANMPP4891R1ZX"),
                key="po_gst_no_input"
            )
            pan_no = st.text_input(
                "PAN No",
                value=st.session_state.get("po_pan_no", "ANMPP4891R"),
                key="po_pan_no_input"
            )
            msme_no = st.text_input(
                "MSME No",
                value=st.session_state.get("po_msme_no", "UDYAM-GJ-01-0117646"),
                key="po_msme_no_input"
            )
            
            # Terms & Authorization
            st.subheader("Terms & Authorization")
            payment_terms = st.text_input("Payment Terms", "30 Days from Invoice date.", key="po_payment_terms_input")
            delivery_days = st.number_input("Delivery (Days)", min_value=1, value=2, key="po_delivery_days_input")
            delivery_terms = st.text_input("Delivery Terms", f"Within {delivery_days} Days.", key="po_delivery_terms_input")
            prepared_by = st.text_input("Prepared By", "Finance Department", key="po_prepared_by_input")
            authorized_by = st.text_input("Authorized By", "CM INFOTECH", key="po_authorized_by_input")
            
            # Preview & Generate Section under Terms & Authorization
            st.subheader("Preview & Generate")
            
            # Show the current PO number prominently with sales person info
            st.info(f"**PO Number:** {st.session_state.po_number}")
            st.info(f"**Sales Person:** {current_sales_person_info['name']} ({po_sales_person}) - {current_sales_person_info['email']}")
            
            total_base = sum(p["basic"] * p["qty"] for p in st.session_state.products)
            total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.products)
            grand_total = total_base + total_gst
            amount_words = num2words(grand_total, to="currency", currency="INR").title()
            st.metric("Grand Total", f"₹{grand_total:,.2f}")

            # Use global logo
            logo_path = global_logo_path
            if not logo_path:
                st.warning("No company logo available. Please upload one in the sidebar.")
            
            if st.button("Generate PO", type="primary", key="po_generate_button", use_container_width=True):
                # Calculate total from all products
                products_total = 0
                for p in st.session_state.products:
                    gst_amt = p["basic"] * p["gst_percent"] / 100
                    per_unit_price = p["basic"] + gst_amt
                    total = per_unit_price * p["qty"]
                    products_total += total

                # Calculate round off to make final amount whole number
                rounded_total = round(products_total)
                round_off = rounded_total - products_total

                # Update grand_total and amount_words with rounded amount
                grand_total = rounded_total
                amount_words = number_to_words(rounded_total)

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
                    "end_mobile": end_mobile,
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
                    next_sequence = get_next_po_sequence()
                    st.session_state.po_seq = next_sequence

                st.success("Purchase Order generated!")
                st.info(f"📧 Sales Person: {current_sales_person_info['name']}")
                
                st.download_button(
                    "⬇ Download Purchase Order",
                    data=pdf_bytes,
                    file_name=f"{end_company}_{st.session_state.po_number.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
        # --- Tab 3: Tax Invoice Generator ---
        # --- Tab 3: Tax Invoice Generator ---
    # --- Tab 3: Tax Invoice Generator ---
        # --- Tab 3: Tax Invoice Generator ---
    with tab3:
    # Display company logo instead of text header
        if global_logo_path and os.path.exists(global_logo_path):
            col_logo, col_text = st.columns([1, 1])
            with col_logo:
                st.image(global_logo_path, width=100)
            with col_text:
                st.header("Tax Invoice Generator")
        else:
            st.header("Tax Invoice Generator")   
        
        today = datetime.date.today()
        current_quarter = get_current_quarter()
        
        # Invoice Settings in sidebar for this tab
        st.sidebar.header("Invoice Settings")
        
        # Generate invoice number - SIMPLER LOGIC THAT WORKS WITH EXISTING COUNTER
        def get_invoice_number():
            if st.session_state.last_invoice_number:
                try:
                    last_prefix, last_year_range, last_quarter, last_sequence = parse_invoice_number(st.session_state.last_invoice_number)
                    
                    if last_quarter == current_quarter:
                        next_sequence = get_next_sequence_number_invoice(st.session_state.last_invoice_number)
                        return generate_invoice_number(next_sequence)
                    else:
                        return generate_invoice_number(1)
                except:
                    return generate_invoice_number(st.session_state.invoice_seq)
            else:
                return generate_invoice_number(st.session_state.invoice_seq)
        
        # Initialize or update invoice number when quarter changes
        if "current_invoice_quarter" not in st.session_state:
            st.session_state.current_invoice_quarter = current_quarter
            st.session_state.invoice_number = get_invoice_number()
        
        # Update invoice number if quarter changes
        if st.session_state.get('current_invoice_quarter', '') != current_quarter:
            st.session_state.current_invoice_quarter = current_quarter
            st.session_state.invoice_number = get_invoice_number()
        
        # Display current quarter info
        st.sidebar.info(f"**Current Quarter:** {current_quarter}")
        
        # Show auto-generated breakdown
        try:
            prefix, year_range, quarter, sequence = parse_invoice_number(st.session_state.invoice_number)
            st.sidebar.success(f"**Auto-generated Invoice Number**")
            st.sidebar.info(f"**Format:** {year_range}/{quarter}/{sequence}")
        except:
            st.sidebar.warning("Could not parse invoice number")
        
        # Editable invoice number - SIMPLER VERSION
        st.sidebar.subheader("Invoice Number Editor")
        
        # Parse current invoice number for editing
        try:
            current_prefix, current_year_range, current_q, current_seq = parse_invoice_number(st.session_state.invoice_number)
            
            # Create editable components
            col1, col2, col3 = st.sidebar.columns([2, 2, 1])
            
            with col1:
                new_year_range = st.text_input("Year Range", value=current_year_range, key="invoice_year_edit")
            
            with col2:
                new_quarter = st.text_input("Quarter", value=current_q, key="invoice_quarter_edit")
            
            with col3:
                new_sequence = st.number_input("Sequence", 
                                            min_value=1, 
                                            value=int(current_seq), 
                                            step=1,
                                            key="invoice_seq_edit")
            
            # Construct new invoice number
            new_invoice_number = f"CMI/{new_year_range}/{new_quarter}/{new_sequence:02d}"
            
            # Update if changed
            if new_invoice_number != st.session_state.invoice_number:
                st.session_state.invoice_number = new_invoice_number
                
        except Exception as e:
            st.sidebar.error(f"Error parsing invoice number: {e}")
            st.session_state.invoice_number = generate_invoice_number(st.session_state.invoice_seq)
        
        # Display final invoice number
        st.sidebar.code(st.session_state.invoice_number)
        
        invoice_auto_increment = st.sidebar.checkbox("Auto-increment Sequence", value=True, key="invoice_auto_increment")
        
        if st.sidebar.button("Reset to Auto-generate", use_container_width=True, key="invoice_reset_auto_generate"):
            # DON'T reset the counter file - just use the next sequence
            next_sequence = get_next_invoice_sequence()
            st.session_state.invoice_seq = next_sequence
            st.session_state.last_invoice_number = ""
            st.session_state.invoice_number = generate_invoice_number(next_sequence)
            st.sidebar.success(f"Invoice number reset to next sequence: {next_sequence}")
            st.rerun()

        # Rest of your invoice tab code remains the same...
        col1, col2 = st.columns([1,1])
        with col1:
            st.subheader("Invoice Details")
            
            # Show the current invoice number prominently with sales person info
            st.info(f"**Invoice Number:** {st.session_state.invoice_number}")
            # st.info(f"**Sales Person:** {current_sales_person_info['name']} ({invoice_sales_person}) - {current_sales_person_info['email']}")
            
            # Use the session state invoice number
            invoice_no = st.text_input("Invoice No", st.session_state.invoice_number, key="invoice_number_input")
            # Rest of your code...
            invoice_date = st.text_input("Invoice Date", datetime.date.today().strftime("%d-%m-%Y"))
            Suppliers_Reference = st.text_input("Supplier's Reference", "NA")
            Others_Reference = st.text_input("Other's Reference", "NA")
            buyers_order_no = st.text_input("Buyer's Order No.", "Online")
            buyers_order_date = st.text_input("Buyer's Order Date", datetime.date.today().strftime("%d-%m-%Y"))
            dispatched_through = st.text_input("Dispatched Through", "Online")
            
            # Payment Terms
            payment_terms = st.text_input("Mode/Terms of Payment", "100% Advance with Purchase")
            
            terms_of_delivery = st.text_input("Terms of delivery", "Within Month")
            
            # Destination
            destination = st.text_input("Destination", "Vadodara")
            
            st.subheader("Seller Details")
            vendor_name = st.text_input("Seller Name", "CM INFOTECH")
            vendor_address = st.text_area("Seller Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur, Chenpur Road, Jagatpur Village, Ahmedabad - 382481")
            vendor_gst = st.text_input("Seller GST No.", "24ANMPP4891R1ZX")
            vendor_msme = st.text_input("Seller MSME Registration No.", "UDYAM-GJ-01-0117646")

        with col2:
            st.subheader("Buyer Details")
            
            # SIMPLE DROPDOWN LIKE QUOTATION TAB
            selected_enduser_invoice = st.selectbox(
                "Select Buyer", 
                options=get_enduser_dropdown_options(),
                key="enduser_dropdown_invoice"
            )
            
            # UPDATE BUYER FIELDS WHEN DROPDOWN SELECTION CHANGES - SIMPLE LIKE QUOTATION
            if selected_enduser_invoice and selected_enduser_invoice != "Select End User":
                enduser_data = END_USER_DATABASE.get(selected_enduser_invoice, {})
                st.session_state.invoice_buyer_company = selected_enduser_invoice
                st.session_state.invoice_buyer_address = enduser_data.get("address", "")
                st.session_state.invoice_buyer_mobile = enduser_data.get("mobile", "")
                st.session_state.invoice_buyer_email = enduser_data.get("email", "")
                st.session_state.invoice_buyer_gst = enduser_data.get("gst_no", "")
            
            # USE SESSION STATE VALUES IN TEXT INPUTS - SIMPLE LIKE QUOTATION
            buyer_name = st.text_input(
                "Buyer Name",
                value=st.session_state.get("invoice_buyer_company", "Baldridge & Associates Pvt Ltd."),
                key="invoice_buyer_company"
            )
            
            buyer_address = st.text_area(
                "Buyer Address",
                value=st.session_state.get("invoice_buyer_address", "406 Sakar East, Vadodara 390009"),
                key="invoice_buyer_address"
            )

            buyer_mobile = st.text_input(
                "Buyer mobile.",
                value=st.session_state.get("invoice_buyer_mobile", "98987 91813"),
                key="invoice_buyer_mobile"
            )
            buyer_email = st.text_input(
                "Buyer email.",
                value=st.session_state.get("invoice_buyer_email", "dmistry@baseengr.com"),
                key="invoice_buyer_email"
            )
            buyer_gst = st.text_input(
                "Buyer GST No.",
                value=st.session_state.get("invoice_buyer_gst", "24AAHCB9"),
                key="invoice_buyer_gst"
            )

            st.subheader("Products")
            items = []
            num_items = st.number_input("Number of Products", 1, 10, 1, key="invoice_num_items")
            for i in range(num_items):
                with st.expander(f"Product {i+1}"):
                    desc = st.text_area(f"Description {i+1}", "Autodesk BIM Collaborate Pro - Single-user\nCLOUD Commercial New Annual Subscription\nSerial #575-26831580\nContract #110004988191\nEnd Date: 17/04/2026", key=f"invoice_desc_{i}")
                    hsn = st.text_input(f"HSN/SAC {i+1}", "997331", key=f"invoice_hsn_{i}")
                    qty = st.number_input(f"Quantity {i+1}", 1.00, 100.00, 1.00, key=f"invoice_qty_{i}")
                    rate = st.number_input(f"Unit Rate {i+1}", 0.00, 100000000.00, 36500.00, key=f"invoice_rate_{i}")
                    rate = round(rate, 2)
                    items.append({"description": desc, "hsn": hsn, "quantity": qty, "unit_rate": rate})

            st.subheader("Declaration")
            declaration = st.text_area("Declaration", "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF NOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED FROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE")
            
            st.subheader("Company Branding")
            st.info("Using global logo and stamp from sidebar settings")
            logo_path = global_logo_path
            stamp_path = global_stamp_path

            if not logo_path:
                st.warning("⚠ No company logo available")
            if not stamp_path:
                st.warning("⚠ No company stamp available")
            
            st.subheader("Invoice Preview & Download")

            if st.button("Generate Invoice", key="generate_invoice_button"):
                # Get the current invoice number from session state (which includes manual edits)
                current_invoice_no = st.session_state.invoice_number
                
                # Parse the manually edited invoice number to get the sequence
                try:
                    prefix, year_range, quarter, sequence = parse_invoice_number(current_invoice_no)
                    manual_sequence = int(sequence)
                    
                    # UPDATE THE COUNTER FILE to match the manual sequence
                    with open(INVOICE_COUNTER_FILE, 'w') as f:
                        f.write(str(manual_sequence))
                    
                    # Update session state to reflect the new sequence
                    st.session_state.invoice_seq = manual_sequence
                    
                    st.success(f"✅ Invoice sequence updated to: {manual_sequence}")
                    
                except Exception as e:
                    st.error(f"Error parsing invoice number: {e}")
                
                # Now use the manually edited invoice number
                invoice_no = current_invoice_no
                
                # Rest of your invoice calculation code...
                # Calculate amounts with proper rounding like in PO generator
                basic_amount = round(sum(item['quantity'] * item['unit_rate'] for item in items), 2)
                sgst = round(basic_amount * 0.09, 2)
                cgst = round(basic_amount * 0.09, 2)
                final_amount_unrounded = basic_amount + sgst + cgst
                
                # ROUND TO WHOLE NUMBER LIKE PO GENERATOR
                final_amount = round(final_amount_unrounded)
                round_off = final_amount - final_amount_unrounded
                
                # Display calculated amounts for verification
                st.info(f"**Calculated Amounts:** Basic: ₹{basic_amount:.2f}, SGST: ₹{sgst:.2f}, CGST: ₹{cgst:.2f}, Final: ₹{final_amount:.2f}")
                if round_off != 0:
                    st.info(f"**Round Off:** ₹{round_off:.2f}")
                
                # Convert to words with proper Indian currency format
                def convert_to_indian_currency(amount):
                    """Convert amount to Indian currency words format"""
                    try:
                        # Split into rupees and paise
                        rupees = int(amount)
                        paise = round((amount - rupees) * 100)
                        
                        rupees_text = num2words(rupees, to='cardinal', lang='en_IN').title()
                        
                        if paise > 0:
                            paise_text = num2words(paise, to='cardinal', lang='en_IN').title()
                            return f"{rupees_text} Rupees And {paise_text} Paise Only/-"
                        else:
                            return f"{rupees_text} Rupees Only/-"
                            
                    except Exception as e:
                        return f"Amount: ₹{amount:.2f}"

                amount_in_words = convert_to_indian_currency(final_amount)
                tax_in_words = convert_to_indian_currency(round(sgst + cgst, 2))

                invoice_data = {
                    "invoice": {"invoice_no": invoice_no, "date": invoice_date},
                    "Reference": {"Suppliers_Reference": Suppliers_Reference, "Other": Others_Reference},
                    "vendor": {"name": vendor_name, "address": vendor_address, "gst": vendor_gst, "msme": vendor_msme},
                    "buyer": {"name": buyer_name, "address": buyer_address, "gst": buyer_gst, "mobile":buyer_mobile, "email":buyer_email},
                    "invoice_details": {
                        "buyers_order_no": buyers_order_no,
                        "buyers_order_date": buyers_order_date,
                        "dispatched_through": dispatched_through,
                        "payment_terms": payment_terms,
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
                    "declaration": declaration
                }

                pdf_file = create_invoice_pdf(invoice_data, logo_path, stamp_path)

                # Store the last invoice number for sequence tracking
                st.session_state.last_invoice_number = invoice_no
                
                # Auto-increment for next invoice - BUT RESPECT MANUAL SEQUENCE
                if invoice_auto_increment:
                    # Get the next sequence based on the manually set sequence
                    next_sequence = manual_sequence + 1
                    st.session_state.invoice_seq = next_sequence
                    
                    # Update the counter file for next time
                    with open(INVOICE_COUNTER_FILE, 'w') as f:
                        f.write(str(next_sequence))

                st.success("Invoice generated successfully!")
                
                st.download_button(
                    "⬇ Download Invoice PDF",
                    data=pdf_file,
                    file_name=f"{buyer_name}_{invoice_date}_{invoice_no.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    key="invoice_download_button")
                                
# Clean up temporary files
for path in ["github_logo.jpg", "github_stamp.jpg", "custom_logo.jpg", "custom_stamp.jpg"]:
    if os.path.exists(path):
        try:
            os.remove(path)
        except:
            pass

st.divider()
st.caption("© 2025 Document Generator - CM INFOTECH")

if __name__ == "__main__":
    main()
















# import streamlit as st
# from fpdf import FPDF
# import pandas as pd
# from num2words import num2words
# import datetime
# import io
# from PIL import Image
# import os
# from fpdf import FPDF, HTMLMixin
# import textwrap
# import html as _html 
# import requests  # Add this import for downloading from GitHub

# # GitHub Configuration - FIXED URLs
# LOGO_URL = "https://raw.githubusercontent.com/cmisales26/purchase-order-dashboard/main/logo_final.jpg"
# STAMP_URL = "https://raw.githubusercontent.com/cmisales26/purchase-order-dashboard/main/stamp.jpg"

# # --- Global Data and Configuration ---
# PRODUCT_CATALOG = {
#     "GstarCAD STDANDARD 2026 Perpetual": {"basic": 34777.0, "gst_percent": 18.0},
#     "GstarCAD STDANDARD 2026 One year upgrade": {"basic": 18303.0, "gst_percent": 18.0},
#     "GstarCAD STDANDARD 2026 Two year upgrade": {"basic": 18303.0, "gst_percent": 18.0},
#     "GstarCAD STDANDARD 2026 Three + year upgrade": {"basic": 22696.0, "gst_percent": 18.0},

#     "GstarCAD PROFESSIONAL 2026 Perpetual": {"basic": 46125.0, "gst_percent": 18.0},
#     "GstarCAD PROFESSIONAL 2026 One year upgrade": {"basic": 25625.0, "gst_percent": 18.0},
#     "GstarCAD PROFESSIONAL 2026 Two year upgrade": {"basic": 25625.0, "gst_percent": 18.0},
#     "GstarCAD PROFESSIONAL 2026 Three + year upgrade": {"basic": 30018.0, "gst_percent": 18.0},

#     "GstarCAD PLUS 2026 Perpetual": {"basic": 57107.0, "gst_percent": 18.0},
#     "GstarCAD PLUS 2026 One year upgrade": {"basic": 29286.0, "gst_percent": 18.0},
#     "GstarCAD PLUS 2026 Two year upgrade": {"basic": 32946.0, "gst_percent": 18.0},
#     "GstarCAD PLUS 2026 Three + year upgrade": {"basic": 41000.0, "gst_percent": 18.0},

#     "GstarCAD MECHANICAL 2025 Perpetual": {"basic": 92250.0, "gst_percent": 18.0},
#     "GstarCAD MECHANICAL 2025 One year upgrade": {"basic": 73214.0, "gst_percent": 18.0},
#     "GstarCAD MECHANICAL 2025 Two year upgrade": {"basic": 87857.0, "gst_percent": 18.0},
#     "GstarCAD MECHANICAL 2025 Three + year upgrade": {"basic": 105428.0, "gst_percent": 18.0},

#     "GstarCAD ARCHITECTURE 2021 Perpetual": {"basic": 92250.0, "gst_percent": 18.0},
#     "GstarCAD ARCHITECTURE 2021 One year upgrade": {"basic": 73214.0, "gst_percent": 18.0},
#     "GstarCAD ARCHITECTURE 2021 Two year upgrade": {"basic": 87857.0, "gst_percent": 18.0},
#     "GstarCAD ARCHITECTURE 2021 Three + year upgrade": {"basic": 105428.0, "gst_percent": 18.0},

#     "Archline.XP LT 2025 Perpetual": {"basic": 30450.0, "gst_percent": 18.0},
#     "Archline.XP LT Yearly Subscription": {"basic": 26617.0, "gst_percent": 18.0},

#     "Archline.XP Interior 2025 Perpetual": {"basic": 94500.0, "gst_percent": 18.0},
#     "Archline.XP Interior Yearly Subscription": {"basic": 70875.0, "gst_percent": 18.0},

#     "Archline.XP Professional 2025 Perpetual": {"basic": 126000.0, "gst_percent": 18.0},
#     "Archline.XP Professional Yearly Subscription": {"basic": 94500.0, "gst_percent": 18.0},

#     "Archline.XP MEP Module for LT 2025": {"basic": 30450.0, "gst_percent": 18.0},
#     "Archline.XP MEP Module Yearly Subscription": {"basic": 21000.0, "gst_percent": 18.0},

#     "Autodesk BIM Collaborate Pro - Single User Commercial Annual Subscription Renewal":{"basic":00.0,"gst_percent": 18.0},

#     "Creative cloud pro plus for Teams": {"basic": 114560.0, "gst_percent": 18.0},
#     "Creative cloud Pro for Teams": {"basic": 104560.0, "gst_percent": 18.0},
#     "Adobe Creative Cloud All Apps": {"basic": 95000.0, "gst_percent": 18.0},
#     "Adobe Acrobat Pro DC": {"basic": 25000.0, "gst_percent": 18.0},
#     "Adobe Substance 3D Collection": {"basic": 85000.0, "gst_percent": 18.0},
#     "Autodesk Commercial Software License": {"basic": 27500.0, "gst_percent": 18.0},
#     "Solidworks Premium": {"basic": 50000.0, "gst_percent": 18.0},
#     "Catia License": {"basic": 75000.0, "gst_percent": 18.0},
#     "Mastercam Module": {"basic": 30000.0, "gst_percent": 18.0},
#     "Siemens NX": {"basic": 65000.0, "gst_percent": 18.0},
# }

# # Vendor Database - You can expand this with more vendors
# VENDOR_DATABASE = {
#     "Arkance IN Pvt. Ltd.": {
#         "address": "One International Centre, Unit-801-802, 8th Floor, Tower-1, Senapati Bapat Marg Dadar West, Prabhadevi, Lower Parel,Mumbai - 400013,State : Maharashtra",
#         "contact": "Ms/Mr",
#         "mobile": "+91 9243493616",
#         "gst_no": "27AAACA7149L1Z2",
#         "pan_no": "AAACA7149L",
#         "msme_no": "UDYAM-MH-01-1234567"
#     },
#     "DIVTECH IT SOLUTION PVT. LTD.": {
#         "address": "Nr.kum kum party plot, TP 13, Chhani Jakatnaka, Vadodara -390024",
#         "contact": "Ms/Mr",
#         "mobile": "+91 9313158878",
#         "gst_no": "24ANMPP4891R1ZX",
#         "pan_no": "ANMPP4891R",
#         "msme_no": "UDYAM-GJ-01-0117646"
#     },
#     "ITCG Solutions Pvt. Ltd.": {
#         "address": "301, Earth The Landmark, Opp. Satsang Party Plot, Sun Pharma Road, Baroda,Gujarat, 390012,India",
#         "contact": "Ms/Mr",
#         "mobile": "+91 4045678901",
#         "gst_no": "36AABCA1234L1Z5",
#         "pan_no": "AABCA1234L",
#         "msme_no": "UDYAM-TS-01-7654321"
#     },
#     "Genesis Infoserve Pvt. Ltd.": {
#         "address": "A-204/205, Eversun CHSL., DLH Junction,Sahakar Nagar, J. P. Road, Andheri (W),Mumbai - 400 053",
#         "contact": "Ms/Mr",
#         "mobile": "022 62845600 / 022 26734433",
#         "gst_no": "29AABCA5678L1Z9",
#         "pan_no": "AABCA5678L",
#         "msme_no": "UDYAM-KA-01-9876543"
#     },
#         "MicroGenesis CADSoft Pvt.Ltd.": {
#         "address": "2nd Floor, 202, Bangashree Tower Co-Operative Housing Society, Daji Ramachandra Road, Charai, Thane, Maharashtra - 400601",
#         "contact": "Ms/Mr",
#         "mobile": "022 - 62233873",
#         "gst_no": "29AABCA5678L1Z9",
#         "pan_no": "AABCA5678L",
#         "msme_no": "UDYAM-KA-01-9876543"
#     },
#         "ACCELTY TECHSOLUTIONS LLP": {
#         "address": "603, Sai Plaza, Next To Sakinaka Telephone Exchange Andheri - Kurla Road,Mumbai - 400072",
#         "contact": "Ms/Mr",
#         "mobile": "+91 4045678901",
#         "gst_no": "29AABCA5678L1Z9",
#         "pan_no": "AABCA5678L",
#         "msme_no": "UDYAM-KA-01-9876543"
#     }
# }



# # End User Database - You can expand this with more end users
# END_USER_DATABASE = {
#     "Baldridge & Associates Structural Engineering Private Limited": {
#         "address": "406 Sakar East B/5 Gurunanak School, 40mt Tarsali danteshwar Ring Road, Vadodara",
#         "contact": "Mr. Divyesh Mistry ",
#         "mobile": "98987 91813",
#         "email": "dmistry@baseww.com",
#         "gst_no": "24AAHCB9936E1ZL"
#     },
#     "Creation Studio": {
#         "address": "Al-Habtula Apartment, Swk Society, Sid, Dah, Guja 389",
#         "contact": "Mr. Musta", 
#         "mobile": "+91 9876543210",
#         "email": "info@dreamcreationstudio.com",
#         "gst_no": "24AABCU9603R1ZN"
#     },
#     "Abhir Design": {
#         "address": "109-110, 3rd floor, Western plaza, Nr. Bhulka bhavan school,Adajan, Surat",
#         "contact": "Mr. Abhishek Ahir ", 
#         "mobile": "+91 79844 12954",
#         "email": "abhirdesign@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "AEC Chennai Private Limited ": {
#         "address": "No.16, 3rd Floor, 16th Street, 3rd Main Road, Nanganallur,Chennai",
#         "contact": "Mr.  M Anand", 
#         "mobile": "+91 9840411705",
#         "email": "aecltd@aecchennai.com",
#         "gst_no": "33AAXCA3635K1ZA"
#     },
#     "Artech Engineering Solutions": {
#         "address": "Office 909, 910, Bsquare 2, Ambli Rd, Vikram Nagar, Ahmedabad, Gujarat 380058",
#         "contact": "Ms. Avni Sikka", 
#         "mobile": "+91 9723433295",
#         "email": "admin@artechengs.com",
#         "gst_no": "24AGXPJ8384R1Z3"
#     },
#     "EDEN Design Consultants": {
#         "address": "1220, Sun Avenue One, Nr. Shreyas Foundation, Manekbaug Road, Ahmedabad",
#         "contact": "Mr. Sheel Shah ", 
#         "mobile": "+91 9909904905",
#         "email": "sheel.shah@edenconsultants.in",
#         "gst_no": "24CWEPS2125N2ZA"
#     },
#     "Falgun Engineering Enterprise": {
#         "address": "14, Shayona Ind. Estate, Nr. Panchratna Estate, Near Ramol Bridge, Ramol Chokadi, Vatva, Ahmedabad.",
#         "contact": "Mr. Falgun ", 
#         "mobile": "+91 98798 32610",
#         "email": "info@falgunengineering.com",
#         "gst_no": "24AFOPD1303E1Z6"
#     },
#     "Pankaj Dharkar & Associates": {
#         "address": "1506-507, Venus Amadeus, Jodhpur Cross Road, Satellite, Ahmedabad - 380015",
#         "contact": "Ms. Gitanjali Dharkar ", 
#         "mobile": "79-26924713/14",
#         "email": "ahmedabad@pdamepconsultants.com",
#         "gst_no": "24AASPD3817C1Z1"
#     },
#     "Pankaj M Patel Consultants Private Limited": {
#         "address": "303, Chakravarty Complex, Opp. Kiran Park Circle, Nawa Vadaj, Ahmedabad, Gujarat 380013",
#         "contact": "Mr. Pankaj Patel  ", 
#         "mobile": "+91 9825024024",
#         "email": "paai@pmpcplindia.com",
#         "gst_no": "24AAGCP8258E1ZB"
#     },
#     "Paradigm Engineering": {
#         "address": "B808, Titanium Business Park, Opp Palladium, Prahladnagar,Ahmedabad",
#         "contact": "Mr. Parth Mandge ", 
#         "mobile": "+91 9725211464",
#         "email": "info@theparadigmengineering.com",
#         "gst_no": "24ABAFP4967E1Z9"
#     },
#     "Parth Equipment Limited": {
#         "address": "Plot no 4208/4209, GIDC, phase -4, Behind New Nirma,Vatva, Ahmedabad",
#         "contact": "Mr Arth Shah ", 
#         "mobile": "+91 94276 16352",
#         "email": "purchase@parthequipment.com",
#         "gst_no": "24AAECP2939G1ZH"
#     },
#     "Shayona Consultant": {
#         "address": "7th Floor, The Capital 2, 701/702, Science City Rd, Sola, Ahmedabad, Gujarat 380060",
#         "contact": "Mr Prashant Parmar ", 
#         "mobile": "+91 9825398519",
#         "email": "shayonaconsultant@gmail.com",
#         "gst_no": "24ASJPP6439R1ZU"
#     },
#     "Shreeji Infotech": {
#         "address": "FF6/A Sambhavi Complex, Opp. Kamal Appartment, Nr.Chanakyapuri Overbridge, Ghatalodia, Ahmedabad",
#         "contact": "Mr Lalit", 
#         "mobile": "+91 9879586899",
#         "email": "lalit@shreejiinfotech.in",
#         "gst_no": "24AMLPP1118K1Z0"
#     },
#     "Stideck Technologies Private Limited": {
#         "address": "514, Pramukh Square, Gandhinagar, Gujarat",
#         "contact": "Mr Ravi Patel ", 
#         "mobile": "+91 9925007200",
#         "email": "info@strideck.com",
#         "gst_no": "24ABMCS6014J1Z7"
#     },
#     "MS PRABHAKAR B BHAGWAT": {
#         "address": "One 42,South Tower, 501, 5th floor, B/h Ashok Vatika, Nr. Jayantilal Park BRTS,  Ambli - Bopal Road, Ahmedabad - 380054",
#         "contact": "Mr Chetan Gajjar", 
#         "mobile": "+91 9979961972",
#         "email": "pbb-ahm@landscapeindia.net",
#         "gst_no": "24AAJFM1692D1ZF"
#     },
#     "VIZ KINGDOME": {
#         "address": "519, STC Spacelink, S. P. Ring Road, Ambli, Ahmedabad",
#         "contact": "Mr Kaushik Vadher", 
#         "mobile": "+91 9714554576",
#         "email": "info@vizkingdom.com",
#         "gst_no": "24AFGPV9879P1Z4"
#     },
#     "ARBIM Studdio Private Limited": {
#         "address": "Office 1007, B square 2, Ambli Road, Vikram Nagar,Ahmedabad, Gujarat",
#         "contact": "Mr Rajan Sikka ", 
#         "mobile": "+91 97234 33296",
#         "email": "info@thearbstudio.com",
#         "gst_no": "24AAXCA3395G1Z9"
#     },
#     "Hire 4 Higher Consulting": {
#         "address": "Olive Arcade, 302, 3rd floor, Opp. Samudra Annex, C G Road, Ahmedabad",
#         "contact": "Mr Shrijay Sheth ", 
#         "mobile": "+91 982 580 6008",
#         "email": "shrijay@hire4higherconsulting.com",
#         "gst_no": "24ASUPS2751A1ZO"
#     },
#     "Hrp Infra Private Limited": {
#         "address": "337, Yash Arian, Near Swamivivekand Circle, Memnagar,Ahmedabad",
#         "contact": "Mr Hiren Patel ", 
#         "mobile": "+91 8128293072",
#         "email": "hrpinfra@gmail.com",
#         "gst_no": "24AACCH8234N1ZC"
#     },
#     "Hydrevo Design": {
#         "address": "24-12, Tulsishyam Flats, Bhimjipura, New Wadaj, Ahmedabad ",
#         "contact": "Mr Hitesh Prajapati ", 
#         "mobile": "+91 91068 55837",
#         "email": "devansh3330@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Inspire Engineering Solutions": {
#         "address": "227, B-Wing, Thirthraj, Opp. VS Hospital, Ellizbridge,Ahmedabad",
#         "contact": "Mr Shivendra pal ", 
#         "mobile": "+91 8000049185",
#         "email": "info@inspireengs.com",
#         "gst_no": "24BPZPP5092J1Z0"
#     },
#     "iSolve Systems": {
#         "address": "FF14, Shubh Complex, Near Rajashtan Hospitals Shahibaug,Ahmedabad",
#         "contact": "Mr Biren", 
#         "mobile": "+91 8000499948",
#         "email": "biren.isolve@gmail.com",
#         "gst_no": "24BRNPM4686F1ZE"
#     },
#     "Khodiyar eSolutions LLP": {
#         "address": "6th Floor, 611, The Link,Near Vijay Cross Road, Drive In Road,Navrangpura, Ahmedabad,",
#         "contact": "Mr Nimesh Patel", 
#         "mobile": "+91 7203008200",
#         "email": "info@khodiyaresolutions.com",
#         "gst_no": "24AAWFK0871B1ZD"
#     },
#     "M/S. Sigma Steel Product": {
#         "address": "Survey No. 243, Kheda Dholka Highway, Chandana Gam,Kheda",
#         "contact": "Mr Rohit Jain", 
#         "mobile": "+91 9723117344",
#         "email": "sigmasteelproduct@gmail.com",
#         "gst_no": "24AYYPJ5776A1Z2"
#     },
#     "MU Architects ": {
#         "address": "3rd Floor, Union Hights, Opp. Rahul Raj Mall, Behind Lalbhai Contractor Staduim, Surat",
#         "contact": "Mr Ketan Solanki", 
#         "mobile": "+91 87582 73494",
#         "email": "info@designcore.co.in",
#         "gst_no": "24AAPFM2663Q1ZL"
#     },
#     "N H Architects ": {
#         "address": "911-912, I Square, Near Shukan Mall, Science City Road, Sola, Ahmedabad",
#         "contact": "Mr Hemal Desai", 
#         "mobile": "+91 9898196718",
#         "email": "nharchitects11@gmail.com",
#         "gst_no": "24AAMFN7983R1Z4"
#     },
#     "NFRAMEX Private Limited": {
#         "address": "B-722, North Plaza, Visat-Gandhinagar Hi-way, Motera,Ahmedabad",
#         "contact": "Mr Paresh Patel ", 
#         "mobile": "+91 8511333587",
#         "email": "support@nframex.com",
#         "gst_no": "24AAGCN8045F1ZI"
#     },
#     "Nymra Studios Private Limited": {
#         "address": "1517-RK Prime Near Silver Heights, Circle, 150 Feet Ring Rd,Nana Mava, Rajkot, Gujarat",
#         "contact": "Mr Divyesh Ghadiya ", 
#         "mobile": "+91 77118 84488",
#         "email": "info@nymra.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Office Way Automation": {
#         "address": "1, Ground Floor - Shila Appartment, Nr, Jhaju Hospital Nr. Ishwar Bhuvan Road, Navrangpura, Ahmedabad-380014",
#         "contact": "Mr Dipal Patwa ", 
#         "mobile": "+91 98254 14819",
#         "email": "info@patwaassociates.com",
#         "gst_no": "24ADZPP3655N1ZL"
#     },
#     "Patwa Associates": {
#         "address": "501,5th Floor,Sarthak-Ii Complex,Swastik Cross Road,Opp Honda Activa Show Room, Navrangpura,Ahmedabad",
#         "contact": "Mr Rupin ", 
#         "mobile": "+91 9898083240",
#         "email": "rupin@officewayautomation.com",
#         "gst_no": "24AVLPB0206D1ZG"
#     },
#     "Phoenix Interio": {
#         "address": "304-Entice, Jayantilal Park Ambli - Bopal Road, Ahmedabad,",
#         "contact": "Mr Jigar  Mehta ", 
#         "mobile": "+91 9824254646",
#         "email": "jigar@phoenixinterio.net",
#         "gst_no": "24ACEPM6631K2ZI"
#     },
#     "Plutomen Technologies Private Limited": {
#         "address": "503, 5th Floor, Venus Atlantis, Anandnagar Road, Prahladnagar, Satellite, Ahmedabad",
#         "contact": "Mr Keyur Balawat ", 
#         "mobile": "+91 99797 65418",
#         "email": "keyur@pluto-men.com",
#         "gst_no": "24AAICP8643B1ZI"
#     },
#     "Setu Infrastructure": {
#         "address": "D 701-704 The First, Behind Keshav Baug Party Plot, Judges Bungtow Road, Vastrapur, Ahmedabad",
#         "contact": "Mr Niyat Patel ", 
#         "mobile": "079-40037661",
#         "email": "setuinf@gmail.com",
#         "gst_no": "24AARFS2603Q1ZP"
#     },
#     "Sulemans Design Studio": {
#         "address": "Office No. 5, Ground Floor, Riddhi Siddhi Arcade-2, Sector-8,Gandhidham",
#         "contact": "Mr Shaad Khatri  ", 
#         "mobile": "+91 94293 41954",
#         "email": "khatrishaads@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "U Design Studio ": {
#         "address": "405, Kairos, Opposite Mahatma Gandhi Labour Institute,Memnagar, Ahmedabad",
#         "contact": "Mr Pratik Soni ", 
#         "mobile": "+91 9909419309",
#         "email": "sonipratik1983@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Yash Constuction": {
#         "address": "415, Sun Avenue One Opposite Royal Enfield Showroom Shyamal-Manekbaug Road, Shyamal Cross Road",
#         "contact": "Mr.Umang Joshi ", 
#         "mobile": "+91 99798 42723",
#         "email": "yashconstruction415@gmail.com",
#         "gst_no": "24AOCPJ5088D1Z5"
#     },
#     "Abacus Technocrats Private Limited": {
#         "address": "1001, Sears Tower, Panchwati, Near Gulbai Tekra, Ahmedabad",
#         "contact": "Mr. Jaykishan Makwana ", 
#         "mobile": "+91 9898159709",
#         "email": "abacus.epc@gmail.com",
#         "gst_no": "24AAECA7755P1Z5"
#     },
#     "Accurate PMS Private Limited": {
#         "address": "H-13-16, Sumel Business Park-6 Dudheshwar Road, Shahibaug, Ahmedabad 380004",
#         "contact": "Mr Pinnag Rathod ", 
#         "mobile": "+91 9924626516",
#         "email": "elv.projects@accuratepms.in",
#         "gst_no": "24AAMCA2528C1Z3"
#     },
#     "Adaptive Technology (India) Private Limited": {
#         "address": "301-305 Sahajanand Trade Center,Opp. Kothawala Flats, Ellisbridge, Ahmedabad - 380 006",
#         "contact": "Mr Mahamadali Patavat ", 
#         "mobile": "+91 9724014745",
#         "email": "mahamadali.patavat@infinitisolutions.com ",
#         "gst_no": "24AABCA8447P1Z9"
#     },
#     "Atomep Enteam Private Limited": {
#         "address": "316, Sangath Central, b/h. 4D square Mall, Visat Koba Road, Motera, Ahmedabad.",
#         "contact": "Mr Apoorv Tripathi ", 
#         "mobile": "+91 9904827161",
#         "email": "mepf@atomep.com",
#         "gst_no": "24AAUCA8738J1Z0"
#     },
#     "AUM ASSOCIATES": {
#         "address": "D-418, Ganesh Glory-11, Jagatput Road, Ahmedabad 382470",
#         "contact": "Mr. Jaydeep ", 
#         "mobile": "+91 8401163977",
#         "email": "jaydeep0308@gmail.com",
#         "gst_no": "24BPNPR1102P2AZM"
#     },
#     "Authentic Computers": {
#         "address": "F1, Woodland Appartment, Opp. Syndicate Bank, Paldi, Ahmedabad",
#         "contact": "Mr. Hansal Jhaveri ", 
#         "mobile": "+91 9825700144",
#         "email": "hansaljhaveri@gmail.com",
#         "gst_no": "24ACZPJ4746P1ZN"
#     },
#     "AV Designs": {
#         "address": "1109, Swati Clover, Near Shilaj Circle, SP Ring Road, Ahmedabad.",
#         "contact": "Mr. Anand Patel", 
#         "mobile": "+91 8849430718",
#         "email": "vstudio.191@gmail.com",
#         "gst_no": "24AOMPP2322N1ZP"
#     },
#     "Blueribbon 3d studio": {
#         "address": "C-1018, Rajyash rise, nr vishala circle, Ahmedabad",
#         "contact": "Mr. Vijay Jadav", 
#         "mobile": "+91 9624465429",
#         "email": "blueribbon3d@gmail.com",
#         "gst_no": "24AOJPJ0934R1ZK"
#     },
#     "BrainZ Institute of Design": {
#         "address": "A-203 Himalaya Arcade, Opp Vastrapur Lake, Vastrapur,Ahmedabad",
#         "contact": "Mr. Anil Dangi ", 
#         "mobile": "+91 9375858567",
#         "email": "brainzgroup@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Brijesh Patel Project Consultancy": {
#         "address": "First Floor, Radha Chamber, Sardarnagar Circle, Rajkot",
#         "contact": "Mr. Brijesh Patel ", 
#         "mobile": "+91 9825078757",
#         "email": "abrijeshpatel@yahoo.co.in",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Craox Technologies LLP": {
#         "address": "B1/ 202, Westgate Business Bay, S.G. Highway, Makarba",
#         "contact": "Mr. Nikhil Dhamsaniya ", 
#         "mobile": "+91 9724416997",
#         "email": "nikhil@craox.com",
#         "gst_no": "24AAOFC2246A1ZY"
#     },
#     "Creative IT Solutions": {
#         "address": "Third Floor, B/10, Hemratna Co. Op. Hous. Soc. Abhinandan Appartment, Nr. Kothari Tower, Sabarmati, Ahmedabad, Gujarat, 380005",
#         "contact": "Mr. Milan Shah ", 
#         "mobile": "+91 9898069097",
#         "email": "creativeitmilan@gmail.com",
#         "gst_no": "24BOPPS6020G1ZU"
#     },
#     "Designcore Studio Private Limited": {
#         "address": "310, Union Heights B/H L.C. Stadium, Dumas Road, Surat, Gujarat",
#         "contact": "Mr. Ketan Solanki", 
#         "mobile": "0261 2971661",
#         "email": "info@designcore.co.in",
#         "gst_no": "24AAICD4127E1Z1"
#     },
#     "Dhanvanti Engineering Private Limited": {
#         "address": "LS.No.: 218, Bhavda-Undrel Road, Near Bhavda Village, Bhavda, Ahmedabad",
#         "contact": "Mr. Jitendra Singh Gehlot", 
#         "mobile": "+91 9712990715",
#         "email": "accounts@dhanvantieng.com",
#         "gst_no": "24AAICD4893M1Z3"
#     },
#     "Kuke Associates": {
#         "address": "303,304 Patron, opp. Kensville Golf Academy, Rajpath Rangoli Rd, near Deendayal Comunity Hall, Ahmedabad,",
#         "contact": "Mr. Tanmay Prajapati", 
#         "mobile": "+91 9904202050",
#         "email": "studio@kukeassociates.com",
#         "gst_no": "24AGCPP6870H1Z8"
#     },
#     "Limited Edition": {
#         "address": "321, Ashvmegh Elegance, Opp. Rudra Tower, Bhudarpura Road, Ambawadi, Ahmedabad",
#         "contact": "Mr. Vijay Jain", 
#         "mobile": "+91 9327574998",
#         "email": "connectlimitededition@gmail.com",
#         "gst_no": "24AEOPJ3084R1ZT"
#     },
#     "MI Architect & Associates": {
#         "address": "Titanium Square, C-204, Cross Road, Nr. SG Highway, Thaltej, Ahmedabad, Gujarat 380054",
#         "contact": "Mr. Mihir Patel ", 
#         "mobile": "+91 9904449410",
#         "email": "info.miarch@gmail.com",
#         "gst_no": "24APLPP4317B1Z6"
#     },
#     "Micro Equipment Corporation": {
#         "address": "504, Supath Opp. Rasranjan, Vijay Cross Road, Navrangpura, Ahmedabad",
#         "contact": "Mr. Hiren Sanghvi", 
#         "mobile": "+91 9825528096",
#         "email": "hiren@microecorp.co.in",
#         "gst_no": "24CQIPS3753G1ZM"
#     },
#     "Pramukh Interior": {
#         "address": "213, Shivam Complex, Science City Road, Ahmedabad",
#         "contact": "Mr. Prashant Parmar", 
#         "mobile": "+91 9825398519",
#         "email": "shayonaconsultant50@yahoo.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Reepra Infotech": {
#         "address": "M-10, Jolly Shopping Point, B/S G-3 Mall, Ghod Dod Road, Surat",
#         "contact": "Mr. Pranav Desai", 
#         "mobile": "+91 98241 55886",
#         "email": "reeprainfotech@gmail.com",
#         "gst_no": "24AFUPD6830J1Z7"
#     },
#     "Sach Infraprojects Private Limited": {
#         "address": "701 Zion Prime, Near Baghban Party Plot, Thaltej Shilaj Road, Ahmedabad, Gujarat",
#         "contact": "Mr. Sachin Gajjar", 
#         "mobile": "+91 9909976501",
#         "email": "mail@sachinfraprojects.com",
#         "gst_no": "24AAPCS2797A1Z7"
#     },
#     "SCOPE UNLIMITED": {
#         "address": "903,904, Shiromani Complex, Satellite, Ahmedabad, Gujarat, 380015",
#         "contact": "Mr. Kanhai Shah", 
#         "mobile": "+91 8849041010",
#         "email": "kanhai@scopeinterior.com",
#         "gst_no": "24ABWFS6202K1ZR"
#     },
#     "Spline Design ": {
#         "address": "201,Sheel Complex,Nr-Mithakhali Six Road, Ahmedabad",
#         "contact": "Mr.  Devang Vaghela", 
#         "mobile": "+91 9825395890",
#         "email": "splinedesign@yahoo.com",
#         "gst_no": "24AFAPV1243B1Z1"
#     },
#     "Sunshine Infotactics": {
#         "address": "FC-2/M-9, Jolly Shopping Point B/SD, G3 Show Room, Ghod Dod Road, Surat",
#         "contact": "Mr. Pranav Desai", 
#         "mobile": "+91 9924188955",
#         "email": "ssinfotics@gmail.com",
#         "gst_no": "24AEGPD4791M1Z9"
#     },
#     "Velox Group": {
#         "address": "156/157, Second Floor, Sona Complex, Kansa Cross Road, Vishnagar-384315",
#         "contact": "Mr.Lalit Patel", 
#         "mobile": "+91 99246 18871",
#         "email": " info@veloxgroup.co.in",
#         "gst_no": "24AAMFV0255A1ZK"
#     },
#     "Aavkash Designs": {
#         "address": "509-510, Luxuria Trade Hub, Surat Dumas Road, Rundh,Surat",
#         "contact": "Mr.Smit Thakkar ", 
#         "mobile": "+91 9979200092",
#         "email": " smit_thakkar@yahoo.com",
#         "gst_no": "24ADYPT9899F1Z9"
#     },
#     "Anupam Architects": {
#         "address": "108, Jal Darsan Tower, Near Multi Stories Building, Nanpura, Surat-395 001",
#         "contact": "Mr. Hansal Lakdawala", 
#         "mobile": "9909005401, 91 261247294, 9925010203",
#         "email": " anupamarchitects@yahoo.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Building Services Bureau": {
#         "address": "2nd Floor, City Mall, Near Rajpath Club, S. G. Highway, Ahmedabad.",
#         "contact": "Mr. Amit Shah ", 
#         "mobile": "9428412444, 9825243906",
#         "email": "amit@bsbdesign.in",
#         "gst_no": "24ACUPS2207F2ZJ"
#     },
#     "COB 7 Studio": {
#         "address": "501, Elite Business Icon, Opp. Shapath Hexa, Sola, S. G. Highway, Ahmedabad-380060",
#         "contact": "Mr. Pratik Gajjar ", 
#         "mobile": "079-48901529",
#         "email": "cob7studio@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Dss Projects Management": {
#         "address": "302, Shivalik Shilp, Iscon cross road, Opp. Shrifal Hotel, S G highway, Ahmedabad, Ahmedabad, Gujarat, 380015",
#         "contact": "Mr. Devang Shah ", 
#         "mobile": "+91 99241 19785",
#         "email": "team@dsspm.com",
#         "gst_no": "24ANSPS3259C1ZR"
#     },
#     "Dip Structural Consultant": {
#         "address": "205, Aditraj Arcade, Opp. Titanium City Center, Anandnagar Road, Ahmedabad - 3800l15",
#         "contact": "Mr. Dipesh Mistry", 
#         "mobile": "079-26740377",
#         "email": "dipstructuralconsultant@gmail.com",
#         "gst_no": "24AAKFD5706E1ZQ"
#     },
#     "I Design": {
#         "address": "301, Arohi-2 Complex, Nr. Shalby Hospital, Nr. Memnagar fire Station, Navarangpura, Ahmedabad-380009",
#         "contact": "Mr. Keyur Bhatt ", 
#         "mobile": "+91 98242 58626",
#         "email": "arkeyur@gmail.com",
#         "gst_no": " 24AIMPB2880R1ZS"
#     },
#     "Khodiyar CAD Center (I) Private Limited": {
#         "address": "3rd Floor, Acumen Complex Near  Passport Office, UniverSity Road, Ahmedabad - 380015",
#         "contact": "Mr. Nimesh Patel", 
#         "mobile": "9898981166, 9725471166",
#         "email": "info@khodiyarcadcenter.com",
#         "gst_no": "24AADCK4967E1ZJ"
#     },
#     "Mecha Civil Designs": {
#         "address": "sf 231, Orange Mall, Nr Sharda Petrol Pump, Chandkheda,Ahmedabad, Gujarat",
#         "contact": "Mr. Vishal", 
#         "mobile": "+91 9725935504",
#         "email": "vish20.surti@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Red & White Multimedia Education": {
#         "address": "1-2, Sardar Complex, B/h. Sarswati School, Gaushala, A. K. Road, Surat 395006",
#         "contact": "Mr. Hitesh Desai ", 
#         "mobile": "+91 93275 06324",
#         "email": "hitesdesai@hotmail.com",
#         "gst_no": "24ASQPD8578E1ZE"
#     },
#     "GreenLawn 3D": {
#         "address": "13, Avi Bunglows, Opp Star Bazaar, Satellite Road, Ahmedabad-380015",
#         "contact": " Mr. Pallav Patel", 
#         "mobile": "+91 997 452 8245",
#         "email": "info@greenlawn3d.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Adhwa Architecture. Interiors": {
#         "address": "A-6, Asim Bunglows, At Bopal, Ta Daskroi, Village Bopal,Ahmedabad",
#         "contact": " Mrs. Ankita Adhwa", 
#         "mobile": "+91 9723522208",
#         "email": "dhwanil@adhwa.in",
#         "gst_no": "24ALFPJ7068R1ZF"
#     },
#     "Anand Patel Architects": {
#         "address": "402, Shanti Mall, Sattadhar Cross Road, Ahnredabad",
#         "contact": " Mr. Anand patel ", 
#         "mobile": "79 27415829",
#         "email": "ar.anandpatel@gmail com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Bharat Beams Private Limited": {
#         "address": "Plot No. 10/3, GIDC Industrial Estate, Vatva, Ahmedabad",
#         "contact": "Mr. Snehal ", 
#         "mobile": "+91 9979775957",
#         "email": "snehal@bharatbeams.com",
#         "gst_no": "24AAECB6127G1ZZ"
#     },
#     "Disegno Architects & Interior Designers": {
#         "address": "Office No. 314, Khinvasara Trade Center, Near Dange Chowk, Wakad Road, Thefgaon, Pune",
#         "contact": "Mrs. Deepali Savant", 
#         "mobile": "+91 8806563311",
#         "email": "architects.disegno@gmail.com",
#         "gst_no": "27DDLPS6070P1ZK"
#     },
#     "Earth Architect": {
#         "address": "101 Shreeji Chambers, Popat Mohalla, Nr Police Station, Nanpura, Surat - 395001",
#         "contact": "Mr. Abhishek Patel ", 
#         "mobile": "+91 98251 94194",
#         "email": "ar.abhishekpatel@gmail.com",
#         "gst_no": "24AHVPP6575D1ZT"
#     },
#     "Earthen Design": {
#         "address": "704, Core House, Near Hirabaug Railway Crossing, Ambawadi-380006",
#         "contact": "Mr Kaivalya Shah", 
#         "mobile": "+91 9825732438",
#         "email": "earthen.design@hotmail.com",
#         "gst_no": "24BEGPS8888R1Z5"
#     },
#     "Eskay Engineers": {
#         "address": "A-401, Millenium Plaza, Vastrapur, Ahmedabad,",
#         "contact": "Mr. Rakshit Patel ", 
#         "mobile": "+91 9601297007",
#         "email": "rakshitpatel@eskayengineers.in",
#         "gst_no": "24AABFE4274F1ZR"
#     },
#     "Ganesh Housing Corporation Ltd": {
#         "address": "Ganesh Corporate House, 100 FT., Hebatpur - Thaltej Road,Off S.G. Highway, Thaltej, Ahmedabad ",
#         "contact": "Mr. Sanjay Patel", 
#         "mobile": "+91 8780717230",
#         "email": "sanjay.ghayal@ganeshhousing.co.in",
#         "gst_no": "24AAACG5590Q1Z4"
#     },
#     "Ghorecha Associate": {
#         "address": "503, Swagat Complex, Beside Lal Bunglow, C. G. Road, Ahmedabad",
#         "contact": "Mr. Yagnesh Ghorecha", 
#         "mobile": "+91 9825955111",
#         "email": "ghorechassociate@yahoo.co.in",
#         "gst_no": "24ABBPG3038L1ZX"
#     },
#     "Ishika Stone Arts ": {
#         "address": "A212, Shastri Nagar, Jodhpur-342003, Rajasthan",
#         "contact": "Mr. Sanjay Mehta", 
#         "mobile": "+91 9414701382",
#         "email": "ishikastonearts@gmail.com",
#         "gst_no": "08AJQPM7957B1ZQ"
#     },
#     "Jigar Panchal Architects": {
#         "address": "1102,Colonnade, opp. Iscon Temple brt stand, Iscon cross roads, Ahnredabad",
#         "contact": "Mr. Jigar Panchal ", 
#         "mobile": "+91 9824364922",
#         "email": "architectjpl135@gmail com",
#         "gst_no": "24AQMPP4349P1Z2"
#     },
#     "LA Dimentia Private Limited": {
#         "address": "11, Krishna Bunglows, Opp. Takshsshila Apartment, Gagban Party Plot, Thaltej, Ahmedabad",
#         "contact": "Mr. Jignesh Suthar ", 
#         "mobile": "+91 9998969488",
#         "email": "info@ ladimentiaarchitects.com",
#         "gst_no": "24AACCL5092L1ZA"
#     },
#     "MMP Architects ": {
#         "address": "4th Floor, Office No. 1, Agrawal Mall, S. G. Highway, Ahmedabad-",
#         "contact": "Mr. Malin Patel", 
#         "mobile": "+91 9327058799",
#         "email": "mmpstudio@yahoo.com",
#         "gst_no": "24AASPP5811E1ZN"
#     },
#     "Morphallaxis (Architecture+Design)": {
#         "address": "A18, Simandhar 2, Opp. Vishwakarma Temple, Gota Road, Chandlodia, Ahmedabad",
#         "contact": "Mr. Abhishek Panchal", 
#         "mobile": "+91 8460406040",
#         "email": "studio@morphallaxis.in",
#         "gst_no": "24AQGPP1499J1ZF"
#     },
#     "N Scale Associate": {
#         "address": "302-303, Maruti Titanium, Near Galaxy Business House, Opp. Torrent Power Station, S. P. Ring Road, Nikol, Ahmedabad,",
#         "contact": "Mr. Vajubhai C Kantariya", 
#         "mobile": "+91 9825259970",
#         "email": "nscaleassociate@gmail.com",
#         "gst_no": "24AFVPK6050J1Z3"
#     },
#     "Param Interactive ": {
#         "address": "Nisarg Bunglow, 45, Near Navrachna School, Sama, Vadodara",
#         "contact": "Mr. Suhit Gajjar ", 
#         "mobile": "+91 9898022048",
#         "email": "suhitgajjar@gmail.com",
#         "gst_no": "24AAUFP8410D1Z7"
#     },
#     "Proportions": {
#         "address": "402, Advait Complex, Near Sandesh Press, Vastrapur, Ahmedabad",
#         "contact": "Mr. Amrish Mandlik", 
#         "mobile": "+91 98792 34928",
#         "email": "aramrishm@gmail.com",
#         "gst_no": "24APVPM6175J1Z6"
#     },
#     "PZARCHSTUDIO": {
#         "address": "GF 11, Green View Avenue, Science City, Ahmedabad-",
#         "contact": "Mr. Pinakin", 
#         "mobile": "+91 9265995355",
#         "email": "pzarchstudio@gmail.com",
#         "gst_no": "24AZBPP7757R1ZH"
#     },
#     "Reema Engineers": {
#         "address": "103, Sarjan Industrial Estate, S. P. Ring Road, Nikol-Kathwada Char Rasta, Odhav, Ahmedabad",
#         "contact": "Mr. Mahesh Patel", 
#         "mobile": "+91 9725 005 006",
#         "email": "remaengg@gmial.com",
#         "gst_no": "24ALYPK2474R1Z3"
#     },
#     "Rim Quality System ": {
#         "address": "A/202, Krishna Complex, Opp. Devashish School, Bodakdev, Ahmedabad-380054",
#         "contact": "Mr. Nikit Shah", 
#         "mobile": "+91 9712906378",
#         "email": "rimqms@yahoo.com",
#         "gst_no": "24AMDPS8174J1ZL"
#     },
#     "Sakshham Consultants ": {
#         "address": "B2, 3rd Floor, Medicare Center, B/h MJ Library, Ellisbridge, Ahmedabad",
#         "contact": "Mr. Valay Shah", 
#         "mobile": "+91 8238000704",
#         "email": "info@sakshham.com",
#         "gst_no": "24ACFFS8757D1ZX"
#     },
#     "Snehal K Ved": {
#         "address": "B-405, Ganesh Plaza, Near Navarangpura Post, Office, Opp. Navarangpura Bus Stop, Navarangpura,Ahmedabad.-380 009",
#         "contact": "Mr. Snehal Ved ", 
#         "mobile": "+91 94260 77093",
#         "email": "snehengineers@yahoo.co.in",
#         "gst_no": "24AAIPV7641Q1ZU"
#     },
#     "Sopan Infotech": {
#         "address": "1/530, 1st Floor, Kubb's Corner, Opp. Kailash Sweet, Timliyawad, Nanpura, Surat",
#         "contact": "Mr. Mahek mistry ", 
#         "mobile": "+91 9725554395",
#         "email": "info@sied.in; mahek.mistry@sopaninfotech.com",
#         "gst_no": "24BAIPM1037N1ZM"
#     },
#     "Squelette Design": {
#         "address": "B/406, Times Square 2, Sindhu Bhavan Marg, beside Avalon Hotel, Thaltej, Ahmedabad,",
#         "contact": "Mr. Prashant Trivedi", 
#         "mobile": "+91 9537113319",
#         "email": "squelettedesign@gmail.com",
#         "gst_no": "24ADWFS9890B1ZE"
#     },
#     "Vee Design ": {
#         "address": "13, Paridise Appartment, Opp. Ketav Petrol Pump, Dr. V. S. Road, Ambawadi",
#         "contact": "Mr. Naman Shah", 
#         "mobile": "+91 9825016458",
#         "email": "veedesign@veedesign.in",
#         "gst_no": "24AABFV1734F1ZJ"
#     },
#     "Ayushmi Creation Private Limited ": {
#         "address": "603/604, Vihav Trade Centre, Vasna Bhayli Road, Nr. Waves Club, Vadodara, Gujarat 391410",
#         "contact": "Mrs. Mousumi Raina", 
#         "mobile": "+91 9510630502",
#         "email": "mousumi@ayushmicreation.com",
#         "gst_no": "24ABDCA0758J1ZR"
#     },
#     "Oneknotone Technologies LLP ": {
#         "address": "5th Floor, Trisha Square 1, Above PN Gadgil Jewelers, Jetalpur Road, Vadodara-390007",
#         "contact": "Mr. Alap Acharya", 
#         "mobile": "+91 7984732336",
#         "email": "info@oneknotone.co",
#         "gst_no": "24AAGFO8583L2ZM"
#     },
#     "Praful Parmar": {
#         "address": "Sneh Plaza Road, Chnadkheda, Ahmedabad",
#         "contact": "Mr. Praful Parmar", 
#         "mobile": "+91 8866522132",
#         "email": "parmarpraful40@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "ARCELIA DEVELOPERS PRIVATE LIMITED": {
#         "address": "4-5, B/H. Rajpath Club, Nr Mann Party, Plot, Sigma Corporate-1, Sindhu Bhavan Road, Bodakdev, Ahmedabad",
#         "contact": "Mr. Vipul Shah", 
#         "mobile": "+91 9099016512",
#         "email": "vshah@pacificacompanies.in",
#         "gst_no": "24AAUCA5161F1ZM"
#     },
#     "Dimore Surfaces Private Limited": {
#         "address": "11, Titanium, First Floor, Near Prahladnagar Garden, Corporate Road, Satellite, Ahmedabad 380015",
#         "contact": "Mr. Nishad Soni", 
#         "mobile": "+91 7069001542",
#         "email": "it@dimore.co.in",
#         "gst_no": "24AAKCD1711G1Z3"
#     },
#     "Urjavinya Solutions Private Limited": {
#         "address": "A-367, Money Plant High Street, B/h Shell Petrol Pump, Jagatpur Road, S G Highway, Ahmedabad 382470",
#         "contact": "Mr. Vipul Patel", 
#         "mobile": "+91 98240 77930",
#         "email": "vipul.patel@urjovinya.com",
#         "gst_no": "24AACCN8260A1ZV"
#     },
#     "JV Consultant": {
#         "address": "UG 13 18, V3 Cornery Honey park Road, Adajan, Surat.",
#         "contact": "Mr. Bipin Gajjar", 
#         "mobile": "+91 98676 86389",
#         "email": "jvmepf@yahoo.com",
#         "gst_no": "24AGUPG3400E1ZT"
#     },
#     "Awakeen Studio Private Limited": {
#         "address": "A 547, MoneyPlant Jagatpur Rd, Jagatpur Village, near GANESH GLORY, Gota, Ahmedabad, Gujarat 382470",
#         "contact": "Mr. Jatin Vaghela", 
#         "mobile": "+91 74055 37233",
#         "email": "jatin@awakeenstudio.com",
#         "gst_no": "24AASCA3812B1Z2"
#     },
#     "Madhya Pradesh Cupro Metals Private Limited": {
#         "address": "D-11, Industrial Estate, Govindpura, Bhopal - 462023",
#         "contact": "Mr.Akshay Nema", 
#         "mobile": "+91 88899 43337",
#         "email": "mpcupro@gmail.com",
#         "gst_no": "23AAACM5106C1Z9"
#     },
#     "FALGUN CENTRIFUGE PRIVATE LIMITED": {
#         "address": "14, Shayona Ind. Estate, Nr. Panchratna Estate, Ahmedabad-382445, Gujarat, India.",
#         "contact": "Mr. Falgun Devmurari", 
#         "mobile": "+91 75676 86574",
#         "email": "falguncentrifuge@gmail.com",
#         "gst_no": "24AAECF9772H1ZC"
#     },
#     "INVOIT PLAST MACHINERY  PRIVATE LIMITED": {
#         "address": "Shade No. 176, NK3 Industrial Estate, Bakrol-Bujarang, Ahmedabad",
#         "contact": "Mr. Arvind Patel", 
#         "mobile": "+91 6354602502",
#         "email": "arvind@invoitplast.net",
#         "gst_no": "24AAECI8405N1ZC"
#     },
#     "ARKILO": {
#         "address": "W No. 8/2108, Anurag Plus, Digi Street, Near Sayaji Liabrary, Madhumati Colony, Navsari-396445, Gujarat ",
#         "contact": "Mr. Jay Kapadia ", 
#         "mobile": "+91 8758662915",
#         "email": "kapadia.architect@gmail.com",
#         "gst_no": "24EKUPK5622Q1ZB"
#     },
#     "M/S. SATYAM ENGINEERING SERVICES": {
#         "address": "805/ 8th floor, Filix Tower, opp. Asian paints, LBS Road, Sonapur, Bhandup (W), Mumbai - 400078",
#         "contact": "Mr. Ganesh Pawar", 
#         "mobile": "+91 9769132888",
#         "email": "ganesh.pawar@satyames.com",
#         "gst_no": "27BJBPP5949J2ZN"
#     },
#     "Upright Consultants": {
#         "address": "E, Royal Homes, Opp. Satyam Vista, Gota Village, Ahmedabad, Ahmedabad, Gujarat, 382481",
#         "contact": "Mr. Rahul Raval", 
#         "mobile": "+91 96244 06822",
#         "email": "uprightconsultants24@gmail.com",
#         "gst_no": "24ASWPR4065Q1ZN"
#     },
#     "Agniforma Techcraft Private Limited": {
#         "address": "101,102, Parashawnath E Square, Corporate Road, Prahladnagar,Ahmedabad-380015",
#         "contact": "Mr. Nirmeet Kacheria", 
#         "mobile": "+91 98980 02236",
#         "email": "nirmeet.kacheria@agniforma.com",
#         "gst_no": "24AAVCA9825B1ZI"
#     },
#     "Studio Black Brick": {
#         "address": "C-212, Sumel 11, Opp. Namste Circle, Shahibaugh Ahmedabad - 380004",
#         "contact": "Mr. Chirag Shah", 
#         "mobile": "+91 7990105299",
#         "email": "studioblackbrick1@gmail.com",
#         "gst_no": "NOT APPLICABLE"
#     },
#     "Base Engineering": {
#         "address": "406, Sakar East, Behind Big Bazaar, Alkapuri, Vadodara - 390007",
#         "contact": "Mr. Dhaval Mistry",
#         "mobile": "9898791813", 
#         "email": "dmistry@baseengr.com",
#         "gst_no": "24AAIFB7147L1ZH"
#     }
# }


# # Sales Person Mapping - ONLY ONE DEFINITION
# SALES_PERSON_MAPPING = {
#     "CP": {"name": "Chirag Prajapati", "email": "chirag@cminfotech.com", "mobile": "+91 87339 15721"},
#     "HP": {"name": "Hiral Patel", "email": "hiral@cminfotech.com", "mobile": "+91 95581 15721"},
#     "KP": {"name": "Khushi Patel", "email": "khushi@cminfotech.com", "mobile": "+91 97241 15721"},
#     "SD": {"name": "Sakshi Darji", "email": "sakshi@cminfotech.com", "mobile": "+91 74051 15721"}
# }

# # --- Helper Functions for Vendor Management ---
# def get_vendor_dropdown_options():
#     """Get vendor names for dropdown"""
#     return ["Select Vendor"] + list(VENDOR_DATABASE.keys())

# def update_vendor_fields(selected_vendor):
#     """Update session state with vendor details when vendor is selected"""
#     if selected_vendor and selected_vendor != "Select Vendor":
#         vendor_data = VENDOR_DATABASE.get(selected_vendor, {})
#         st.session_state.po_vendor_name = selected_vendor
#         st.session_state.po_vendor_address = vendor_data.get("address", "")
#         st.session_state.po_vendor_contact = vendor_data.get("contact", "")
#         st.session_state.po_vendor_mobile = vendor_data.get("mobile", "")
#         st.session_state.po_gst_no = vendor_data.get("gst_no", "")
#         st.session_state.po_pan_no = vendor_data.get("pan_no", "")
#         st.session_state.po_msme_no = vendor_data.get("msme_no", "")

# # --- Helper Functions for End User Management ---
# def get_enduser_dropdown_options():
#     """Get end user names for dropdown"""
#     return ["Select End User"] + list(END_USER_DATABASE.keys())

# def update_enduser_fields(selected_enduser):
#     """Update session state with end user details when end user is selected"""
#     if selected_enduser and selected_enduser != "Select End User":
#         enduser_data = END_USER_DATABASE.get(selected_enduser, {})
#         st.session_state.po_end_company = selected_enduser
#         st.session_state.po_end_address = enduser_data.get("address", "")
#         st.session_state.po_end_person = enduser_data.get("contact", "")
#         st.session_state.po_end_mobile = enduser_data.get("mobile", "")
#         st.session_state.po_end_email = enduser_data.get("email", "")
#         st.session_state.po_end_gst_no = enduser_data.get("gst_no", "")


# # --- Helper Functions for Quotation and PO ---
# def get_current_quarter():
#     """Get current quarter (Q1, Q2, Q3, Q4) based on current month"""
#     month = datetime.datetime.now().month
#     if month in [4, 5, 6]:
#         return "Q1"
#     elif month in [7, 8, 9]:
#         return "Q2"
#     elif month in [10, 11, 12]:
#         return "Q3"
#     else:
#         return "Q4"

# import os

# # Simple file-based counter for PO sequence
# PO_COUNTER_FILE = "po_counter.txt"

# def get_next_po_sequence():
#     """Simple file-based PO sequence counter"""
#     try:
#         # Read current number from file
#         if os.path.exists(PO_COUNTER_FILE):
#             with open(PO_COUNTER_FILE, 'r') as f:
#                 current = int(f.read().strip())
#         else:
#             current = 0
#     except:
#         current = 0
    
#     # Increment
#     next_seq = current + 1
    
#     # Save the new number back to file
#     with open(PO_COUNTER_FILE, 'w') as f:
#         f.write(str(next_seq))
    
#     return next_seq

# def get_current_po_sequence():
#     """Get current PO sequence without incrementing"""
#     try:
#         if os.path.exists(PO_COUNTER_FILE):
#             with open(PO_COUNTER_FILE, 'r') as f:
#                 return int(f.read().strip())
#     except:
#         pass
#     return 1


# def parse_po_number(po_number):
#     """Parse PO number to extract components"""
#     try:
#         parts = po_number.split('/')
#         if len(parts) >= 4:
#             prefix = parts[0]  # C
#             sales_person = parts[1]  # CP, SD, HP, KP
#             year = parts[2]  # 2025
#             quarter_sequence = parts[3]  # Q4_001
#             quarter = quarter_sequence.split('_')[0]  # Q4
#             sequence = quarter_sequence.split('_')[1] if '_' in quarter_sequence else "001"  # 001, 002, etc.
#             return prefix, sales_person, year, quarter, sequence
#     except:
#         pass
#     return "CMI", "CP", str(datetime.datetime.now().year), get_current_quarter(), "001"

# def generate_po_number(sales_person, sequence_number):
#     """Generate PO number with current quarter and sequence"""
#     current_date = datetime.datetime.now()
#     quarter = get_current_quarter()
#     year = str(current_date.year)
#     sequence = f"{sequence_number:03d}"
    
#     return f"CMI/{sales_person}/{year}/{quarter}_{sequence}"

# def get_next_sequence_number_po(po_number):
#     """Extract and increment sequence number from PO number"""
#     try:
#         parts = po_number.split('_')
#         if len(parts) > 1:
#             sequence = parts[-1]
#             return int(sequence) + 1
#     except:
#         pass
#     return 1
# import os

# # Simple file-based counter for quotations
# QUOTATION_COUNTER_FILE = "quotation_counter.txt"

# def get_next_quotation_sequence():
#     """Simple file-based sequence counter"""
#     try:
#         # Read current number from file
#         if os.path.exists(QUOTATION_COUNTER_FILE):
#             with open(QUOTATION_COUNTER_FILE, 'r') as f:
#                 current = int(f.read().strip())
#         else:
#             current = 0
#     except:
#         current = 0
    
#     # Increment
#     next_seq = current + 1
    
#     # Save the new number back to file
#     with open(QUOTATION_COUNTER_FILE, 'w') as f:
#         f.write(str(next_seq))
    
#     return next_seq

# def get_current_quotation_sequence():
#     """Get current sequence without incrementing"""
#     try:
#         if os.path.exists(QUOTATION_COUNTER_FILE):
#             with open(QUOTATION_COUNTER_FILE, 'r') as f:
#                 return int(f.read().strip())
#     except:
#         pass
#     return 1


# def parse_quotation_number(quotation_number):
#     """Parse quotation number to extract components"""
#     try:
#         parts = quotation_number.split('/')
#         if len(parts) >= 5:
#             prefix = parts[0]  # CMI
#             sales_person = parts[1]  # SD, CP, HP, KP
#             quarter = parts[2]  # Q1, Q2, Q3, Q4
#             date_part = parts[3]  # DD-MM-YYYY
#             year_range = parts[4].split('_')[0]  # 2025-2026
#             sequence = parts[4].split('_')[1] if '_' in parts[4] else "001"  # 001, 002, etc.
#             return prefix, sales_person, quarter, date_part, year_range, sequence
#     except:
#         pass
#     return "CMI", "SD", get_current_quarter(), datetime.datetime.now().strftime("%d-%m-%Y"), f"{datetime.datetime.now().year}-{datetime.datetime.now().year+1}", "001"

# def generate_quotation_number(sales_person, sequence_number):
#     """Generate quotation number with current quarter and sequence"""
#     current_date = datetime.datetime.now()
#     quarter = get_current_quarter()
#     year_range = f"{current_date.year}-{current_date.year+1}"
#     sequence = f"{sequence_number:03d}"
    
#     return f"CMI/{sales_person}/{quarter}/{current_date.strftime('%d-%m-%Y')}/{year_range}_{sequence}"

# # --- Add this function with other helper functions ---
# def calculate_quotation_totals(products):
#     """Calculate quotation totals with round-off like PO generator"""
#     products_total = 0
#     for p in products:
#         gst_amt = p["basic"] * p["gst_percent"] / 100
#         per_unit_price = p["basic"] + gst_amt
#         total = per_unit_price * p["qty"]
#         products_total += total

#     # Calculate round off to make final amount whole number (like PO)
#     rounded_total = round(products_total)
#     round_off = rounded_total - products_total
    
#     return {
#         "total_base": sum(p["basic"] * p["qty"] for p in products),
#         "total_gst": sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in products),
#         "grand_total_unrounded": products_total,
#         "grand_total": rounded_total,
#         "round_off": round_off
#     }

# def get_next_sequence_number(quotation_number):
#     """Extract and increment sequence number from quotation number"""
#     try:
#         parts = quotation_number.split('_')
#         if len(parts) > 1:
#             sequence = parts[-1]
#             return int(sequence) + 1
#     except:
#         pass
#     return 1


# import os

# # Simple file-based counter for Invoice sequence
# INVOICE_COUNTER_FILE = "invoice_counter.txt"

# def get_next_invoice_sequence():
#     """Simple file-based Invoice sequence counter"""
#     try:
#         # Read current number from file
#         if os.path.exists(INVOICE_COUNTER_FILE):
#             with open(INVOICE_COUNTER_FILE, 'r') as f:
#                 current = int(f.read().strip())
#         else:
#             current = 0
#     except:
#         current = 0
    
#     # Increment
#     next_seq = current + 1
    
#     # Save the new number back to file
#     with open(INVOICE_COUNTER_FILE, 'w') as f:
#         f.write(str(next_seq))
    
#     return next_seq

# def get_current_invoice_sequence():
#     """Get current Invoice sequence without incrementing"""
#     try:
#         if os.path.exists(INVOICE_COUNTER_FILE):
#             with open(INVOICE_COUNTER_FILE, 'r') as f:
#                 return int(f.read().strip())
#     except:
#         pass
#     return 1

# # --- Helper Functions for Invoice ---
# def parse_invoice_number(invoice_number):
#     """Parse invoice number to extract components"""
#     try:
#         parts = invoice_number.split('/')
#         if len(parts) >= 4:
#             prefix = parts[0]  # CMI
#             year_range = parts[1]  # 25-26
#             quarter = parts[2]  # Q3
#             sequence = parts[3]  # 01, 02, etc.
#             return prefix, year_range, quarter, sequence
#     except:
#         pass
#     return "CMI", f"{str(datetime.datetime.now().year)[2:]}-{str(datetime.datetime.now().year + 1)[2:]}", get_current_quarter(), "01"

# def generate_invoice_number(sequence_number):
#     """Generate invoice number with current quarter and sequence"""
#     current_date = datetime.datetime.now()
#     quarter = get_current_quarter()
#     year_range = f"{str(current_date.year)[2:]}-{str(current_date.year + 1)[2:]}"
#     sequence = f"{sequence_number:02d}"
    
#     return f"CMI/{year_range}/{quarter}/{sequence}"

# def get_next_sequence_number_invoice(invoice_number):
#     """Extract and increment sequence number from invoice number"""
#     try:
#         parts = invoice_number.split('/')
#         if len(parts) >= 4:
#             sequence = parts[3]
#             return int(sequence) + 1
#     except:
#         pass
#     return 1

# # --- PDF Class for Two-Page Quotation (Matching Demo Format) ---
# class QUOTATION_PDF(FPDF):
#     def __init__(self, quotation_number="Q-N/A", quotation_date="Date N/A", sales_person_code="CP"):
#         super().__init__()
#         self.set_auto_page_break(auto=True, margin=15)
#         self.set_left_margin(15)
#         self.set_right_margin(15)
#         self.quotation_number = quotation_number
#         self.quotation_date = quotation_date
#         self.sales_person_code = sales_person_code
#         font_dir = os.path.join(os.path.dirname(__file__), "fonts")
#         try:
#             self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
#             self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
#             self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
#             self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
#             self.default_font = "Calibri"
#         except:
#             self.default_font = "Helvetica"
        
#     def sanitize_text(self, text):
#         try:
#             return text.encode('latin-1', 'ignore').decode('latin-1')
#         except:
#             return text

#     def header(self):
#         # Logo placement (top right) - FIXED
#         if hasattr(self, 'logo_path') and self.logo_path and os.path.exists(self.logo_path):
#             try:
#                 self.image(self.logo_path, x=155, y=8, w=50)
#             except:
#                 # If image fails, show placeholder
#                 self.set_font(self.default_font, "B", 10)
#                 self.set_xy(150, 8)
#                 self.cell(40, 5, "[LOGO]", border=0, align="C")
            
#         # Main Title (Centered)
#         self.set_font(self.default_font, "B", 16)
#         self.set_y(15)
#         self.ln(5)

#     def footer(self):
#         # Position from bottom (same as invoice)
#         self.set_y(-12)
        
#         # Horizontal line
#         # self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
#         # self.ln(2)
        
#         # Footer content - Computer generated text
#         # self.set_font("Helvetica", "I", 10)
#         # self.cell(0, 4, "This is a Computer Generated Quotation", ln=True, align="C")
        
#         # Company address
#         self.set_font("Helvetica", "", 10)
#         self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
#         # Clickable contact info (same as invoice)
#         self.set_font("Helvetica", "U", 10)
#         self.set_text_color(0, 0, 255)  # Blue for links
        
#         email1 = "info@cminfotech.com"
#         phone_number = "+91 873 391 5721"
#         website = "www.cminfotech.com"
        
#         # Center the contact information
#         contact_text = f"{email1} | {phone_number} | {website}"
#         contact_width = self.get_string_width(contact_text)
#         x_contact = (self.w - contact_width) / 2
        
#         self.set_x(x_contact)
#         self.cell(self.get_string_width(email1), 4, email1, link=f"mailto:{email1}")
#         self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | "))
#         self.cell(self.get_string_width(phone_number), 4, phone_number, link=f"tel:{phone_number}")
#         self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | ") + self.get_string_width(phone_number) + self.get_string_width(" | "))
#         self.cell(self.get_string_width(website), 4, website, link="https://www.cminfotech.com/")
        
#         self.set_text_color(0, 0, 0)

#     # def footer(self):
#     #     self.set_y(-18)
#     #     self.set_font(self.default_font, "", 10)
#     #     self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
#     #     # Make footer emails and phone clickable - FIXED OVERLAP
#     #     self.set_text_color(0, 0, 255)  # Blue color for links
        
#     #     # Website link
#     #     # self.cell(0, 4, "www.cminfotech.com", ln=True, align="C", link="https://www.cminfotech.com/")
        
#     #     # Email and phone on same line - FIXED
#     #     self.set_font(self.default_font, "U", 10)
#     #     email_text = " info@cminfotech.com "
#     #     phone_text = " +91 873 391 5721"
        
#     #     # Calculate positions for proper alignment
#     #     page_width = self.w - 2 * self.l_margin
#     #     email_width = self.get_string_width(email_text)
#     #     phone_width = self.get_string_width(phone_text)
#     #     separator_width = self.get_string_width(" | ")
        
#     #     total_width = email_width + separator_width + phone_width
#     #     start_x = (page_width - total_width) / 2 + self.l_margin
        
#     #     self.set_x(start_x)
#     #     self.cell(email_width, 4, email_text, ln=0, link=f"mailto:{email_text}")
#     #     self.cell(separator_width, 4, " | ", ln=0)
#     #     self.cell(phone_width, 4, phone_text, ln=True, link=f"tel:{phone_text.replace(' ', '').replace('+', '')}")

#     #     self.cell(0, 4, "www.cminfotech.com", ln=True, align="C", link="https://www.cminfotech.com/")
        
#     #     self.set_text_color(0, 0, 0)  # Reset to black

# def add_clickable_email(pdf, email, label="Email: "):
#     """Add clickable email with label - FIXED OVERLAP"""
#     pdf.set_font(pdf.default_font, "B", 12)
#     label_width = pdf.get_string_width(label)
#     pdf.cell(label_width, 4, label, ln=0)
    
#     pdf.set_text_color(0, 0, 255)  # Blue for clickable
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(0, 4, email, ln=True, link=f"mailto:{email}")
#     pdf.set_text_color(0, 0, 0)  # Reset to black

# def add_clickable_phone(pdf, phone, label="Mobile: "):
#     """Add clickable phone number with label - FIXED OVERLAP"""
#     pdf.set_font(pdf.default_font, "B", 12)
#     label_width = pdf.get_string_width(label)
#     pdf.cell(label_width, 4, label, ln=0)
    
#     pdf.set_text_color(0, 0, 255)  # Blue for clickable
#     pdf.set_font(pdf.default_font, "", 12)
#     # Remove spaces and + for tel link
#     tel_number = phone.replace(' ', '').replace('+', '')
#     pdf.cell(0, 4, phone, ln=True, link=f"tel:{tel_number}")
#     pdf.set_text_color(0, 0, 0)  # Reset to black

# def add_page_one_intro(pdf, data):
#     # Reference Number & Date (Top Right)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.set_y(35)
#     pdf.cell(0, 5, f"REF NO.: {data['quotation_number']}", ln=True, align="L")
#     pdf.cell(0, 5, f"Date: {data['quotation_date']}", ln=True, align="L")
#     pdf.ln(5)

#     # Recipient Details
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(0, 5, "To,", ln=True)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(0, 6, pdf.sanitize_text(data['vendor_name']), ln=True)
#     pdf.set_font(pdf.default_font, "", 12)
    
#     # Address handling
#     pdf.multi_cell(94, 4, pdf.sanitize_text(data['vendor_address']))
    
#     pdf.ln(3)
    
#     # Clickable Email
#     if data.get('vendor_email'):
#         add_clickable_email(pdf, data['vendor_email'])
        
#     pdf.ln(1)
#     # Clickable Mobile
#     if data.get('vendor_mobile'):
#         add_clickable_phone(pdf, data['vendor_mobile'])
    
#     pdf.set_font(pdf.default_font, "BU", 12)
#     pdf.cell(0, 5, f"Kind Attention :- {pdf.sanitize_text(data['vendor_contact'])}", align="C", ln=True)
#     pdf.ln(5)

#     # Subject Line
#     pdf.set_font(pdf.default_font, "BU", 12)
#     pdf.cell(0, 6, f"Subject :- {pdf.sanitize_text(data['subject'])}", ln=True)
#     pdf.ln(8)  # Increased spacing

#     # Write the user's custom intro paragraph
#     intro_text = pdf.sanitize_text(data.get("intro_paragraph", ""))
#     if intro_text:
#         write_simple_justified_paragraph(pdf, intro_text)

#     # Fixed company introduction paragraphs - USE THE SIMPLE VERSION
#     fixed_paragraphs = [
#         "Enclosed please find our Quotation for your information and necessary action. You're electing CM Infotech's proposal; your company is assured of our pledge to provide immediate and long-term operational advantages.",
        
#         "CMI (CM INFOTECH) is now one of the leading IT solution providers in India, serving more than 1,000 subscribers across the India in Architecture, Construction, Geospatial, Infrastructure, Manufacturing, Multimedia and Graphic Solutions.",
        
#         "Our partnership with Autodesk, GstarCAD, Grabert, CMS Intellicad, ZWCAD, Etabs, Trimble, Bentley, Solidworks, Solid Edge, Bluebeam, Adobe, Microsoft, Corel, Chaos, Nitro, Tally Quick Heal and many more brings in India the best solutions for design, construction and manufacturing. We are committed to making each of our clients successful with their design technology.",
        
#         "As one of our privileged customers, we look forward to having you take part in our journey as we keep our eye on the future, where we will unleash ideas to create a better world!"
#     ]

#     for paragraph in fixed_paragraphs:
#         write_simple_justified_paragraph(pdf, paragraph)
#         pdf.ln(3)  # Add space between paragraphs

#     # Contact Information - MAKE SURE WE HAVE ENOUGH SPACE
#     # Check if we need a new page
#     if pdf.get_y() > 220:  # If we're too low on the page
#         pdf.add_page()
    
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.set_text_color(0, 0, 0)

#     # Normal text - make sure it's complete
#     contact_text = "Please revert back to us, if you need any clarification / information at the below mentioned address or email at "
#     pdf.write(5, contact_text)

#     # Get sales person info dynamically
#     sales_person_code = data.get('sales_person_code', 'SD')
#     sales_person_info = SALES_PERSON_MAPPING.get(sales_person_code, SALES_PERSON_MAPPING['SD'])
    
#     # Email clickable - DYNAMIC from sales person
#     pdf.set_text_color(0, 0, 255)
#     pdf.set_font(pdf.default_font, "U", 12)
#     pdf.write(5, sales_person_info["email"], link=f"mailto:{sales_person_info['email']}")

#     # Back to normal for separator + Mobile:
#     pdf.set_text_color(0, 0, 0)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.write(5, "  Mobile: ")

#     # Mobile clickable - DYNAMIC from sales person
#     pdf.set_text_color(0, 0, 255)
#     pdf.set_font(pdf.default_font, "U", 12)
#     pdf.write(5, sales_person_info["mobile"], link=f"tel:{sales_person_info['mobile'].replace(' ', '').replace('+', '')}")

#     pdf.ln(10)  # Add space after contact info
#     pdf.set_text_color(0, 0, 0)
#     # Continue with the rest of your contact information...
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(0, 4, "For more information, please visit our web site & Social Media :-", ln=True)
#     pdf.set_font(pdf.default_font, "", 12)
    
#     # Clickable website - RIGHT ALIGNED
#     pdf.set_font(pdf.default_font, "U", 12)
#     pdf.set_text_color(0, 0, 255)

#     # Calculate the width needed for the longest link
#     links = [
#         "https://www.cminfotech.com/",
#         "https://www.linkedin.com/", 
#         "https://wa.me/918733915721",
#         "https://www.facebook.com/",
#         "https://www.instagram.com/"
#     ]

#     # Get the maximum width
#     max_link_width = max(pdf.get_string_width(link) for link in links)

#     # Set right margin position
#     right_margin = pdf.w - pdf.r_margin

#     # Print each link aligned to the right
#     for link in links:
#         # Calculate x position to right-align
#         x_position = right_margin - max_link_width
#         pdf.set_x(x_position)
#         pdf.cell(max_link_width, 4, link, ln=True, link=link)

#     pdf.set_text_color(0, 0, 0)

# def write_simple_justified_paragraph(pdf, text):
#     """Ultra-simple justified paragraphs using multi_cell"""
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.set_text_color(0, 0, 0)
    
#     paragraphs = text.split('\n')
    
#     for paragraph in paragraphs:
#         paragraph = paragraph.strip()
#         if paragraph:
#             # Use multi_cell with justification
#             pdf.multi_cell(0, 5, paragraph, align='J')
#             pdf.ln(3)

# def add_quotation_header(pdf, annexure_text, quotation_text):
#     """Add dynamic quotation header with both annexure and title"""
#     pdf.set_font(pdf.default_font, "BU", 14)
#     pdf.cell(0, 8, annexure_text, ln=True, align="C")
#     pdf.set_font(pdf.default_font, "BU", 12)
#     pdf.cell(0, 6, quotation_text, ln=True, align="C")
#     pdf.ln(8)

# def add_page_two_commercials(pdf, data):
#     pdf.add_page()
#     pdf.ln(10)
#     # Use dynamic header function
#     annexure_text = data.get('annexure_text', 'Annexure I - Commercials')
#     quotation_title = data.get('quotation_title', 'Quotation for Adobe Software')
    
#     add_quotation_header(pdf, annexure_text, quotation_title)

#     # --- Products Table - FIXED COLUMN WIDTHS (Wider Description) ---
#     col_widths = [70, 25, 25, 25, 15, 25]  # Increased Description from 70 to 100
#     headers = ["Description", "Basic Price", "GST Tax @ 18%", "Per Unit Price", "Qty.", "Total"]
    
#     # Table Header
#     pdf.set_fill_color(220, 220, 220)
#     pdf.set_font(pdf.default_font, "B", 10)
#     for width, header in zip(col_widths, headers):
#         pdf.cell(width, 6, header, border=1, align="C", fill=True)
#     pdf.ln()
    
#     # Table Rows
#     pdf.set_font(pdf.default_font, "", 12)
#     grand_total_unrounded = 0.0
    
#     for product in data["products"]:
#         basic_price = product["basic"]
#         qty = product["qty"]
#         gst_amount = basic_price * (product.get("gst_percent", 18.0) / 100)
#         per_unit_price = basic_price + gst_amount
#         total = per_unit_price * qty
#         grand_total_unrounded += total
        
#         # Get current position
#         start_y = pdf.get_y()
        
#         # Description cell (with proper text wrapping)
#         desc = product["name"]
#         pdf.set_font(pdf.default_font, "", 10)
        
#         # Calculate how many lines the description will take
#         desc_lines = pdf.multi_cell(col_widths[0], 5, desc, border=0, split_only=True)
#         desc_height = len(desc_lines) * 6
        
#         # Set position for description
#         pdf.set_xy(pdf.l_margin, start_y)
        
#         # Draw description cell with proper height
#         if len(desc_lines) > 1:
#             # Multi-line description
#             pdf.multi_cell(col_widths[0], 6, desc, border=1)
#             current_y = pdf.get_y()
            
#             # Set positions for other cells WITH COMMA FORMATTING
#             pdf.set_xy(pdf.l_margin + col_widths[0], start_y)
#             pdf.cell(col_widths[1], desc_height, f"{basic_price:,.2f}", border=1, align="R")
#             pdf.cell(col_widths[2], desc_height, f"{gst_amount:,.2f}", border=1, align="R")
#             pdf.cell(col_widths[3], desc_height, f"{per_unit_price:,.2f}", border=1, align="R")
#             pdf.cell(col_widths[4], desc_height, f"{qty:.0f}", border=1, align="C")
#             pdf.cell(col_widths[5], desc_height, f"{total:,.2f}", border=1, align="R")
            
#             # Move to next row
#             pdf.set_y(current_y)
#         else:
#             # Single line description WITH COMMA FORMATTING
#             pdf.cell(col_widths[0], 6, desc, border=1)
#             pdf.cell(col_widths[1], 6, f"{basic_price:,.2f}", border=1, align="R")
#             pdf.cell(col_widths[2], 6, f"{gst_amount:,.2f}", border=1, align="R")
#             pdf.cell(col_widths[3], 6, f"{per_unit_price:,.2f}", border=1, align="R")
#             pdf.cell(col_widths[4], 6, f"{qty:.0f}", border=1, align="C")
#             pdf.cell(col_widths[5], 6, f"{total:,.2f}", border=1, align="R")
#             pdf.ln()

#     # Round Off Row (NEW - like PO) WITH COMMA FORMATTING
#     round_off = data.get('round_off', 0.0)
#     pdf.set_font(pdf.default_font, "B", 10)
#     pdf.cell(sum(col_widths[:-1]), 7, "Round Off", border=1, align="R")
#     pdf.cell(col_widths[5], 7, f"{round_off:,.2f}", border=1, align="R")
#     pdf.ln()

#     # Grand Total Row - WITH COMMA FORMATTING
#     grand_total = data.get('grand_total', grand_total_unrounded)
#     pdf.set_font(pdf.default_font, "B", 10)
#     pdf.cell(sum(col_widths[:-1]), 7, "Final Amount to be Paid", border=1, align="R")
#     pdf.cell(col_widths[5], 7, f"{grand_total:,.2f}", border=1, align="R")
#     pdf.ln(15)

#     # --- Enhanced Box for Terms & Conditions and Bank Details ---
#     pdf.set_font(pdf.default_font, "", 9)

#     # Terms & Conditions with ALL terms in bold
#     price_validity = data.get('price_validity', '10 days from Quotation date')
#     terms = [
#         ("1. Above charges are Inclusive of GST.", ""),
#         ("2. Any changes in Govt. duties, Taxes & Forex rate at the time of dispatch shall be applicable.", ""),
#         ("3. TDS should not be deducted at the time of payment as per Govt. NOTIFICATION NO. 21/2012 [F.No.142/10/2012-SO (TPL)] S.O. 1323(E), DATED 13-6-2012.", ""),
#         ("4. ELD licenses are paper licenses that do not contain media.", ""),
#         ("5. An Internet connection is required to access cloud services.", ""),
#         ("6. Training will be charged at extra cost depending on no. of participants.", ""),
#         ("7. Price Validity: ", price_validity),
#         ("8. Payment: ", "100% Advance along with purchase order"),
#         ("9. Delivery period: ", "1-2 Weeks from the date of Purchase Order"),
#         ("10. Support: ","Includes 12 months of technical support and software updates from OEM."),
#         ("11. Installation: ","Online"),
#         ("12. Cheque to be issued on name of: ", '"CM INFOTECH"'),
#         ("13. Order to be placed on: ", "CM INFOTECH \nE/402, Ganesh Glory 11, Near BSNL Office,Jagatpur - Chenpur Road, \nJagatpur Village,Ahmedabad - 382481")
#     ]

#     # Bank Details
#     bank_info = [
#         ("Name", "CM INFOTECH"),
#         ("Account Number", "88130420182"),
#         ("IFSC Code", "IDFB0040335"),
#         ("SWIFT Code", "IDFBINBBMUM"),
#         ("Bank Name", "IDFC FIRST"),
#         ("Branch", "AHMEDABAD - SHYAMAL BRANCH"),
#         ("MSME", "UDYAM-GJ-01-0117646"),
#         ("GSTIN", "24ANMPP4891R1ZX"),
#         ("PAN No", "ANMPP4891R")
#     ]

#     # Box dimensions and styling
#     x_start = pdf.get_x()
#     y_start = pdf.get_y()
#     page_width = pdf.w - 1.6 * pdf.l_margin
#     col1_width = page_width * 0.62  # 60% for Terms
#     col2_width = page_width * 0.38  # 40% for Bank Details
#     padding = 2.5
#     line_height = 4
#     section_spacing = 2

#     # Calculate required height for both columns
#     def calculate_column_height(items, col_width):
#         height = 0
#         for label, value in items:
#             if value:  # If there's a value part
#                 text = f"{label}{value}"
#             else:
#                 text = label
#             lines = pdf.multi_cell(col_width - 2*padding, line_height, text, split_only=True)
#             height += len(lines) * line_height + section_spacing
#         return height + 3*padding  # Add padding

#     terms_height = calculate_column_height(terms, col1_width)

#     # Calculate bank details height WITHOUT signature section
#     bank_items_height = calculate_column_height(bank_info, col2_width)
#     signature_height = 35  # Estimated height for signature section
    
#     # Use the maximum height between terms and bank items + signature
#     box_height = max(terms_height, bank_items_height + signature_height)

#     # Draw the main box
#     pdf.rect(x_start, y_start, page_width, box_height)

#     # Draw vertical separator line
#     pdf.line(x_start + col1_width, y_start, x_start + col1_width, y_start + box_height)

#     # Add section headers
#     pdf.set_font(pdf.default_font, "B", 12)

#     # Terms & Conditions header
#     pdf.set_xy(x_start + padding, y_start + padding)
#     pdf.cell(col1_width - 2*padding, 5, "Terms & Conditions:", ln=True)

#     # Terms content - INSIDE THE BOX
#     terms_y = pdf.get_y()
#     for i, (label, value) in enumerate(terms):
#         pdf.set_xy(x_start + padding, terms_y)
        
#         if i < 6:  # First 6 terms - ALL BOLD
#             pdf.set_font(pdf.default_font, "B", 10)
#             pdf.multi_cell(col1_width - 2*padding, line_height, label)
            
#         elif value:  # Terms 7-13 with mixed formatting (label + bold value)
#             # Write the regular font part
#             pdf.set_font(pdf.default_font, "", 10)
#             pdf.cell(pdf.get_string_width(label), line_height, label, ln=0)
            
#             # Write the bold part
#             pdf.set_font(pdf.default_font, "B", 10)
#             remaining_width = col1_width - 2*padding - pdf.get_string_width(label)
#             pdf.multi_cell(remaining_width, line_height, value)
            
#             # Reset to regular font
#             pdf.set_font(pdf.default_font, "", 10)
#         else:
#             # Regular terms without special formatting
#             pdf.multi_cell(col1_width - 2*padding, line_height, label)
        
#         terms_y = pdf.get_y()

#     # Bank Details header - INSIDE THE BOX
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.set_xy(x_start + col1_width + padding, y_start + padding)
#     pdf.cell(col2_width - 2*padding, 5, "Bank Details:", ln=True)
#     pdf.set_font(pdf.default_font, "", 12)  # Set to regular for labels

#     # Bank details content - INSIDE THE BOX
#     bank_y = pdf.get_y()
#     for label, value in bank_info:
#         pdf.set_xy(x_start + col1_width + padding, bank_y)
        
#         # Write label in regular font
#         pdf.set_font(pdf.default_font, "", 10)
#         pdf.cell(pdf.get_string_width(f"{label}: "), line_height, f"{label}: ", ln=0)
        
#         # Write value in BOLD font
#         pdf.set_font(pdf.default_font, "B", 10)
#         remaining_width = col2_width - 2*padding - pdf.get_string_width(f"{label}: ")
#         pdf.multi_cell(remaining_width, line_height, value)
        
#         bank_y = pdf.get_y()

#     # --- Signature Block INSIDE BANK DETAILS BOX - POSITIONED NEAR BOTTOM ---
#     # Calculate position to place signature near bottom of the box
#     signature_start_y = y_start + box_height - signature_height - 15
    
#     pdf.set_font(pdf.default_font, "B", 10)
#     pdf.set_xy(x_start + col1_width + padding, signature_start_y)
#     pdf.cell(col2_width - 2*padding, 5, "Yours Truly,", ln=True)
    
#     pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
#     pdf.cell(col2_width - 2*padding, 5, "For CM INFOTECH", ln=True)
    
#     # --- Signature Block with Dynamic Sales Person ---
#     sales_person_code = data.get('sales_person_code', 'SD')
#     sales_person_info = SALES_PERSON_MAPPING.get(sales_person_code, SALES_PERSON_MAPPING['SD'])
    
#     # Add stamp between "For CM INFOTECH" and sales person name
#     if data.get('stamp_path') and os.path.exists(data['stamp_path']):
#         try:
#             # Position stamp centered between "For CM INFOTECH" and sales person name
#             stamp_y = pdf.get_y() + 2  # Small space after "For CM INFOTECH"
#             stamp_x = x_start + col1_width + padding  # Center the stamp
#             pdf.image(data['stamp_path'], x=stamp_x, y=stamp_y, w=20)
#             # Move cursor down after stamp
#             pdf.set_y(stamp_y + 20)  # Space for stamp + some padding
#         except:
#             pdf.set_y(pdf.get_y() + 8)  # If stamp fails, add some space
#     else:
#         pdf.set_y(pdf.get_y() + 8)  # Space if no stamp
    
#     pdf.set_font(pdf.default_font, "", 9)
#     pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
#     pdf.cell(col2_width - 2*padding, 4, sales_person_info["name"], ln=True)
    
#     pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
#     pdf.cell(col2_width - 2*padding, 4, "Inside Sales Executive", ln=True)
    
#     # Clickable email in signature
#     pdf.set_font(pdf.default_font, "", 9)
#     pdf.set_text_color(0, 0, 0)
#     pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
#     label = "Email: "
#     pdf.cell(pdf.get_string_width(label), 4, label, ln=0)
#     pdf.set_font(pdf.default_font, "U", 9)
#     pdf.set_text_color(0, 0, 255)
#     pdf.cell(col2_width - 2*padding - pdf.get_string_width(label), 4, sales_person_info["email"], 
#              ln=True, link=f"mailto:{sales_person_info['email']}")
    
#     # Clickable phone in signature
#     pdf.set_text_color(0, 0, 0)
#     pdf.set_font(pdf.default_font, "", 9)
#     pdf.set_xy(x_start + col1_width + padding, pdf.get_y())
#     label = "Mobile: "
#     pdf.cell(pdf.get_string_width(label), 4, label, ln=0)
#     pdf.set_font(pdf.default_font, "U", 9)
#     pdf.set_text_color(0, 0, 255)
#     pdf.cell(col2_width - 2*padding - pdf.get_string_width(label), 4, sales_person_info["mobile"], 
#              ln=True, link=f"tel:{sales_person_info['mobile'].replace(' ', '').replace('+', '')}")
#     pdf.set_text_color(0, 0, 0)

#     # Move cursor below the box
#     pdf.set_xy(x_start, y_start + box_height + 10)

    
# def create_quotation_pdf(quotation_data, logo_path=None, stamp_path=None):
#     """Orchestrates the creation of the two-page PDF."""
#     sales_person_code = quotation_data.get('sales_person_code', 'SD')
#     pdf = QUOTATION_PDF(quotation_number=quotation_data['quotation_number'], 
#                         quotation_date=quotation_data['quotation_date'],
#                         sales_person_code=sales_person_code)
    
#     # Set logo path for header
#     if logo_path and os.path.exists(logo_path):
#         pdf.logo_path = logo_path
    
#     quotation_data['stamp_path'] = stamp_path

#     pdf.add_page()
    
#     # 1. Add Page 1 (Introduction Letter)
#     add_page_one_intro(pdf, quotation_data)

#     # 2. Add Page 2 (Commercials, Terms, Bank Details)
#     add_page_two_commercials(pdf, quotation_data)
    
#     # Handle PDF output properly
#     try:
#         pdf_output = pdf.output(dest='S')
        
#         if isinstance(pdf_output, str):
#             return pdf_output.encode('latin-1')
#         elif isinstance(pdf_output, bytearray):
#             return bytes(pdf_output)
#         elif isinstance(pdf_output, bytes):
#             return pdf_output
#         else:
#             return str(pdf_output).encode('latin-1')
            
#     except Exception:
#         # Fallback method
#         try:
#             buffer = io.BytesIO()
#             pdf.output(dest=buffer)
#             return buffer.getvalue()
#         except Exception as e:
#             st.error(f"PDF generation failed: {e}")
#             return b""

# from fpdf import FPDF
# # --- PDF Class for Tax Invoice ---
# class PDF(FPDF):
#     def __init__(self):
#         super().__init__()
        
#         font_dir = os.path.join(os.path.dirname(__file__), "fonts")
#         try:
#             self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
#             self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
#             self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
#             self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
#             self.default_font = "Calibri"
#         except:
#             self.default_font = "Helvetica"

#         self.set_font(self.default_font, "", 8)
#         self.set_left_margin(10)
#         self.set_right_margin(15)
        
#         # Store logo file path for use in header
#         self.logo_file = None

#     def header(self):
#         # Add logo on every page (including second page)
#         if self.logo_file and self.page_no() >= 1:  # Show logo on all pages
#             try:
#                 self.image(self.logo_file, x=155, y=8, w=50)
#             except Exception as e:
#                 # You can add a warning here if needed, but don't show in header
#                 pass
#         self.ln(9)
#         self.set_font(self.default_font, "B", 15)
#         self.cell(0, 6, "TAX INVOICE", ln=True, align="C")
#         self.ln(5)
        
#     def footer(self):
#         # Position at 1.5 cm from bottom
#         self.set_y(-15)
        
#         # Footer content
#         self.set_font(self.default_font, "I", 10)
#         self.cell(0, 4, "This is a Computer Generated Invoice", ln=True, align="C")
        
#         self.set_font(self.default_font, "", 10)
#         self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
#         # Clickable contact info
#         self.set_font(self.default_font, "U", 10)
#         self.set_text_color(0, 0, 255)
        
#         email1 = "info@cminfotech.com"
#         phone_number = "+91 873 391 5721"
#         website = "www.cminfotech.com"
        
#         # Center the contact information
#         contact_text = f"{email1} | {phone_number} | {website}"
#         contact_width = self.get_string_width(contact_text)
#         x_contact = (self.w - contact_width) / 2
        
#         self.set_x(x_contact)
#         self.cell(self.get_string_width(email1), 4, email1, link=f"mailto:{email1}")
#         self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | "))
#         self.cell(self.get_string_width(phone_number), 4, phone_number, link=f"tel:{phone_number}")
#         self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | ") + self.get_string_width(phone_number) + self.get_string_width(" | "))
#         self.cell(self.get_string_width(website), 4, website, link="https://www.cminfotech.com/")
        
#         self.set_text_color(0, 0, 0)


# # --- Function to Create Invoice PDF ---
# def create_invoice_pdf(invoice_data, logo_file="logo_final.jpg", stamp_file="stamp.jpg"):
#     pdf = PDF()
#     pdf.set_auto_page_break(auto=True, margin=10)
    
#     # Store logo file path in the PDF instance for use in header
#     pdf.logo_file = logo_file
    
#     pdf.add_page()

#     # --- Logo on top right --- (This will now be handled by header() on all pages)
#     # Remove the individual logo placement since it's now in header()

#     # === HEADER (Vendor + Invoice Details) ===
#     pdf.set_font(pdf.default_font, "B", 13)
#     pdf.cell(95, 8, "CM Infotech.", border="LRT", ln=0)
#     pdf.cell(48, 8, "Invoice No.", border=1, ln=0, align="L")
#     pdf.cell(48, 8, "Invoice Date", border=1, ln=1, align="L")

#     y_left_start = pdf.get_y()

#     # --- Left Side (Vendor Details) ---
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(95, 4, invoice_data['vendor']['address'], border="L")
    
#     # Vendor details lines
#     vendor_lines = [
#         ("GST No.:", invoice_data['vendor']['gst']),
#         ("MSME Registration No.:", invoice_data['vendor']['msme']),
#         ("E-Mail:", "cm.infotech2014@gmail.com"),
#         ("Mobile No.:", "8733915721"),
#     ]
    
#     for i, (label, value) in enumerate(vendor_lines):
#         pdf.set_x(10)
#         pdf.set_font(pdf.default_font, "B", 12)
#         label_width = pdf.get_string_width(label) 
#         pdf.cell(label_width, 6, label, border="L", ln=0)
#         pdf.set_font(pdf.default_font, "", 12)
#         border = "R" if i < len(vendor_lines) - 1 else "R"
#         pdf.cell(95 - label_width, 6, value, border=border, ln=1)

#     y_left_end = pdf.get_y()

#     # --- Right Side (Invoice Details) ---
#     pdf.set_xy(105, y_left_start)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(48, 8, invoice_data['invoice']['invoice_no'], border="LR", ln=0, align="L")
#     pdf.cell(48, 8, invoice_data['invoice']['date'], border="R", ln=1, align="L")

#     # Payment terms - NOW AS INPUT
#     pdf.set_x(105)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(48, 8, "Mode/Terms of Payment:", border="LRT", ln=0)
#     pdf.set_font(pdf.default_font, "", 12)

#     # Use multi_cell to wrap text to next line - NOW USING INPUT VALUE
#     payment_terms = invoice_data['invoice_details'].get('payment_terms', '100% Advance with Purchase')

#     # Get current Y position before adding the cell
#     y_before = pdf.get_y()

#     # Set position and draw the payment terms cell
#     pdf.set_xy(153, y_before)
#     pdf.multi_cell(48, 4, payment_terms, border="LRT", align="L")

#     # Get Y position after adding the cell
#     y_after = pdf.get_y()

#     # Calculate the actual height of the content
#     actual_height = y_after - y_before

#     # If the actual height is less than 8mm, add an empty cell to make up the difference
#     if actual_height < 8:
#         remaining_height = 8 - actual_height
#         pdf.set_xy(153, y_after)
#         pdf.cell(48, remaining_height, "", border="LR", ln=True)

#     # Supplier's reference
#     pdf.set_x(105)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(48, 8, "Supplier's Reference:", border="LRT", ln=0)
#     pdf.set_font(pdf.default_font, "", 12)
#     other_ref_value = invoice_data['Reference']['Suppliers_Reference']
#     pdf.cell(48, 8, other_ref_value, border="LRTB", ln=1)

#     # Other's reference
#     pdf.set_x(105)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(48, 8, "Other's Reference:", border="LRTB", ln=0)
#     pdf.set_font(pdf.default_font, "", 12)
#     other_ref_value = invoice_data['Reference']['Other']
#     pdf.cell(48, 8, other_ref_value, border="LRTB", ln=1)

#     # === BUYER SECTION ===
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(95, 6, "Buyer", border="LT", ln=0)
#     pdf.cell(48, 6, "Buyer's Order No.", border=1, ln=0, align="L")
#     pdf.cell(48, 6, "Buyer's Order Date", border=1, ln=1, align="L")

#     y_buyer_start = pdf.get_y()

#     # --- Buyer Left Details ---
#     y_left_buyer_start = pdf.get_y()
    
#     # Buyer name and address
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(95, 5, invoice_data['buyer']['name'], border="LR", ln=1)
    
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(95, 4, invoice_data['buyer']['address'], border="LR")
    
#     # Buyer contact details
#     buyer_lines = [
#         ("Email:", "dmistry@baseengr.com"),
#         ("Tel No.:", "98987 91813"),
#         ("GST No.:", invoice_data['buyer']['gst']),
#     ]
    
#     for i, (label, value) in enumerate(buyer_lines):
#         pdf.set_x(10)
#         pdf.set_font(pdf.default_font, "B", 12)
#         label_width = pdf.get_string_width(label) + 2
#         pdf.cell(label_width, 6, label, border="L", ln=0)
#         pdf.set_font(pdf.default_font, "", 12)
#         border = "" if i < len(buyer_lines) - 1 else ""
#         pdf.cell(95 - label_width, 6, value, border=border, ln=1)

#     y_buyer_left_end = pdf.get_y()
#     total_left_buyer_height = y_buyer_left_end - y_left_buyer_start

#     # --- Buyer Right Details ---
#     pdf.set_xy(105, y_buyer_start)
    
#     # Row 1: Buyer's Order No/Date
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(48, 4, invoice_data['invoice_details']['buyers_order_no'], border="RB", ln=0, align="L")
#     pdf.cell(48, 4, invoice_data['invoice_details']['buyers_order_date'], border="RB", ln=1, align="L")

#     # Calculate remaining height needed for address space
#     name_height = 5
#     contact_lines_height = 18
#     remaining_height_for_address = total_left_buyer_height - name_height - contact_lines_height
    
#     # Add empty space for address if needed
#     if remaining_height_for_address > 0:
#         pdf.set_x(105)
#         pdf.cell(96, remaining_height_for_address, "", border="R", ln=1)

#     # Row 2: Dispatched Through
#     pdf.set_x(105)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(48, 6, "Dispatched Through", border="LRT", ln=0)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(48, 6, invoice_data['invoice_details']['dispatched_through'], border="RT", ln=1)

#     # Row 3: Destination - NOW AS INPUT
#     pdf.set_x(105)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(48, 6, "Destination", border="LRT", ln=0)
#     pdf.set_font(pdf.default_font, "", 12)
#     destination = invoice_data['invoice_details'].get('destination', 'Vadodara')
#     pdf.cell(48, 6, destination, border="RT", ln=1)

#     # Row 4: Terms of delivery
#     pdf.set_x(105)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(48, 6, "Terms of delivery", border="LRT", ln=0)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(48, 6, invoice_data['invoice_details']['terms_of_delivery'], border="LRT", ln=1)
#     pdf.ln(0.3)
    
#     # --- Item Table Header ---
#     pdf.set_font(pdf.default_font, "B", 12)
#     col_widths = [15, 80, 22, 23, 23, 28]
    
#     # Header row
#     pdf.cell(col_widths[0], 5, "Sr. No.", border=1, align="C")
#     pdf.cell(col_widths[1], 5, "Description of Goods", border=1, align="C")
#     pdf.cell(col_widths[2], 5, "HSN/SAC", border=1, align="C")
#     pdf.cell(col_widths[3], 5, "Quantity", border=1, align="C")
#     pdf.cell(col_widths[4], 5, "Unit Rate", border=1, align="C")
#     pdf.cell(col_widths[5], 5, "Amount", border=1, ln=True, align="C")

#     # --- Items ---
#     pdf.set_font(pdf.default_font, "", 12)
#     line_height = 5

#     # Store HSN/SAC codes for use in tax summary
#     hsn_codes = []
    
#     for i, item in enumerate(invoice_data["items"], start=1):
#         # Store HSN code for tax summary
#         hsn_codes.append(item['hsn'])
        
#         # Check if we need a new page before adding each item
#         if pdf.get_y() + 25 > pdf.page_break_trigger:
#             pdf.add_page()
#             # Re-add header for new page
#             pdf.set_font(pdf.default_font, "B", 12)
#             pdf.cell(col_widths[0], 5, "Sr. No.", border=1, align="C")
#             pdf.cell(col_widths[1], 5, "Description of Goods", border=1, align="C")
#             pdf.cell(col_widths[2], 5, "HSN/SAC", border=1, align="C")
#             pdf.cell(col_widths[3], 5, "Quantity", border=1, align="C")
#             pdf.cell(col_widths[4], 5, "Unit Rate", border=1, align="C")
#             pdf.cell(col_widths[5], 5, "Amount", border=1, ln=True, align="C")
#             pdf.set_font(pdf.default_font, "", 12)
            
#         x_start = pdf.get_x()
#         y_start = pdf.get_y()

#         # Description cell (multi-line)
#         pdf.set_xy(x_start + col_widths[0], y_start)
#         pdf.multi_cell(col_widths[1], line_height, item['description'], border="LRT", align="L")
#         y_after_desc = pdf.get_y()
        
#         row_height = y_after_desc - y_start
        
#         # Other cells for the row WITH COMMA FORMATTING
#         pdf.set_xy(x_start, y_start)
#         pdf.multi_cell(col_widths[0], row_height, str(i), border="LRT", align="C")
        
#         pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
#         pdf.multi_cell(col_widths[2], row_height, item['hsn'], border="LRT", align="C")
        
#         pdf.set_xy(x_start + sum(col_widths[:3]), y_start)
#         pdf.multi_cell(col_widths[3], row_height, str(item['quantity']), border="LRT", align="C")
        
#         pdf.set_xy(x_start + sum(col_widths[:4]), y_start)
#         pdf.multi_cell(col_widths[4], row_height, f"{item['unit_rate']:,.2f}", border="LRT", align="R")  # Added comma formatting
        
#         amount = item['quantity'] * item['unit_rate']
#         pdf.set_xy(x_start + sum(col_widths[:-1]), y_start)
#         pdf.multi_cell(col_widths[5], row_height, f"{amount:,.2f}", border="LRT", align="R")  # Added comma formatting

#         pdf.set_xy(x_start, y_start + row_height)

#     # --- ADD EMPTY PRODUCT TABLE ROW FOR SPACE ---
#     x_start = pdf.get_x()
#     y_start = pdf.get_y()
    
#     # Create an empty row with the same structure
#     empty_row_height = 15  # Height for the empty space row
    
#     pdf.set_xy(x_start, y_start)
#     pdf.multi_cell(col_widths[0], empty_row_height, "", border="LRB", align="C")
    
#     pdf.set_xy(x_start + col_widths[0], y_start)
#     pdf.multi_cell(col_widths[1], empty_row_height, "", border="LRB", align="C")
    
#     pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
#     pdf.multi_cell(col_widths[2], empty_row_height, "", border="LRB", align="C")
    
#     pdf.set_xy(x_start + sum(col_widths[:3]), y_start)
#     pdf.multi_cell(col_widths[3], empty_row_height, "", border="LRB", align="C")
    
#     pdf.set_xy(x_start + sum(col_widths[:4]), y_start)
#     pdf.multi_cell(col_widths[4], empty_row_height, "", border="LRB", align="C")
    
#     pdf.set_xy(x_start + sum(col_widths[:-1]), y_start)
#     pdf.multi_cell(col_widths[5], empty_row_height, "", border="LRB", align="C")
    
#     pdf.set_xy(x_start, y_start + empty_row_height)

#     # Check if we need a new page before totals
#     if pdf.get_y() + 60 > pdf.page_break_trigger:
#         pdf.add_page()

# # --- Totals WITH COMMA FORMATTING ---
#     pdf.set_font(pdf.default_font, "B", 12)
#     total_width = sum(col_widths[:5])
#     pdf.ln(0.2)
#     pdf.cell(total_width, 5, "Basic Amount", border=1, align="L")
#     pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['basic_amount']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting
    
#     pdf.cell(total_width, 5, "SGST @ 9%", border=1, align="L")
#     pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['sgst']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting
    
#     pdf.cell(total_width, 5, "CGST @ 9%", border=1, align="L")
#     pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['cgst']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting
    
#     # Add Round Off row if needed WITH COMMA FORMATTING
#     round_off = invoice_data['totals']['final_amount'] - (invoice_data['totals']['basic_amount'] + invoice_data['totals']['sgst'] + invoice_data['totals']['cgst'])
#     if round_off != 0:
#         pdf.cell(total_width, 5, "Round Off", border=1, align="L")
#         pdf.cell(col_widths[5], 5, f"{round_off:,.2f}", border=1, ln=True, align="R")  # Added comma formatting

#     pdf.cell(total_width, 5, "Final Amount to be Paid", border=1, align="L")
#     pdf.cell(col_widths[5], 5, f"{invoice_data['totals']['final_amount']:,.2f}", border=1, ln=True, align="R")  # Added comma formatting

    
#     # --- Amount in Words ---
#     # First set the position and draw the border
#     pdf.cell(191, 5, "", border=1, ln=True)

#     # Now go back and write the text with mixed formatting
#     pdf.set_y(pdf.get_y() - 5)  # Move back up to the same line
#     pdf.set_x(10)  # Starting X position

#     # Write bold label
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(pdf.get_string_width("Amount Chargeable (in words): "), 5, "Amount Chargeable (in words): ", ln=0)

#     # Write normal value
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(0, 5, invoice_data['totals']['amount_in_words'], ln=True)

#     # Check if we need a new page before tax summary
#     if pdf.get_y() + 60 > pdf.page_break_trigger:
#         pdf.add_page()

#     # --- Tax Summary Table ---
#     pdf.set_font(pdf.default_font, "B", 12)
    
#     # Main header
#     pdf.cell(34, 10, "HSN/SAC", border="LRT", align="C")
#     pdf.cell(34, 10, "Taxable Value", border="LRT", align="C")
#     pdf.cell(60, 5, "Central Tax", border=1, align="C")
#     pdf.cell(63, 5, "State Tax", border=1, ln=True, align="C")

#     # Sub-header
#     pdf.cell(34, 1, "", border="L", ln=False)
#     pdf.cell(34, 1, "", border="L", ln=False)
#     pdf.cell(30, 5, "Rate", border="L", align="C")
#     pdf.cell(30, 5, "Amount", border="LR", align="C")
#     pdf.cell(32, 5, "Rate", border="L", align="C")
#     pdf.cell(31, 5, "Amount", border="LR", ln=True, align="C")

#     pdf.set_font(pdf.default_font, "", 10)
    
#     # Get the HSN code from the first item (assuming all items have same HSN)
#     # If you have multiple HSN codes, you might want to aggregate them differently
#     primary_hsn = hsn_codes[0] if hsn_codes else ""
    
#     hsn_tax_value = sum(item['quantity'] * item['unit_rate'] for item in invoice_data["items"])
#     hsn_sgst = hsn_tax_value * 0.09
#     hsn_cgst = hsn_tax_value * 0.09
    
#     # Data row - using the actual HSN code from products WITH COMMA FORMATTING
#     pdf.cell(34, 5, primary_hsn, border=1, align="C")
#     pdf.cell(34, 5, f"{hsn_tax_value:,.2f}", border=1, align="C")  # Added comma formatting
#     pdf.cell(30, 5, "9%", border=1, align="C")
#     pdf.cell(30, 5, f"{hsn_sgst:,.2f}", border=1, align="C")  # Added comma formatting
#     pdf.cell(32, 5, "9%", border=1, align="C")
#     pdf.cell(31, 5, f"{hsn_cgst:,.2f}", border=1, ln=True, align="C")  # Added comma formatting

#     # Total row WITH COMMA FORMATTING
#     pdf.set_font(pdf.default_font, "B", 10)
#     pdf.cell(34, 5, "Total", border=1, align="C")
#     pdf.cell(34, 5, f"{hsn_tax_value:,.2f}", border=1, align="C")  # Added comma formatting
#     pdf.cell(30, 5, "", border=1, align="C")
#     pdf.cell(30, 5, f"{hsn_sgst:,.2f}", border=1, align="C")  # Added comma formatting
#     pdf.cell(32, 5, "", border=1, align="C")
#     pdf.cell(31, 5, f"{hsn_cgst:,.2f}", border=1, ln=True, align="C")  # Added comma formatting
    
#     # --- Amount in Words ---
#     pdf.set_font(pdf.default_font, "B", 12)
#     # Write just the label part in bold
#     label_part = "Tax Amount (in words): "
#     pdf.cell(pdf.get_string_width(label_part), 5, label_part, border="LTB", ln=0)

#     pdf.set_font(pdf.default_font, "", 12)
#     # Write the value part in normal font and complete the border
#     value_part = invoice_data['totals']['tax_in_words']
#     remaining_width = 189.7 - pdf.get_string_width(label_part)
#     pdf.cell(remaining_width, 5, value_part, border="TRB", ln=True)
    
#     # # Tax in words
#     # pdf.set_font(pdf.default_font, "B", 10)
#     # pdf.cell(191, 5, f"Tax Amount (in words): {invoice_data['totals']['tax_in_words']}", ln=True, border=1)

#     # Check if we need a new page before footer content
#     if pdf.get_y() + 80 > pdf.page_break_trigger:
#         pdf.add_page()

#     # --- Bank Details & Declaration (Side by Side) ---
#     pdf.set_font(pdf.default_font, "B", 10)
#     pdf.cell(95, 5, "Company's Bank Details", ln=0, border=1)
#     pdf.cell(96, 5, "Declaration:", ln=1, border=1)

#     pdf.set_font(pdf.default_font, "", 10)

#     # Left column (bank)
#     bank_text = (
#         "Bank Name : IDFC FIRST\n"
#         "Branch        : AHMEDABAD Shyamal Branch\n"
#         "Account No : 88130420182\n"
#         "IFS Code    : IDFB0040335"
#     )

#     # Save current Y position
#     y_before = pdf.get_y()
#     x_left = pdf.get_x()

#     # Left cell (Bank) with border
#     pdf.multi_cell(95, 5, bank_text, border=1)
#     y_after_left = pdf.get_y()
    
#     # Right cell (Declaration) with border
#     pdf.set_xy(x_left + 95, y_before)
#     pdf.multi_cell(96, 4, invoice_data['declaration'], border=1)
#     y_after_right = pdf.get_y()
    
#     # Set Y to the maximum of both columns
#     max_y = max(y_after_left, y_after_right)
#     pdf.set_y(max_y)

#     # --- Signature Boxes (Side by Side) ---
#     y_signature_start = pdf.get_y()

#     # Left side - Buyer's Company Signature (Blank box for future use)
#     pdf.set_font(pdf.default_font, "B", 10)
#     pdf.cell(95, 6, "Buyer's Company Signature", border="LR", ln=0, align="C")

#     # Right side - Our Company Signature
#     pdf.cell(96, 6, "For CM Infotech.", border="LR", ln=1, align="C")

#     # Create the signature boxes with DIFFERENT heights
#     left_signature_box_height = 33
#     right_signature_box_height = 33

#     # Left signature box (Buyer - Blank)
#     pdf.set_font(pdf.default_font, "I", 10)
#     pdf.set_text_color(128, 128, 128)

#     # Check if buyer logo is available
#     buyer_logo_file = invoice_data.get('buyer', {}).get('logo_file')

#     if buyer_logo_file:
#         try:
#             # Add buyer logo at the top of the left box
#             logo_width = 25
#             logo_x = 10 + (95 - logo_width) / 2
#             logo_y = pdf.get_y() + 4
            
#             # Add buyer company logo
#             pdf.image(buyer_logo_file, x=logo_x, y=logo_y, w=logo_width)
            
#             # Add buyer company name below logo
#             pdf.set_xy(10, logo_y + logo_width + 2)
#             pdf.set_font(pdf.default_font, "B", 9)
#             pdf.cell(95, 4, invoice_data['buyer']['name'], border=0, ln=1, align="C")
            
#             # Add signature line and text
#             pdf.set_xy(10, pdf.get_y() + 8)
#             pdf.set_font(pdf.default_font, "", 9)
#             pdf.cell(95, 4, "_________________________", border=0, ln=1, align="C")
#             pdf.cell(95, 4, "Authorized Signatory", border=0, ln=1, align="C")
            
#             # Draw the border around everything
#             pdf.set_xy(10, y_signature_start + 6)
#             pdf.cell(95, left_signature_box_height, "", border="LRB")
            
#             # Update Y position after left box
#             y_after_left_signature = y_signature_start + 6 + left_signature_box_height
            
#         except Exception as e:
#             st.warning(f"Could not add buyer logo: {e}")
#             # Fallback without logo
#             pdf.multi_cell(95, left_signature_box_height/5, "\n\n(Space for Buyer's Company\nStamp and Signature)", border="LRB", align="C")
#             y_after_left_signature = pdf.get_y()
#     else:
#         # No buyer logo available, show original placeholder
#         pdf.multi_cell(95, left_signature_box_height/5, "\n\n\n(Space for Buyer's Company\nStamp and Signature)", border="LRB", align="C")
#         y_after_left_signature = pdf.get_y()

#     # Right signature box (Our Company)
#     pdf.set_xy(105, y_signature_start + 5)
#     pdf.set_text_color(0, 0, 0)

#     # Add stamp if available
#     if stamp_file:
#         try:
#             stamp_width = 20
#             stamp_x = 105 + (96 - stamp_width) / 2
#             stamp_y = pdf.get_y() + 2
#             pdf.image(stamp_file, x=stamp_x, y=stamp_y, w=stamp_width)
#         except Exception as e:
#             st.warning(f"Could not add stamp: {e}")

#     # Position for the signature text in right box
#     pdf.set_xy(105, y_signature_start + 6 + right_signature_box_height - 10)
#     pdf.set_font(pdf.default_font, "B", 10)
#     pdf.cell(96, 5, "Authorized Signatory", border=0, ln=True, align="C")

#     # Draw border for right signature box
#     pdf.set_xy(105, y_signature_start + 6)
#     pdf.cell(96, right_signature_box_height, "", border="LRB")

#     # Set Y position to continue after both signature boxes
#     pdf.set_y(max(y_after_left_signature, y_signature_start + 6 + right_signature_box_height))

#     pdf_bytes = pdf.output(dest="S").encode('latin-1') if isinstance(pdf.output(dest="S"), str) else pdf.output(dest="S")
#     return pdf_bytes

# # --- PDF Class ---
# class PO_PDF(FPDF):
#     def __init__(self):
#         super().__init__()
#         self.set_auto_page_break(auto=False, margin=10)
#         self.set_left_margin(15)
#         self.set_right_margin(15)
#         self.logo_path = os.path.join(os.path.dirname(__file__),"logo_final.jpg")
#         font_dir = os.path.join(os.path.dirname(__file__), "fonts")
#         try:
#             self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
#             self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
#             self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
#             self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
#             self.default_font = "Calibri"
#         except:
#             self.default_font = "Helvetica"

#         self.website_url = "https://cminfotech.com/"
#     def header(self):
#         self.ln(5)
#         if self.page_no() == 1:
#             # Logo (if available)
#             self.ln(1)
#             if self.logo_path and os.path.exists(self.logo_path):
#                 self.image(self.logo_path, x=155, y=8, w=50,link=self.website_url)
#                 # (self.logo_path, x=155, y=8, w=50)
#                 # (self.logo_path, x=160, y=5.5, w=45,link=self.website_url)
#                 # self.image(self.logo_path, x=150, y=10, w=40)
#             self.ln(4)
#             # Title
#             self.set_font(self.default_font, "BU", 15)
#             self.cell(0, 15, "PURCHASE ORDER", ln=True, align="C")
#             self.ln(1)

#             # PO info
#             self.set_font(self.default_font, "", 12)
#             # PO Number (right aligned)
#             self.set_xy(140,33)
#             self.multi_cell(60,4,
#                             f"PO No: {self.sanitize_text(st.session_state.po_number)}\n"
#                             f"Date: {self.sanitize_text(st.session_state.po_date)}")
#             # self.cell(0, 8, f"PO No: {self.sanitize_text(st.session_state.po_number)}", ln=1, align='R')
#             # # Date (right aligned, under PO Number)
#             # self.cell(0, 8, f"Date: {self.sanitize_text(st.session_state.po_date)}", ln=0, align='R')
#             # self.ln(4)

#     def footer(self):
#         # Position from bottom (same as invoice)
#         self.set_y(-12)
        
#         # Horizontal line
#         # self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
#         # self.ln(2)
        
#         # Footer content - Computer generated text
#         # self.set_font("Helvetica", "I", 10)
#         # self.cell(0, 4, "This is a Computer Generated Quotation", ln=True, align="C")
        
#         # Company address
#         self.set_font("Helvetica", "", 10)
#         self.cell(0, 4, "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Jagatpur Village, Ahmedabad - 382481", ln=True, align="C")
        
#         # Clickable contact info (same as invoice)
#         self.set_font("Helvetica", "U", 10)
#         self.set_text_color(0, 0, 255)  # Blue for links
        
#         email1 = "info@cminfotech.com"
#         phone_number = "+91 873 391 5721"
#         website = "www.cminfotech.com"
        
#         # Center the contact information
#         contact_text = f"{email1} | {phone_number} | {website}"
#         contact_width = self.get_string_width(contact_text)
#         x_contact = (self.w - contact_width) / 2
        
#         self.set_x(x_contact)
#         self.cell(self.get_string_width(email1), 4, email1, link=f"mailto:{email1}")
#         self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | "))
#         self.cell(self.get_string_width(phone_number), 4, phone_number, link=f"tel:{phone_number}")
#         self.set_x(x_contact + self.get_string_width(email1) + self.get_string_width(" | ") + self.get_string_width(phone_number) + self.get_string_width(" | "))
#         self.cell(self.get_string_width(website), 4, website, link="https://www.cminfotech.com/")
        
#         self.set_text_color(0, 0, 0)


#     # def footer(self):
#     #     self.set_y(-18)
#     #     self.set_font(self.default_font, "", 10)
#     #     self.multi_cell(0, 4, "E402, Ganesh Glory 11, Near BSNL Office, Jagatpur - Chenpur Road, Ahmedabad - 382481\n", align="C")
#     #     self.set_text_color(0, 0, 255)
#     #     self.set_font(self.default_font, "U", 10)
#     #     # email1 = "cad@cmi.com"
#     #     email1 = "info@cminfotech.com "
#     #     phone_number =" +91 873 391 5721"
#     #     self.set_text_color(0, 0, 255)
#     #     self.cell(0, 4, f"{email1} | {phone_number}", ln=True, align="C", link=f"mailto:{email1}")
#     #     self.set_x((self.w - 80) / 2)
#     #     self.cell(0, 0, "", link=f"tel:{phone_number}")
#     #     self.set_x((self.w - 60) / 2)
#     #     website ="www.cminfotech.com"
#     #     self.set_text_color(0, 0, 255)
#     #     self.cell(60, 4, f"{website}", ln=True, align="C", link=website)
#     #     self.set_text_color(0, 0, 0)

#     def section_title(self, title):
#         self.set_font(self.default_font, "B", 12)
#         self.cell(0, 6, self.sanitize_text(title), ln=True)
#         self.ln(1)

#     def sanitize_text(self, text):
#         return text.encode('ascii', 'ignore').decode('ascii')
# def number_to_words(number):
#     """Convert number to words"""
#     try:
#         from num2words import num2words
#         return num2words(number, lang='en_IN').title() + " Rupees Only/-"
#     except ImportError:
#         # Simple fallback if num2words is not available
#         words = f"Rupees {number:,.2f} Only/-"
#         return words

# # If you don't have num2words installed, you can install it with:
# # pip install num2words
# def create_po_pdf(po_data, logo_path = "logo_final.jpg"):
#     pdf = PO_PDF()
#     pdf.logo_path = logo_path
#     pdf.add_page()

    
#     # Sanitize all input strings
#     sanitized_vendor_name = pdf.sanitize_text(po_data['vendor_name'])
#     sanitized_vendor_address = pdf.sanitize_text(po_data['vendor_address'])
#     sanitized_vendor_contact = pdf.sanitize_text(po_data['vendor_contact'])
#     sanitized_vendor_mobile = pdf.sanitize_text(po_data['vendor_mobile'])
#     sanitized_gst_no = pdf.sanitize_text(po_data['gst_no'])
#     sanitized_pan_no = pdf.sanitize_text(po_data['pan_no'])
#     sanitized_msme_no = pdf.sanitize_text(po_data['msme_no'])
#     sanitized_bill_to_company = pdf.sanitize_text(po_data['bill_to_company'])
#     sanitized_bill_to_address = pdf.sanitize_text(po_data['bill_to_address'])
#     sanitized_ship_to_company = pdf.sanitize_text(po_data['ship_to_company'])
#     sanitized_ship_to_address = pdf.sanitize_text(po_data['ship_to_address'])
#     sanitized_end_company = pdf.sanitize_text(po_data['end_company'])
#     sanitized_end_address = pdf.sanitize_text(po_data['end_address'])
#     sanitized_end_person = pdf.sanitize_text(po_data['end_person'])
#     sanitized_end_mobile = pdf.sanitize_text(po_data['end_mobile'])
#     sanitized_end_email = pdf.sanitize_text(po_data['end_email'])
#     sanitized_payment_terms = pdf.sanitize_text(po_data['payment_terms'])
#     sanitized_delivery_terms = pdf.sanitize_text(po_data['delivery_terms'])
#     sanitized_prepared_by = pdf.sanitize_text(po_data['prepared_by'])
#     sanitized_authorized_by = pdf.sanitize_text(po_data['authorized_by'])
#     sanitized_company_name = pdf.sanitize_text(po_data['company_name'])
    
#     # # --- Vendor & Bill/Ship ---
#     # pdf.set_font(pdf.default_font, "B", 12)
#     # pdf.section_title("To:")
#     # pdf.set_font(pdf.default_font, "B", 12)
#     # pdf.multi_cell(95, 5, sanitized_vendor_name)
#     # pdf.set_font(pdf.default_font, "", 12)
#     # pdf.multi_cell(95, 5, f"{sanitized_vendor_address}\nKind Attend: {sanitized_vendor_contact}\nMobile: {sanitized_vendor_mobile}")
#     # pdf.ln(5)
#     # # pdf.set_xy(110, pdf.get_y() - 20)
#     # # pdf.set_font(pdf.default_font, "B", 10)
#     # pdf.multi_cell(70, 5, f"Bill To: \n{sanitized_bill_to_company}\n{sanitized_bill_to_address}")
#     # pdf.set_xy(125, pdf.get_y() - 25)
#     # pdf.multi_cell(0, 5, f"Ship To: \n{sanitized_ship_to_company}\n{sanitized_ship_to_address}")
#     # pdf.ln(2)
#     # pdf.multi_cell(0, 5, f"GST NO: {sanitized_gst_no}\nPAN NO: {sanitized_pan_no}\nMSME Registration No: {sanitized_msme_no}")
#     # pdf.ln(2)
#     # --- Vendor & Bill/Ship ---
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.section_title("To:")

#     # Vendor Name (Bold)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.multi_cell(90, 5, sanitized_vendor_name)

#     # Vendor Address (Normal)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(90, 5, sanitized_vendor_address)

#     # Kind Attend: (Bold label + Normal value)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.write(5, "Kind Attend: ")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(95, 5, sanitized_vendor_contact)

#     # Mobile: (Bold label + Normal value)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.write(5, "Mobile: ")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(95, 5, sanitized_vendor_mobile)

#     pdf.ln(5)

#     # Save current Y position
#     start_y = pdf.get_y()

#     # --- BILL TO (Left Side) ---
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(90, 5, "Bill To:", ln=1)
#     # pdf.set_x(10)

#     # Bill To - Company Name in Bold
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.multi_cell(90, 5, sanitized_bill_to_company)

#     # Bill To - Address in Normal
#     # pdf.set_x(10)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(90, 5, sanitized_bill_to_address)

#     # Get Y position after Bill To
#     y_after_bill = pdf.get_y()

#     # --- SHIP TO (Right Side) ---
#     pdf.set_xy(110, start_y)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(90, 5, "Ship To:", ln=1)
#     pdf.set_x(110)

#     # Ship To - Company Name in Bold
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.multi_cell(90, 5, sanitized_ship_to_company)

#     # Ship To - Address in Normal
#     pdf.set_x(110)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(90, 5, sanitized_ship_to_address)

#     # Get Y position after Ship To
#     y_after_ship = pdf.get_y()

#     # Set to the maximum Y position
#     pdf.set_y(max(y_after_bill, y_after_ship))
#     pdf.ln(2)
#     # GST NO:
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.write(5, "GST NO: ")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, sanitized_gst_no)

#     # PAN NO:
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.write(5, "PAN NO: ")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, sanitized_pan_no)

#     # MSME Registration No:
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.write(5, "MSME Registration No: ")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, sanitized_msme_no)

#     pdf.ln(2)
# #  --- Products Table ---
#     col_widths = [65, 22, 30, 25, 15, 22]
#     headers = ["Product", "Basic", "GST TAX @ 18%", "Per Unit Price", "Qty.", "Total"]
#     pdf.set_fill_color(220, 220, 220)
#     pdf.set_font(pdf.default_font, "B", 12)
#     for h, w in zip(headers, col_widths):
#         pdf.cell(w, 6, pdf.sanitize_text(h), border=1, align="C", fill=True)
#     pdf.ln()

#     pdf.set_font(pdf.default_font, "", 12)
#     line_height = 5

#     # Calculate total from all products
#     products_total = 0
#     for p in po_data["products"]:
#         gst_amt = p["basic"] * p["gst_percent"] / 100
#         per_unit_price = p["basic"] + gst_amt
#         total = per_unit_price * p["qty"]
#         products_total += total

#     # Calculate round off to make final amount whole number
#     rounded_total = round(products_total)
#     round_off = rounded_total - products_total

#     # Now display the products table WITH COMMA FORMATTING
#     for p in po_data["products"]:
#         gst_amt = p["basic"] * p["gst_percent"] / 100
#         per_unit_price = p["basic"] + gst_amt
#         total = per_unit_price * p["qty"]
#         name = pdf.sanitize_text(p["name"])

#         num_lines = pdf.multi_cell(col_widths[0], line_height, name, border=0, split_only=True)
#         max_lines = max(len(num_lines), 1)
#         row_height = line_height * max_lines

#         x_start = pdf.get_x()
#         y_start = pdf.get_y()

#         pdf.multi_cell(col_widths[0], line_height, name, border=1)
#         pdf.set_xy(x_start + col_widths[0], y_start)
#         pdf.cell(col_widths[1], row_height, f"{p['basic']:,.2f}", border=1, align="R")  # Added comma formatting
#         pdf.cell(col_widths[2], row_height, f"{gst_amt:,.2f}", border=1, align="R")    # Added comma formatting
#         pdf.cell(col_widths[3], row_height, f"{per_unit_price:,.2f}", border=1, align="R")  # Added comma formatting
#         pdf.cell(col_widths[4], row_height, f"{p['qty']:.2f}", border=1, align="C")
#         pdf.cell(col_widths[5], row_height, f"{total:,.2f}", border=1, align="R")      # Added comma formatting
#         pdf.ln(row_height)

#     # Round Off Row WITH COMMA FORMATTING
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(sum(col_widths[:-1]), 6, "Round Off", border=1, align="R")
#     pdf.cell(col_widths[5], 6, f"{round_off:,.2f}", border=1, align="R")  # Added comma formatting
#     pdf.ln()

#     # Grand Total Row WITH COMMA FORMATTING
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(sum(col_widths[:-1]), 6, "Final Amount to be Paid", border=1, align="R")
#     pdf.cell(col_widths[5], 6, f"{rounded_total:,.2f}", border=1, align="R")  # Added comma formatting
#     pdf.ln(4)

#     # --- Amount in Words ---
#     pdf.ln(5)
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 4, "Amount in Words")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 4, pdf.sanitize_text(po_data['amount_words']))
#     # pdf.ln(2)

#     # --- Terms & Conditions ---
#     # pdf.section_title("Terms & Conditions")
#     pdf.set_font(pdf.default_font, "B", 12)

#     # Taxes
#     pdf.cell(45, 5, "Taxes")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"As specified above")

#     # Payment
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 5, "Payment")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"{sanitized_payment_terms}")

#     # Delivery
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 5, "Delivery")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"{sanitized_delivery_terms}")

#     pdf.ln(2)

#     # --- End User ---
#     pdf.section_title("End User Details")
#     pdf.set_font(pdf.default_font, "", 12)

#     # Company Name
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 5, "Company Name")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"{sanitized_end_company}")

#     # Company Address
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 5, "Company Address")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"{sanitized_end_address}")
#     # Authorization Section

#     # Contact
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 5, "Contact")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"{sanitized_end_person}")

#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 5, "Mobile No:")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"{sanitized_end_mobile}")

#     # Email
#     pdf.set_font(pdf.default_font, "B", 12)
#     pdf.cell(45, 5, "Email")
#     pdf.cell(5, 4, ":")
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.multi_cell(0, 5, f"{sanitized_end_email}")

#     # pdf.ln(2)
#     # pdf.set_font(pdf.default_font, "B", 12)
#     # pdf.cell(45, 5, "Authorized By")
#     # pdf.cell(5, 4, ":")
#     # pdf.set_font(pdf.default_font, "", 12)
#     # pdf.multi_cell(0, 5, f"{sanitized_authorized_by}")
    

#     # --- Footer (Company Name + Stamp) that floats) ---
#     pdf.ln(5)
#     pdf.set_font(pdf.default_font, "", 12)
#     pdf.cell(0, 5, f"For, {sanitized_company_name}", ln=True, border=0, align="L")
#     stamp_path = os.path.join(os.path.dirname(__file__), "stamp.jpg")
#     if os.path.exists(stamp_path):
#         pdf.ln(2)
#         pdf.image(stamp_path, x=pdf.get_x(), y=pdf.get_y(), w=25)
#         pdf.ln(15)

#     pdf_bytes = pdf.output(dest="S").encode('latin-1')
#     return pdf_bytes

# # --- Utility to safely get string from session_state ---
# def safe_str_state(key, default=""):
#     """Ensure session_state value exists and is always a string."""
#     if key not in st.session_state or not isinstance(st.session_state[key], str):
#         st.session_state[key] = str(default)
#     return st.session_state[key] 

# # --- Image Management Functions ---
# def safe_image_path(image_path, default_name):
#     """Safely handle image paths, return None if file doesn't exist"""
#     if image_path and os.path.exists(image_path):
#         return image_path
#     else:
#         st.sidebar.warning(f"⚠ {default_name} not found")
#         return None

# def load_images_from_github():
#     """Download images from GitHub"""
#     logo_path = None
#     stamp_path = None
    
#     try:
#         # Download logo
#         logo_response = requests.get(LOGO_URL, timeout=10)
#         if logo_response.status_code == 200:
#             logo_path = "github_logo.jpg"
#             with open(logo_path, "wb") as f:
#                 f.write(logo_response.content)
#         else:
#             st.sidebar.warning(f"⚠ Could not load logo from GitHub (Status: {logo_response.status_code})")
#     except Exception as e:
#         st.sidebar.warning(f"⚠ Logo download failed: {str(e)}")
    
#     try:
#         # Download stamp
#         stamp_response = requests.get(STAMP_URL, timeout=10)
#         if stamp_response.status_code == 200:
#             stamp_path = "github_stamp.jpg"
#             with open(stamp_path, "wb") as f:
#                 f.write(stamp_response.content)
#         else:
#             st.sidebar.warning(f"⚠ Could not load stamp from GitHub (Status: {stamp_response.status_code})")
#     except Exception as e:
#         st.sidebar.warning(f"⚠ Stamp download failed: {str(e)}")
    
#     return logo_path, stamp_path

# def save_uploaded_file(uploaded_file, filename):
#     """Save uploaded file to disk"""
#     try:
#         with open(filename, "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         return filename
#     except Exception as e:
#         st.sidebar.error(f"Error saving {filename}: {str(e)}")
#         return None

# # --- The main function with Logo/Stamp Management ---
# def main():
#     st.set_page_config(page_title="Document Generator", page_icon="📑", layout="wide")
#     st.title("📑 Document Generator - Invoice, PO & Quotation")

#     # --- Logo and Stamp Configuration in Sidebar ---
#     st.sidebar.header("📷 Company Branding")
    
#     # Option 1: Use GitHub images
#     use_github = st.sidebar.checkbox("Use GitHub Images", value=True, 
#                                    help="Use logo and stamp from GitHub repository")
    
#     # Option 2: Upload custom images
#     uploaded_logo = None
#     uploaded_stamp = None
    
#     if not use_github:
#         st.sidebar.subheader("Upload Custom Images")
#         uploaded_logo = st.sidebar.file_uploader("Upload Company Logo", 
#                                                type=["png", "jpg", "jpeg"], 
#                                                key="global_logo")
#         uploaded_stamp = st.sidebar.file_uploader("Upload Company Stamp", 
#                                                 type=["png", "jpg", "jpeg"], 
#                                                 key="global_stamp")
    
#     # Load images based on selection
#     global_logo_path = None
#     global_stamp_path = None
    
#     if use_github:
#         with st.sidebar.status("Loading images from GitHub..."):
#             global_logo_path, global_stamp_path = load_images_from_github()
            
#             if global_logo_path:
#                 st.sidebar.success("✓ GitHub logo loaded")
#             else:
#                 st.sidebar.error("❌ GitHub logo failed")
                
#             if global_stamp_path:
#                 st.sidebar.success("✓ GitHub stamp loaded")
#             else:
#                 st.sidebar.error("❌ GitHub stamp failed")
#     else:
#         if uploaded_logo:
#             global_logo_path = save_uploaded_file(uploaded_logo, "custom_logo.jpg")
#             if global_logo_path:
#                 st.sidebar.success("✓ Custom logo loaded")
        
#         if uploaded_stamp:
#             global_stamp_path = save_uploaded_file(uploaded_stamp, "custom_stamp.jpg")
#             if global_stamp_path:
#                 st.sidebar.success("✓ Custom stamp loaded")
    
#     # Display image status
#     st.sidebar.subheader("Image Status")
#     if global_logo_path:
#         st.sidebar.info("Logo: ✅ Loaded")
#     else:
#         st.sidebar.error("Logo: ❌ Not available")
    
#     if global_stamp_path:
#         st.sidebar.info("Stamp: ✅ Loaded")
#     else:
#         st.sidebar.error("Stamp: ❌ Not available")

#     # --- Initialize Session State ---
#     if "quotation_seq" not in st.session_state:
#         # Load from file instead of starting from 1
#         st.session_state.quotation_seq = get_current_quotation_sequence()
#     if "quotation_products" not in st.session_state:
#         st.session_state.quotation_products = []
#     if "last_quotation_number" not in st.session_state:
#         st.session_state.last_quotation_number = ""
#     # if "quotation_seq" not in st.session_state:
#     #     st.session_state.quotation_seq = 1
#     # if "quotation_products" not in st.session_state:
#     #     st.session_state.quotation_products = []
#     # if "last_quotation_number" not in st.session_state:
#     #     st.session_state.last_quotation_number = ""
#     if "po_seq" not in st.session_state:
#         # Load from file instead of starting from 1
#         st.session_state.po_seq = get_current_po_sequence()
#     # if "po_seq" not in st.session_state:
#     #     st.session_state.po_seq = 1
#     if "products" not in st.session_state:
#         st.session_state.products = []
#     if "company_name" not in st.session_state:
#         st.session_state.company_name = "CM Infotech"
#     if "po_number" not in st.session_state:
#         st.session_state.po_number = generate_po_number("CP", st.session_state.po_seq)
#     if "po_date" not in st.session_state:
#         st.session_state.po_date = datetime.date.today().strftime("%d-%m-%Y")
#     if "last_po_number" not in st.session_state:
#         st.session_state.last_po_number = ""
#     if "quotation_number" not in st.session_state:
#         st.session_state.quotation_number = generate_quotation_number("SD", st.session_state.quotation_seq)
#     if "current_quote_sales_person" not in st.session_state:
#         st.session_state.current_quote_sales_person = "SD"
#     if "current_po_sales_person" not in st.session_state:
#         st.session_state.current_po_sales_person = "CP"
#     if "current_po_quarter" not in st.session_state:
#         st.session_state.current_po_quarter = get_current_quarter()


#     if "invoice_seq" not in st.session_state:
#         # Load from file instead of starting from 1
#         st.session_state.invoice_seq = get_current_invoice_sequence()
#     # NEW: Invoice session state
#     if "invoice_seq" not in st.session_state:
#         st.session_state.invoice_seq = 1
#     if "invoice_number" not in st.session_state:
#         st.session_state.invoice_number = generate_invoice_number(st.session_state.invoice_seq)
#     if "last_invoice_number" not in st.session_state:
#         st.session_state.last_invoice_number = ""
#     if "current_invoice_quarter" not in st.session_state:
#         st.session_state.current_invoice_quarter = get_current_quarter()
        
#     # Initialize vendor session states
#     if "po_vendor_name" not in st.session_state:
#         st.session_state.po_vendor_name = "Arkance IN Pvt. Ltd."
#     if "po_vendor_address" not in st.session_state:
#         st.session_state.po_vendor_address = "Unit 801-802, 8th Floor, Tower 1..."
#     if "po_vendor_contact" not in st.session_state:
#         st.session_state.po_vendor_contact = "Ms/Mr"
#     if "po_vendor_mobile" not in st.session_state:
#         st.session_state.po_vendor_mobile = "+91 1234567890"
#     if "po_gst_no" not in st.session_state:
#         st.session_state.po_gst_no = "24ANMPP4891R1ZX"
#     if "po_pan_no" not in st.session_state:
#         st.session_state.po_pan_no = "ANMPP4891R"
#     if "po_msme_no" not in st.session_state:
#         st.session_state.po_msme_no = "UDYAM-GJ-01-0117646"

#     if "quote_end_company" not in st.session_state:
#         st.session_state.quote_end_company = "Baldridge & Associates Pvt Ltd."
#     if "quote_end_address" not in st.session_state:
#         st.session_state.quote_end_address = "406 Sakar East, Vadodara 390009"
#     if "quote_end_person" not in st.session_state:
#         st.session_state.quote_end_person = "Mr. Dev"
#     if "quote_end_mobile" not in st.session_state:
#         st.session_state.quote_end_mobile = "1234567891"
#     if "quote_end_email" not in st.session_state:
#         st.session_state.quote_end_email = "info@company.com"
#     if "quote_end_gst_no" not in st.session_state:
#         st.session_state.quote_end_gst_no = "24AAHCB9"
    

#     # --- Upload Excel and Load Vendor/End User ---
#     uploaded_excel = st.file_uploader("📂 Upload Vendor & End User Excel", type=["xlsx"])

#     if uploaded_excel:
#         vendors_df = pd.read_excel(uploaded_excel, sheet_name="Vendors", dtype={"Mobile": str})
#         endusers_df = pd.read_excel(uploaded_excel, sheet_name="EndUsers")

#         st.success("✅ Excel loaded successfully!")

#         # --- Select Vendor ---
#         vendor_name = st.selectbox("Select Vendor", vendors_df["Vendor Name"].unique())
#         vendor = vendors_df[vendors_df["Vendor Name"] == vendor_name].iloc[0]

#         # --- Select End User ---
#         end_user_name = st.selectbox("Select End User", endusers_df["End User Company"].unique())
#         end_user = endusers_df[endusers_df["End User Company"] == end_user_name].iloc[0]

#         # --- Clean and Convert Mobile (avoid float or NaN issues) ---
#         def safe_strip(value):
#             """Safely convert any value to string and strip whitespace."""
#             try:
#                 if pd.isna(value):
#                     return ""
#                 return str(value).split(".")[0].strip()
#             except Exception:
#                 return ""

#         vendor_mobile = safe_strip(vendor.get("Mobile", ""))
#         End_user_mobile = safe_strip(end_user.get("End Mobile", ""))

#         # Save to session_state (so Invoice & PO can use)
#         st.session_state.po_vendor_name = vendor["Vendor Name"]
#         st.session_state.po_vendor_address = vendor["Vendor Address"]
#         st.session_state.po_vendor_contact = vendor["Contact Person"]
#         st.session_state.po_vendor_mobile = vendor_mobile
#         st.session_state.po_end_company = end_user["End User Company"]
#         st.session_state.po_end_address = end_user["End User Address"]
#         st.session_state.po_end_person = end_user["End User Contact"]
#         st.session_state.po_end_mobile = End_user_mobile
#         st.session_state.po_end_email = end_user["End User Email"]
#         st.session_state.po_end_gst_no = end_user["GST NO"]

#         st.info("Vendor & End User details auto-filled from Excel ✅")

#     # Create tabs for different document types
#     tab1, tab2, tab3 = st.tabs(["Quotation Generator", "Purchase Order Generator", "Tax Invoice Generator"])

#     # --- Tab 1: Quotation Generator ---
#     with tab1:
#         st.header("📑 Adobe Software Quotation Generator")
        
#         today = datetime.date.today()
#         current_quarter = get_current_quarter()
        
#         # Sales Person Selection - ONLY ONE SELECTION
#         st.sidebar.header("Quotation Settings")
#         sales_person = st.sidebar.selectbox("Select Sales Person", 
#                                         options=list(SALES_PERSON_MAPPING.keys()), 
#                                         format_func=lambda x: f"{x} - {SALES_PERSON_MAPPING[x]['name']}",
#                                         key="quote_sales_person")
        
#         # Get current sales person info
#         current_sales_person_info = SALES_PERSON_MAPPING.get(sales_person, SALES_PERSON_MAPPING['SD'])
        
#         # Generate quotation number based on selected sales person
#         def get_quotation_number():
#             # Check if we need to increment sequence
#             if st.session_state.last_quotation_number:
#                 try:
#                     last_prefix, last_sales_person, last_quarter, last_date, last_year_range, last_sequence = parse_quotation_number(st.session_state.last_quotation_number)
                    
#                     if last_sales_person == sales_person and last_quarter == current_quarter:
#                         # Same sales person and same quarter, increment sequence
#                         next_sequence = get_next_sequence_number(st.session_state.last_quotation_number)
#                         return generate_quotation_number(sales_person, next_sequence)
#                     else:
#                         # Different sales person or new quarter, start from sequence 1
#                         return generate_quotation_number(sales_person, 1)
#                 except:
#                     # If parsing fails, use current sequence
#                     return generate_quotation_number(sales_person, st.session_state.quotation_seq)
#             else:
#                 # No previous quotation, start from current sequence
#                 return generate_quotation_number(sales_person, st.session_state.quotation_seq)
        
#         # Initialize or update quotation number when sales person changes
#         if "current_quote_sales_person" not in st.session_state:
#             st.session_state.current_quote_sales_person = sales_person
#             st.session_state.quotation_number = get_quotation_number()
        
#         # Update quotation number if sales person changes or quarter changes
#         if (st.session_state.current_quote_sales_person != sales_person or 
#             st.session_state.get('current_quarter', '') != current_quarter):
#             st.session_state.current_quote_sales_person = sales_person
#             st.session_state.current_quarter = current_quarter
#             st.session_state.quotation_number = get_quotation_number()
        
#         # Display current sales person info
#         st.sidebar.info(f"**Current Sales Person:** {current_sales_person_info['name']}")
#         st.sidebar.info(f"**Current Quarter:** {current_quarter}")
        
#         # Show auto-generated breakdown
#         try:
#             prefix, current_sp, quarter, date_part, year_range, sequence = parse_quotation_number(st.session_state.quotation_number)
#             st.sidebar.success(f"**Auto-generated Quotation Number**")
#             st.sidebar.info(f"**Format:** {current_sp}/{quarter}/{date_part}/{year_range}_{sequence}")
#         except:
#             st.sidebar.warning("Could not parse quotation number")
        
#         # Editable quotation number WITHOUT sales person selection
#         st.sidebar.subheader("Quotation Number Editor")
        
#         # Parse current quotation number for editing
#         try:
#             current_prefix, current_sp, current_q, current_date, current_year_range, current_seq = parse_quotation_number(st.session_state.quotation_number)
            
#             # Create editable components (NO SALES PERSON SELECTION)
#             col1, col2, col3, col4 = st.sidebar.columns([1, 2, 2, 1])
            
#             with col1:
#                 # Show current sales person (read-only)
#                 st.text_input("Sales Person", value=current_sp, key="quote_sp_display", disabled=True)
            
#             with col2:
#                 new_date = st.text_input("Date", value=current_date, key="quote_date_edit")
            
#             with col3:
#                 new_year_range = st.text_input("Year Range", value=current_year_range, key="quote_year_edit")
            
#             with col4:
#                 new_sequence = st.number_input("Sequence", 
#                                             min_value=1, 
#                                             value=int(current_seq), 
#                                             step=1,
#                                             key="quote_seq_edit")
            
#             # Construct new quotation number using the SELECTED sales person, not the edited one
#             new_quotation_number = f"CMI/{sales_person}/{current_q}/{new_date}/{new_year_range}_{new_sequence:03d}"
            
#             # Update if changed
#             if new_quotation_number != st.session_state.quotation_number:
#                 st.session_state.quotation_number = new_quotation_number
                
#         except Exception as e:
#             st.sidebar.error(f"Error parsing quotation number: {e}")
#             # Fallback to default
#             st.session_state.quotation_number = generate_quotation_number(sales_person, st.session_state.quotation_seq)
        
#         # Display final quotation number
#         st.sidebar.code(st.session_state.quotation_number)
        
#         quotation_auto_increment = st.sidebar.checkbox("Auto-increment Sequence", value=True, key="quote_auto_increment")
        
#         if st.sidebar.button("Reset to Auto-generate", use_container_width=True):
#             st.session_state.quotation_seq = 1
#             st.session_state.last_quotation_number = ""
#             st.session_state.quotation_number = get_quotation_number()
#             st.sidebar.success("Quotation number reset to auto-generated")
#             st.rerun()
        
#         # Main form
#         col1, col2 = st.columns([1, 1])
        
#         with col1:
#             st.header("Recipient Details")
            
#             # REPLACE VENDOR DROPDOWN WITH END USER DROPDOWN
#             selected_enduser_quote = st.selectbox(
#                 "Select Company", 
#                 options=get_enduser_dropdown_options(),
#                 key="enduser_dropdown_quote"
#             )
            
#             # UPDATE END USER FIELDS WHEN DROPDOWN SELECTION CHANGES FOR QUOTATION
#             if selected_enduser_quote and selected_enduser_quote != "Select End User":
#                 enduser_data = END_USER_DATABASE.get(selected_enduser_quote, {})
#                 st.session_state.quote_end_company = selected_enduser_quote
#                 st.session_state.quote_end_address = enduser_data.get("address", "")
#                 st.session_state.quote_end_person = enduser_data.get("contact", "")
#                 st.session_state.quote_end_mobile = enduser_data.get("mobile", "")
#                 st.session_state.quote_end_email = enduser_data.get("email", "")
#                 st.session_state.quote_end_gst_no = enduser_data.get("gst_no", "")
            
#             # UPDATE TEXT INPUT FIELDS TO USE END USER DATA INSTEAD OF VENDOR DATA
#             vendor_name = st.text_input("Company Name", 
#                                     value=st.session_state.get("quote_end_company", "Baldridge & Associates Pvt Ltd."), 
#                                     key="quote_end_company")
#             vendor_address = st.text_area("Company Address", 
#                                         value=st.session_state.get("quote_end_address", "406 Sakar East, Vadodara 390009"), 
#                                         key="quote_end_address")
#             vendor_email = st.text_input("Email", 
#                                     value=st.session_state.get("quote_end_email", "info@company.com"), 
#                                     key="quote_end_email")
#             vendor_contact = st.text_input("Contact Person (Kind Attention)", 
#                                         value=st.session_state.get("quote_end_person", "Mr. Dev"), 
#                                         key="quote_end_person")
#             vendor_mobile = st.text_input("Mobile", 
#                                         value=st.session_state.get("quote_end_mobile", "1234567891"), 
#                                         key="quote_end_mobile")
            
#             # You can also add GST field if needed
#             vendor_gst = st.text_input("GST No (Optional)", 
#                                     value=st.session_state.get("quote_end_gst_no", ""), 
#                                     key="quote_end_gst_no")

#             st.header("Quotation Details")
#             price_validity = st.text_input("Price Validity", "10 days from Quotation date", key="quote_price_validity")
#             subject_line = st.text_input("Subject", "Proposal for Adobe Commercial Software License", key="quote_subject")
#             intro_paragraphs_1 = st.text_area("Introduction Paragraph",
#             """This is with reference to your requirement for Adobe Software. It gives us great pleasure to know that we are being considered by you and are invited to fulfill the requirements of your organization. """,
#             key="quote_intro"
#             )

        
#         with col2:
#             st.header("Products & Services")
            
#             # Add input fields for both annexure and quotation title
#             col_annexure, col_title = st.columns(2)
            
#             with col_annexure:
#                 annexure_text = st.text_input(
#                     "Annexure Text", 
#                     "Annexure I - Commercials", 
#                     key="quote_annexure_input",
#                     help="Enter annexure text (e.g., Annexure I - Commercials, Annexure II - Terms)"
#                 )
            
#             with col_title:
#                 quotation_title = st.text_input(
#                     "Quotation Title", 
#                     "Quotation for Adobe Software", 
#                     key="quote_title_input",
#                     help="Enter the main title that will appear below annexure"
#                 )
            
#             # --- SAME PRODUCT SELECTION LOGIC AS PO ---
#             st.subheader("Add Products")
#             selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="quote_product_select_catalog")
            
#             if st.button("➕ Add Selected Product", key="quote_add_selected_product"):
#                 if selected_product:
#                     details = PRODUCT_CATALOG[selected_product]
#                     st.session_state.quotation_products.append({
#                         "name": selected_product,
#                         "basic": details["basic"],
#                         "gst_percent": details["gst_percent"],
#                         "qty": 1.0,
#                     })
#                     st.success(f"{selected_product} added!")
            
#             if st.button("➕ Add Empty Product", key="quote_add_empty_product"):
#                 st.session_state.quotation_products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

#             # Display current products with EDITABLE fields (same as PO)
#             st.subheader("Current Products")
#             for i, p in enumerate(st.session_state.quotation_products):
#                 with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
#                     st.session_state.quotation_products[i]["name"] = st.text_input("Name", p["name"], key=f"quote_name_{i}")
#                     st.session_state.quotation_products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"quote_basic_{i}")
#                     st.session_state.quotation_products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"quote_gst_{i}")
#                     st.session_state.quotation_products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"quote_qty_{i}")
#                     if st.button("Remove", key=f"quote_remove_{i}"):
#                         st.session_state.quotation_products.pop(i)
#                         st.rerun()
        
#         # Preview and Generate Section
#         st.header("Preview & Generate Quotation")
        
#         # Show the current quotation number prominently with sales person info
#         st.info(f"**Quotation Number:** {st.session_state.quotation_number}")
#         st.info(f"**Sales Person:** {current_sales_person_info['name']} ({sales_person}) - {current_sales_person_info['email']}")
        
#         # Calculate totals
#         # Calculate totals with round-off (like PO)
#         totals = calculate_quotation_totals(st.session_state.quotation_products)
        
#         # Preview and totals calculation (same as PO)
#         total_base = sum(p["basic"] * p["qty"] for p in st.session_state.quotation_products)
#         total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.quotation_products)
#         grand_total = total_base + total_gst
#         amount_words = num2words(grand_total, to="currency", currency="INR").title()
        
#         col3, col4, col5 = st.columns(3)
#         with col3:
#             st.metric("Total Base Amount", f"₹{total_base:,.2f}")
#         with col4:
#             st.metric("Total GST", f"₹{total_gst:,.2f}")
#         with col5:
#             st.metric("Grand Total", f"₹{grand_total:,.2f}")
        
#         # Use global images
#         st.subheader("Company Branding")
#         st.info("Using global logo and stamp from sidebar settings")
#         logo_path = global_logo_path
#         stamp_path = global_stamp_path

#         if not logo_path:
#             st.warning("⚠ No company logo available")
#         if not stamp_path:
#             st.warning("⚠ No company stamp available")
        
#         if st.button("Generate Quotation PDF", type="primary", use_container_width=True, key="generate_quote"):
#             if not st.session_state.quotation_products:
#                 st.error("Please add at least one product to generate the quotation.")
#             else:
#                 # Calculate total from all products (same as PO logic)
#                 products_total = 0
#                 for p in st.session_state.quotation_products:
#                     gst_amt = p["basic"] * p["gst_percent"] / 100
#                     per_unit_price = p["basic"] + gst_amt
#                     total = per_unit_price * p["qty"]
#                     products_total += total

#                 # Calculate round off to make final amount whole number (same as PO)
#                 rounded_total = round(products_total)
#                 round_off = rounded_total - products_total

#                 # Update grand_total and amount_words with rounded amount
#                 grand_total = rounded_total
#                 amount_words = number_to_words(rounded_total)

#                 quotation_data = {
#                     "quotation_number": st.session_state.quotation_number,
#                     "quotation_date": today.strftime("%d-%m-%Y"),
#                     "vendor_name": vendor_name,
#                     "vendor_address": vendor_address,
#                     "vendor_email": vendor_email,
#                     "vendor_contact": vendor_contact,
#                     "vendor_mobile": vendor_mobile,
#                     "products": st.session_state.quotation_products,
#                     "price_validity": price_validity,
#                     "grand_total": grand_total,  # Updated with rounded amount
#                     "round_off": round_off,  # Include round off for display
#                     "amount_words": amount_words,  # Words for rounded amount
#                     "subject": subject_line,
#                     "intro_paragraph": intro_paragraphs_1,
#                     "product_name": selected_product if selected_product else "Software",   
#                     "sales_person_code": sales_person,  
#                     "annexure_text": annexure_text,  
#                     "quotation_title": quotation_title
#                 }
                
#                 try:
#                     pdf_bytes = create_quotation_pdf(quotation_data, logo_path, stamp_path)
                    
#                     # Store the last quotation number for sequence tracking
#                     st.session_state.last_quotation_number = st.session_state.quotation_number
                    
#                     # Auto-increment for next quotation
#                     if quotation_auto_increment:
#                         # This automatically increments and saves to file
#                         next_sequence = get_next_quotation_sequence()
#                         st.session_state.quotation_seq = next_sequence
#                     # if quotation_auto_increment:
#                     #     try:
#                     #         next_sequence = get_next_sequence_number(st.session_state.quotation_number)
#                     #         # Update the sequence in session state for next time
#                     #         st.session_state.quotation_seq = next_sequence
#                     #     except:
#                     #         st.session_state.quotation_seq += 1
                    
#                     st.success("✅ Quotation generated successfully!")
#                     st.info(f"📧 Sales Person: {current_sales_person_info['name']}")
                    
#                     # Download button
#                     st.download_button(
#                         "⬇ Download Quotation PDF",
#                         data=pdf_bytes,
#                         file_name=f"{vendor_name}_{st.session_state.quotation_number.replace('/', '_')}.pdf",
#                         mime="application/pdf",
#                         use_container_width=True
#                     )
                    
#                 except Exception as e:
#                     st.error(f"Error generating PDF: {str(e)}")

                
#     # --- Tab 2: Purchase Order Generator ---
#     with tab2:
#         st.header("Purchase Order Generator")
        
#         today = datetime.date.today()
#         current_quarter = get_current_quarter()
        
#         # PO Settings in sidebar for this tab
#         st.sidebar.header("PO Settings")
        
#         # Sales Person Selection for PO
#         po_sales_person = st.sidebar.selectbox("Select Sales Person", 
#                                             options=list(SALES_PERSON_MAPPING.keys()), 
#                                             format_func=lambda x: f"{x} - {SALES_PERSON_MAPPING[x]['name']}",
#                                             key="po_sales_person_select")
        
#         # Get current sales person info
#         current_sales_person_info = SALES_PERSON_MAPPING.get(po_sales_person, SALES_PERSON_MAPPING['CP'])
        
#         # Generate PO number based on selected sales person
#         def get_po_number():
#             # Check if we need to increment sequence
#             if st.session_state.last_po_number:
#                 try:
#                     last_prefix, last_sales_person, last_year, last_quarter, last_sequence = parse_po_number(st.session_state.last_po_number)
                    
#                     if last_sales_person == po_sales_person and last_quarter == current_quarter:
#                         # Same sales person and same quarter, increment sequence
#                         next_sequence = get_next_sequence_number_po(st.session_state.last_po_number)
#                         return generate_po_number(po_sales_person, next_sequence)
#                     else:
#                         # Different sales person or new quarter, start from sequence 1
#                         return generate_po_number(po_sales_person, 1)
#                 except:
#                     # If parsing fails, use current sequence
#                     return generate_po_number(po_sales_person, st.session_state.po_seq)
#             else:
#                 # No previous PO, start from current sequence
#                 return generate_po_number(po_sales_person, st.session_state.po_seq)
        
#         # Initialize or update PO number when sales person changes
#         if "current_po_sales_person" not in st.session_state:
#             st.session_state.current_po_sales_person = po_sales_person
#             st.session_state.po_number = get_po_number()
        
#         # Update PO number if sales person changes or quarter changes
#         if (st.session_state.current_po_sales_person != po_sales_person or 
#             st.session_state.get('current_po_quarter', '') != current_quarter):
#             st.session_state.current_po_sales_person = po_sales_person
#             st.session_state.current_po_quarter = current_quarter
#             st.session_state.po_number = get_po_number()
        
#         # Display current sales person info
#         st.sidebar.info(f"**Current Sales Person:** {current_sales_person_info['name']}")
#         st.sidebar.info(f"**Current Quarter:** {current_quarter}")
        
#         # Show auto-generated breakdown
#         try:
#             prefix, current_sp, year, quarter, sequence = parse_po_number(st.session_state.po_number)
#             st.sidebar.success(f"**Auto-generated PO Number**")
#             st.sidebar.info(f"**Format:** {current_sp}/{year}/{quarter}_{sequence}")
#         except:
#             st.sidebar.warning("Could not parse PO number")
        
#         # Editable PO number WITH sales person selection
#         st.sidebar.subheader("PO Number Editor")
        
#         # Parse current PO number for editing
#         try:
#             current_prefix, current_sp, current_year, current_q, current_seq = parse_po_number(st.session_state.po_number)
            
#             # Create editable components
#             col1, col2, col3, col4 = st.sidebar.columns([1, 2, 2, 1])
            
#             with col1:
#                 # Show current sales person (read-only)
#                 st.text_input("Sales Person", value=current_sp, key="po_sp_display", disabled=True)
            
#             with col2:
#                 new_year = st.text_input("Year", value=current_year, key="po_year_edit")
            
#             with col3:
#                 new_quarter = st.text_input("Quarter", value=current_q, key="po_quarter_edit")
            
#             with col4:
#                 new_sequence = st.number_input("Sequence", 
#                                             min_value=1, 
#                                             value=int(current_seq), 
#                                             step=1,
#                                             key="po_seq_edit")
            
#             # Construct new PO number using the SELECTED sales person, not the edited one
#             new_po_number = f"CMI/{po_sales_person}/{new_year}/{new_quarter}_{new_sequence:03d}"
            
#             # Update if changed
#             if new_po_number != st.session_state.po_number:
#                 st.session_state.po_number = new_po_number
                
#         except Exception as e:
#             st.sidebar.error(f"Error parsing PO number: {e}")
#             # Fallback to default
#             st.session_state.po_number = generate_po_number(po_sales_person, st.session_state.po_seq)
        
#         # Display final PO number
#         st.sidebar.code(st.session_state.po_number)
        
#         po_auto_increment = st.sidebar.checkbox("Auto-increment Sequence", value=True, key="po_auto_increment_checkbox")
        
#         if st.sidebar.button("Reset to Auto-generate", use_container_width=True, key="po_reset_auto_generate"):
#             st.session_state.po_seq = 1
#             st.session_state.last_po_number = ""
#             st.session_state.po_number = get_po_number()
#             st.sidebar.success("PO number reset to auto-generated")
#             st.rerun()
        
#         tab_vendor, tab_products, tab_terms, tab_preview = st.tabs(["Vendor Details", "Products", "Terms", "Preview & Generate"])
        
#         with tab_vendor:
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.subheader("Vendor Selection")
                
#                 # Vendor Dropdown
#                 selected_vendor = st.selectbox(
#                     "Select Vendor", 
#                     options=get_vendor_dropdown_options(),
#                     key="vendor_dropdown_po"
#                 )
                
#                 # Update vendor fields when dropdown selection changes
#                 if selected_vendor and selected_vendor != "Select Vendor":
#                     update_vendor_fields(selected_vendor)
                
#                 st.subheader("Vendor Details")
#                 vendor_name = st.text_input(
#                     "Vendor Name",
#                     value=st.session_state.get("po_vendor_name", "Arkance IN Pvt. Ltd."),
#                     key="po_vendor_name"
#                 )
#                 vendor_address = st.text_area(
#                     "Vendor Address",
#                     value=st.session_state.get("po_vendor_address", "Unit 801-802, 8th Floor, Tower 1..."),
#                     key="po_vendor_address"
#                 )
#                 vendor_contact = st.text_input(
#                     "Contact Person",
#                     value=st.session_state.get("po_vendor_contact", "Ms/Mr"),
#                     key="po_vendor_contact"
#                 )
#                 vendor_mobile = st.text_input(
#                     "Mobile",
#                     value=st.session_state.get("po_vendor_mobile", "+91 1234567890"),
#                     key="po_vendor_mobile"
#                 )
                
#                 st.subheader("End User Details")
                
#                 # End User Dropdown
#                 selected_enduser = st.selectbox(
#                     "Select End User", 
#                     options=get_enduser_dropdown_options(),
#                     key="enduser_dropdown_po"
#                 )
                
#                 # Update end user fields when dropdown selection changes
#                 if selected_enduser and selected_enduser != "Select End User":
#                     update_enduser_fields(selected_enduser)
                
#                 end_company = st.text_input(
#                     "End User Company",
#                     value=st.session_state.get("po_end_company", "Baldridge & Associates Pvt Ltd."),
#                     key="po_end_company"
#                 )
#                 end_address = st.text_area(
#                     "End User Address",
#                     value=st.session_state.get("po_end_address", "406 Sakar East, Vadodara 390009"),
#                     key="po_end_address"
#                 )
#                 end_person = st.text_input(
#                     "End User Contact",
#                     value=st.session_state.get("po_end_person", "Mr. Dev"),
#                     key="po_end_person"
#                 )
#                 end_mobile = st.text_input(
#                     "End Mobile",
#                     value=str(st.session_state.get("po_end_mobile", "1234567891") or "").strip(),
#                     key="po_end_mobile"
#                 )
#                 end_email = st.text_input(
#                     "End User Email",
#                     value=st.session_state.get("po_end_email", "info@company.com"),
#                     key="po_end_email"
#                 )


#             with col2:
#                 st.subheader("Company & Tax Details")
#                 bill_to_company = st.text_input(
#                     "Bill To",
#                     value=safe_str_state("po_bill_to_company", "CM INFOTECH"),
#                     key="po_bill_to_company_input"
#                 )
#                 bill_to_address = st.text_area(
#                     "Bill To Address",
#                     value=safe_str_state("po_bill_to_address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481"),
#                     key="po_bill_to_address_input"
#                 )
#                 ship_to_company = st.text_input(
#                     "Ship To",
#                     value=safe_str_state("po_ship_to_company", "CM INFOTECH"),
#                     key="po_ship_to_company_input"
#                 )
#                 ship_to_address = st.text_area(
#                     "Ship To Address",
#                     value=safe_str_state("po_ship_to_address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur Chenpur Road, Jagatpur Village, Ahmedabad - 382481"),
#                     key="po_ship_to_address_input"
#                 )
#                 gst_no = st.text_input(
#                     "GST No",
#                     value=st.session_state.get("po_gst_no", "24ANMPP4891R1ZX"),
#                     key="po_gst_no_input"
#                 )
#                 pan_no = st.text_input(
#                     "PAN No",
#                     value=st.session_state.get("po_pan_no", "ANMPP4891R"),
#                     key="po_pan_no_input"
#                 )
#                 msme_no = st.text_input(
#                     "MSME No",
#                     value=st.session_state.get("po_msme_no", "UDYAM-GJ-01-0117646"),
#                     key="po_msme_no_input"
#                 )

#         with tab_products:
#             st.header("Products")
#             selected_product = st.selectbox("Select from Catalog", [""] + list(PRODUCT_CATALOG.keys()), key="po_product_select_catalog")
            
#             if st.button("➕ Add Selected Product", key="po_add_selected_product"):
#                 if selected_product:
#                     details = PRODUCT_CATALOG[selected_product]
#                     st.session_state.products.append({
#                         "name": selected_product,
#                         "basic": details["basic"],
#                         "gst_percent": details["gst_percent"],
#                         "qty": 1.0,
#                     })
#                     st.success(f"{selected_product} added!")
            
#             if st.button("➕ Add Empty Product", key="po_add_empty_product"):
#                 st.session_state.products.append({"name": "New Product", "basic": 0.0, "gst_percent": 18.0, "qty": 1.0})

#             for i, p in enumerate(st.session_state.products):
#                 with st.expander(f"Product {i+1}: {p['name']}", expanded=i == 0):
#                     st.session_state.products[i]["name"] = st.text_input("Name", p["name"], key=f"po_name_{i}")
#                     st.session_state.products[i]["basic"] = st.number_input("Basic (₹)", p["basic"], format="%.2f", key=f"po_basic_{i}")
#                     st.session_state.products[i]["gst_percent"] = st.number_input("GST %", p["gst_percent"], format="%.1f", key=f"po_gst_{i}")
#                     st.session_state.products[i]["qty"] = st.number_input("Qty", p["qty"], format="%.2f", key=f"po_qty_{i}")
#                     if st.button("Remove", key=f"po_remove_{i}"):
#                         st.session_state.products.pop(i)
#                         st.rerun()
                        
#         with tab_terms:
#             st.header("Terms & Authorization")
#             col1, col2 = st.columns(2)
#             with col1:
#                 payment_terms = st.text_input("Payment Terms", "30 Days from Invoice date.", key="po_payment_terms_input")
#                 delivery_days = st.number_input("Delivery (Days)", min_value=1, value=2, key="po_delivery_days_input")
#                 delivery_terms = st.text_input("Delivery Terms", f"Within {delivery_days} Days.", key="po_delivery_terms_input")
#             with col2:
#                 prepared_by = st.text_input("Prepared By", "Finance Department", key="po_prepared_by_input")
#                 authorized_by = st.text_input("Authorized By", "CM INFOTECH", key="po_authorized_by_input")
        
#         with tab_preview:
#             st.header("Preview & Generate")
            
#             # Show the current PO number prominently with sales person info
#             st.info(f"**PO Number:** {st.session_state.po_number}")
#             st.info(f"**Sales Person:** {current_sales_person_info['name']} ({po_sales_person}) - {current_sales_person_info['email']}")
            
#             total_base = sum(p["basic"] * p["qty"] for p in st.session_state.products)
#             total_gst = sum(p["basic"] * p["gst_percent"] / 100 * p["qty"] for p in st.session_state.products)
#             grand_total = total_base + total_gst
#             amount_words = num2words(grand_total, to="currency", currency="INR").title()
#             st.metric("Grand Total", f"₹{grand_total:,.2f}")

#             # Use global logo
#             logo_path = global_logo_path
#             if not logo_path:
#                 st.warning("No company logo available. Please upload one in the sidebar.")
            
#             if st.button("Generate PO", type="primary", key="po_generate_button"):
#                 # Calculate total from all products
#                 products_total = 0
#                 for p in st.session_state.products:
#                     gst_amt = p["basic"] * p["gst_percent"] / 100
#                     per_unit_price = p["basic"] + gst_amt
#                     total = per_unit_price * p["qty"]
#                     products_total += total

#                 # Calculate round off to make final amount whole number
#                 rounded_total = round(products_total)
#                 round_off = rounded_total - products_total

#                 # Update grand_total and amount_words with rounded amount
#                 grand_total = rounded_total
#                 amount_words = number_to_words(rounded_total)  # Use your number to words function

#                 po_data = {
#                     "po_number": st.session_state.po_number,
#                     "po_date": st.session_state.po_date,
#                     "vendor_name": vendor_name,
#                     "vendor_address": vendor_address,
#                     "vendor_contact": vendor_contact,
#                     "vendor_mobile": vendor_mobile,
#                     "gst_no": gst_no,
#                     "pan_no": pan_no,
#                     "msme_no": msme_no,
#                     "bill_to_company": bill_to_company,
#                     "bill_to_address": bill_to_address,
#                     "ship_to_company": ship_to_company,
#                     "ship_to_address": ship_to_address,
#                     "end_company": end_company,
#                     "end_address": end_address,
#                     "end_person": end_person,
#                     "end_mobile": end_mobile,
#                     "end_email": end_email,
#                     "products": st.session_state.products,
#                     "grand_total": grand_total,  # Updated with rounded amount
#                     "amount_words": amount_words,  # Updated with words for rounded amount
#                     "payment_terms": payment_terms,
#                     "delivery_terms": delivery_terms,
#                     "prepared_by": prepared_by,
#                     "authorized_by": authorized_by,
#                     "company_name": st.session_state.company_name
#                 }

#                 pdf_bytes = create_po_pdf(po_data, logo_path)
#                 # Store the last PO number for sequence tracking
#                 st.session_state.last_po_number = st.session_state.po_number
                
#                 # Auto-increment for next PO
#                 if po_auto_increment:
#                     # This automatically increments and saves to file
#                     next_sequence = get_next_po_sequence()
#                     st.session_state.po_seq = next_sequence
#                 # if po_auto_increment:
#                 #     try:
#                 #         next_sequence = get_next_sequence_number_po(st.session_state.po_number)
#                 #         # Update the sequence in session state for next time
#                 #         st.session_state.po_seq = next_sequence
#                 #     except:
#                 #         st.session_state.po_seq += 1

#                 st.success("Purchase Order generated!")
#                 st.info(f"📧 Sales Person: {current_sales_person_info['name']}")
                
#                 st.download_button(
#                     "⬇ Download Purchase Order",
#                     data=pdf_bytes,
#                     file_name=f"PO_{st.session_state.po_number.replace('/', '_')}.pdf",
#                     mime="application/pdf"
#                 )
#     # --- Tab 3: Tax Invoice Generator ---
#     with tab3:
#         st.header("Tax Invoice Generator")
        
#         today = datetime.date.today()
#         current_quarter = get_current_quarter()
        
#         # Invoice Settings in sidebar for this tab
#         st.sidebar.header("Invoice Settings")
        
#         # Generate invoice number based on current quarter
#         def get_invoice_number():
#             # Check if we need to increment sequence
#             if st.session_state.last_invoice_number:
#                 try:
#                     last_prefix, last_year_range, last_quarter, last_sequence = parse_invoice_number(st.session_state.last_invoice_number)
                    
#                     if last_quarter == current_quarter:
#                         # Same quarter, increment sequence
#                         next_sequence = get_next_sequence_number_invoice(st.session_state.last_invoice_number)
#                         return generate_invoice_number(next_sequence)
#                     else:
#                         # New quarter, start from sequence 1
#                         return generate_invoice_number(1)
#                 except:
#                     # If parsing fails, use current sequence
#                     return generate_invoice_number(st.session_state.invoice_seq)
#             else:
#                 # No previous invoice, start from current sequence
#                 return generate_invoice_number(st.session_state.invoice_seq)
        
#         # Initialize or update invoice number when quarter changes
#         if "current_invoice_quarter" not in st.session_state:
#             st.session_state.current_invoice_quarter = current_quarter
#             st.session_state.invoice_number = get_invoice_number()
        
#         # Update invoice number if quarter changes
#         if st.session_state.get('current_invoice_quarter', '') != current_quarter:
#             st.session_state.current_invoice_quarter = current_quarter
#             st.session_state.invoice_number = get_invoice_number()
        
#         # Display current quarter info
#         st.sidebar.info(f"**Current Quarter:** {current_quarter}")
        
#         # Show auto-generated breakdown
#         try:
#             prefix, year_range, quarter, sequence = parse_invoice_number(st.session_state.invoice_number)
#             st.sidebar.success(f"**Auto-generated Invoice Number**")
#             st.sidebar.info(f"**Format:** {year_range}/{quarter}/{sequence}")
#         except:
#             st.sidebar.warning("Could not parse invoice number")
        
#         # Editable invoice number
#         st.sidebar.subheader("Invoice Number Editor")
        
#         # Parse current invoice number for editing
#         try:
#             current_prefix, current_year_range, current_q, current_seq = parse_invoice_number(st.session_state.invoice_number)
            
#             # Create editable components
#             col1, col2, col3 = st.sidebar.columns([2, 2, 1])
            
#             with col1:
#                 new_year_range = st.text_input("Year Range", value=current_year_range, key="invoice_year_edit")
            
#             with col2:
#                 new_quarter = st.text_input("Quarter", value=current_q, key="invoice_quarter_edit")
            
#             with col3:
#                 new_sequence = st.number_input("Sequence", 
#                                             min_value=1, 
#                                             value=int(current_seq), 
#                                             step=1,
#                                             key="invoice_seq_edit")
            
#             # Construct new invoice number
#             new_invoice_number = f"CMI/{new_year_range}/{new_quarter}/{new_sequence:02d}"
            
#             # Update if changed
#             if new_invoice_number != st.session_state.invoice_number:
#                 st.session_state.invoice_number = new_invoice_number
                
#         except Exception as e:
#             st.sidebar.error(f"Error parsing invoice number: {e}")
#             # Fallback to default
#             st.session_state.invoice_number = generate_invoice_number(st.session_state.invoice_seq)
        
#         # Display final invoice number
#         st.sidebar.code(st.session_state.invoice_number)
        
#         invoice_auto_increment = st.sidebar.checkbox("Auto-increment Sequence", value=True, key="invoice_auto_increment")
        
#         if st.sidebar.button("Reset to Auto-generate", use_container_width=True, key="invoice_reset_auto_generate"):
#             st.session_state.invoice_seq = 1
#             st.session_state.last_invoice_number = ""
#             st.session_state.invoice_number = get_invoice_number()
#             st.sidebar.success("Invoice number reset to auto-generated")
#             st.rerun()

#         col1, col2 = st.columns([1,1])
#         with col1:
#             st.subheader("Invoice Details")
#             invoice_no = st.text_input("Invoice No", st.session_state.invoice_number, key="invoice_number_input")
#             invoice_date = st.text_input("Invoice Date", datetime.date.today().strftime("%d-%m-%Y"))
#             Suppliers_Reference = st.text_input("Supplier's Reference", "NA")
#             Others_Reference = st.text_input("Other's Reference", "NA")
#             buyers_order_no = st.text_input("Buyer's Order No.", "Online")
#             buyers_order_date = st.text_input("Buyer's Order Date", datetime.date.today().strftime("%d-%m-%Y"))
#             dispatched_through = st.text_input("Dispatched Through", "Online")
            
#             # NEW INPUT: Payment Terms
#             payment_terms = st.text_input("Mode/Terms of Payment", "100% Advance with Purchase")
            
#             terms_of_delivery = st.text_input("Terms of delivery", "Within Month")
            
#             # NEW INPUT: Destination
#             destination = st.text_input("Destination", "Vadodara")
            
#             st.subheader("Seller Details")
#             vendor_name = st.text_input("Seller Name", "CM Infotech")
#             vendor_address = st.text_area("Seller Address", "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur, Chenpur Road, Jagatpur Village, Ahmedabad - 382481")
#             vendor_gst = st.text_input("Seller GST No.", "24ANMPP4891R1ZX")
#             vendor_msme = st.text_input("Seller MSME Registration No.", "UDYAM-GJ-01-0117646")

#         with col2:
#             st.subheader("Buyer Details")
            
#             # End User Dropdown for Invoice
#             selected_enduser_invoice = st.selectbox(
#                 "Select Buyer", 
#                 options=get_enduser_dropdown_options(),
#                 key="enduser_dropdown_invoice"
#             )
            
#             # Update buyer fields when dropdown selection changes
#             if selected_enduser_invoice and selected_enduser_invoice != "Select End User":
#                 enduser_data = END_USER_DATABASE.get(selected_enduser_invoice, {})
#                 st.session_state.po_end_company = selected_enduser_invoice
#                 st.session_state.po_end_address = enduser_data.get("address", "")
#                 st.session_state.po_end_gst_no = enduser_data.get("gst_no", "")
            
#             buyer_name = st.text_input(
#                 "Buyer Name",
#                 value = st.session_state.get("po_end_company","Baldridge & Associates Pvt Ltd.")
#             )
#             buyer_address = st.text_area(
#                 "Buyer Address",
#                 value=st.session_state.get("po_end_address","406 Sakar East, Vadodara 390009")
#             )
#             buyer_gst = st.text_input(
#                 "Buyer GST No.",
#                 value=st.session_state.get("po_end_gst_no","24AAHCB9")
#             )

#             st.subheader("Products")
#             items = []
#             num_items = st.number_input("Number of Products", 1, 10, 1, key="invoice_num_items")
#             for i in range(num_items):
#                 with st.expander(f"Product {i+1}"):
#                     desc = st.text_area(f"Description {i+1}", "Autodesk BIM Collaborate Pro - Single-user\nCLOUD Commercial New Annual Subscription\nSerial #575-26831580\nContract #110004988191\nEnd Date: 17/04/2026", key=f"invoice_desc_{i}")
#                     hsn = st.text_input(f"HSN/SAC {i+1}", "997331", key=f"invoice_hsn_{i}")
#                     qty = st.number_input(f"Quantity {i+1}", 1.00, 100.00, 1.00, key=f"invoice_qty_{i}")
#                     rate = st.number_input(f"Unit Rate {i+1}", 0.00, 100000000.00, 36500.00, key=f"invoice_rate_{i}")
#                     rate = round(rate, 2)
#                     items.append({"description": desc, "hsn": hsn, "quantity": qty, "unit_rate": rate})

#             st.subheader("Declaration")
#             declaration = st.text_area("Declaration", "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF NOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED FROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE")
            
#             st.subheader("Company Branding")
#             st.info("Using global logo and stamp from sidebar settings")
#             logo_path = global_logo_path
#             stamp_path = global_stamp_path

#             if not logo_path:
#                 st.warning("⚠ No company logo available")
#             if not stamp_path:
#                 st.warning("⚠ No company stamp available")
            
#             st.subheader("Invoice Preview & Download")

#             if st.button("Generate Invoice", key="generate_invoice_button"):
#                 # Calculate amounts with proper rounding like in PO generator
#                 basic_amount = round(sum(item['quantity'] * item['unit_rate'] for item in items), 2)
#                 sgst = round(basic_amount * 0.09, 2)
#                 cgst = round(basic_amount * 0.09, 2)
#                 final_amount_unrounded = basic_amount + sgst + cgst
                
#                 # ROUND TO WHOLE NUMBER LIKE PO GENERATOR
#                 final_amount = round(final_amount_unrounded)
#                 round_off = final_amount - final_amount_unrounded
                
#                 # Display calculated amounts for verification
#                 st.info(f"**Calculated Amounts:** Basic: ₹{basic_amount:.2f}, SGST: ₹{sgst:.2f}, CGST: ₹{cgst:.2f}, Final: ₹{final_amount:.2f}")
#                 if round_off != 0:
#                     st.info(f"**Round Off:** ₹{round_off:.2f}")
                
#                 # Convert to words with proper Indian currency format
#                 def convert_to_indian_currency(amount):
#                     """Convert amount to Indian currency words format"""
#                     try:
#                         # Split into rupees and paise
#                         rupees = int(amount)
#                         paise = round((amount - rupees) * 100)
                        
#                         rupees_text = num2words(rupees, to='cardinal', lang='en_IN').title()
                        
#                         if paise > 0:
#                             paise_text = num2words(paise, to='cardinal', lang='en_IN').title()
#                             return f"{rupees_text} Rupees And {paise_text} Paise Only/-"
#                         else:
#                             return f"{rupees_text} Rupees Only/-"
                            
#                     except Exception as e:
#                         return f"Amount: ₹{amount:.2f}"

#                 amount_in_words = convert_to_indian_currency(final_amount)
#                 tax_in_words = convert_to_indian_currency(round(sgst + cgst, 2))

#                 invoice_data = {
#                     "invoice": {"invoice_no": invoice_no, "date": invoice_date},
#                     "Reference": {"Suppliers_Reference":Suppliers_Reference, "Other": Others_Reference},
#                     "vendor": {"name": vendor_name, "address": vendor_address, "gst": vendor_gst, "msme": vendor_msme},
#                     "buyer": {"name": buyer_name, "address": buyer_address, "gst": buyer_gst},
#                     "invoice_details": {
#                         "buyers_order_no": buyers_order_no,
#                         "buyers_order_date": buyers_order_date,
#                         "dispatched_through": dispatched_through,
#                         "payment_terms": payment_terms,
#                         "terms_of_delivery": terms_of_delivery,
#                         "destination": destination
#                     },
#                     "items": items,
#                     "totals": {
#                         "basic_amount": basic_amount,
#                         "sgst": sgst,
#                         "cgst": cgst,
#                         "final_amount": final_amount,
#                         "amount_in_words": amount_in_words,
#                         "tax_in_words": tax_in_words
#                     },
#                     "declaration": declaration
#                 }

#                 pdf_file = create_invoice_pdf(invoice_data, logo_path, stamp_path)

#                 # Store the last invoice number for sequence tracking
#                 st.session_state.last_invoice_number = invoice_no
                
#                 # Auto-increment for next invoice
#                 if invoice_auto_increment:
#                     # This automatically increments and saves to file
#                     next_sequence = get_next_invoice_sequence()
#                     st.session_state.invoice_seq = next_sequence

#                 st.success("Invoice generated successfully!")
                
#                 st.download_button(
#                     "⬇ Download Invoice PDF",
#                     data=pdf_file,
#                     file_name=f"Invoice_{invoice_no.replace('/', '_')}.pdf",
#                     mime="application/pdf",
#                     key="invoice_download_button")
                
#     # Clean up temporary files
#     for path in ["github_logo.jpg", "github_stamp.jpg", "custom_logo.jpg", "custom_stamp.jpg"]:
#         if os.path.exists(path):
#             try:
#                 os.remove(path)
#             except:
#                 pass
    
#     st.divider()
#     st.caption("© 2025 Document Generator - CM Infotech")

# if __name__ == "__main__":
#     main()
