from reportlab.pdfgen import canvas

def hello(c):
    print("Hello World")
    c.drawString(100,100,"(100,100)")
    c.drawString(250,250,"(250,250)")
    c.drawString(500,500,"(500,500)")
    c.drawString(250,800,"(250,800)")
    # 100, 100 is the x, y position of the text, it starts from bottom left
    # 500, 500 is the x, y position of the text, it starts from bottom left

c = canvas.Canvas("hello.pdf")
hello(c)
c.showPage()
c.save()
