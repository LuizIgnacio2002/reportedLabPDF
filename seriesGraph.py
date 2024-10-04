import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

def create_bar_graph(x, y):
    """Create a bar graph from the given data and save it to a BytesIO object."""
    plt.figure(figsize=(6, 4))
    ax = plt.gca()

    # Plot the bar graph
    ax.bar(x, y, width=1, color='#00dd00', edgecolor="white", linewidth=0.7)

    # Fill the area from the bottom of the bars to the top
    ax.fill_between(x, 0, y, color='#00dd00', alpha=0.3)

    # Set limits and ticks for the axes
    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
           ylim=(0, 8), yticks=np.arange(1, 9))
    
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Histogram (Todo)')

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer

def create_line_plot():
    """Create a line plot with a shadow area and save it to a BytesIO object."""
    np.random.seed(1)
    x = np.linspace(0, 8, 20)
    y1 = 3 + 4 * x / 8 + np.random.uniform(0.0, 0.5, len(x))
    y2 = 1 + 2 * x / 8 + np.random.uniform(0.0, 0.5, len(x))

    plt.figure(figsize=(6, 4))
    ax = plt.gca()

    # Plot the two main lines
    ax.plot(x, y1, label='Line 1', color='blue')
    ax.plot(x, y2, label='Line 2', color='orange')

    # Specify the two points for the shadow area
    start_index = 5
    end_index = 15

    # Add the shadow area between the two specified points
    ax.fill_between(x[start_index:end_index + 1], y1[start_index:end_index + 1], 
                     y2[start_index:end_index + 1], 
                     color='grey', alpha=0.5, label='Shadow Area')

    # Add dotted vertical lines
    for i in range(len(x) - 1):
        ax.plot([x[i], x[i]], [y2[i], y1[i]], linestyle='dotted', color='black', linewidth=1)

    # Set limits and ticks for the axes
    ax.set(xlim=(0, 8), xticks=np.arange(1, 9),
           ylim=(0, 8), yticks=np.arange(1, 9))

    ax.legend()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer

def save_plot_to_pdf(img_buffer, pdf_filename, x, y):
    """Insert the image from the BytesIO object into a PDF at specified coordinates."""
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    
    image_reader = ImageReader(img_buffer)

    img_width = 5 * inch
    img_height = (img_width * 4) / 6  # Maintain aspect ratio

    c.drawImage(image_reader, x, y, width=img_width, height=img_height)
    c.save()
    print(f"PDF generated: {pdf_filename}")

def main():
    # Data for the bar graph
    x_bar = 0.5 + np.arange(8)
    y_bar = [4.8, 5.5, 3.5, 4.6, 6.5, 6.6, 2.6, 3.0]
    
    # Create bar graph and save it to a BytesIO object
    img_buffer_bar = create_bar_graph(x_bar, y_bar)
    
    # Create line plot and save it to a BytesIO object
    img_buffer_line = create_line_plot()

    # Specify the PDF filename
    pdf_filename = "seriesGraph.pdf"
    
    # Specify the coordinates for the images
    x_position_bar = 1 * inch  # X coordinate for bar graph
    y_position_bar = 5 * inch  # Y coordinate for bar graph
    y_position_line = 1 * inch  # Y coordinate for line plot
    
    # Save the bar graph image to the PDF at specified coordinates
    save_plot_to_pdf(img_buffer_bar, pdf_filename, x_position_bar, y_position_bar)
    
    # Save the line plot image to the PDF at specified coordinates
    save_plot_to_pdf(img_buffer_line, pdf_filename, x_position_bar, y_position_line)

if __name__ == "__main__":
    main()
