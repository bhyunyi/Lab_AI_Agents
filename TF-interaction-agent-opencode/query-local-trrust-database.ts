import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * Path to the local TRRUST flat file (.tsv).
 * Override by setting the TRRUST_FILE_PATH environment variable before
 * launching opencode, e.g.:
 */
const TRRUST_FILE_PATH =
  process.env.TRRUST_FILE_PATH ?? "/Users/b.hyunyi/Desktop/TF-interaction-agent-opencode/trrust_rawdata.human.tsv"

export default tool({
  description:
    "Queries the local TRRUST database file to find regulatory relationships for a gene. " +
    "Use this tool whenever the user asks about transcription factors, gene targets, " +
    "or interaction mechanisms (activation/repression) for a specific gene.",

  args: {
    gene_symbol: tool.schema
      .string()
      .describe("The standard uppercase gene name or symbol (e.g., 'TP53', 'MYC', 'STAT3')."),
  },

  // opencode requires this file to be TS/JS, but the actual lookup logic
  // runs in Python (query_trrust.py)
  async execute(args, context) {
    const script = path.join(context.worktree, "query_trrust.py")

    try {
      const result = await Bun.$`python3 ${script} ${args.gene_symbol} ${TRRUST_FILE_PATH}`.text()
      return result.trim()
    } catch (e) {
      return `Error executing query_trrust.py: ${String(e)}`
    }
  },
})
