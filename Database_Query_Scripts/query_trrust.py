#!/usr/bin/env python3
"""
query_trrust.py

Reads the TRRUST TSV with pandas, filters by gene symbol, and prints a formatted result to stdout.

Usage:
    python3 query_trrust.py <GENE_SYMBOL> <TRRUST_FILE_PATH>
"""

import sys
import os
import pandas as pd


def query_local_trrust_database(gene_symbol: str, file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: TRRUST file not found at {file_path}. Please verify the path."

    try:
        df = pd.read_csv(
            file_path,
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
        print("Usage: python3 query_trrust.py <GENE_SYMBOL> <TRRUST_FILE_PATH>", file=sys.stderr)
        sys.exit(1)

    gene_symbol_arg = sys.argv[1]
    file_path_arg = sys.argv[2]

    print(query_local_trrust_database(gene_symbol_arg, file_path_arg))
