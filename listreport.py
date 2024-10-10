import io
import csv
import re
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Spacer

# Function to read CSV file and prepare DataFrame
def handle_csv_upload(csv_file):
    print("CSV file received.")
    
    csv_file.seek(0)
    file_content = csv_file.read()
    if not file_content:
        print("Uploaded CSV file is empty.")
        return None, 'Uploaded CSV file is empty.'

    data_rows = []
    try:
        csv_file.seek(0)
        csv_data = file_content.decode('ISO-8859-1', errors='ignore')
        io_string = io.StringIO(csv_data)
        reader = csv.reader(io_string, delimiter=',')
        for row in reader:
            data_rows.append(row[:10])

        if data_rows and len(data_rows) > 1:
            df = pd.DataFrame(data_rows[1:], columns=[col.strip() for col in data_rows[0][:10]])
            return df, None
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None, str(e)

# Function to safely convert strings to integers, skipping invalid entries
def safe_int_conversion(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# Function to check if a time is within a given range
def is_time_in_range(start, end, current):
    if start <= end:
        return start <= current < end
    else:  # Over midnight
        return start <= current or current < end

# Function to fill missing rows in the DataFrame
def fill_missing_rows(df):
    filled_rows = []
    skip_sequence = False

    for index, row in df.iterrows():
        if row['PA(mmHg)'] == '---/---' or pd.isna(row['PA(mmHg)']) or row['PA(mmHg)'] == "---":
            if not skip_sequence:  # Mark the first skipped row
                skip_sequence = True
                for next_index in range(index + 1, len(df)):
                    next_row = df.iloc[next_index]
                    if next_row['PA(mmHg)'] != '---/---' and not pd.isna(next_row['PA(mmHg)']) and next_row['PA(mmHg)'] != "---":
                        filled_row = next_row.copy()
                        filled_row['Original'] = row['PA(mmHg)']
                        filled_rows.append(filled_row)
                        break
            else:
                continue
        else:
            skip_sequence = False
            row['Original'] = row['PA(mmHg)']
            filled_rows.append(row)

    return pd.DataFrame(filled_rows).reset_index(drop=True)

# Function to generate numbering with skips
def get_numbering_with_skips(filled_df):
    numbering = []
    actual_index = 1
    skip_marked = False

    for idx, row in filled_df.iterrows():
        if row['Original'] == '---/---' or pd.isna(row['Original']) or row['Original'] == "---":
            if not skip_marked:
                numbering.append(f"{actual_index}++")
                skip_marked = True
            else:
                numbering.append(str(actual_index))
        else:
            numbering.append(str(actual_index))
            actual_index += 1
            skip_marked = False
    return numbering

# Function to remove redundant rows
def remove_redundant_rows_after_first(filled_df, numbering_with_skips):
    rows_to_keep = [0]
    seen_numbers = set()

    for index in range(1, len(numbering_with_skips)):
        number = numbering_with_skips[index]
        if re.match(r'\d+\+$', number):
            rows_to_keep.append(index)
            continue

        base_number = re.sub(r'\+\+$', '', number)
        if base_number not in seen_numbers:
            seen_numbers.add(base_number)
            rows_to_keep.append(index)

    return filled_df.iloc[rows_to_keep].reset_index(drop=True), [numbering_with_skips[i] for i in rows_to_keep]

# Function to generate PDF report with table
def generate_pdf_report(df, output_filename):
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    print("the df is", df)
    elements = []

    # Add a spacer to lower the table position by 20 units
    elements.append(Spacer(1, 20))

    table_data = [['Núm', 'Fecha', 'Tiempo', 'Sys', 'Map', 'Dia', 'PP', 'FR', 'Estado', 'Comentario']]
    df[['SYS', 'DIA']] = df['PA(mmHg)'].str.split('/', expand=True)

    filled_df = fill_missing_rows(df)
    numbering_with_skips = get_numbering_with_skips(filled_df)
    filled_df, numbering_with_skips = remove_redundant_rows_after_first(filled_df, numbering_with_skips)

    columns = list(filled_df.columns)
    last_column = columns.pop()
    columns.insert(-1, last_column)
    filled_df = filled_df[columns]

    for index, row in filled_df.iterrows():
        spo2_value = 0 if row['SpO2(%)'] == "---" else row['SpO2(%)']
        
        row_data = [
            numbering_with_skips[index], row['Fecha'], row['Hora'],
            row['SYS'], row['PAM(mmHg)'], row['DIA'], row['PP(mmHg)'],
            row['FP(BPM)'], spo2_value, row['Coment']
        ]
        table_data.append(row_data)

    table = Table(table_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Highlight cells based on "Sys" values and time conditions
    for i, row in enumerate(filled_df.itertuples(), start=1):
        # for sys_value in row.SYS:
        sys_value = safe_int_conversion(row.SYS)
        # for pam_value in df.PAM:
        #         row_data = [
        #     numbering_with_skips[index], row['Fecha'], row['Hora'],
        #     row['SYS'], row['PAM(mmHg)'], row['DIA'], row['PP(mmHg)'],
        #     row['FP(BPM)'], spo2_value, row['Coment']
        # ]
        dia_value = safe_int_conversion(row.DIA)

        if sys_value is not None:
            try:
                time_value = datetime.strptime(row.Hora, "%H:%M").time()
                if is_time_in_range(datetime.strptime("18:00", "%H:%M").time(), datetime.strptime("22:00", "%H:%M").time(), time_value):
                    if sys_value > 135:
                        style.add('BACKGROUND', (3, i), (3, i), colors.pink)

                    if dia_value > 85:
                        style.add('BACKGROUND', (5, i), (5, i), colors.pink)

                elif is_time_in_range(datetime.strptime("22:01", "%H:%M").time(), datetime.strptime("06:59", "%H:%M").time(), time_value):
                    if sys_value > 120:
                        style.add('BACKGROUND', (3, i), (3, i), colors.pink)

                    if dia_value > 75:
                        style.add('BACKGROUND', (5, i), (5, i), colors.pink)
                    # Add shading for "Fecha" and "Tiempo" columns
                    style.add('BACKGROUND', (1, i), (2, i), colors.lightgrey)
                else:
                    if sys_value > 135:
                        style.add('BACKGROUND', (3, i), (3, i), colors.pink)

                    if dia_value > 85:
                        style.add('BACKGROUND', (5, i), (5, i), colors.pink)
            except ValueError:
                continue

    table.setStyle(style)
    elements.append(table)
    doc.build(elements)

# Main function
def main():
    csv_filename = 'ACR.csv'
    with open(csv_filename, 'rb') as csv_file:
        df, error = handle_csv_upload(csv_file)

    if error:
        print(error)
        return

    output_filename = "ACR_report.pdf"
    generate_pdf_report(df, output_filename)
    print(f"PDF report generated: {output_filename}")

if __name__ == "__main__":
    main()
