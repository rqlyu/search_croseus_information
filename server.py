"""
Flask Web Server for C. roseus Gene Database with GO Enrichment
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests
from collections import defaultdict
import json
import os

app = Flask(__name__)
CORS(app)

# Global variables for GO data
GO_DATA = None
TERM2GENE = None
TERM2NAME = None
TERM2ONTOLOGY = None
BACKGROUND_GENES = None

def load_go_annotations():
    """Load GO annotations at startup"""
    global GO_DATA, TERM2GENE, TERM2NAME, TERM2ONTOLOGY, BACKGROUND_GENES
    
    go_file = 'Croseus_GO_NP.xlsx'
    if not os.path.exists(go_file):
        print(f"Warning: {go_file} not found. GO enrichment will not be available.")
        return False
    
    print("Loading GO annotations...")
    GO_DATA = pd.read_excel(go_file)
    
    # Create mappings
    TERM2GENE = defaultdict(list)
    for _, row in GO_DATA.iterrows():
        TERM2GENE[row['GO_term']].append(row['Gene_ID'])
    
    TERM2NAME = dict(zip(GO_DATA['GO_term'], GO_DATA['Description']))
    TERM2ONTOLOGY = dict(zip(GO_DATA['GO_term'], GO_DATA['Ontology']))
    BACKGROUND_GENES = set(GO_DATA['Gene_ID'].unique())
    
    print(f"✓ Loaded {len(TERM2GENE)} GO terms for {len(BACKGROUND_GENES)} genes")
    return True

def perform_go_enrichment(gene_list, pvalue_cutoff=0.05, qvalue_cutoff=0.2, min_genes=2):
    """
    Perform GO enrichment analysis using Fisher's exact test
    """
    if TERM2GENE is None:
        return {'error': 'GO annotations not loaded'}
    
    # Validate genes
    gene_set = set(gene_list)
    valid_genes = gene_set & BACKGROUND_GENES
    
    if len(valid_genes) < min_genes:
        return {
            'error': f'Only {len(valid_genes)} valid genes found in background. Need at least {min_genes}.',
            'valid_genes': len(valid_genes),
            'total_genes': len(gene_list)
        }
    
    # Perform enrichment for each GO term
    results = []
    
    for go_term, term_genes in TERM2GENE.items():
        term_gene_set = set(term_genes)
        
        # Skip small categories
        if len(term_gene_set) < min_genes:
            continue
        
        # Create 2x2 contingency table
        a = len(valid_genes & term_gene_set)
        b = len(valid_genes - term_gene_set)
        c = len(term_gene_set - valid_genes)
        d = len(BACKGROUND_GENES - term_gene_set - valid_genes)
        
        if a == 0:
            continue
        
        # Fisher's exact test
        oddsratio, pvalue = fisher_exact([[a, b], [c, d]], alternative='greater')
        
        overlap_genes = list(valid_genes & term_gene_set)
        
        results.append({
            'GO_term': go_term,
            'Description': TERM2NAME.get(go_term, 'Unknown'),
            'Ontology': TERM2ONTOLOGY.get(go_term, 'Unknown'),
            'Count': a,
            'GeneRatio': f"{a}/{len(valid_genes)}",
            'BgRatio': f"{len(term_gene_set)}/{len(BACKGROUND_GENES)}",
            'pvalue': pvalue,
            'GeneID': overlap_genes[:20],  # First 20 genes
            'Total_genes': len(overlap_genes)
        })
    
    if not results:
        return {
            'error': 'No enriched terms found',
            'tested_genes': len(valid_genes)
        }
    
    # Create DataFrame and adjust p-values
    df = pd.DataFrame(results)
    df['p.adjust'] = multipletests(df['pvalue'], method='fdr_bh')[1]
    
    # Filter by cutoffs
    df = df[(df['pvalue'] < pvalue_cutoff) & (df['p.adjust'] < qvalue_cutoff)]
    
    if df.empty:
        return {
            'error': 'No significant enrichment found after correction',
            'tested_genes': len(valid_genes),
            'terms_tested': len(results)
        }
    
    # Sort by adjusted p-value
    df = df.sort_values('p.adjust')
    
    # Convert to dict for JSON
    return {
        'success': True,
        'tested_genes': len(valid_genes),
        'total_input': len(gene_list),
        'enriched_terms': len(df),
        'results': df.to_dict('records')
    }

# Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/data.json')
def serve_data():
    """Serve the gene database JSON"""
    return send_from_directory('.', 'data.json')

@app.route('/api/go_enrichment', methods=['POST'])
def go_enrichment():
    """
    API endpoint for GO enrichment analysis
    
    Expected JSON body:
    {
        "genes": ["M9H77_13438", "M9H77_32446", ...],
        "pvalue_cutoff": 0.05,
        "qvalue_cutoff": 0.2
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'genes' not in data:
            return jsonify({'error': 'No gene list provided'}), 400
        
        gene_list = data['genes']
        pvalue_cutoff = data.get('pvalue_cutoff', 0.05)
        qvalue_cutoff = data.get('qvalue_cutoff', 0.2)
        
        if len(gene_list) == 0:
            return jsonify({'error': 'Empty gene list'}), 400
        
        # Perform enrichment
        results = perform_go_enrichment(
            gene_list=gene_list,
            pvalue_cutoff=pvalue_cutoff,
            qvalue_cutoff=qvalue_cutoff
        )
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'go_loaded': TERM2GENE is not None,
        'background_genes': len(BACKGROUND_GENES) if BACKGROUND_GENES else 0
    })

if __name__ == '__main__':
    print("="*80)
    print("C. roseus Gene Database Server")
    print("="*80)
    
    # Load GO annotations
    go_loaded = load_go_annotations()
    
    if go_loaded:
        print("\n✅ Server ready with GO enrichment!")
    else:
        print("\n⚠️  Server running without GO enrichment")
    
    print("\n🌐 Starting server at http://localhost:5000")
    print("="*80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
