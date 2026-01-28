# 🧬 C. roseus Gene Database with GO Enrichment Analysis

## Complete Setup and Usage Guide

---

## 📋 Overview

This system provides a web-based interface for:
1. **Gene Search** - Search by gene name, ID, or keyword
2. **Sequence Viewing** - View protein and CDS sequences
3. **Gene Selection** - Select multiple genes for analysis
4. **GO Enrichment** - Find overrepresented Gene Ontology terms

---

## 🛠️ Prerequisites

### Required Python Packages
```bash
pip install --break-system-packages pandas openpyxl scipy statsmodels flask flask-cors matplotlib numpy
```

### Required Files
- `Cr_Annotations_Eggo.xlsx` - Gene annotations
- `Croseus_GO_NP.xlsx` - GO term annotations
- `Cr_NP.fasta` - Protein sequences
- `Cr_NP_cds.fasta` - CDS sequences
- `id_mapping.csv` - ID mappings (optional)

---

## 🚀 Setup Instructions

### Step 1: Generate the Database

Run the data generation script:
```bash
python make_data_with_go.py
```

This will:
- Load all annotation files
- Parse FASTA sequences
- Integrate GO terms
- Create `data.json` (the main database)

Expected output:
```
================================================================================
✅ SUCCESS! Database ready with 17,000 records
================================================================================

📈 Statistics:
   - Total genes: 17,000
   - With protein sequences: 16,500 (97.1%)
   - With CDS sequences: 16,800 (98.8%)
   - With GO annotations: 15,200 (89.4%)

✨ Ready for GO enrichment analysis!
```

### Step 2: Start the Web Server

```bash
python server.py
```

The server will:
- Load GO annotations into memory
- Start on `http://localhost:5000`

Expected output:
```
================================================================================
C. roseus Gene Database Server
================================================================================
Loading GO annotations...
✓ Loaded 8,532 GO terms for 20,614 genes

✅ Server ready with GO enrichment!

🌐 Starting server at http://localhost:5000
================================================================================
```

### Step 3: Access the Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

---

## 💡 How to Use

### 1. Search for Genes

**Example searches:**
- By gene name: `CrWRKY7`
- By gene ID: `M9H77_13438`
- By keyword: `WRKY transcription factor`
- By function: `protein binding`

![Search Example](search_example.png)

### 2. View Gene Details

Click the **"View"** button to see:
- Full gene information
- GO term annotations
- Protein sequence (with length)
- CDS sequence (with length)

**Features:**
- Tab between Protein and CDS sequences
- Copy sequences to clipboard
- View associated GO terms

### 3. Select Genes for GO Enrichment

**Method 1: Individual Selection**
- Check the boxes next to genes of interest
- A purple bar appears showing selected count

**Method 2: Bulk Selection**
- Use the checkbox in the header to select all visible results
- Useful for analyzing a specific gene family

**Tips:**
- Select genes with related functions
- Minimum 2 genes required for analysis
- Recommended: 10-100 genes for best results

### 4. Run GO Enrichment Analysis

Once genes are selected:

1. Click **"Run GO Enrichment"** in the purple bar
2. The system will:
   - Validate genes against background
   - Perform Fisher's exact test for each GO term
   - Apply Benjamini-Hochberg correction
   - Display significantly enriched terms

**Results Display:**
- Horizontal bar chart showing enrichment strength
- Terms sorted by adjusted p-value
- Shows gene count and ratio
- Color-coded by ontology (BP/MF/CC)

---

## 📊 Understanding GO Enrichment Results

### Result Components

```
GO:0006355 - regulation of transcription, DNA-templated  [biological_process]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8 genes (8/25)                                    p.adj: 1.2e-05
```

**Interpretation:**
- **GO:0006355** - GO term identifier
- **Description** - What this term means
- **Ontology** - biological_process, molecular_function, or cellular_component
- **8 genes** - Number of selected genes in this term
- **(8/25)** - 8 out of 25 selected genes have this annotation
- **p.adj** - Adjusted p-value (lower = more significant)

### Statistical Thresholds

- **p-value cutoff:** 0.05
- **Adjusted p-value cutoff:** 0.2
- **Minimum genes:** 2

---

## 🔬 Example Use Cases

### Use Case 1: Analyzing WRKY Transcription Factors

**Goal:** Find common functions among WRKY genes

```
1. Search: "WRKY"
2. Select all WRKY genes (check "Select All")
3. Click "Run GO Enrichment"
4. Expected results:
   - DNA binding
   - Transcription regulation
   - Response to stress
```

### Use Case 2: Finding Co-regulated Genes

**Goal:** Discover genes with similar GO annotations

```
1. Search: "stress response"
2. Select genes of interest
3. Run GO enrichment
4. Review enriched pathways
```

### Use Case 3: Validating Gene Families

**Goal:** Confirm functional coherence

```
1. Search for your gene family
2. Select all members
3. Run GO enrichment
4. Check if enriched terms match expected functions
```

---

## 📁 File Structure

```
project/
│
├── make_data_with_go.py       # Data generation script
├── go_enrichment.py            # GO enrichment module (standalone)
├── server.py                   # Web server with API
├── index_complete.html         # Web interface
│
├── Cr_Annotations_Eggo.xlsx    # Input: annotations
├── Croseus_GO_NP.xlsx          # Input: GO terms
├── Cr_NP.fasta                 # Input: protein sequences
├── Cr_NP_cds.fasta             # Input: CDS sequences
├── id_mapping.csv              # Input: ID mappings (optional)
│
└── data.json                   # Output: complete database
```

---

## 🔧 Advanced Configuration

### Adjusting Enrichment Parameters

Edit in `server.py` or pass to API:

```python
# In server.py, modify defaults:
pvalue_cutoff = 0.05      # Raw p-value threshold
qvalue_cutoff = 0.2       # Adjusted p-value threshold
min_genes = 2             # Minimum genes per term
```

### Custom API Requests

```javascript
fetch('/api/go_enrichment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        genes: ['M9H77_13438', 'M9H77_32446', ...],
        pvalue_cutoff: 0.01,    // Stricter threshold
        qvalue_cutoff: 0.1      // Stricter correction
    })
});
```

---

## 📈 Performance Notes

- **Database loading:** ~2-3 seconds for 17,000 genes
- **GO enrichment:** < 1 second for 50 genes
- **Maximum genes selected:** Recommended < 500 for performance
- **Results display:** Top 15 terms shown by default

---

## 🐛 Troubleshooting

### Issue: "GO annotations not loaded"

**Solution:**
```bash
# Check if GO file exists
ls -lh Croseus_GO_NP.xlsx

# Restart server
python server.py
```

### Issue: "No significant enrichment found"

**Possible causes:**
1. Too few genes selected (need ≥2)
2. Genes don't share common functions
3. Thresholds too strict

**Solutions:**
- Select more genes (10-50 recommended)
- Check if genes are in background (20,614 genes)
- Relax p-value cutoffs

### Issue: "Server won't start"

**Check dependencies:**
```bash
pip list | grep -E "flask|scipy|pandas|statsmodels"
```

**Install missing packages:**
```bash
pip install --break-system-packages flask flask-cors scipy statsmodels pandas openpyxl
```

---

## 📊 Data Format Details

### JSON Structure (data.json)

```json
{
  "Gene_ID": "M9H77_13438",
  "Gene_Name": "CrWRKY7",
  "Description": "WRKY7 protein [Catharanthus roseus]",
  "Protein_Sequence": "MSEHHHQEEN...",
  "CDS_Sequence": "ATGAGCGAAC...",
  "GO_terms": [
    {
      "term": "GO:0003700",
      "description": "DNA-binding transcription factor activity",
      "ontology": "molecular_function"
    }
  ],
  "GO_count": 15,
  "GO_descriptions": "DNA binding; transcription regulation; ..."
}
```

### GO Enrichment API Response

```json
{
  "success": true,
  "tested_genes": 25,
  "total_input": 30,
  "enriched_terms": 12,
  "results": [
    {
      "GO_term": "GO:0006355",
      "Description": "regulation of transcription",
      "Ontology": "biological_process",
      "Count": 8,
      "GeneRatio": "8/25",
      "BgRatio": "1200/20614",
      "pvalue": 0.00001,
      "p.adjust": 0.00012,
      "GeneID": ["M9H77_13438", "M9H77_32446", ...],
      "Total_genes": 8
    }
  ]
}
```

---

## 🎯 Best Practices

### For GO Enrichment:

1. **Select biologically related genes**
   - Same gene family
   - Co-expressed genes
   - Genes from same pathway

2. **Use appropriate sample size**
   - Too few (< 5): May not find enrichment
   - Optimal (10-100): Best results
   - Too many (> 500): May be too broad

3. **Interpret results carefully**
   - Check p.adjust values (< 0.05 is significant)
   - Look at gene ratios
   - Consider biological context

4. **Compare ontologies**
   - Biological Process: What the genes do
   - Molecular Function: How they do it
   - Cellular Component: Where they do it

---

## 📚 References

### Statistical Method
- **Fisher's Exact Test:** Tests for overrepresentation
- **Benjamini-Hochberg:** Controls false discovery rate
- Similar to R's `clusterProfiler::enricher()`

### GO Ontology
- Gene Ontology Consortium: http://geneontology.org/
- Three ontologies: BP, MF, CC
- Hierarchical structure

---

## ✅ Quick Start Checklist

- [ ] Install required Python packages
- [ ] Prepare all input files
- [ ] Run `python make_data_with_go.py`
- [ ] Verify `data.json` was created
- [ ] Run `python server.py`
- [ ] Open browser to http://localhost:5000
- [ ] Search for genes
- [ ] Select genes (checkbox)
- [ ] Click "Run GO Enrichment"
- [ ] Analyze results!

---

## 💻 System Requirements

- **Python:** 3.7+
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 500MB for data files
- **Browser:** Chrome, Firefox, Safari, or Edge (modern versions)

---

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all input files are present
3. Check server logs for error messages
4. Ensure all dependencies are installed

---

**Happy analyzing! 🧬🔬**
