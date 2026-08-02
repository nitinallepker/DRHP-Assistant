import os
import re
from typing import List, Dict, Any
from fpdf import FPDF

class DRHPPDF(FPDF):
    """
    Custom FPDF subclass adding SEBI-compliant running headers,
    footers, page boundaries, and page numbering on subsequent pages.
    """
    def __init__(self, workspace_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_name = workspace_name

    def header(self):
        # Suppress headers on the Cover Page (Page 1)
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, f"DRAFT RED HERRING PROSPECTUS - {self.workspace_name.upper()} LIMITED", border=0, align="L")
            self.cell(0, 10, "SEBI FILING COMPLIANCE DRAFT", border=0, align="R")
            self.ln(8)
            # Draw header line divider
            self.set_draw_color(200, 200, 200)
            self.line(10, 18, 200, 18)
            self.ln(4)

    def footer(self):
        # Suppress footers on the Cover Page (Page 1)
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            # Draw footer line divider
            self.set_draw_color(200, 200, 200)
            self.line(10, 282, 200, 282)
            self.cell(0, 10, "CONFIDENTIAL - SECURITIES AND INVESTMENT BANKING DIVISION", border=0, align="L")
            self.cell(0, 10, f"Page {self.page_no()}", border=0, align="R")


class PDFCompiler:
    """
    PDFCompiler parses markdown text sections, converts them to basic HTML flow tags,
    draws professional cover sheets, and builds the consolidated DRHP book.
    """
    
    def markdown_to_html(self, md_text: str) -> str:
        """
        Converts basic markdown elements (headings, bold, lists, tables)
        into clean, lightweight HTML tags compatible with fpdf2's write_html().
        """
        if not md_text:
            return ""
            
        lines = md_text.split("\n")
        html_lines = []
        in_table = False
        in_list = False
        
        for line in lines:
            line_strip = line.strip()
            
            # 1. Table structure parsing
            if line_strip.startswith("|"):
                if not in_table:
                    in_table = True
                    html_lines.append("<table border='1' cellpadding='4'>")
                
                # Skip divider rows like |---|---|
                if "---" in line_strip:
                    continue
                    
                cells = [c.strip() for c in line_strip.split("|")[1:-1]]
                html_lines.append("<tr>")
                for cell in cells:
                    # Treat header rows or specific keys as bold table headers
                    if "Metric" in cell or "Value" in cell or "Category" in cell or "Fact" in cell or "Term" in cell or "Definition" in cell:
                        html_lines.append(f"<td><b>{cell}</b></td>")
                    else:
                        html_lines.append(f"<td>{cell}</td>")
                html_lines.append("</tr>")
                continue
            else:
                if in_table:
                    in_table = False
                    html_lines.append("</table>")
            
            # 2. Bullet list structures
            if line_strip.startswith("- ") or line_strip.startswith("* "):
                if not in_list:
                    in_list = True
                    html_lines.append("<ul>")
                item_text = line_strip[2:]
                html_lines.append(f"<li>{item_text}</li>")
                continue
            else:
                if in_list:
                    in_list = False
                    html_lines.append("</ul>")
            
            # 3. Heading structures
            if line_strip.startswith("# "):
                html_lines.append(f"<h1>{line_strip[2:]}</h1>")
            elif line_strip.startswith("## "):
                html_lines.append(f"<h2>{line_strip[3:]}</h2>")
            elif line_strip.startswith("### "):
                html_lines.append(f"<h3>{line_strip[4:]}</h3>")
            elif not line_strip:
                html_lines.append("<br>")
            else:
                html_lines.append(f"<p>{line_strip}</p>")
                
        # Close open tags at EOF
        if in_table:
            html_lines.append("</table>")
        if in_list:
            html_lines.append("</ul>")
            
        html_content = "".join(html_lines)
        
        # 4. Inline tag conversions (bold and italics regexes)
        html_content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", html_content)
        html_content = re.sub(r"\*(.*?)\*", r"<i>\1</i>", html_content)
        
        return html_content

    def compile(self, workspace_name: str, sections: Dict[str, str], output_pdf_path: str):
        """
        Orchestrates compiling the dictionary of section markdowns into the finished PDF.
        """
        # Instantiate A4 Portrait document
        pdf = DRHPPDF(workspace_name=workspace_name, orientation="P", unit="mm", format="A4")
        pdf.set_margins(15, 20, 15)
        pdf.set_auto_page_break(auto=True, margin=20)
        
        # --- 1. RENDER COVER PAGE (Suppress headers/footers) ---
        pdf.add_page()
        
        # Draw a double-line visual page border for premium styling
        pdf.set_draw_color(50, 50, 100) # Deep Navy blue
        pdf.set_line_width(0.8)
        pdf.rect(10, 10, 190, 277)
        pdf.set_line_width(0.2)
        pdf.rect(12, 12, 186, 273)
        
        pdf.ln(15)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(50, 50, 100)
        pdf.cell(0, 10, "SUBMITTED FOR REGULATORY REVIEW / SEBI COMPLIANCE", border=0, align="C")
        
        pdf.ln(25)
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 12, f"{workspace_name.upper()} LIMITED", border=0, align="C")
        
        pdf.ln(5)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 10, "Incorporated under the Companies Act, 2013", border=0, align="C")
        
        pdf.ln(15)
        pdf.set_draw_color(150, 150, 150)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "DRAFT RED HERRING PROSPECTUS", border=0, align="C")
        
        # Parse the cover page details to extract sizes if possible, otherwise print standard template
        cover_content = sections.get("COVER_PAGE", "")
        
        pdf.ln(12)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        
        issue_details = "Fresh Issue size: Up to [●] Crores | OFS: Up to [●] Crores"
        if "Fresh Issue Size" in cover_content:
            sizes = re.findall(r"Fresh Issue Size.*", cover_content)
            if sizes:
                issue_details = sizes[0]
        elif "Fresh Issue" in cover_content:
            sizes = re.findall(r"Fresh Issue.*", cover_content)
            if sizes:
                issue_details = sizes[0]

        pdf.multi_cell(0, 6, 
            "The Company proposes an Initial Public Offering (IPO) of equity shares. "
            f"Details: {issue_details}. All terms are subject to change prior to registration.",
            border=0, align="C"
        )
        
        pdf.ln(15)
        pdf.set_draw_color(150, 150, 150)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        
        # Bottom Warning disclaimer box
        pdf.set_y(-60)
        pdf.set_fill_color(245, 245, 250)
        pdf.rect(15, pdf.get_y(), 180, 40, "F")
        pdf.set_y(pdf.get_y() + 2)
        pdf.set_font("helvetica", "B", 8)
        pdf.set_text_color(150, 0, 0)
        pdf.cell(0, 5, "REGULATORY SEBI WARNING & DISCLAIMER CLAUSE", border=0, align="C")
        pdf.ln(5)
        pdf.set_font("helvetica", "", 7.5)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 4, 
            "Mutual fund investments are subject to market risks. Please read all scheme related documents carefully. "
            "Every person who desires to apply for or otherwise acquire any securities of the Company may do so only "
            "on the basis of information contained in the final Red Herring Prospectus. SEBI does not take any "
            "responsibility for the financial soundness of the Company or the correctness of statements made.",
            border=0, align="C"
        )

        # --- 2. RENDER THE REST OF THE DRHP SECTIONS ---
        section_order = [
            "GLOSSARY_DEFINITIONS",
            "COMPANY_OVERVIEW",
            "INDUSTRY_OVERVIEW",
            "BUSINESS_OVERVIEW_STRENGTHS",
            "RISK_FACTORS",
            "IPO_DETAILS_OBJECTS_CAPITAL",
            "FINANCIAL_HIGHLIGHTS_MDA",
            "LEGAL_LITIGATION_DECLARATION"
        ]
        
        for slug in section_order:
            content = sections.get(slug)
            if not content:
                continue
                
            pdf.add_page()
            
            # Format title
            title = slug.replace("_", " ").title()
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(50, 50, 100)
            pdf.cell(0, 10, title, border=0, align="L")
            pdf.ln(12)
            
            # Parse markdown content into html and render it
            html_text = self.markdown_to_html(content)
            
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.write_html(html_text)
            
        # Ensure directories exist and save the compiled output PDF
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        pdf.output(output_pdf_path)
        return output_pdf_path
