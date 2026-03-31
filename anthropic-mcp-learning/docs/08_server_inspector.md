# 08 — Server Inspector

## What is the MCP Server Inspector?

The MCP Server Inspector is an **in-browser debugger** for testing MCP servers without connecting to actual applications or AI models. It lets you manually invoke tools, read resources, and test prompts during development.

---

## Launching the Inspector

```bash
# Activate your Python environment first
source .venv/bin/activate

# Launch the inspector
mcp dev server.py
```

This starts the server and opens a web interface on localhost.

---

## Inspector Interface

```
┌─────────────────────────────────────────────────────┐
│  MCP Inspector                        [Connect]     │
├─────────┬───────────────────────────────────────────┤
│         │                                           │
│ Sidebar │  Resources  │  Prompts  │  Tools          │
│         │                                           │
│ Server  │  ┌─────────────────────────────────┐     │
│ Info    │  │ read_doc_contents                │     │
│         │  │ edit_document                    │     │
│         │  │                                  │     │
│         │  │ Selected: read_doc_contents      │     │
│         │  │ ┌─────────────┐                  │     │
│         │  │ │ doc_id: [  ]│   [Run Tool]     │     │
│         │  │ └─────────────┘                  │     │
│         │  │                                  │     │
│         │  │ Result:                          │     │
│         │  │ "The report details the..."      │     │
│         │  └─────────────────────────────────┘     │
└─────────┴───────────────────────────────────────────┘
```

---

## Testing Workflow

### 1. Connect to Server

Click the **Connect** button in the sidebar to establish a connection.

### 2. Test Tools

1. Navigate to the **Tools** tab
2. Select a tool from the list (e.g., `read_doc_contents`)
3. Fill in required parameters (e.g., `doc_id: report.pdf`)
4. Click **Run Tool**
5. Verify the output matches expectations

### 3. Test Resources

1. Navigate to the **Resources** tab
2. Select a resource URI (e.g., `docs://documents`)
3. Click to fetch and view the returned data

### 4. Test Prompts

1. Navigate to the **Prompts** tab
2. Select a prompt (e.g., `format`)
3. Fill in arguments
4. View the generated message template

---

## Example Testing Session

```bash
# Terminal
$ mcp dev projects/mcp_document_server/server.py
  Starting MCP Inspector...
  Server running on http://localhost:5173
```

In the browser:

1. **Connect** to the server
2. **Tools tab** → Select `read_doc_contents` → Enter `doc_id: report.pdf` → Run
   - Expected: `"The report details the state of a 20m condenser tower."`
3. **Tools tab** → Select `edit_document` → Enter params → Run
   - Verify the edit succeeded
4. **Resources tab** → Select `docs://documents`
   - Expected: `["report.pdf", "plan.md", ...]`
5. **Prompts tab** → Select `format` → Enter `doc_id: report.pdf`
   - Verify the generated prompt template

---

## Debugging Tips

| Issue | Solution |
|-------|----------|
| Inspector won't start | Ensure `mcp` package is installed and Python env is activated |
| No tools showing | Check that `@mcp.tool` decorators are correct |
| Tool returns error | Check function logic, especially input validation |
| Connection fails | Verify `mcp.run(transport="stdio")` is in your server |

---

## Inspector vs. Production Testing

| Aspect | Inspector | Production |
|--------|-----------|------------|
| Purpose | Manual testing during dev | Real usage with Claude |
| Invocation | You click buttons | Claude decides tool calls |
| Speed | Instant feedback | Full conversation loop |
| Scope | Individual tool/resource | Full workflow |

---

## Best Practices

1. **Test every tool** before connecting a client — catch bugs early
2. **Test edge cases** — empty strings, missing documents, invalid IDs
3. **Test resources** — verify MIME types and serialization
4. **Test prompts** — check argument interpolation
5. **Use during development** — keep inspector running as you code

---

## Exercises

1. Create a server with two tools and test both in the inspector
2. Add a resource to your server and verify it returns correct data
3. Test error handling by providing invalid inputs to tools in the inspector
