#!/usr/bin/env python3
"""
Standalone GO Enrichment Analysis Tool
Run GO enrichment from command line without web server

Usage:
    python go_analysis_cli.py genes.txt
    python go_analysis_cli.py --genes M9H77_13438,M9H77_32446,M9H77_01367

"""

import argparse
import sys
from go_enrichment import GOEnrichment

def load_genes_from_file(filename):
    """Load gene list from text file (one gene per line)"""
    with open(filename, 'r') as f:
        genes = [line.strip() for line in f if line.strip()]
    return genes

def main():
    parser = argparse.ArgumentParser(
        description='Run GO enrichment analysis on a list of genes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # From file (one gene ID per line)
  python go_analysis_cli.py genes.txt

  # From command line (comma-separated)
  python go_analysis_cli.py --genes M9H77_13438,M9H77_32446,M9H77_01367

  # With custom parameters
  python go_analysis_cli.py genes.txt --pvalue 0.01 --qvalue 0.1

  # Filter by ontology
  python go_analysis_cli.py genes.txt --ontology biological_process
        '''
    )
    
    # Input arguments
    parser.add_argument('input_file', nargs='?', 
                       help='Text file with gene IDs (one per line)')
    parser.add_argument('--genes', type=str,
                       help='Comma-separated list of gene IDs')
    
    # Analysis parameters
    parser.add_argument('--pvalue', type=float, default=0.05,
                       help='P-value cutoff (default: 0.05)')
    parser.add_argument('--qvalue', type=float, default=0.2,
                       help='Adjusted p-value cutoff (default: 0.2)')
    parser.add_argument('--mingenes', type=int, default=2,
                       help='Minimum genes in GO category (default: 2)')
    parser.add_argument('--ontology', type=str, choices=['biological_process', 'molecular_function', 'cellular_component'],
                       help='Filter by GO ontology')
    
    # Output options
    parser.add_argument('--output', '-o', type=str, default='GO_enrichment_results.xlsx',
                       help='Output Excel file (default: GO_enrichment_results.xlsx)')
    parser.add_argument('--plot', '-p', type=str,
                       help='Save plot to file (e.g., plot.png)')
    parser.add_argument('--top', type=int, default=15,
                       help='Number of top terms to show/plot (default: 15)')
    
    # GO annotation file
    parser.add_argument('--gofile', type=str, default='Croseus_GO_NP.xlsx',
                       help='GO annotation file (default: Croseus_GO_NP.xlsx)')
    
    args = parser.parse_args()
    
    # Get gene list
    if args.input_file:
        try:
            gene_list = load_genes_from_file(args.input_file)
            print(f"📂 Loaded {len(gene_list)} genes from {args.input_file}")
        except FileNotFoundError:
            print(f"❌ Error: File '{args.input_file}' not found")
            return 1
    elif args.genes:
        gene_list = [g.strip() for g in args.genes.split(',')]
        print(f"📝 Using {len(gene_list)} genes from command line")
    else:
        parser.print_help()
        return 1
    
    if not gene_list:
        print("❌ Error: No genes provided")
        return 1
    
    print(f"\nGenes to analyze: {', '.join(gene_list[:5])}")
    if len(gene_list) > 5:
        print(f"... and {len(gene_list) - 5} more")
    
    # Initialize GO enrichment
    print(f"\n{'='*80}")
    try:
        go_enricher = GOEnrichment(args.gofile)
    except FileNotFoundError:
        print(f"❌ Error: GO annotation file '{args.gofile}' not found")
        return 1
    
    # Run enrichment analysis
    print(f"\n{'='*80}")
    print("Running GO enrichment analysis...")
    print(f"Parameters: pvalue={args.pvalue}, qvalue={args.qvalue}, min_genes={args.mingenes}")
    if args.ontology:
        print(f"Filtering by ontology: {args.ontology}")
    print(f"{'='*80}\n")
    
    results = go_enricher.enrichment_analysis(
        gene_list=gene_list,
        pvalue_cutoff=args.pvalue,
        qvalue_cutoff=args.qvalue,
        min_genes=args.mingenes,
        ontology=args.ontology
    )
    
    if results.empty:
        print("\n❌ No significant enrichment found")
        print("\nTips:")
        print("  - Try relaxing thresholds (--pvalue 0.1 --qvalue 0.3)")
        print("  - Check if genes exist in background")
        print("  - Ensure genes have common biological functions")
        return 0
    
    # Display results
    print(f"\n{'='*80}")
    print(f"✅ Found {len(results)} significantly enriched GO terms")
    print(f"{'='*80}\n")
    
    print(f"Top {min(args.top, len(results))} enriched terms:\n")
    
    display_cols = ['GO_term', 'Description', 'Ontology', 'Count', 'GeneRatio', 'pvalue', 'p.adjust']
    for i, (_, row) in enumerate(results.head(args.top).iterrows(), 1):
        print(f"{i}. {row['GO_term']} - {row['Description']}")
        print(f"   Ontology: {row['Ontology']}")
        print(f"   Genes: {row['Count']} ({row['GeneRatio']})")
        print(f"   P-value: {row['pvalue']:.2e}, Adj. P-value: {row['p.adjust']:.2e}")
        print()
    
    # Save results
    print(f"{'='*80}")
    go_enricher.save_results(results, args.output)
    
    # Create plot if requested
    if args.plot:
        go_enricher.plot_results(results, top_n=args.top, filename=args.plot)
    
    print(f"{'='*80}")
    print("✨ Analysis complete!")
    print(f"{'='*80}\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
