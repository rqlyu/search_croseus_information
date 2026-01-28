"""
GO Enrichment Analysis Module
Performs Gene Ontology enrichment analysis similar to R's clusterProfiler
"""

import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests
import json
from collections import defaultdict

class GOEnrichment:
    def __init__(self, go_file_path):
        """
        Initialize GO enrichment analyzer
        
        Args:
            go_file_path: Path to GO annotation file (Excel)
        """
        print("Loading GO annotations...")
        self.go_data = pd.read_excel(go_file_path)
        
        # Create TERM2GENE mapping (GO_term -> list of genes)
        self.term2gene = defaultdict(list)
        for _, row in self.go_data.iterrows():
            self.term2gene[row['GO_term']].append(row['Gene_ID'])
        
        # Create TERM2NAME mapping (GO_term -> Description)
        self.term2name = dict(zip(self.go_data['GO_term'], self.go_data['Description']))
        
        # Create TERM2ONTOLOGY mapping
        self.term2ontology = dict(zip(self.go_data['GO_term'], self.go_data['Ontology']))
        
        # Get background genes
        self.background_genes = set(self.go_data['Gene_ID'].unique())
        
        print(f"✓ Loaded {len(self.term2gene)} GO terms")
        print(f"✓ Background: {len(self.background_genes)} genes")
    
    def enrichment_analysis(self, gene_list, pvalue_cutoff=0.05, qvalue_cutoff=0.2, 
                          min_genes=2, ontology=None):
        """
        Perform GO enrichment analysis using Fisher's exact test
        
        Args:
            gene_list: List of gene IDs to test
            pvalue_cutoff: P-value threshold
            qvalue_cutoff: Adjusted p-value threshold
            min_genes: Minimum genes in category
            ontology: Filter by ontology ('biological_process', 'molecular_function', 
                     'cellular_component'), or None for all
        
        Returns:
            DataFrame with enrichment results
        """
        # Validate genes
        gene_set = set(gene_list)
        valid_genes = gene_set & self.background_genes
        
        if len(valid_genes) < min_genes:
            print(f"Warning: Only {len(valid_genes)} valid genes in background")
            return pd.DataFrame()
        
        print(f"Testing {len(valid_genes)} genes against background of {len(self.background_genes)}")
        
        # Perform enrichment for each GO term
        results = []
        
        for go_term, term_genes in self.term2gene.items():
            # Filter by ontology if specified
            if ontology and self.term2ontology.get(go_term) != ontology:
                continue
            
            term_gene_set = set(term_genes)
            
            # Skip small categories
            if len(term_gene_set) < min_genes:
                continue
            
            # Create 2x2 contingency table for Fisher's exact test
            # |           | In GO term | Not in GO term |
            # |-----------|------------|----------------|
            # | In list   |     a      |       b        |
            # | Not list  |     c      |       d        |
            
            a = len(valid_genes & term_gene_set)  # genes in both list and term
            b = len(valid_genes - term_gene_set)  # genes in list but not term
            c = len(term_gene_set - valid_genes)  # genes in term but not list
            d = len(self.background_genes - term_gene_set - valid_genes)  # neither
            
            # Skip if no overlap
            if a == 0:
                continue
            
            # Fisher's exact test (right-tailed for enrichment)
            oddsratio, pvalue = fisher_exact([[a, b], [c, d]], alternative='greater')
            
            # Calculate gene ratio and background ratio
            gene_ratio = f"{a}/{len(valid_genes)}"
            bg_ratio = f"{len(term_gene_set)}/{len(self.background_genes)}"
            
            # Get gene names
            overlap_genes = list(valid_genes & term_gene_set)
            
            results.append({
                'GO_term': go_term,
                'Description': self.term2name.get(go_term, 'Unknown'),
                'Ontology': self.term2ontology.get(go_term, 'Unknown'),
                'GeneRatio': gene_ratio,
                'BgRatio': bg_ratio,
                'pvalue': pvalue,
                'Count': a,
                'GeneID': '/'.join(overlap_genes[:50]),  # Limit to first 50
                'Total_genes': len(overlap_genes)
            })
        
        if not results:
            print("No enriched terms found")
            return pd.DataFrame()
        
        # Create DataFrame and adjust p-values
        df = pd.DataFrame(results)
        
        # Multiple testing correction (Benjamini-Hochberg)
        df['p.adjust'] = multipletests(df['pvalue'], method='fdr_bh')[1]
        
        # Filter by cutoffs
        df = df[(df['pvalue'] < pvalue_cutoff) & (df['p.adjust'] < qvalue_cutoff)]
        
        # Sort by adjusted p-value
        df = df.sort_values('p.adjust')
        
        print(f"✓ Found {len(df)} significantly enriched terms")
        
        return df
    
    def plot_results(self, enrichment_df, top_n=10, filename=None):
        """
        Create a bar plot of top enriched GO terms
        
        Args:
            enrichment_df: Results from enrichment_analysis
            top_n: Number of top terms to plot
            filename: Output filename (PNG)
        """
        try:
            import matplotlib.pyplot as plt
            
            if enrichment_df.empty:
                print("No results to plot")
                return
            
            # Get top N terms
            plot_df = enrichment_df.head(top_n).copy()
            
            # Calculate -log10(p.adjust)
            plot_df['neg_log_p'] = -np.log10(plot_df['p.adjust'])
            
            # Truncate long descriptions
            plot_df['Label'] = plot_df['Description'].apply(
                lambda x: x[:52] + '...' if len(x) > 55 else x
            )
            
            # Reverse order for plotting (top term at top)
            plot_df = plot_df.iloc[::-1]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create bar plot
            bars = ax.barh(range(len(plot_df)), plot_df['neg_log_p'], 
                          color='white', edgecolor='black', linewidth=1.5)
            
            # Add labels inside bars
            for i, (idx, row) in enumerate(plot_df.iterrows()):
                ax.text(0.1, i, row['Label'], 
                       va='center', ha='left', fontsize=10)
            
            # Customize plot
            ax.set_yticks([])
            ax.set_xlabel('-log10(adj. p-value)', fontsize=12, fontweight='bold')
            ax.set_title('GO Enrichment Analysis', fontsize=14, fontweight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
            
            if filename:
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                print(f"✓ Plot saved to {filename}")
            else:
                plt.show()
            
            plt.close()
            
        except ImportError:
            print("matplotlib not available for plotting")
    
    def save_results(self, enrichment_df, filename):
        """
        Save enrichment results to Excel file
        
        Args:
            enrichment_df: Results from enrichment_analysis
            filename: Output filename (Excel)
        """
        if enrichment_df.empty:
            print("No results to save")
            return
        
        enrichment_df.to_excel(filename, index=False)
        print(f"✓ Results saved to {filename}")


def main():
    """
    Example usage of GO enrichment analysis
    """
    # Initialize
    go_enricher = GOEnrichment('Croseus_GO_NP.xlsx')
    
    # Example gene list (replace with your genes)
    test_genes = [
        'M9H77_13438',  # CrWRKY7
        'M9H77_32446',
        'M9H77_01367',
        'M9H77_05742',
        'M9H77_33525'
    ]
    
    print(f"\nTesting enrichment for {len(test_genes)} genes...")
    
    # Run enrichment analysis
    results = go_enricher.enrichment_analysis(
        gene_list=test_genes,
        pvalue_cutoff=0.05,
        qvalue_cutoff=0.2
    )
    
    if not results.empty:
        print("\nTop 10 enriched terms:")
        print(results[['GO_term', 'Description', 'Count', 'pvalue', 'p.adjust']].head(10))
        
        # Save results
        go_enricher.save_results(results, 'GO_enrichment_results.xlsx')
        
        # Create plot
        go_enricher.plot_results(results, top_n=10, filename='GO_enrichment_plot.png')
    else:
        print("No significant enrichment found")


if __name__ == '__main__':
    main()
