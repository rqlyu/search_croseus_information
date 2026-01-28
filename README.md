# Croseus Gene Search Tool

A comprehensive web-based tool for searching and analyzing Catharanthus roseus genes across multiple versions.

## Features

1. **Gene ID Search** - Find genes by their ID across all available versions
2. **Sequence Search** - Search by DNA or protein sequence similarity 
3. **Cross-Version Mapping** - See equivalent gene IDs across all versions
4. **GO Enrichment Analysis** - Perform Gene Ontology enrichment analysis
5. **Gene Annotations** - View detailed gene descriptions, names, and protein domains

## Available Versions

- **Cr_NP**: Canonical (NP) version: Sun, S. et al. Single-cell RNA sequencing provides a high-resolution roadmap for understanding the multicellular compartmentation of specialized metabolism.               Nat. Plants 9, 179–190 (2023). https://doi.org/10.1038/s41477-022-01291-y
- **Cr_NCB**: Li, C.. Single-cell multi-omics in the medicinal plant Catharanthus roseus. Nat Chem Biol 19, 1031–1041 (2023). https://doi.org/10.1038/s41589-023-01327-0
- **Cr_2023**: A near-complete genome assembly of Catharanthus roseus and insights into its vinblastine biosynthesis and high susceptibility to the Huanglongbing pathogen
               Xu, Zhongping et al.Plant Communications, Volume 4, Issue 6, 100661, DOI: 10.1016/j.xplc.2023.100661.
- **Cr_2022**: Cuello C, Stander EA, Jansen HJ, Dugé De Bernonville T, Oudin A, Birer Williams C, Lanoue A, Giglioli Guivarc'h N, Papon N, Dirks RP, Jensen MK, O'Connor SE, Besseau S,                          Courdavault V. An updated version of the Madagascar periwinkle genome. F1000Res. 2022 Dec 21;11:1541. doi: 10.12688/f1000research.129212.1. PMID: 36761838; PMCID: PMC9902796.
- **Cr_2016**: Kellner, Franziska, et al. "Genome‐guided investigation of plant natural product biosynthesis." The Plant Journal 82.4 (2015): 680-692.
- **Cr_2015**: Kellner F, Kim J, Clavijo BJ, Hamilton JP, Childs KL, Vaillancourt B, Cepela J, Habermann M, Steuernagel B, Clissold L, McLay K, Buell CR, O'Connor SE. Genome-guided                             investigation of plant natural product biosynthesis. Plant J. 2015 May;82(4):680-92. doi: 10.1111/tpj.12827. Epub 2015 Apr 11. Erratum in: Plant J. 2019 May;98(4):760. doi:                      10.1111/tpj.14358.    PMID: 25759247.

## Installation

### Requirements

- Python 3.7+
- Flask
- Pandas
- Openpyxl
- Scipy
- Numpy
- SQLite3

### Setup

1. Install dependencies:
```bash
pip install flask pandas openpyxl scipy numpy
```

2. Ensure your data files are in the correct location:
```
/mnt/user-data/uploads/
├── Cr_NP.fasta
├── Cr_NCB.fasta
├── Cr_2023.fasta
├── Cr_2022.fasta
├── Cr_2016.fasta
├── Cr_2015.fasta
├── Cr_Annotations_Eggo.xlsx
└── Croseus_GO_NP.xlsx
```

3. Run the application:
```bash
python3 croseus_gene_search.py
```

4. Open your browser to `http://localhost:5000`

## Usage

### Gene ID Search

1. Select "Gene ID" as search type
2. Enter a gene ID (e.g., `M9H77_00686`)
3. Click "Search"
4. View results showing:
   - Gene IDs across all versions
   - Protein sequence
   - Annotations and descriptions
   - GO terms

### Sequence Search

1. Select "Sequence" as search type
2. Enter a protein sequence
3. Set minimum similarity threshold (default 80%)
4. Click "Search"
5. View similar sequences with similarity scores

### GO Enrichment Analysis

1. Switch to "GO Enrichment" tab
2. Enter gene IDs (one per line) from any version
3. Click "Analyze GO Enrichment"
4. View enriched GO terms with statistics

## Data Structure

The application builds a SQLite database with the following tables:

- **sequences**: Stores gene sequences from all FASTA files
- **gene_mappings**: Cross-version gene ID mappings
- **annotations**: Gene annotations from Excel file
- **go_terms**: GO terms for enrichment analysis

## Architecture

- **Backend**: Flask web framework with SQLite database
- **Frontend**: Bootstrap 5 responsive web interface
- **Data Processing**: Pandas for Excel files, custom FASTA parser
- **Statistics**: Scipy for hypergeometric tests in GO enrichment

## Release on GitHub

To release this tool on GitHub:

1. Create a new repository: `croseus-gene-search-tool`

2. Repository structure:
```
croseus-gene-search-tool/
├── README.md
├── requirements.txt
├── croseus_gene_search.py
├── templates/
│   └── index.html
├── data/
│   └── README.md (instructions for data placement)
└── screenshots/
    ├── search_interface.png
    ├── gene_results.png
    └── go_enrichment.png
```

3. Add installation and usage instructions

4. Include sample data or instructions for obtaining data

5. Add screenshots of the interface

6. Create releases with versioning

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under the MIT License - see the LICENSE file for details.

## Citation

If you use this tool in your research, please cite:

```
Croseus Gene Search Tool
Ruiqing Lyu
KTRDC, University of Kentucky
2026
Available at: https://rqlyu.github.io/search_croseus_information/
```

## Contact

For questions or support, please open an issue on GitHub.
