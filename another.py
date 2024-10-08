import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import re
import io
import csv

def create_custom_plot(pa_values, fp_values):
    x = np.arange(len(pa_values))  # Create an x array based on the length of the input values

    # Double the figure size
    fig, ax1 = plt.subplots(figsize=(16, 12))  # Changed from (8, 6) to (16, 12)

    # PA line plot (left axis)
    ax1.plot(x, pa_values, color='blue', label='PA [mmHg]')
    ax1.set_xlabel('Hour')
    ax1.set_ylabel('PA [mmHg]', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax1.set_yticks(np.arange(10, 220, 10))
    ax1.set_ylim(10, 210)

    # Secondary y-axis for FP
    ax2 = ax1.twinx()
    ax2.plot(x, fp_values, color='red', label='FP [BPM]')
    ax2.set_ylabel('FP [BPM]', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    ax2.set_yticks(np.arange(40, 240, 10))

    # Adding dotted lines between PA and FP curves
    for i in range(len(x)):
        fp_value_scaled = ax1.get_ylim()[0] + (fp_values[i] - ax2.get_ylim()[0]) * (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / (ax2.get_ylim()[1] - ax2.get_ylim()[0])
        ax1.plot([x[i], x[i]], [pa_values[i], fp_value_scaled], color='black', linestyle='dotted', linewidth=1)

    # Set x-axis ticks for the specified hours only
    hour_labels = [17, 18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    hour_indices = np.linspace(0, len(pa_values) - 1, num=len(hour_labels), dtype=int)  # Indices for x-ticks

    ax1.set_xticks(hour_indices)  # Set x-ticks to the hour indices
    ax1.set_xticklabels(hour_labels, rotation=45)  # Set hour labels with optional rotation

    plt.title('Tendencia PA vs Tiempo')
    ax1.grid(True)

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close()
    img_buffer.seek(0)

    return img_buffer




def save_plot_to_pdf(img_buffer, pdf_filename, y):
    """Insert the image from the BytesIO object into a PDF at specified coordinates, centered."""
    c = canvas.Canvas(pdf_filename, pagesize=letter)  # Create a PDF canvas
    
    image_reader = ImageReader(img_buffer)  # Read the image from buffer

    # Set image dimensions
    img_width = 9 * inch  # Set image width
    img_height = (img_width * 4) / 6  # Maintain aspect ratio

    # Calculate x position to center the image
    page_width = letter[0]  # Width of the PDF page
    x_position = (page_width - img_width) / 2  # Center the image horizontally

    c.drawImage(image_reader, x_position, y, width=img_width, height=img_height)  # Draw the image on PDF
    c.save()  # Save the PDF
    print(f"PDF generated: {pdf_filename}")  # Confirmation message

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

# Main function to generate the PDF with the custom plothe plot to PDF
def main():
    # Read the CSV file from your source (simulated here)
    csv_filename = 'ACR.csv'  # Replace with your actual CSV filename
    csv_file = open(csv_filename, 'rb')  # Open in binary mode

    df, error = handle_csv_upload(csv_file)  # Process the CSV file
    csv_file.close()  # Don't forget to close the file after reading

    if error:
        print(error)  # Print any error message
        return

    # Process the DataFrame
    df[['SYS', 'DIA']] = df['PA(mmHg)'].str.split('/', expand=True)  # Split PA into SYS and DIA

    # Extract PA and FP values
    pa_values = []
    for i in df['SYS']:
        if re.search('-', i):
            print(f"Invalid PA value: {i}")
        else:
            pa_values.append(int(i))
    
    fp_values = []
    for i in df['FP(BPM)']:
        if re.search('-', i):
            print(f"Invalid FP value: {i}")
        else:
            fp_values.append(int(i))

    # Print lengths and values for debugging
    print(f"Length of PA values: {len(pa_values)}")
    print(f"Length of FP values: {len(fp_values)}")
    print(f"PA values: {pa_values}")
    print(f"FP values: {fp_values}")

    # Generate hour labels based on the number of data points
    num_data_points = len(pa_values)
    hour_labels = [(17 + i) % 24 for i in range(24)]  # Adjusting for 24-hour format
    print(f"Length of hour labels: {len(hour_labels)}")
    print(f"Hour labels: {hour_labels}")

    # Create custom plot and save it to a BytesIO object
    img_buffer = create_custom_plot(pa_values, fp_values)  # Generate the plot image

    # Specify the PDF filename
    pdf_filename = "customGraph.pdf"  # Output PDF file name
    
    # Specify the coordinates for the image
    x_position = 1 * inch  # X coordinate for the graph
    y_position = 5 * inch  # Y coordinate for the graph
    
    # Save the custom graph image to the PDF at specified coordinates
    save_plot_to_pdf(img_buffer, pdf_filename, y_position)  # Save the plot to PDF


if __name__ == "__main__":
    main()  # Run the main function
