import pandas as pd

# Load the CSV file into a DataFrame
file_path = 'model_times.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path)

# Set the value for base.en
base_value = 0.5

# Set the value for medium.en
medium_value = 0.6

# Insert values into the DataFrame
df['base.en'] = base_value

# Check if 'medium.en' column exists, if not, create it
if 'medium.en' not in df.columns:
    df['medium.en'] = None

# Insert the value into the 'medium.en' column
df.loc[:, 'medium.en'] = medium_value

# Save the updated DataFrame back to the CSV file
df.to_csv(file_path, index=False)
