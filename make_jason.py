import pandas as pd
import json
import os

# --- CONFIGURATION ---
ANNOTATION_FILE = 'Cr_Annotations_Eggo.xlsx'
GO_FILE = 'Croseus_GO_NP.xlsx'
FASTA_FILE = 'Cr_NP.fasta'  # Protein sequences
CDS_FASTA_FILE = 'Cr_NP_cds.fasta'  # NEW: CDS sequences
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
    print("="*80)
    print("C. roseus Gene Database Builder")
    print("="*80)
    
    print("\n1. Loading Annotations...")
    try:
        df_anno = pd.read_excel(ANNOTATION_FILE)
    except FileNotFoundError:
        print(f"❌ Error: '{ANNOTATION_FILE}' not found.")
        return

    # Clean columns
    df_anno.columns = [c.strip() for c in df_anno.columns]
    df_anno = df_anno.fillna("")

    print(f"   ✓ Columns found: {df_anno.columns.tolist()[:5]}... (showing first 5)")
    print(f"   ✓ Total records: {len(df_anno)}")

    print("\n2. Loading ID Mappings (Other Versions)...")
    mapping_dict = {}
    if os.path.exists(MAPPING_FILE):
        try:
            df_map = pd.read_csv(MAPPING_FILE)
            for _, row in df_map.iterrows():
                gid = str(row['Gene_ID']).strip()
                others = str(row['Other_IDs']).strip()
                mapping_dict[gid] = others
            print(f"   ✓ Loaded {len(mapping_dict)} ID mappings.")
        except Exception as e:
            print(f"   ⚠️ Error reading mapping file: {e}")
    else:
        print(f"   ⚠️ '{MAPPING_FILE}' not found. Skipping cross-reference IDs.")

    print("\n3. Loading Protein Sequences...")
    protein_seq_dict = parse_fasta(FASTA_FILE)
    if protein_seq_dict:
        print(f"   ✓ Loaded {len(protein_seq_dict)} protein sequences.")
    else:
        print(f"   ⚠️ No protein sequences loaded.")

    print("\n4. Loading CDS Sequences...")
    cds_seq_dict = parse_fasta(CDS_FASTA_FILE)
    if cds_seq_dict:
        print(f"   ✓ Loaded {len(cds_seq_dict)} CDS sequences.")
    else:
        print(f"   ⚠️ No CDS sequences loaded.")

    print("\n5. Merging Data...")
    records = df_anno.to_dict(orient='records')
    
    final_data = []
    for row in records:
        # Use 'qseqid' as the primary Gene ID
        gene_id = str(row.get('qseqid', '')).strip()
        
        # Create a standardized record with consistent field names
        record = {
            'Gene_ID': gene_id,
            'Gene_Name': str(row.get('GN', '')).strip(),
            'Protein_Name': str(row.get('protein_name', '')).strip(),
            'Description': str(row.get('protein_name', '')).strip(),
            'Organism': str(row.get('OS', '')).strip(),
            'Hit_DB': str(row.get('hit_db', '')).strip(),
            'Hit_Accession': str(row.get('hit_accession', '')).strip(),
            'E_value': row.get('evalue', ''),
            'Percent_Identity': row.get('pident', ''),
            
            # NEW: Both Protein and CDS sequences
            'Protein_Sequence': protein_seq_dict.get(gene_id, "Protein sequence not available"),
            'CDS_Sequence': cds_seq_dict.get(gene_id, "CDS sequence not available"),
            
            'Other_IDs': mapping_dict.get(gene_id, ""),
        }
        
        # Keep backward compatibility with old field name
        record['Sequence'] = record['Protein_Sequence']
        
        # Include all original columns as well for reference
        record['_original'] = row

        final_data.append(record)

    print(f"\n6. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ SUCCESS! Database ready with {len(final_data)} records.")
    print(f"{'='*80}")
    
    print(f"\n📊 Sample record structure:")
    if final_data:
        sample = {k: v for k, v in final_data[0].items() if k != '_original'}
        # Truncate sequences for display
        sample_display = sample.copy()
        if len(sample_display.get('Protein_Sequence', '')) > 50:
            sample_display['Protein_Sequence'] = sample_display['Protein_Sequence'][:50] + '... (truncated)'
        if len(sample_display.get('CDS_Sequence', '')) > 50:
            sample_display['CDS_Sequence'] = sample_display['CDS_Sequence'][:50] + '... (truncated)'
        
        print(json.dumps(sample_display, indent=2)[:800] + "\n...")
    
    # Statistics
    protein_count = sum(1 for r in final_data if r['Protein_Sequence'] != "Protein sequence not available")
    cds_count = sum(1 for r in final_data if r['CDS_Sequence'] != "CDS sequence not available")
    
    print(f"\n📈 Statistics:")
    print(f"   - Total genes: {len(final_data)}")
    print(f"   - With protein sequences: {protein_count} ({protein_count/len(final_data)*100:.1f}%)")
    print(f"   - With CDS sequences: {cds_count} ({cds_count/len(final_data)*100:.1f}%)")
    print(f"\n✨ Ready to use with the updated HTML interface!")

if __name__ == "__main__":
    main()
