import pandas as pd
import json

# --- UPDATED CONFIGURATION ---
# 1. Update these names to match EXACTLY what is in your folder
ANNOTATION_FILE = 'Cr_Annotations_Eggo.xlsx' 
GO_FILE = 'Croseus_GO_NP.xlsx'  
FASTA_FILE = 'Cr_NP.fasta'
OUTPUT_FILE = 'data.json'

def parse_fasta(file_path):
    sequences = {}
    current_id = None
    current_seq = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_id:
                    sequences[current_id] = ''.join(current_seq)
                current_id = line[1:].split()[0]
                current_seq = []
            else:
                current_seq.append(line)
        if current_id:
            sequences[current_id] = ''.join(current_seq)
    return sequences

def main():
    print("1. Loading Annotations (Excel mode)...")
    
    # CHANGED: Using read_excel instead of read_csv
    # This requires the 'openpyxl' library. If you get an error, run: pip install openpyxl
    df_anno = pd.read_excel(ANNOTATION_FILE) 
    
    # Clean up column names
    df_anno.columns = [c.strip() for c in df_anno.columns]
    df_anno = df_anno.fillna("")

    print("2. Loading Sequences...")
    seq_dict = parse_fasta(FASTA_FILE)

    print("3. Merging Data...")
    records = df_anno.to_dict(orient='records')
    
    final_data = []
    for row in records:
        gene_id = str(row.get('Gene_ID', '')).strip()
        
        if gene_id in seq_dict:
            row['Sequence'] = seq_dict[gene_id]
        else:
            row['Sequence'] = "Sequence not available"

        if not row.get('Description'):
            row['Description'] = row.get('Preferred_name', '')

        final_data.append(row)

    print(f"4. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_data, f)
    
    print(f"Done! Processed {len(final_data)} genes.")

if __name__ == "__main__":
    main()