import csv

# Define the path to your CSV file
csv_file_path = 'rsna_per_breast.csv'

# Read the content of the CSV file
with open(csv_file_path, mode='r', newline='') as file:
    reader = csv.reader(file)
    rows = list(reader)

# Check if the CSV already has a header row and how many columns it has
header_row = rows[0]
num_existing_columns = len(header_row)

# Add new column names for "inference_1", "inference_2", ..., "inference_512"
# Starting from the column after the existing ones
for i in range(1, 513):
    header_row.append(f'inference_{i}')

# Write the modified content back to the CSV
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header_row)  # Write the updated header row
    for row in rows[1:]:  # Write the rest of the rows (excluding the original header)
        # If your CSV needs to fill the new columns with default values, add them here
        row.extend([''] * 512)  # Assuming you want to fill new columns with empty strings
        writer.writerow(row)