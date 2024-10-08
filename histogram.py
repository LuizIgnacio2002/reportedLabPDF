import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import io
import csv
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

def create_bar_graph(data, bins):
    # Create a histogram
    counts, edges, patches = plt.hist(data, bins=bins, edgecolor='black', color='green')

    # Add percentages above the bars, but only if the percentage is greater than 0
    total = len(data)
    for i in range(len(patches)):
        height = patches[i].get_height()
        if height > 0:
            percentage = f'{height / total:.0%}'
            plt.text(patches[i].get_x() + patches[i].get_width() / 2, height, percentage, ha='center', va='bottom')

    plt.title('Histogram of PA Values')

    # Set x-axis ticks to be the bin edges
    plt.xticks(bins)

    # Set y-axis ticks and labels
    y_ticks = np.arange(0, 100, 10)  # Adjust the step as needed
    plt.yticks(y_ticks)

    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)  # Move the cursor to the start of the buffer
    plt.close()  # Close the plot to release memory

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
    for i in df['SYS']:
        if re.search('-', i):
            print(f"Invalid value found: {i}")
        else:
            pa_values.append(int(i))

    # Create bins for x values
    bins = [80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]

    # Create bar graph and save it to a BytesIO object
    img_buffer = create_bar_graph(pa_values, bins)
    
    # Specify the PDF filename
    pdf_filename = "histogram_report.pdf"
    
    # Specify the coordinates for the image
    x_position = 1 * inch  # X coordinate
    y_position = 5 * inch  # Y coordinate
    
    # Save the bar graph image to the PDF at specified coordinates
    save_bar_graph_to_pdf(img_buffer, pdf_filename, x_position, y_position)

if __name__ == "__main__":
    main()
