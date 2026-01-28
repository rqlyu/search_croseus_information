import pandas as pd
import json
import os

# --- 1. CONFIGURATION: filenames ---
# Canonical File (The "Master" List)
CANONICAL_FASTA = 'Cr_NP.fasta'
ANNOTATION_FILE = 'Cr_Annotations_Eggo.xlsx'

# Old Version Files (To extract "Other IDs" from)
OLD_FASTAS = [
    'Cr_2015.fasta', 
    'Cr_2016.fasta', 
    'Cr_2022.fasta', 
    'Cr_2023.fasta', 
    'Cr_NCB.fasta'
]
OUTPUT_FILE = 'data.json'

def clean_seq(seq_lines):
    """Joins lines and removes trailing *"""
    s = "".join(seq_lines).strip().upper()
    if s.endswith('*'): s = s[:-1]
    return s

def read_fasta(filepath):
    """Returns dict: { SequenceString: [List of IDs] }"""
    print(f"   Reading {filepath}...")
    seq_map = {}
    if not os.path.exists(filepath):
        print(f"   ⚠️ File not found: {filepath}")
        return {}
        
    with open(filepath, 'r') as f:
        curr_id, curr_seq = None, []
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if curr_id:
                    s = clean_seq(curr_seq)
                    if s not in seq_map: seq_map[s] = []
                    seq_map[s].append(curr_id)
                curr_id = line[1:].split()[0] # Get ID only
                curr_seq = []
            else:
                curr_seq.append(line)
        if curr_id:
            s = clean_seq(curr_seq)
            if s not in seq_map: seq_map[s] = []
            seq_map[s].append(curr_id)
    return seq_map

def main():
    print("--- STEP 1: Memorizing Old Sequences ---")
    old_seq_db = {} # { Sequence: [List of Old IDs] }
    
    for fname in OLD_FASTAS:
        data = read_fasta(fname)
        for seq, ids in data.items():
            if seq not in old_seq_db: old_seq_db[seq] = []
            for i in ids:
                if i not in old_seq_db[seq]: old_seq_db[seq].append(i)
    
    print(f"   Memorized {len(old_seq_db)} unique protein sequences from old versions.")

    print("\n--- STEP 2: Loading Canonical Sequences & Mapping ---")
    # We build the main dictionary: { Canonical_ID: {Sequence: "...", Other_IDs: "..."} }
    gene_db = {} 
    
    with open(CANONICAL_FASTA, 'r') as f:
        curr_id, curr_seq = None, []
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if curr_id:
                    s = clean_seq(curr_seq)
                    # Find matches
                    others = old_seq_db.get(s, [])
                    gene_db[curr_id] = {
                        "Gene_ID": curr_id,
                        "Sequence": s,
                        "Other_IDs": ", ".join(others)
                    }
                curr_id = line[1:].split()[0]
                curr_seq = []
            else:
                curr_seq.append(line)
        # Last one
        if curr_id:
            s = clean_seq(curr_seq)
            others = old_seq_db.get(s, [])
            gene_db[curr_id] = {
                "Gene_ID": curr_id,
                "Sequence": s,
                "Other_IDs": ", ".join(others)
            }
            
    print(f"   Loaded {len(gene_db)} canonical genes.")

    print("\n--- STEP 3: Merging Annotations ---")
    try:
        df = pd.read_excel(ANNOTATION_FILE)
        df = df.fillna("")
        
        # Merge annotation info into our gene_db
        count = 0
        for _, row in df.iterrows():
            gid = str(row.get('Gene_ID', '')).strip()
            if gid in gene_db:
                gene_db[gid]['Description'] = row.get('Description', '')
                gene_db[gid]['Preferred_name'] = row.get('Preferred_name', '')
                gene_db[gid]['GO_term'] = row.get('GO_term', '')
                count += 1
                
        print(f"   Added annotations to {count} genes.")
        
    except FileNotFoundError:
        print(f"   ❌ Error: Annotation file {ANNOTATION_FILE} not found!")

    print("\n--- STEP 4: Saving JSON ---")
    final_list = list(gene_db.values())
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_list, f)
        
    print(f"✅ SUCCESS! Created {OUTPUT_FILE} with {len(final_list)} genes.")
    print("   Upload this file to GitHub now.")

if __name__ == "__main__":
    main()
