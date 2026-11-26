import pandas as pd
import numpy as np
from pathlib import Path
from openpyxl import load_workbook
import re

def parse_samplename(samplename: str) -> dict:
    '''
    Parse sample's file name from first column of input data to extract conditions:
    * lipofectamine ratio
    * dna dose
    * rna dose
    * cell count

    Args:
        samplename (str): Sample's name

    Returns:
        dict: Dictionary with extracted sample conditions
    '''
    lipo = np.nan
    dna_dose = np.nan
    rna_dose = np.nan
    cell_no = np.nan

    l = re.search(r'Lipo1-(\d+)', samplename)
    if l:
        lipo = int(l.group(1))

    d = re.search(r'GFP(\d+)', samplename)
    if d:
        dna_dose = int(d.group(1))

    r = re.search(r'CHER(\d+)', samplename)
    if r:
        rna_dose = int(r.group(1))

    c = re.search(r'_(\d+)k(?:_|\.fcs)', samplename)
    if c:
        cell_no = int(c.group(1))*1000

    return {'lipo_ratio, 1:': lipo,
            'dna_dose, ng': dna_dose,
            'mrna_dose, ng': rna_dose,
            'cell_count': cell_no
            }

def parse_filename(filename: str) -> dict:
    '''
    Parse file name from from excel file name for:
    * time point
    * experiment code

    Args:
        filename (str): Experiment file name

    Returns:
        dict: Dictionary with extracted sample conditions
    '''
    time = np.nan
    exp_code = np.nan

    t = re.search(r'_(\d+)h_', filename)
    if t:
        time = int(t.group(1))

    exp_code = filename.split('_')[0]
    print(exp_code)

    return {'experiment': exp_code,
    'time, h': time
    }

cwd = Path(__file__).parent

# Load input experiment and master data file
exp_file = '468-040-01-Exp3_24h_26-11-17.xls'
tidy_file = '468-040-01_tidy_data.xlsx'

exp_df = pd.read_excel(cwd / exp_file, engine='calamine')
tidy_df = pd.read_excel(cwd / tidy_file, engine='calamine')

# FlowJo saves values as strings, converting to float
cols_to_parse = ['%viability', '%GFP-only', '%CHE-only', '%co-transfected']
for col in cols_to_parse:
    if col not in exp_df.columns:
        continue

    exp_df[col] = (exp_df[col]
             .astype(str)
             .str.replace('%', '')
             .str.strip()
             .replace('n/a', pd.NA)
             .astype(float)
             )

    exp_df.loc[exp_df[col] < 0.6, col] = 0  # Removing single incorrect events from gates

# Extract time point and experiment code from file name
filename_parsed = parse_filename(exp_file)

# Extract condition parameters from the FlowJo sample name
new_rows = []
for _, row in exp_df.iterrows():

    parsed = parse_samplename(row[exp_df.columns[0]])

    # Left: col names from tidy data file, right: col names from experiment data file
    tidy_row = {
      'fccs_sample_name': row.iloc[0],
      **parsed,
      **filename_parsed,
      '%viability': row.get('%viability'),
      'cel_count':  row.get('count'),
      'GFP_%':      row.get('%GFP-only'),
      'GFP_mfi':    row.get('GFP+_mfi'),
      'CHER_%':     row.get('%CHE-only'),
      'CHER_mfi':   row.get('CHE+_mfi'),
      'cotrans_%':  row.get('%co-transfected'),
  }

  # Check if row is already present in the tidy dataframe (all below cell values in row match)
    if tidy_df.empty:
        exists = False
    else:
        exists = (
        (tidy_df['%viability'] == tidy_row['%viability']) &
        (tidy_df['GFP_%'] == tidy_row['GFP_%']) &
        (tidy_df['CHER_%'] == tidy_row['CHER_%']) &
        (tidy_df['cotrans_%'] == tidy_row['cotrans_%'])
        ).any()

    if not exists:
      new_rows.append(tidy_row)

# Construct interim dataframe from extracted values
temp_df = pd.DataFrame(new_rows)

# Not all columns are encoded in file name or FlowJo output file, add missing values as NaN
for col in tidy_df.columns:
    if col not in temp_df.columns:
        temp_df[col] = np.nan

temp_df = temp_df[tidy_df.columns]

# Pandas overrides exel file, losing formatting. Using openpyxl to preserve formatting.
wb = load_workbook(cwd / tidy_file)
ws = wb.active

# openpyxl detect cell formatting as row with data, detecting those
last_row = 1
for row in range(ws.max_row, 1, -1):
    if ws.cell(row, 1).value is not None:
        last_row = row
        break

print(f'Last data row: {last_row}')

start_row = last_row + 1
for row, values in enumerate(temp_df.itertuples(index=False, name=None), start=start_row):
    for col, value in enumerate(values, start=1):
        ws.cell(row=row, column=col, value=value)

wb.save(cwd / tidy_file)

print('Data import successfull')
