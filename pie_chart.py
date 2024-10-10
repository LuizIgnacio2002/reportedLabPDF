import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

import re
import io
import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import pandas as pd

def create_circle_graph_with_legend(sections, labels):
    """Create a pie chart with custom legend placement."""
    plt.figure(figsize=(8, 6))
    
    # Data for the pie chart
    colors = ['limegreen', 'red', 'yellow']  # Custom colors for mmHg values
    
    # Create pie chart
    plt.pie(sections, labels=labels, colors=colors[:len(sections)], autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.
    
    # Add title
    plt.title('Sistólica (mmHg)')

    # Add custom legend for color explanation
    legend_labels = ['Encima (Above 140)', 'mmHg (100-140)', 'Bajo (Below 100)']
    legend_colors = ['red', 'limegreen', 'yellow']
    plt.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_colors],
               labels=legend_labels, title="Color Explanation", loc='center left',
               bbox_to_anchor=(1, 0.5))  # Moves legend to the right outside the plot
    
    # Adjust layout to make space for the legend
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer

def save_plot_to_pdf(circle_img_buffer, pdf_filename):
    """Insert the circle graph from the BytesIO object into a PDF."""
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    
    # Circle graph
    circle_image_reader = ImageReader(circle_img_buffer)
    c.drawImage(circle_image_reader, 1 * inch, 5 * inch, width=5 * inch, height=5 * inch)

    c.save()
    print(f"PDF generated: {pdf_filename}")

def handle_csv_upload(csv_file):
    """Process uploaded CSV file and generate a DataFrame."""
    print("CSV file received.")
    
    # Check if the file is empty
    csv_file.seek(0)  # Reset file pointer to the beginning
    file_content = csv_file.read()  # Read the content of the file
    if not file_content:  # Check if file content is empty
        print("Uploaded CSV file is empty.")
        return None, 'Uploaded CSV file is empty.'

    data_rows = []  # Initialize list to hold rows of data
    try:
        # Reset file pointer again after reading
        csv_file.seek(0)  
        csv_data = file_content.decode('ISO-8859-1', errors='ignore')  # Specify encoding
        io_string = io.StringIO(csv_data)  # Create a StringIO object for CSV reading
        reader = csv.reader(io_string, delimiter=',')  # Create CSV reader

        for row in reader:
            data_rows.append(row[:10])  # Take only the first 10 elements of each row

        if data_rows and len(data_rows) > 1:
            # Create DataFrame using the first row as header
            df = pd.DataFrame(data_rows[1:], columns=[col.strip() for col in data_rows[0][:10]])
            return df, None  # Return DataFrame and no error message

    except Exception as e:
        print(f"Error processing CSV file: {e}")  # Print any errors
        return None, str(e)



def main():

    csv_filename = 'ACR.csv'
    with open(csv_filename, 'rb') as csv_file:
        df, error = handle_csv_upload(csv_file)

    if error:
        print(error)
        return

    # Process the DataFrame
    df[['SYS', 'DIA']] = df['PA(mmHg)'].str.split('/', expand=True)

    # Extract PA values
    pa_values = []
    above_140 = 0
    between_100_140 = 0
    below_100 = 0
    total = len(df['SYS'])
    for i in df['SYS']:
        if re.search('-', i):
            print(f"Invalid value found: {i}")
        else:
            pa_values.append(int(i))
            if int(i) > 140:
                above_140 += 1
            elif int(i) >= 100:
                between_100_140 += 1
            else:
                below_100 += 1

    # percentage for each category
    above_140 = (above_140 / total) * 100
    between_100_140 = (between_100_140 / total) * 100
    below_100 = (below_100 / total) * 100

    # Data for the circle graph
    sections = [between_100_140, above_140, below_100]
    labels = ['mmHg (100-140)', 'Encima (Above 140)', 'Bajo (Below 100)']
    
    # Create circle graph with custom legend and save it to a BytesIO object
    img_buffer_circle = create_circle_graph_with_legend(sections, labels)

    # Specify the PDF filename
    pdf_filename = "circle_graph_with_legend.pdf"
    
    # Save the circle graph to the PDF
    save_plot_to_pdf(img_buffer_circle, pdf_filename)

if __name__ == "__main__":
    main()
