import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * Path to the local TFMarker flat file (.csv).
 * Override by setting the TFMARKER_FILE_PATH environment variable before
 * launching opencode, e.g.:
 */
const TFMARKER_FILE_PATH =
  process.env.TFMARKER_FILE_PATH ?? "/Users/b.hyunyi/Desktop/OpenCode_AI_Agents/TF-interaction-agent-opencode/All TF-markers.csv"

export default tool({
  description:
    "Queries the local TFMarker database file to find regulatory relationships for a gene that is cell type specific. " +
    "Use this tool whenever the user asks about transcription factors, gene targets, " +
    "or interaction mechanisms (activation/repression) for a specific gene within a specfic cell type.",

  args: {
    gene_symbol: tool.schema
      .string()
      .describe("The standard uppercase gene name or symbol (e.g., 'TP53', 'MYC', 'STAT3')."),
    cell_type: tool.schema
      .string()
      .describe("The specification of the type of cell in which the regulatory relationships are to be evaluated.")
  },

  // opencode requires this file to be TS/JS, but the actual lookup logic
  // runs in Python (query_TFMarker.py)
  async execute(args, context) {
    const script = path.join(context.worktree, "query_TFMarker.py")

    try {
      const result = await Bun.$`python3 ${script} ${args.gene_symbol} ${args.cell_type} ${TFMARKER_FILE_PATH}`.text()
      return result.trim()
    } catch (e) {
      return `Error executing query_TFMarker.py: ${String(e)}`
    }
  },
})
