import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

def create_circle_graph(sections, labels):
    """Create a pie chart using Seaborn color palette."""
    plt.figure(figsize=(6, 6))
    colors = sns.color_palette('pastel')[0:5]
    plt.pie(sections, labels=labels, colors=colors, autopct='%.0f%%')
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is a circle.
    plt.title('2D Circle Graph with 5 Sections')

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer

def create_bar_graph(data, labels):
    """Create a bar graph using Seaborn and save it to a BytesIO object."""
    plt.figure(figsize=(6, 4))
    sns.barplot(x=labels, y=data, palette='pastel')
    plt.title('Bar Graph of Sections')
    plt.xlabel('Labels')
    plt.ylabel('Values')

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer

def save_plot_to_pdf(circle_img_buffer, bar_img_buffer, pdf_filename):
    """Insert the images from the BytesIO objects into a PDF."""
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    
    # Circle graph
    circle_image_reader = ImageReader(circle_img_buffer)
    c.drawImage(circle_image_reader, 1 * inch, 5 * inch, width=5 * inch, height=5 * inch)

    # Bar graph
    bar_image_reader = ImageReader(bar_img_buffer)
    c.drawImage(bar_image_reader, 1 * inch, 1 * inch, width=5 * inch, height=4 * inch)

    c.save()
    print(f"PDF generated: {pdf_filename}")

def main():
    # Data for the circle graph and bar graph
    sections = [15, 25, 25, 30, 5]
    labels = ['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5']
    
    # Create circle graph and save it to a BytesIO object
    img_buffer_circle = create_circle_graph(sections, labels)

    # Create bar graph and save it to a BytesIO object
    img_buffer_bar = create_bar_graph(sections, labels)

    # Specify the PDF filename
    pdf_filename = "circle_bar_graph.pdf"
    
    # Save the plots to the PDF
    save_plot_to_pdf(img_buffer_circle, img_buffer_bar, pdf_filename)

if __name__ == "__main__":
    main()
