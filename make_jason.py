import pandas as pd
import json
import os
from collections import defaultdict

# --- CONFIGURATION ---
ANNOTATION_FILE = 'Cr_Annotations_Eggo.xlsx'
GO_FILE = 'Croseus_GO_NP.xlsx'
FASTA_FILE = 'Cr_NP.fasta'
CDS_FASTA_FILE = 'Cr_NP_cds.fasta'
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
        print(f"⚠️  Warning: FASTA file '{file_path}' not found.")
        return {}
    return sequences

def load_go_annotations(go_file):
    """Load GO annotations and create gene->GO mapping"""
    print("Loading GO annotations...")
    try:
        df_go = pd.read_excel(go_file)
        
        # Create a dictionary: gene_id -> list of GO terms
        gene_go_map = defaultdict(list)
        gene_go_desc_map = defaultdict(list)
        
        for _, row in df_go.iterrows():
            gene_id = row['Gene_ID']
            go_term = row['GO_term']
            description = row['Description']
            ontology = row['Ontology']
            
            gene_go_map[gene_id].append({
                'term': go_term,
                'description': description,
                'ontology': ontology
            })
            gene_go_desc_map[gene_id].append(description)
        
        print(f"   ✓ Loaded GO annotations for {len(gene_go_map)} genes")
        return gene_go_map, gene_go_desc_map
    
    except FileNotFoundError:
        print(f"   ⚠️  '{go_file}' not found. GO terms will be empty.")
        return {}, {}

def main():
    print("="*80)
    print("C. roseus Gene Database Builder (with GO Enrichment)")
    print("="*80)
    
    print("\n1. Loading Annotations...")
    try:
        df_anno = pd.read_excel(ANNOTATION_FILE)
    except FileNotFoundError:
        print(f"❌ Error: '{ANNOTATION_FILE}' not found.")
        return

    df_anno.columns = [c.strip() for c in df_anno.columns]
    df_anno = df_anno.fillna("")
    print(f"   ✓ Total annotation records: {len(df_anno)}")

    print("\n2. Loading ID Mappings...")
    mapping_dict = {}
    if os.path.exists(MAPPING_FILE):
        try:
            df_map = pd.read_csv(MAPPING_FILE)
            for _, row in df_map.iterrows():
                gid = str(row['Gene_ID']).strip()
                others = str(row['Other_IDs']).strip()
                mapping_dict[gid] = others
            print(f"   ✓ Loaded {len(mapping_dict)} ID mappings")
        except Exception as e:
            print(f"   ⚠️  Error reading mapping file: {e}")
    else:
        print(f"   ⚠️  '{MAPPING_FILE}' not found.")

    print("\n3. Loading Protein Sequences...")
    protein_seq_dict = parse_fasta(FASTA_FILE)
    if protein_seq_dict:
        print(f"   ✓ Loaded {len(protein_seq_dict)} protein sequences")

    print("\n4. Loading CDS Sequences...")
    cds_seq_dict = parse_fasta(CDS_FASTA_FILE)
    if cds_seq_dict:
        print(f"   ✓ Loaded {len(cds_seq_dict)} CDS sequences")

    print("\n5. Loading GO Annotations...")
    gene_go_map, gene_go_desc_map = load_go_annotations(GO_FILE)

    print("\n6. Merging Data...")
    records = df_anno.to_dict(orient='records')
    
    final_data = []
    for row in records:
        gene_id = str(row.get('qseqid', '')).strip()
        
        # Get GO terms for this gene
        go_terms = gene_go_map.get(gene_id, [])
        go_descriptions = gene_go_desc_map.get(gene_id, [])
        
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
            'Protein_Sequence': protein_seq_dict.get(gene_id, "Protein sequence not available"),
            'CDS_Sequence': cds_seq_dict.get(gene_id, "CDS sequence not available"),
            'Other_IDs': mapping_dict.get(gene_id, ""),
            
            # NEW: GO annotations
            'GO_terms': go_terms,
            'GO_count': len(go_terms),
            'GO_descriptions': '; '.join(go_descriptions[:5]) if go_descriptions else ""  # First 5 for search
        }
        
        # Backward compatibility
        record['Sequence'] = record['Protein_Sequence']
        record['_original'] = row

        final_data.append(record)

    print(f"\n7. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ SUCCESS! Database ready with {len(final_data)} records")
    print(f"{'='*80}")
    
    # Statistics
    protein_count = sum(1 for r in final_data if r['Protein_Sequence'] != "Protein sequence not available")
    cds_count = sum(1 for r in final_data if r['CDS_Sequence'] != "CDS sequence not available")
    go_count = sum(1 for r in final_data if r['GO_count'] > 0)
    
    print(f"\n📈 Statistics:")
    print(f"   - Total genes: {len(final_data)}")
    print(f"   - With protein sequences: {protein_count} ({protein_count/len(final_data)*100:.1f}%)")
    print(f"   - With CDS sequences: {cds_count} ({cds_count/len(final_data)*100:.1f}%)")
    print(f"   - With GO annotations: {go_count} ({go_count/len(final_data)*100:.1f}%)")
    print(f"\n✨ Ready for GO enrichment analysis!")

if __name__ == "__main__":
    main()
