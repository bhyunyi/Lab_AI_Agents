import { tool } from "@opencode-ai/plugin"
import path from "path"

// this will create the tool for open code
export default tool({
  description:
    "This AI subagent will transcribe audio files given by the user to text. " +
    "If the text contains a query, an answer will be provided by the LLM model it functions on.",

  args: {
    audio_path: tool.schema
      .string()
      .describe("The path to the audio recording that will be transcribed."),
  },

  // opencode requires this file to be TS/JS, but the actual lookup logic
  // runs in Python (whispr.py)
  async execute(args, context) {
    const script = path.join(context.worktree, "whispr.py")

    try {
      const result = await Bun.$`python3 ${script} ${args.audio_path}`.text()
      return result.trim()
    } catch (e) {
      return JSON.stringify({
          success: false,
          error: `Error executing whispr.py script: ${String(e)}`
          })
    }
  },
})