#!/bin/bash

echo "Starting Croseus Gene Search Tool..."
echo "=================================="

# Check if required files exist
if [ ! -f "/mnt/user-data/uploads/Cr_NP.fasta" ]; then
    echo "Warning: Cr_NP.fasta not found in /mnt/user-data/uploads/"
fi

if [ ! -f "/mnt/user-data/uploads/Cr_Annotations_Eggo.xlsx" ]; then
    echo "Warning: Cr_Annotations_Eggo.xlsx not found in /mnt/user-data/uploads/"
fi

if [ ! -f "/mnt/user-data/uploads/Croseus_GO_NP.xlsx" ]; then
    echo "Warning: Croseus_GO_NP.xlsx not found in /mnt/user-data/uploads/"
fi

# Start the application
cd /home/claude
echo "Starting Flask application..."
echo "Access the tool at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"

python3 croseus_gene_search.py
