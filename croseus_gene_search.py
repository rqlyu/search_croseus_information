#!/usr/bin/env python3
"""
Croseus Gene Search Tool
A comprehensive tool for searching and analyzing Croseus genes across multiple versions.

Features:
1. Search by Gene ID or sequence (DNA/protein)
2. Cross-version gene ID mapping
3. GO enrichment analysis
4. Gene annotation display
"""

import os
import pandas as pd
import sqlite3
from flask import Flask, render_template, request, jsonify, send_from_directory
# Simple FASTA parser to replace Biopython
class SimpleSeqRecord:
    def __init__(self, id, seq):
        self.id = id
        self.seq = seq

def parse_fasta(filepath):
    """Simple FASTA parser"""
    records = []
    current_id = None
    current_seq = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_id is not None:
                    records.append(SimpleSeqRecord(current_id, ''.join(current_seq)))
                current_id = line[1:]  # Remove '>' prefix
                current_seq = []
            else:
                current_seq.append(line)
        
        # Add last record
        if current_id is not None:
            records.append(SimpleSeqRecord(current_id, ''.join(current_seq)))
    
    return records
import re
from collections import defaultdict
import json
from scipy.stats import hypergeom
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'croseus_gene_search_2024'

class CroseusDatabase:
    def __init__(self, data_dir='/mnt/user-data/uploads'):
        self.data_dir = data_dir
        self.db_path = '/home/claude/croseus.db'
        self.gene_mappings = defaultdict(dict)
        self.sequences = {}
        self.annotations = {}
        self.go_terms = {}
        self.version_names = {
            'Cr_NP': 'Canonical (NP)',
            'Cr_NCB': 'NCB',
            'Cr_2023': '2023 Version', 
            'Cr_2022': '2022 Version',
            'Cr_2016': '2016 Version',
            'Cr_2015': '2015 Version'
        }
        
    def init_database(self):
        """Initialize SQLite database and load all data"""
        print("Initializing Croseus database...")
        
        # Create SQLite database
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_tables()
        
        # Load data
        self.load_sequences()
        self.load_annotations() 
        self.load_go_terms()
        self.build_gene_mappings()
        
        print("Database initialization complete!")
        
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Sequences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY,
                gene_id TEXT,
                version TEXT,
                sequence TEXT,
                sequence_type TEXT,
                length INTEGER
            )
        ''')
        
        # Gene mappings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gene_mappings (
                id INTEGER PRIMARY KEY,
                canonical_id TEXT,
                version TEXT,
                version_id TEXT
            )
        ''')
        
        # Annotations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY,
                protein_id TEXT,
                gene_id TEXT,
                description TEXT,
                preferred_name TEXT,
                go_term TEXT,
                kegg_ko TEXT,
                kegg_pathway TEXT
            )
        ''')
        
        # GO terms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS go_terms (
                id INTEGER PRIMARY KEY,
                gene_id TEXT,
                go_term TEXT,
                description TEXT,
                ontology TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_gene_id ON sequences(gene_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_version ON sequences(version)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_canonical ON gene_mappings(canonical_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_go_gene ON go_terms(gene_id)')
        
        self.conn.commit()
        
    def load_sequences(self):
        """Load sequences from all FASTA files"""
        print("Loading sequences...")
        cursor = self.conn.cursor()
        
        fasta_files = {
            'Cr_NP': 'Cr_NP.fasta',
            'Cr_NCB': 'Cr_NCB.fasta', 
            'Cr_2023': 'Cr_2023.fasta',
            'Cr_2022': 'Cr_2022.fasta',
            'Cr_2016': 'Cr_2016.fasta',
            'Cr_2015': 'Cr_2015.fasta'
        }
        
        for version, filename in fasta_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                print(f"Warning: {filepath} not found, skipping...")
                continue
                
            print(f"Processing {filename}...")
            count = 0
            
            try:
                for record in parse_fasta(filepath):
                    gene_id = record.id
                    sequence = str(record.seq)
                    seq_type = 'protein'  # Assuming protein sequences
                    
                    cursor.execute('''
                        INSERT INTO sequences (gene_id, version, sequence, sequence_type, length)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (gene_id, version, sequence, seq_type, len(sequence)))
                    
                    self.sequences[f"{version}:{gene_id}"] = {
                        'sequence': sequence,
                        'type': seq_type,
                        'length': len(sequence)
                    }
                    
                    count += 1
                    if count % 1000 == 0:
                        print(f"  Processed {count} sequences from {version}")
                        
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue
                
            print(f"  Loaded {count} sequences from {version}")
            
        self.conn.commit()
        
    def load_annotations(self):
        """Load gene annotations"""
        print("Loading annotations...")
        
        annotations_file = os.path.join(self.data_dir, 'Cr_Annotations_Eggo.xlsx')
        if not os.path.exists(annotations_file):
            print(f"Annotations file not found: {annotations_file}")
            return
            
        try:
            df = pd.read_excel(annotations_file)
            cursor = self.conn.cursor()
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO annotations 
                    (protein_id, gene_id, description, preferred_name, go_term, kegg_ko, kegg_pathway)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Protein_ID', ''),
                    row.get('Gene_ID', ''),
                    row.get('Description', ''),
                    row.get('Preferred_name', ''),
                    row.get('GO_term', ''),
                    row.get('KEGG_ko', ''),
                    row.get('KEGG_Pathway', '')
                ))
                
                self.annotations[row.get('Gene_ID', '')] = {
                    'protein_id': row.get('Protein_ID', ''),
                    'description': row.get('Description', ''),
                    'preferred_name': row.get('Preferred_name', ''),
                    'go_term': row.get('GO_term', ''),
                    'kegg_ko': row.get('KEGG_ko', ''),
                    'kegg_pathway': row.get('KEGG_Pathway', '')
                }
                
            self.conn.commit()
            print(f"Loaded {len(df)} annotation records")
            
        except Exception as e:
            print(f"Error loading annotations: {e}")
            
    def load_go_terms(self):
        """Load GO terms for enrichment analysis"""
        print("Loading GO terms...")
        
        go_file = os.path.join(self.data_dir, 'Croseus_GO_NP.xlsx') 
        if not os.path.exists(go_file):
            print(f"GO file not found: {go_file}")
            return
            
        try:
            df = pd.read_excel(go_file, sheet_name='Croseus_GO_merged_final')
            cursor = self.conn.cursor()
            
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO go_terms (gene_id, go_term, description, ontology)
                    VALUES (?, ?, ?, ?)
                ''', (
                    row.get('Gene_ID', ''),
                    row.get('GO_term', ''),
                    row.get('Description', ''),
                    row.get('Ontology', '')
                ))
                
                gene_id = row.get('Gene_ID', '')
                if gene_id not in self.go_terms:
                    self.go_terms[gene_id] = []
                self.go_terms[gene_id].append({
                    'go_term': row.get('GO_term', ''),
                    'description': row.get('Description', ''),
                    'ontology': row.get('Ontology', '')
                })
                
            self.conn.commit()
            print(f"Loaded {len(df)} GO term records")
            
        except Exception as e:
            print(f"Error loading GO terms: {e}")
            
    def build_gene_mappings(self):
        """Build cross-version gene mappings based on sequence similarity"""
        print("Building gene mappings...")
        cursor = self.conn.cursor()
        
        # For now, use a simple approach - genes are considered equivalent if they have high sequence similarity
        # In a production system, you might want to use more sophisticated alignment methods
        
        # Get canonical genes (from Cr_NP)
        cursor.execute('SELECT gene_id, sequence FROM sequences WHERE version = "Cr_NP"')
        canonical_genes = cursor.fetchall()
        
        for canonical_id, canonical_seq in canonical_genes:
            # Insert canonical mapping to itself
            cursor.execute('''
                INSERT INTO gene_mappings (canonical_id, version, version_id)
                VALUES (?, ?, ?)
            ''', (canonical_id, 'Cr_NP', canonical_id))
            
            # Find similar sequences in other versions
            for version in ['Cr_NCB', 'Cr_2023', 'Cr_2022', 'Cr_2016', 'Cr_2015']:
                cursor.execute('SELECT gene_id, sequence FROM sequences WHERE version = ?', (version,))
                version_genes = cursor.fetchall()
                
                best_match = None
                best_similarity = 0
                
                for version_id, version_seq in version_genes:
                    # Simple sequence similarity check (exact match or high similarity)
                    if canonical_seq == version_seq:
                        similarity = 1.0
                    else:
                        # Calculate a simple similarity score
                        similarity = self.calculate_similarity(canonical_seq, version_seq)
                    
                    if similarity > best_similarity and similarity > 0.95:  # High similarity threshold
                        best_similarity = similarity
                        best_match = version_id
                        
                if best_match:
                    cursor.execute('''
                        INSERT INTO gene_mappings (canonical_id, version, version_id)
                        VALUES (?, ?, ?)
                    ''', (canonical_id, version, best_match))
                    
        self.conn.commit()
        print("Gene mapping complete")
        
    def calculate_similarity(self, seq1, seq2):
        """Calculate simple sequence similarity"""
        if len(seq1) == 0 or len(seq2) == 0:
            return 0
        
        # Simple similarity based on common characters
        min_len = min(len(seq1), len(seq2))
        max_len = max(len(seq1), len(seq2))
        
        matches = sum(1 for i in range(min_len) if seq1[i] == seq2[i])
        return matches / max_len
        
    def search_by_gene_id(self, gene_id):
        """Search for gene by ID across all versions"""
        cursor = self.conn.cursor()
        
        # Direct search first
        cursor.execute('''
            SELECT s.gene_id, s.version, s.sequence, s.length,
                   a.description, a.preferred_name
            FROM sequences s
            LEFT JOIN annotations a ON s.gene_id = a.gene_id  
            WHERE s.gene_id = ?
        ''', (gene_id,))
        
        direct_results = cursor.fetchall()
        
        # Search through mappings
        cursor.execute('''
            SELECT gm.canonical_id, gm.version, gm.version_id,
                   s.sequence, s.length,
                   a.description, a.preferred_name
            FROM gene_mappings gm
            JOIN sequences s ON gm.version_id = s.gene_id AND gm.version = s.version
            LEFT JOIN annotations a ON s.gene_id = a.gene_id
            WHERE gm.canonical_id = ? OR gm.version_id = ?
        ''', (gene_id, gene_id))
        
        mapping_results = cursor.fetchall()
        
        # Combine and format results
        results = {
            'gene_id': gene_id,
            'versions': {},
            'annotations': {},
            'go_terms': []
        }
        
        # Process direct results
        for row in direct_results:
            version = row[1]
            results['versions'][version] = {
                'gene_id': row[0],
                'sequence': row[2],
                'length': row[3],
                'description': row[4] or '',
                'preferred_name': row[5] or ''
            }
            
        # Process mapping results
        for row in mapping_results:
            version = row[1] 
            results['versions'][version] = {
                'gene_id': row[2],
                'sequence': row[3],
                'length': row[4],
                'description': row[5] or '',
                'preferred_name': row[6] or ''
            }
            
        # Get GO terms
        cursor.execute('SELECT go_term, description, ontology FROM go_terms WHERE gene_id = ?', (gene_id,))
        results['go_terms'] = [{'term': row[0], 'description': row[1], 'ontology': row[2]} for row in cursor.fetchall()]
        
        return results
        
    def search_by_sequence(self, query_sequence, min_similarity=0.8):
        """Search for genes by sequence similarity"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT gene_id, version, sequence FROM sequences')
        
        results = []
        query_sequence = query_sequence.upper().strip()
        
        for gene_id, version, sequence in cursor.fetchall():
            similarity = self.calculate_similarity(query_sequence, sequence)
            if similarity >= min_similarity:
                results.append({
                    'gene_id': gene_id,
                    'version': version,
                    'similarity': similarity,
                    'sequence': sequence,
                    'length': len(sequence)
                })
                
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:50]  # Return top 50 matches
        
    def go_enrichment_analysis(self, gene_list, background_size=None):
        """Perform GO enrichment analysis"""
        cursor = self.conn.cursor()
        
        if background_size is None:
            cursor.execute('SELECT COUNT(DISTINCT gene_id) FROM go_terms')
            background_size = cursor.fetchone()[0]
            
        # Get GO terms for input genes
        placeholders = ','.join(['?' for _ in gene_list])
        cursor.execute(f'''
            SELECT go_term, description, ontology, COUNT(*) as count
            FROM go_terms 
            WHERE gene_id IN ({placeholders})
            GROUP BY go_term, description, ontology
        ''', gene_list)
        
        enriched_terms = []
        
        for go_term, description, ontology, observed_count in cursor.fetchall():
            # Get total genes with this GO term
            cursor.execute('SELECT COUNT(DISTINCT gene_id) FROM go_terms WHERE go_term = ?', (go_term,))
            total_with_term = cursor.fetchone()[0]
            
            # Hypergeometric test
            p_value = hypergeom.sf(observed_count - 1, background_size, total_with_term, len(gene_list))
            
            enriched_terms.append({
                'go_term': go_term,
                'description': description,
                'ontology': ontology,
                'observed': observed_count,
                'total_with_term': total_with_term,
                'input_size': len(gene_list),
                'background_size': background_size,
                'p_value': p_value,
                'enrichment_ratio': (observed_count / len(gene_list)) / (total_with_term / background_size)
            })
            
        # Sort by p-value
        enriched_terms.sort(key=lambda x: x['p_value'])
        return enriched_terms


# Initialize database
db = CroseusDatabase()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', version_names=db.version_names)

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests"""
    data = request.json
    search_type = data.get('search_type')
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Please enter a search query'})
        
    try:
        if search_type == 'gene_id':
            results = db.search_by_gene_id(query)
        elif search_type == 'sequence':
            min_similarity = float(data.get('min_similarity', 0.8))
            results = db.search_by_sequence(query, min_similarity)
        else:
            return jsonify({'error': 'Invalid search type'})
            
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        return jsonify({'error': f'Search error: {str(e)}'})

@app.route('/go_enrichment', methods=['POST'])
def go_enrichment():
    """Handle GO enrichment analysis"""
    data = request.json
    gene_list = data.get('gene_list', [])
    
    if not gene_list:
        return jsonify({'error': 'Please provide a list of genes'})
        
    try:
        results = db.go_enrichment_analysis(gene_list)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'error': f'GO enrichment error: {str(e)}'})

@app.route('/api/gene_info/<gene_id>')
def get_gene_info(gene_id):
    """Get detailed gene information"""
    try:
        results = db.search_by_gene_id(gene_id)
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("Starting Croseus Gene Search Tool...")
    try:
        db.init_database()
        print("Database initialized successfully!")
        print("Starting Flask web server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
