import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import seaborn as sns  # Importing seaborn for potential future use

def create_bar_graph(x, y):
    """Create a bar graph from the given data and save it to a BytesIO object."""
    plt.figure(figsize=(6, 4))
    ax = plt.gca()

    # Plot the bar graph
    ax.bar(x, y, width=1, color='#00dd00', edgecolor="white", linewidth=0.7)

    # Set limits and ticks for the axes
    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
           ylim=(0, 8), yticks=np.arange(1, 8))
    
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Histogram (Todo)')

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer

def save_bar_graph_to_pdf(img_buffer, pdf_filename, x, y):
    """Insert the image from the BytesIO object into a PDF at specified coordinates."""
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    
    # Wrap the BytesIO object with ImageReader
    image_reader = ImageReader(img_buffer)

    # Set image dimensions
    img_width = 5 * inch
    img_height = (img_width * 4) / 6  # Maintain aspect ratio

    # Draw the image at the specified coordinates (x, y)
    c.drawImage(image_reader, x, y, width=img_width, height=img_height)

    # Finalize the PDF
    c.save()
    print(f"PDF generated: {pdf_filename}")

def main():
    # Data for the bar graph
    x = 0.5 + np.arange(8)
    y = [4.8, 5.5, 3.5, 4.6, 6.5, 6.6, 2.6, 3.0]
    
    # Create bar graph and save it to a BytesIO object
    img_buffer = create_bar_graph(x, y)
    
    # Specify the PDF filename
    pdf_filename = "histogram_report11.pdf"
    
    # Specify the coordinates for the image
    x_position = 1 * inch  # X coordinate
    y_position = 5 * inch  # Y coordinate
    
    # Save the bar graph image to the PDF at specified coordinates
    save_bar_graph_to_pdf(img_buffer, pdf_filename, x_position, y_position)

if __name__ == "__main__":
    main()
