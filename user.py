from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Create a PDF document
c = canvas.Canvas("rectangle_example.pdf", pagesize=letter)

# Define the rectangle coordinates
x1, y1 = 20, 660  # Bottom-left corner
x2, y2 = 592, 780  # Top-right corner

# Draw the rectangle
c.rect(x1, y1, x2 - x1, y2 - y1)

# Save the PDF
c.save()

# Bottom-left corner: (0, 0)
# Bottom-right corner: (612, 0)
# Top-left corner: (0, 792)
# Top-right corner: (612, 792)