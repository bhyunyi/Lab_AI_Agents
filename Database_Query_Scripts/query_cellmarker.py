#!/usr/bin/env python3
"""
query_cellmarker.py

Reads the CELL MARKER tsv with pandas, filters by gene symbol and cell type, and prints a formatted result to stdout.

Usage:
    python3 query_cellmarker.py <GENE_SYMBOL> <CELL_TYPE> <CellMarker_FILE_PATH>
"""

import sys
import os
import pandas as pd


def query_local_cellmarker_database(gene_symbol: str, cell_type: str, file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: Cell Marker file not found at {file_path}. Please verify the path."

    try:
        df = pd.read_csv(
            file_path,
            sep="\t",
            header=0
        )

        df = df[df["species"] == "Human"]

        search_term_gene = str(gene_symbol).strip().upper()
        search_term_cell = str(cell_type).strip().upper()

        # Safely clean the DataFrame columns for accurate matching
        df["Gene Name_clean"] = df["symbol"].astype(str).str.strip().str.upper()
        df["Cell Name_clean"] = df["cell_name"].astype(str).str.strip().str.upper()

        matches_gene = df[df["Gene Name_clean"] == search_term_gene]

        matches = matches_gene[matches_gene["Cell Name_clean"] == search_term_cell]

        if matches.empty:
            return f"No cell marker data found in the local cell marker file for the gene symbol and cell type: '{search_term_gene}' , '{search_term_cell}'."

        output_lines = [
            f"Found {len(matches)} cell marker records for '{search_term_gene}', '{search_term_cell}':"
        ]
        for _, row in matches.iterrows():
            line = f"- Gene: {row['symbol']} | Gene_Type: {row['gene_type']} | Cell_Name: {row['cell_name']} | Tissue_Type: {row['tissue_type']} | Disease: {row['disease']}"
            output_lines.append(line)

        return "\n".join(output_lines)

    except Exception as e:
        return f"An error occurred while scanning the local file: {str(e)}"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 query_cellmarker.py <GENE_SYMBOL> <CELL_TYPE> <CELLMARKER_FILE_PATH>", file=sys.stderr)
        sys.exit(1)

    gene_symbol_arg = sys.argv[1]
    cell_type_arg = sys.argv[2]
    file_path_arg = sys.argv[3]

    print(query_local_cellmarker_database(gene_symbol_arg, cell_type_arg, file_path_arg))
