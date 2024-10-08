from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create a PDF document
c = canvas.Canvas("user.pdf", pagesize=letter)

# Define the rectangle coordinates
x1, y1 = 20, 660  # Bottom-left corner
x2, y2 = 592, 780  # Top-right corner

# Draw the rectangle
c.rect(x1, y1, x2 - x1, y2 - y1)



c.drawString(40, 760, "nombre")
c.drawString(140, 760, "apellido")
c.drawString(240, 760, "qqq")
c.drawString(340, 760, "eeee")

# Save the PDF
c.save()
