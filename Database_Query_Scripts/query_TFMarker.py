#!/usr/bin/env python3
"""
query_TFMarker.py

Reads the TF-Marker CSV with pandas, filters by gene symbol and cell type, and prints a formatted result to stdout.

Usage:
    python3 query_TFMarker.py <GENE_SYMBOL> <CELL_TYPE>
"""

import sys
import os
import pandas as pd

TFMarker_FILE_PATH = /path/to/database

def query_local_TFMarker_database(gene_symbol: str, cell_type: str) -> str:
    if not os.path.exists(TFMarker_FILE_PATH):
        return f"Error: TFMarker file not found at {TFMarker_FILE_PATH}. Please verify the path."

    try:
        df = pd.read_csv(
            TFMarker_FILE_PATH,
            header=0
        )

        search_term_gene = str(gene_symbol).strip().upper()
        search_term_cell = str(cell_type).strip().upper()

        # Safely clean the DataFrame columns for accurate matching
        df["Gene Name_clean"] = df["Gene Name"].astype(str).str.strip().str.upper()
        df["Cell Name_clean"] = df["Cell Name"].astype(str).str.strip().str.upper()

        matches_gene = df[
            (df["Gene Name_clean"] == search_term_gene)
            | (df["Interacting Gene"].astype(str).str.upper().str.contains(search_term_gene, na=False))
        ]

        matches = matches_gene[matches_gene["Cell Name_clean"] == search_term_cell]

        if matches.empty:
            return f"No regulatory data found in the local TFMarker file for the gene symbol and cell type: '{search_term_gene}' , '{search_term_cell}'."

        output_lines = [
            f"Found {len(matches)} TFMarker regulatory records for '{search_term_gene}', '{search_term_cell}':"
        ]
        for _, row in matches.iterrows():
            line = f"- TF: {row['Gene Name']} | Gene_Type: {row['Gene Type']} | Cell_Name: {row['Cell Name']} | Cell_Type: {row['Cell Type']} | Tissue_Type: {row['Tissue Type']} | Function: {row['Function']} | Interacting_genes: {row['Interacting Gene']}"
            output_lines.append(line)

        return "\n".join(output_lines)

    except Exception as e:
        return f"An error occurred while scanning the local file: {str(e)}"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 query_TFMarker.py <GENE_SYMBOL> <CELL_TYPE>", file=sys.stderr)
        sys.exit(1)

    gene_symbol_arg = sys.argv[1]
    cell_type_arg = sys.argv[2]

    print(query_local_TFMarker_database(gene_symbol_arg, cell_type_arg))
