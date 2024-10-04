from reportlab.pdfgen import canvas

def print_coordinates(c):
    # Iterate over coordinates from 0,0 to 800,800, adding 10 to both x and y each time
    for x in range(0, 801, 60):
        for y in range(0, 801, 60):
            # Draw string at each coordinate
            c.drawString(x, y, f"({x},{y})")

c = canvas.Canvas("hello.pdf")
print_coordinates(c)
c.showPage()
c.save()