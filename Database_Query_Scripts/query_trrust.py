#!/usr/bin/env python3
"""
query_trrust.py

Reads the TRRUST TSV with pandas, filters by gene symbol, and prints a formatted result to stdout.

Usage:
    python3 query_trrust.py <GENE_SYMBOL> 
"""

import sys
import os
import pandas as pd

TRRUST_FILE_PATH = /path/to/database

def query_local_trrust_database(gene_symbol: str) -> str:
    if not os.path.exists(TRRUST_FILE_PATH):
        return f"Error: TRRUST file not found at {TRRUST_FILE_PATH}. Please verify the path."

    try:
        df = pd.read_csv(
            TRRUST_FILE_PATH,
            sep="\t",
            header=None,
            names=["Transcription_Factor", "Target_Gene", "Mode", "PubMed_ID"],
        )

        search_term = str(gene_symbol).strip().upper()

        matches = df[
            (df["Transcription_Factor"] == search_term)
            | (df["Target_Gene"] == search_term)
        ]

        if matches.empty:
            return f"No regulatory data found in the local TRRUST file for the gene symbol: '{search_term}'."

        output_lines = [
            f"Found {len(matches)} TRRUST regulatory records for '{search_term}':"
        ]
        for _, row in matches.iterrows():
            line = f"- TF: {row['Transcription_Factor']} | Target: {row['Target_Gene']} | Mode: {row['Mode']} (PubMed: {row['PubMed_ID']})"
            output_lines.append(line)

        return "\n".join(output_lines)

    except Exception as e:
        return f"An error occurred while scanning the local file: {str(e)}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 query_trrust.py <GENE_SYMBOL>", file=sys.stderr)
        sys.exit(1)

    gene_symbol_arg = sys.argv[1]
    
    print(query_local_trrust_database(gene_symbol_arg))
