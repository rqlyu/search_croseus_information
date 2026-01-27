import pandas as pd
import json

# --- CONFIGURATION ---
# These names must match the files on your Desktop EXACTLY
ANNOTATION_FILE = 'Cr_Annotations_Eggo.xlsx'
GO_FILE = 'Croseus_GO_NP.xlsx'
FASTA_FILE = 'Cr_NP.fasta'
OUTPUT_FILE = 'data.json'

def parse_fasta(file_path):
    """Reads fasta and returns {GeneID: Sequence}"""
    sequences = {}
    current_id = None
    current_seq = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id:
                        sequences[current_id] = ''.join(current_seq)
                    # Parse ID: ">M9H77_00686" -> "M9H77_00686"
                    current_id = line[1:].split()[0]
                    current_seq = []
                else:
                    current_seq.append(line)
            if current_id:
                sequences[current_id] = ''.join(current_seq)
    except FileNotFoundError:
        print(f"ERROR: Could not find fasta file: {file_path}")
        return {}
        
    return sequences

def main():
    print("1. Loading Annotations from Excel...")
    
    try:
        # Load the Excel file
        df_anno = pd.read_excel(ANNOTATION_FILE)
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find file '{ANNOTATION_FILE}'")
        print("   Please check that the file is in the same folder as this script.")
        return

    # Clean up column names
    df_anno.columns = [c.strip() for c in df_anno.columns]
    df_anno = df_anno.fillna("")

    print("2. Loading Sequences...")
    seq_dict = parse_fasta(FASTA_FILE)
    if not seq_dict:
        print("❌ Stopping because FASTA file was not found.")
        return

    print("3. Merging Data...")
    records = df_anno.to_dict(orient='records')
    
    final_data = []
    for row in records:
        # Get Gene ID (ensure it's a string)
        gene_id = str(row.get('Gene_ID', '')).strip()
        
        # Add Sequence
        if gene_id in seq_dict:
            row['Sequence'] = seq_dict[gene_id]
        else:
            row['Sequence'] = "Sequence not available"

        # Ensure Description exists
        if not row.get('Description'):
            row['Description'] = row.get('Preferred_name', '')

        final_data.append(row)

    print(f"4. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_data, f)
    
    print(f"✅ Success! Processed {len(final_data)} genes. Upload 'data.json' to GitHub.")

if __name__ == "__main__":
    main()
