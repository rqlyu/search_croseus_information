import os
import csv

# --- CONFIGURATION ---
CANONICAL_FILE = 'Cr_NP.fasta'
# Add ALL your sequence files here
OTHER_FILES = [
    'Cr_2015.fasta',
    'Cr_2016.fasta',
    'Cr_2022.fasta',
    'Cr_2023.fasta',
    'Cr_2023.fasta',
    'Cr_T1.fasta'
]
OUTPUT_MAP = 'id_mapping.csv'

def clean_sequence(seq_list):
    """Joins lines, removes whitespace and trailing asterisks (*)."""
    full_seq = "".join(seq_list).upper().strip()
    if full_seq.endswith('*'):
        full_seq = full_seq[:-1] # Remove the star
    return full_seq

def read_fasta_to_dict(filename):
    seq_map = {}
    current_ids = []
    current_seq = []
    
    print(f"   Reading {filename}...")
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # Save previous
                    if current_seq and current_ids:
                        final_seq = clean_sequence(current_seq)
                        if final_seq not in seq_map: seq_map[final_seq] = []
                        seq_map[final_seq].extend(current_ids)
                    
                    # Start new
                    raw_header = line[1:]
                    gene_id = raw_header.split()[0]
                    current_ids = [gene_id]
                    current_seq = []
                else:
                    current_seq.append(line)
            # Save last
            if current_seq and current_ids:
                final_seq = clean_sequence(current_seq)
                if final_seq not in seq_map: seq_map[final_seq] = []
                seq_map[final_seq].extend(current_ids)
    except FileNotFoundError:
        print(f"⚠️  Warning: Could not find {filename}")
    return seq_map

def main():
    print("--- 1. Memorizing 'Old' Sequences (ignoring *) ---")
    sequence_database = {} 

    for fname in OTHER_FILES:
        file_map = read_fasta_to_dict(fname)
        for seq, ids in file_map.items():
            if seq not in sequence_database: sequence_database[seq] = []
            for i in ids:
                if i not in sequence_database[seq]: sequence_database[seq].append(i)

    print(f"   Memorized {len(sequence_database)} unique sequences.")

    print("\n--- 2. Linking to Canonical IDs ---")
    canonical_map = [] 
    
    try:
        with open(CANONICAL_FILE, 'r') as f:
            current_id = None
            current_seq = []
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id and current_seq:
                        final_seq = clean_sequence(current_seq)
                        if final_seq in sequence_database:
                            old_ids_str = ", ".join(sequence_database[final_seq])
                            canonical_map.append([current_id, old_ids_str])
                    current_id = line[1:].split()[0]
                    current_seq = []
                else:
                    current_seq.append(line)
            # Last one
            if current_id and current_seq:
                final_seq = clean_sequence(current_seq)
                if final_seq in sequence_database:
                    canonical_map.append([current_id, ", ".join(sequence_database[final_seq])])

    except FileNotFoundError:
        print(f"❌ Error: Canonical file {CANONICAL_FILE} not found.")
        return

    print(f"--- 3. Saving {len(canonical_map)} matches to {OUTPUT_MAP} ---")
    with open(OUTPUT_MAP, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Gene_ID', 'Other_IDs'])
        writer.writerows(canonical_map)
    print("✅ Done! Now run 'make_jason.py' again.")

if __name__ == "__main__":
    main()