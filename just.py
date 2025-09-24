from fpdf import FPDF
from num2words import num2words
import os
from datetime import datetime

# --- PDF Class for Customization ---
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        self.add_font("Calibri", "", os.path.join(font_dir, "calibri.ttf"), uni=True)
        self.add_font("Calibri", "B", os.path.join(font_dir, "calibrib.ttf"), uni=True)
        self.add_font("Calibri", "I", os.path.join(font_dir, "calibrii.ttf"), uni=True)
        self.add_font("Calibri", "BI", os.path.join(font_dir, "calibriz.ttf"), uni=True)
        self.set_font("Calibri", "", 10)
        self.set_left_margin(15)
        self.set_right_margin(15)

    def header(self):
        self.set_font("Calibri", "", 10)
        self.cell(0, 5, "CM Infotech", ln=1, align='R')
        self.cell(0, 5, "We aim for the best", ln=1, align='R')
        self.ln(2)
        self.set_font("Calibri", "B", 18)
        self.cell(0, 15, "TAX INVOICE", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Calibri", "I", 8)
        self.cell(0, 5, "This is a Computer Generated Invoice", ln=1, align="C")

    def _render_section_title(self, title):
        self.set_font("Calibri", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 7, self.sanitize_text(title), border='T,L,R', ln=1, fill=True)
        self.set_font("Calibri", "", 10)

    def sanitize_text(self, text):
        return text.encode('latin-1', 'ignore').decode('latin-1')

def create_invoice_pdf(invoice_data):
    pdf = PDF()
    pdf.add_page()

    # --- Supplier and Buyer Details Section ---
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(100, 5, "Supplier", border='T,L,R', ln=0)
    pdf.cell(0, 5, "Buyer", border='T,L,R', ln=1)
    
    # Store initial y position for multi-line cells
    y_start = pdf.get_y()
    
    # Supplier details (left column)
    pdf.set_font("Calibri", "B", 10)
    pdf.multi_cell(100, 5, pdf.sanitize_text(invoice_data["supplier"]["name"]), border='L,R')
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(100, 5, pdf.sanitize_text(invoice_data["supplier"]["address"]), border='L,R')
    pdf.multi_cell(100, 5, f"GST No.: {pdf.sanitize_text(invoice_data['supplier']['gst_no'])}", border='L,R')
    pdf.multi_cell(100, 5, f"MSME Registration No.: {pdf.sanitize_text(invoice_data['supplier']['msme_reg_no'])}", border='L,R')
    pdf.multi_cell(100, 5, f"E-Mail: {pdf.sanitize_text(invoice_data['supplier']['email'])}", border='L,R')
    pdf.multi_cell(100, 5, f"Mobile No.: {pdf.sanitize_text(invoice_data['supplier']['mobile_no'])}", border='L,R,B')
    
    # Move cursor back to the start of the right column
    pdf.set_xy(115, y_start)
    
    # Buyer details (right column)
    pdf.set_font("Calibri", "B", 10)
    pdf.multi_cell(95, 5, pdf.sanitize_text(invoice_data["buyer"]["name"]), border='L,R')
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(95, 5, pdf.sanitize_text(invoice_data["buyer"]["address"]), border='L,R')
    pdf.multi_cell(95, 5, f"GST No.: {pdf.sanitize_text(invoice_data['buyer']['gst_no'])}", border='L,R')
    pdf.multi_cell(95, 5, f"Email: {pdf.sanitize_text(invoice_data['buyer']['email'])}", border='L,R')
    pdf.multi_cell(95, 5, f"Tel No.: {pdf.sanitize_text(invoice_data['buyer']['tel_no'])}", border='L,R')
    pdf.multi_cell(95, 5, f"Destination: {pdf.sanitize_text(invoice_data['buyer']['destination'])}", border='L,R,B')
    pdf.ln(5)

    # --- Invoice Details Table ---
    pdf.set_font("Calibri", "B", 10)
    col1_width, col2_width, col3_width, col4_width = 45, 50, 45, 50
    pdf.cell(col1_width, 7, "Invoice No.", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["invoice"]["invoice_no"]), border=1)
    pdf.cell(col3_width, 7, "Invoice Date", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["invoice"]["invoice_date"]), border=1, ln=1)
    
    pdf.cell(col1_width, 7, "Buyer's Order No.", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["invoice"]["buyers_order_no"]), border=1)
    pdf.cell(col3_width, 7, "Buyer's Order Date", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["invoice"]["buyers_order_date"]), border=1, ln=1)
    
    pdf.cell(col1_width, 7, "Mode/Terms of Payment", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["invoice"]["terms_of_payment"]), border=1)
    pdf.cell(col3_width, 7, "Dispatch Document No.", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["invoice"]["dispatch_doc_no"]), border=1, ln=1)
    
    pdf.cell(col1_width, 7, "Dispatched Through", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["invoice"]["dispatched_through"]), border=1)
    pdf.cell(col3_width, 7, "Delivery Note Date", border=1)
    pdf.cell(col4_width, 7, pdf.sanitize_text(invoice_data["invoice"]["delivery_note_date"]), border=1, ln=1)
    
    pdf.cell(col1_width, 7, "Terms of Delivery", border=1)
    pdf.cell(col2_width, 7, pdf.sanitize_text(invoice_data["invoice"]["terms_of_delivery"]), border=1)
    pdf.cell(col3_width, 7, "", border=1)
    pdf.cell(col4_width, 7, "", border=1, ln=1)
    pdf.ln(5)

    # --- Products Table ---
    pdf.set_font("Calibri", "B", 10)
    col_widths = [10, 80, 20, 20, 20, 20]
    headers = ["Sr. No.", "Description of Goods", "HSN/SAC", "Quantity", "Unit Rate", "Amount"]
    pdf.set_fill_color(220, 220, 220)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Calibri", "", 10)
    total_basic = 0.0
    for i, p in enumerate(invoice_data["items"]):
        amount = p["unit_rate"] * p["quantity"]
        total_basic += amount
        
        y_before = pdf.get_y()
        pdf.set_x(15)
        pdf.cell(col_widths[0], 7, str(i+1), border='L', align="C")
        pdf.set_x(pdf.get_x())
        pdf.multi_cell(col_widths[1], 5, pdf.sanitize_text(p["description"]), border=0)
        y_after = pdf.get_y()
        row_height = y_after - y_before
        
        pdf.set_xy(15 + col_widths[0], y_before)
        pdf.cell(col_widths[1], row_height, "", border='R,B,T', ln=0)
        pdf.set_xy(15 + col_widths[0] + col_widths[1], y_before)
        pdf.cell(col_widths[2], row_height, pdf.sanitize_text(p['hsn_sac']), border='L,R,B,T', align="C")
        pdf.cell(col_widths[3], row_height, f"{p['quantity']:.2f}", border='L,R,B,T', align="R")
        pdf.cell(col_widths[4], row_height, f"{p['unit_rate']:.2f}", border='L,R,B,T', align="R")
        pdf.cell(col_widths[5], row_height, f"{amount:.2f}", border='L,R,B,T', align="R")
        pdf.ln(row_height)

    # Totals
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(sum(col_widths[:-1]), 7, "Basic Amount", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{total_basic:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "SGST @ 9%", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{invoice_data['totals']['sgst']:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "CGST @ 9%", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{invoice_data['totals']['cgst']:.2f}", border=1, align="R", ln=1)
    pdf.cell(sum(col_widths[:-1]), 7, "Final Amount to be Paid", border=1, align="R")
    pdf.cell(col_widths[-1], 7, f"{invoice_data['totals']['final_amount']:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # --- Amount in Words ---
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(0, 7, "Amount Chargeable (in words):", ln=1)
    pdf.set_font("Calibri", "", 10)
    pdf.multi_cell(0, 7, pdf.sanitize_text(invoice_data["totals"]["amount_in_words"]))
    pdf.ln(5)

    # --- Tax Details Table ---
    pdf._render_section_title("HSN/SAC Tax Details")
    col_widths = [20, 40, 20, 30, 20, 30]
    headers = ["HSN/SAC", "Taxable Value", "Central Tax Rate", "Central Tax Amount", "State Tax Rate", "State Tax Amount"]
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Calibri", "B", 10)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Calibri", "", 10)
    pdf.cell(col_widths[0], 7, invoice_data["tax_details"]["hsn_sac"], border=1, align="C")
    pdf.cell(col_widths[1], 7, f"{invoice_data['tax_details']['taxable_value']:.2f}", border=1, align="R")
    pdf.cell(col_widths[2], 7, f"{invoice_data['tax_details']['central_rate']}%", border=1, align="C")
    pdf.cell(col_widths[3], 7, f"{invoice_data['tax_details']['central_amount']:.2f}", border=1, align="R")
    pdf.cell(col_widths[4], 7, f"{invoice_data['tax_details']['state_rate']}%", border=1, align="C")
    pdf.cell(col_widths[5], 7, f"{invoice_data['tax_details']['state_amount']:.2f}", border=1, align="R", ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(col_widths[0], 7, "Total", border=1, align="C")
    pdf.cell(col_widths[1], 7, f"{invoice_data['tax_details']['total_taxable']:.2f}", border=1, align="R")
    pdf.cell(col_widths[2], 7, "", border=1)
    pdf.cell(col_widths[3], 7, f"{invoice_data['tax_details']['total_tax'] / 2:.2f}", border=1, align="R")
    pdf.cell(col_widths[4], 7, "", border=1)
    pdf.cell(col_widths[5], 7, f"{invoice_data['tax_details']['total_tax'] / 2:.2f}", border=1, align="R", ln=1)
    pdf.ln(5)

    # --- Bank Details ---
    pdf._render_section_title("Company's Bank Details")
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "Bank Name:", border='L', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank_details"]["bank_name"]), border='R', ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "Branch:", border='L', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank_details"]["branch"]), border='R', ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "Account No.:", border='L', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank_details"]["account_no"]), border='R', ln=1)
    pdf.set_font("Calibri", "B", 10)
    pdf.cell(50, 7, "IFS Code:", border='L,B', ln=0)
    pdf.set_font("Calibri", "", 10)
    pdf.cell(0, 7, pdf.sanitize_text(invoice_data["bank_details"]["ifs_code"]), border='R,B', ln=1)
    pdf.ln(5)

    # --- Declaration and Signature ---
    pdf.set_font("Calibri", "", 8)
    pdf.multi_cell(0, 4, pdf.sanitize_text(invoice_data["declaration"]))
    pdf.ln(5)
    
    pdf.set_font("Calibri", "", 10)
    pdf.cell(100, 7, "Customer's Seal and Signature", ln=0)
    pdf.cell(0, 7, "For, CM Infotech", ln=1, align="R")
    pdf.ln(15)
    pdf.cell(100, 7, "", ln=0)
    pdf.set_font("Calibri", "I", 10)
    pdf.cell(0, 7, "Authorized Signatory", ln=1, align="R")

    return pdf.output("tax_invoice.pdf")

if __name__ == "__main__":
    invoice_data = {
        "supplier": {
            "name": "CM Infotech",
            "address": "E/402, Ganesh Glory 11, Near BSNL Office, Jagatpur, Chenpur Road, Jagatpur Village, Ahmedabad - 382481",
            "gst_no": "24ANMPP4",
            "msme_reg_no": "UDYAM-",
            "email": "cm.infot",
            "mobile_no": "873391",
        },
        "buyer": {
            "name": "Baldridge Pvt Ltd.",
            "address": "406, Sakar East, 40mt Tarsali - Danteshwar Ring Road, Vadodara 390009",
            "email": "dmistry@b",
            "tel_no": "98987",
            "gst_no": "24AAHCB9",
            "destination": "Vadodara",
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
        },
        "items": [
            {
                "sr_no": 1,
                "description": "Autodesk BIM Collaborate Pro - Single-user CLOUD Commercial New Annual Subscription Serial #575-26831580 Contract #110004988191 End Date: 17/04/2026",
                "hsn_sac": "997331",
                "quantity": 1.00,
                "unit_rate": 36500.00,
            }
        ],
        "totals": {
            "basic_amount": 36500.00,
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
            "ifs_code": "IDFB004",
        },
        "declaration": "IT IS HEREBY DECLARED THAT THE SOFTWARE HAS ALREADY BEEN DEDUCTED FOR TDS/WITH HOLDING TAX AND BY VIRTUE OF NOTIFICATION NO.: 21/20, SO 1323[E] DT 13/06/2012, YOU ARE EXEMPTED FROM DEDUCTING TDS ON PAYMENT/CREDIT AGAINST THIS INVOICE"
    }

    create_invoice_pdf(invoice_data)
