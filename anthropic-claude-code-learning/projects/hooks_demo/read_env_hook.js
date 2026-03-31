#!/usr/bin/env node
/**
 * Pre-tool Hook: Block .env file access
 *
 * This hook is invoked by Claude Code BEFORE tool execution.
 * It reads the tool call JSON from stdin and checks whether the
 * tool is attempting to read or write a .env file.
 *
 * Exit codes:
 *   0 — Allow the tool call to proceed.
 *   2 — Block the tool call (reason sent via stderr).
 *
 * Hook configuration goes in .claude/settings.local.json.
 */

const fs = require("fs");

const BLOCKED_PATTERNS = [".env", ".env.local", ".env.production", ".env.staging"];

function main() {
  let input = "";

  process.stdin.setEncoding("utf8");

  process.stdin.on("data", (chunk) => {
    input += chunk;
  });

  process.stdin.on("end", () => {
    try {
      const event = JSON.parse(input);
      const toolName = event.tool_name || "";
      const toolInput = event.tool_input || {};

      // Only inspect file-related tools
      const fileTools = ["read_file", "write_file", "edit_file", "create_file"];
      if (!fileTools.includes(toolName)) {
        process.exit(0); // Allow non-file tools
      }

      // Check the file_path field
      const filePath = toolInput.file_path || toolInput.path || "";

      for (const pattern of BLOCKED_PATTERNS) {
        if (filePath.includes(pattern)) {
          process.stderr.write(
            `BLOCKED: Access to '${filePath}' denied. ` +
              `Files matching '${pattern}' are restricted for security.\n`
          );
          process.exit(2);
        }
      }

      // Allow if nothing matched
      process.exit(0);
    } catch (err) {
      // If we can't parse the input, allow the call (fail open for non-security hooks)
      // For a stricter policy, use process.exit(2) here.
      process.stderr.write(`Hook error: ${err.message}\n`);
      process.exit(0);
    }
  });
}

main();
