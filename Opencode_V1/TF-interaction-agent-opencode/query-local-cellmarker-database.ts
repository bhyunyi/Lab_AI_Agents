import { tool } from "@opencode-ai/plugin"
import path from "path"

/**
 * Path to the local Cell Marker flat file (.txt).
 * Override by setting the CELLMARKER_FILE_PATH environment variable before
 * launching opencode, e.g.:
 */
const CELLMARKER_FILE_PATH =
  process.env.CELLMARKER_FILE_PATH ?? "/Users/b.hyunyi/Desktop/OpenCode_AI_Agents/TF-interaction-agent-opencode/human_cell_marker.txt"

export default tool({
  description:
    "Queries the local Cell Marker database file to find gene cell markers for specific cell types." +
    "Use this tool whenever the user asks about specific gene markers within a specific cell type.",

  args: {
    gene_symbol: tool.schema
      .string()
      .describe("The standard uppercase gene name or symbol (e.g., 'TP53', 'MYC', 'STAT3')."),
    cell_type: tool.schema
      .string()
      .describe("The specification of the type of cell in which the regulatory relationships are to be evaluated.")
  },

  // opencode requires this file to be TS/JS, but the actual lookup logic
  // runs in Python (query_cellmarker.py)
  async execute(args, context) {
    const script = path.join(context.worktree, "query_cellmarker.py")

    try {
      const result = await Bun.$`python3 ${script} ${args.gene_symbol} ${args.cell_type} ${CELLMARKER_FILE_PATH}`.text()
      return result.trim()
    } catch (e) {
      return `Error executing query_cellmarker.py: ${String(e)}`
    }
  },
})
