import pandas as pd
import json
import os

# --- CONFIGURATION ---
ANNOTATION_FILE = 'Cr_Annotations_Eggo.xlsx'
GO_FILE = 'Croseus_GO_NP.xlsx'
FASTA_FILE = 'Cr_NP.fasta'
# NEW: File containing the ID mapping
MAPPING_FILE = 'id_mapping.csv' 
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
                    current_id = line[1:].split()[0]
                    current_seq = []
                else:
                    current_seq.append(line)
            if current_id:
                sequences[current_id] = ''.join(current_seq)
    except FileNotFoundError:
        print(f"⚠️ Warning: FASTA file '{file_path}' not found. Sequences will be empty.")
        return {}
    return sequences

def main():
    print("1. Loading Annotations...")
    try:
        df_anno = pd.read_excel(ANNOTATION_FILE)
    except FileNotFoundError:
        print(f"❌ Error: '{ANNOTATION_FILE}' not found.")
        return

    # Clean columns
    df_anno.columns = [c.strip() for c in df_anno.columns]
    df_anno = df_anno.fillna("")

    print("2. Loading ID Mappings (Other Versions)...")
    mapping_dict = {}
    if os.path.exists(MAPPING_FILE):
        try:
            # Assumes CSV has columns: Gene_ID, Other_IDs
            df_map = pd.read_csv(MAPPING_FILE)
            # Create a dictionary: { "M9H77...": "CRO_T123, Cro001..." }
            for _, row in df_map.iterrows():
                gid = str(row['Gene_ID']).strip()
                others = str(row['Other_IDs']).strip()
                mapping_dict[gid] = others
            print(f"   - Loaded {len(mapping_dict)} ID mappings.")
        except Exception as e:
            print(f"⚠️ Error reading mapping file: {e}")
    else:
        print(f"⚠️ '{MAPPING_FILE}' not found. Skipping cross-reference IDs.")

    print("3. Loading Sequences...")
    seq_dict = parse_fasta(FASTA_FILE)

    print("4. Merging Data...")
    records = df_anno.to_dict(orient='records')
    
    final_data = []
    for row in records:
        gene_id = str(row.get('Gene_ID', '')).strip()
        
        # 1. Attach Sequence
        row['Sequence'] = seq_dict.get(gene_id, "Sequence not available")

        # 2. Attach Other Versions (New Feature)
        # If we have a mapping, add it. If not, use empty string.
        row['Other_IDs'] = mapping_dict.get(gene_id, "")

        # 3. Ensure Description
        if not row.get('Description'):
            row['Description'] = row.get('Preferred_name', '')

        final_data.append(row)

    print(f"5. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_data, f)
    
    print(f"✅ Success! Database ready.")

if __name__ == "__main__":
    main()
