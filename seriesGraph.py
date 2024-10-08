import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import re
import io
import csv


import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

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


def create_custom_plot(pa_values, fp_values, dia_values, time_labels):
    """
    Create a line plot with shaded areas, secondary y-axis, and dotted lines between curves.

    Parameters:
    - pa_values: List or array of PA values (mmHg).
    - fp_values: List or array of FP values (BPM).
    - dia_values: List or array of DIA values (mmHg).
    - time_labels: List of time labels in HH:MM format.

    Returns:
    - img_buffer: A BytesIO object containing the saved plot image.
    """
    x = np.arange(len(pa_values))  # Create an x array based on the length of the input values

    # Plot configuration
    fig, ax1 = plt.subplots(figsize=(16, 12))

    # PA and DIA line plots (left axis)
    ax1.plot(x, pa_values, color='blue', label='PA [mmHg]')
    ax1.plot(x, dia_values, color='green', label='DIA [mmHg]')  # Plot DIA values
    ax1.set_xlabel('Time')
    ax1.set_ylabel('PA [mmHg] & DIA [mmHg]', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_yticks(np.arange(10, 220, 10))
    ax1.set_ylim(10, 210)

    # Secondary y-axis for FP
    ax2 = ax1.twinx()
    ax2.plot(x, fp_values, color='red', label='FP [BPM]')
    ax2.set_ylabel('FP [BPM]', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_yticks(np.arange(40, 240, 10))

    # Adding dotted lines between PA and DIA curves
    for i in range(len(x)):
        ax1.plot([x[i], x[i]], [pa_values[i], dia_values[i]], color='black', linestyle='dotted', linewidth=1)

    # Shade the area between x=22:00 and x=07:00
    start_index = time_labels.index('22:00')  # Find the index for 22:00
    end_index = time_labels.index('07:00')    # Find the index for 07:00
    last_index = len(time_labels) - 1          # Last index of the time labels
    ax1.axvspan(start_index, end_index, color='gray', alpha=0.3)  # From 22:00 to end

    # Set x-axis ticks to represent time labels
    ax1.set_xticks(np.arange(0, len(time_labels), 2))
    ax1.set_xticklabels(time_labels[::2], rotation=90)

    # Add step line for yellow line with steps
    step_x = np.array([0, start_index, start_index, end_index, end_index, last_index])  # Create the stepped x-values
    step_y = np.array([135, 135, 120, 120, 135, 135])
    ax1.step(step_x, step_y, color='yellow', linewidth=2, where='post')

    # Add step line for yellow line with steps
    step_x = np.array([0, start_index, start_index, end_index, end_index, last_index])  # Create the stepped x-values
    step_y = np.array([85, 85, 70, 70, 85, 85])
    ax1.step(step_x, step_y, color='yellow', linewidth=2, where='post')


    plt.title('Tendencia PA y DIA vs Tiempo')
    ax1.grid(True)

    # Add legends
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Save plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    img_buffer.seek(0)

    return img_buffer


# The rest of your code remains unchanged



def save_plot_to_pdf(img_buffer, pdf_filename, y):
    """Insert the image from the BytesIO object into a PDF at specified coordinates, centered."""
    c = canvas.Canvas(pdf_filename, pagesize=letter)  # Create a PDF canvas
    
    image_reader = ImageReader(img_buffer)  # Read the image from buffer

    # Double the image dimensions
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

# Main function to generate the PDF with the custom plot
def main():
    csv_filename = 'ACR.csv'
    with open(csv_filename, 'rb') as csv_file:
        df, error = handle_csv_upload(csv_file)

    if error:
        print(error)
        return

    # Process the DataFrame
    df[['SYS', 'DIA']] = df['PA(mmHg)'].str.split('/', expand=True)

    # Extract PA and FP values
    pa_values = []
    for i in df['SYS']:
        if re.search('-', i):
            print(i)
        else:
            pa_values.append(int(i))

    fp_values = []
    for i in df['FP(BPM)']:
        if re.search('-', i):
            print(i)
        else:
            fp_values.append(int(i))


    dia_values = []
    for i in df['DIA']:
        if re.search('-', i):
            print(i)
        else:
            dia_values.append(int(i))

    # Extract time labels
    time_labels = df['Hora'].tolist()

    # Create custom plot and save it to a BytesIO object
    img_buffer = create_custom_plot(pa_values, fp_values, dia_values, time_labels)

    # Specify the PDF filename
    pdf_filename = "customGraph.pdf"  # Output PDF file name
    
    # Specify the coordinates for the image
    x_position = 1 * inch  # X coordinate for the graph
    y_position = 5 * inch  # Y coordinate for the graph
    
    # Save the custom graph image to the PDF at specified coordinates
    save_plot_to_pdf(img_buffer, pdf_filename, y_position)  # Save the plot to PDF

if __name__ == "__main__":
    main()  # Run the main function
