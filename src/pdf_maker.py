from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak

import textwrap

def create_pdf_from_files(f1_path, f2_path, output_pdf_path):
    # Read lines from each file
    with open(f1_path, 'r') as f1, open(f2_path, 'r') as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()
    
    # Ensure both files have the same number of lines
    max_lines = max(len(f1_lines), len(f2_lines))
    f1_lines += [''] * (max_lines - len(f1_lines))
    f2_lines += [''] * (max_lines - len(f2_lines))
    
    # Prepare table data
    table_data = [['story', 'atoms']]  # Table header
    for line1, line2 in zip(f1_lines, f2_lines):
        # Wrap each line to fit within the maximum width
        wrapped_line1 = "\n".join(textwrap.wrap(line1.strip(), width=40))
        wrapped_line2 = "\n".join(textwrap.wrap(line2.strip(), width=40))
        table_data.append([wrapped_line1, wrapped_line2])


    # Create the PDF with page margins
    pdf = SimpleDocTemplate(
        output_pdf_path, 
        pagesize=A4,
        leftMargin=0.5 * inch, 
        rightMargin=0.5 * inch, 
        topMargin=0.5 * inch, 
        bottomMargin=0.5 * inch
    )

    # Set column widths and create the table
    table = Table(table_data, colWidths=[3 * inch, 3 * inch])

    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # Build PDF
    elements = [table, PageBreak()]
    pdf.build(elements)

# Example usage
#create_pdf_from_files('stories.txt', 'test.txt', 'output.pdf')


#combine the two functions into one
#alternate the lines from the two files

f1 = open("stories.txt", "r")
f2 = open("test2.txt", "r")
f3 = open("output.txt", "w")

for line1, line2 in zip(f1, f2):
    if line1 != "\n":
        f3.write(line1)
        f3.write("\n")
    if line2 != "\n":
        f3.write(line2)
        f3.write("\n")