# 🧬 C. roseus Gene Database with GO Enrichment

Complete gene database system with integrated Gene Ontology enrichment analysis

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install --break-system-packages -r requirements.txt
```

### 2. Generate Database
```bash
python make_data_with_go.py
```

### 3. Start Web Server
```bash
python server.py
```

### 4. Open Browser
Navigate to: http://localhost:5000

## 📦 What's Included

### Core Scripts
- **`make_data_with_go.py`** - Generates database with GO annotations
- **`server.py`** - Flask web server with GO enrichment API
- **`index_complete.html`** - Web interface with gene selection

### Additional Tools
- **`go_enrichment.py`** - Standalone GO enrichment module
- **`go_analysis_cli.py`** - Command-line GO enrichment tool

### Documentation
- **`GO_ENRICHMENT_GUIDE.md`** - Complete setup and usage guide
- **`requirements.txt`** - Python dependencies
- **`sample_genes.txt`** - Example gene list

## 📋 Required Input Files

Place these files in the same directory:
- `Cr_Annotations_Eggo.xlsx` - Gene annotations
- `Croseus_GO_NP.xlsx` - GO term annotations  
- `Cr_NP.fasta` - Protein sequences
- `Cr_NP_cds.fasta` - CDS sequences
- `id_mapping.csv` - ID mappings (optional)

## 💡 Features

### Web Interface
✅ Search genes by name, ID, or keyword
✅ View protein and CDS sequences
✅ Select multiple genes with checkboxes
✅ Run GO enrichment analysis
✅ Interactive bar chart results

### Command Line Tool
```bash
# Run GO enrichment on gene list
python go_analysis_cli.py sample_genes.txt

# With custom parameters
python go_analysis_cli.py sample_genes.txt --pvalue 0.01 --plot results.png

# From command line
python go_analysis_cli.py --genes M9H77_13438,M9H77_32446
```

## 📊 Example Usage

### Web Interface
1. Search for "WRKY" genes
2. Select all results (checkbox in header)
3. Click "Run GO Enrichment"
4. View enriched biological processes

### Command Line
```bash
python go_analysis_cli.py sample_genes.txt \
    --pvalue 0.05 \
    --qvalue 0.2 \
    --output my_results.xlsx \
    --plot my_plot.png
```

## 🔬 GO Enrichment

Uses Fisher's exact test with Benjamini-Hochberg correction, similar to R's clusterProfiler package.

**Statistical thresholds:**
- P-value: < 0.05
- Adjusted p-value: < 0.2
- Minimum genes: 2

## 📚 Documentation

See `GO_ENRICHMENT_GUIDE.md` for:
- Detailed setup instructions
- Usage examples
- Troubleshooting
- API documentation
- Best practices

## 🛠️ System Requirements

- Python 3.7+
- 4GB RAM (8GB recommended)
- Modern web browser
- 500MB disk space

## ⚡ Performance

- Database: 17,000+ genes
- GO terms: 8,500+ terms
- Enrichment: < 1 second for 50 genes
- Web interface: Real-time search

## 📁 File Structure

```
.
├── make_data_with_go.py      # Data generation
├── server.py                  # Web server
├── index_complete.html        # Web interface
├── go_enrichment.py           # GO module
├── go_analysis_cli.py         # CLI tool
├── requirements.txt           # Dependencies
├── sample_genes.txt           # Example input
├── GO_ENRICHMENT_GUIDE.md     # Full guide
└── README.md                  # This file
```

## 🐛 Troubleshooting

**"GO annotations not loaded"**
- Check that `Croseus_GO_NP.xlsx` exists
- Restart the server

**"No significant enrichment"**
- Need ≥2 genes
- Try relaxing p-value cutoffs
- Select genes with related functions

**Server won't start**
- Install missing packages: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.7+)

## 🎯 Tips for Best Results

1. Select 10-100 related genes
2. Use genes from same pathway/family
3. Check p.adjust < 0.05 for significance
4. Compare across ontologies (BP/MF/CC)

## 📞 Support

See troubleshooting section in `GO_ENRICHMENT_GUIDE.md`

---

**Happy Analyzing! 🧬🔬✨**
