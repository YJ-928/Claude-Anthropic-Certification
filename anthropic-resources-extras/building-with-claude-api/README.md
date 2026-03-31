# Building with the Claude API — Anthropic Certification Course

A complete hands-on course covering everything you need to build real applications with Claude, Anthropic's AI API. By the end you will be able to make API calls, engineer better prompts, implement tool use, build RAG pipelines, and use advanced features like streaming, caching, and extended thinking.

---

## What is this course about?

This course teaches you how to go from zero to building production-ready AI applications using the Claude API. You will learn:

- How Claude works internally (tokenization, embeddings, generation)
- How to make API calls in Python and manage conversations
- How to engineer prompts that consistently produce high-quality outputs
- How to give Claude tools so it can call external APIs and execute code
- How to build a Retrieval Augmented Generation (RAG) pipeline for querying large documents
- Advanced features: streaming, caching, images, PDFs, extended thinking, and more

---

## Prerequisites

- Basic Python knowledge
- An [Anthropic API key](https://console.anthropic.com/)
- Python 3.9+ with `pip`

### Setup

```bash
pip install anthropic python-dotenv
```

Create a `.env` file in this folder:

```
ANTHROPIC_API_KEY="your_key_here"
```

---

## Course Modules

### Module 1 — Understanding Claude Models

Claude comes in three families:

| Model | Best For | Trade-off |
|-------|----------|-----------|
| **Opus** | Complex reasoning, multi-step tasks | Highest cost and latency |
| **Sonnet** | Balanced everyday use, coding | Best cost/quality ratio |
| **Haiku** | Speed-critical, high-volume tasks | No extended reasoning |

**Key insight:** Real applications often use multiple models — Haiku for fast/cheap calls, Sonnet for general tasks, Opus when deep reasoning is required.

---

### Module 2 — Making Your First API Request

**How the API works (5 steps):**
1. Your server receives a user message
2. Your server calls the Anthropic API (never call it from the client to keep your key secret)
3. Claude tokenizes input → creates embeddings → generates tokens one-by-one
4. Generation stops when `max_tokens` is reached or an end-of-sequence token appears
5. API returns the response + `stop_reason` + token usage counts

**Minimum required parameters:**
```python
client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,            # upper limit, not a target
    messages=[{"role": "user", "content": "Hello!"}]
)
```

Access the text: `response.content[0].text`

---

### Module 3 — Multi-Turn Conversations

Claude stores **nothing** between requests. You must maintain conversation history yourself and send the full history with every request.

```python
messages = []
messages.append({"role": "user",      "content": "My name is Alice"})
messages.append({"role": "assistant", "content": response_text})
messages.append({"role": "user",      "content": "What is my name?"})
# Claude can now answer "Alice" because history was sent
```

Helper functions to build: `add_user_message()`, `add_assistant_message()`, `chat()`.

---

### Module 4 — System Prompts

System prompts let you define **how** Claude responds (its persona, tone, rules) without changing the user's message.

```python
client.messages.create(
    model="...",
    max_tokens=1024,
    system="You are a patient math tutor. Give hints, never full answers.",
    messages=[{"role": "user", "content": "How do I solve 2x + 5 = 11?"}]
)
```

---

### Module 5 — Temperature

Temperature (0–1) controls how creative/random the output is:

| Temperature | Behaviour | Use case |
|-------------|-----------|----------|
| 0 | Deterministic, always picks highest probability word | Data extraction, factual Q&A |
| 0.5 | Balanced | General use |
| 1.0 | Very creative, more surprising | Brainstorming, jokes, marketing copy |

```python
client.messages.create(..., temperature=0.9)
```

---

### Module 6 — Response Streaming

Instead of waiting 10–30 seconds for a full response, stream it word-by-word for a better user experience.

```python
with client.messages.stream(model=..., max_tokens=..., messages=...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

final_message = stream.get_final_message()  # for storing in a database
```

**Event types:** `message_start` → `content_block_delta` (the actual text) → `message_stop`

---

### Module 7 — Controlling Model Output

**Technique 1 — Pre-filling assistant messages**

Add a partial assistant message to steer the response direction:

```python
messages = [
    {"role": "user",      "content": "Coffee vs tea: which is better?"},
    {"role": "assistant", "content": "Coffee is better because"}   # Claude continues from here
]
```

**Technique 2 — Stop sequences**

Force Claude to stop when it generates a specific string:

```python
client.messages.create(..., stop_sequences=["five"])
# If prompt is "count 1 to 10", output stops at "four, "
```

---

### Module 8 — Structured Data Extraction

Combine pre-filling + stop sequences to get raw JSON/code without Claude's usual commentary:

```python
messages = [
    {"role": "user",      "content": "Extract the names and ages as JSON"},
    {"role": "assistant", "content": "```json"}   # pre-fill with opening delimiter
]
response = client.messages.create(..., stop_sequences=["```"])
# Output is clean JSON, no markdown wrapper needed
```

---

### Module 9 — Prompt Engineering & Evaluation

**The Eval Workflow (6 steps):**
1. Write an initial prompt
2. Create a test dataset (JSON array of test inputs — can be generated by Claude itself)
3. For each test case, merge it into the prompt template
4. Send each variation to Claude and collect outputs
5. Grade outputs (0–10 score) using a grader
6. Average scores, tweak prompt, repeat

**Grader types:**
- **Code graders** — validate JSON/Python/regex syntax programmatically
- **Model graders** — ask Claude to score its own output (flexible, slightly inconsistent)
- **Human graders** — most accurate, most time-consuming

**Scoring formula:** `final_score = (model_score + syntax_score) / 2`

---

### Module 10 — Prompt Engineering Techniques

Apply these techniques in order and re-evaluate after each one to measure improvement:

| Technique | What it does | Example score gain |
|-----------|--------------|--------------------|
| **Clear & Direct** | Start with an action verb, state the task plainly | 2.32 → 3.92 |
| **Be Specific** | Add output attributes (length, format) or reasoning steps | 3.92 → 7.86 |
| **XML Tags** | Wrap dynamic content in descriptive tags to reduce ambiguity | Consistent gains |
| **Examples (few-shot)** | Show sample input/ideal output pairs | Handles edge cases |

```python
# Example of all four techniques combined
prompt = """Generate a one-day meal plan for an athlete.

Guidelines:
- Include breakfast, lunch, dinner, and two snacks
- Total calories between 2500-3500 kcal
- Specify macros for each meal

<athlete_information>
{athlete_info}
</athlete_information>

<example>
<input>Height: 180cm, Weight: 80kg, Goal: muscle gain, Restrictions: none</input>
<output>Breakfast: Oatmeal with berries (600 kcal, 80g carbs, 30g protein)...</output>
</example>
"""
```

---

### Module 11 — Tool Use

Tools let Claude call external functions to get real-time information or take actions.

**Flow:**
1. You send a request + tool schemas to Claude
2. Claude decides a tool is needed and responds with a `tool_use` block
3. Your code executes the function and gets the result
4. You send the result back as a `tool_result` block
5. Claude incorporates the result and gives a final answer

**Tool schema structure:**
```python
{
    "name": "get_current_datetime",
    "description": "Returns the current date and time. Call this when you need to know what time it is now.",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {"type": "string", "description": "strftime format string"}
        },
        "required": []
    }
}
```

**Multi-turn tool loop:**
```python
while True:
    response = chat(messages, tools=tools)
    messages.append({"role": "assistant", "content": response.content})
    if response.stop_reason != "tool_use":
        break
    tool_results = run_tools(response)
    messages.append({"role": "user", "content": tool_results})
```

**Project — Reminder Bot:** Build three tools that chain together so Claude can accept natural language like "remind me next Thursday" and actually set the reminder:
1. `get_current_datetime` — what time is it now?
2. `add_duration_to_datetime` — calculate the future date
3. `set_reminder` — create the reminder

---

### Module 12 — Advanced Tool Features

**Batch Tool** — Trick Claude into running multiple tools in parallel by wrapping them in a single "batch" tool:
```python
# Claude calls batch({invocations: [{tool: "A", args: ...}, {tool: "B", args: ...}]})
# Your code runs A and B, returns both results at once
```

**Structured Data Extraction via Tools** — More reliable than pre-fill + stop sequences:
```python
client.messages.create(
    ...,
    tools=[extraction_schema],
    tool_choice={"type": "tool", "name": "extract_data"}  # force tool call
)
data = response.content[0].input  # directly a Python dict
```

**Built-in Tools (no code needed):**
- `text_editor_20250124` — Claude reads/writes/edits files (you implement the file operations)
- `web_search_20250305` — Claude searches the web and returns citations automatically

**Fine-Grained Streaming** — Set `fine_grained: true` to disable server-side JSON buffering. Provides faster streaming at the cost of possible invalid JSON chunks.

---

### Module 13 — Retrieval Augmented Generation (RAG)

RAG solves the problem of querying large documents (100–1000+ pages) that exceed Claude's context window.

**Full RAG Pipeline:**

```
Document → Chunking → Embeddings → Vector DB
                                        ↓
User Query → Query Embedding → Similarity Search → Top-K Chunks → Claude
```

**Step-by-step:**

1. **Chunking** — Split documents into small pieces
   - *Size-based:* equal character count + overlap to preserve context
   - *Structure-based:* split on headers/paragraphs (best for markdown/HTML)
   - *Semantic:* group related sentences using NLP (most advanced)

2. **Embeddings** — Convert each chunk to a vector (list of numbers) using an embedding model (e.g., Voyage AI). Similar texts produce similar vectors.

3. **Vector Database** — Store vectors for fast similarity search using cosine distance.

4. **Hybrid Search** — More accurate than vector search alone:
   - *Vector search:* finds semantically similar chunks
   - *BM25 lexical search:* finds exact keyword matches (rare terms weighted higher)
   - *Combine with Reciprocal Rank Fusion (RRF):* `score = Σ 1/(rank + 1)` across both indexes

5. **Reranking** — After retrieval, pass candidates to Claude to re-order by relevance. Adds latency but improves accuracy for nuanced queries.

6. **Contextual Retrieval** — Before storing chunks, prepend a short context sentence (generated by Claude) explaining how each chunk relates to the full document. Dramatically improves retrieval accuracy.

---

### Module 14 — Extended Thinking

Extended thinking gives Claude time to reason before answering, improving accuracy on hard problems.

```python
client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},  # min 1024
    messages=[...]
)
# response.content[0] = ThinkingBlock (Claude's reasoning)
# response.content[1] = TextBlock  (final answer)
```

**When to use:** Only after prompt engineering optimizations have been exhausted. It costs more (thinking tokens are billed) and adds latency.

---

### Module 15 — Images & PDFs

**Images:**
```python
{"role": "user", "content": [
    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64_data}},
    {"type": "text",  "text": "Describe this image in detail"}
]}
```
Tip: image analysis quality depends heavily on prompt quality, not just image quality.

**PDFs:**
```python
{"role": "user", "content": [
    {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64_data}},
    {"type": "text", "text": "Summarize this PDF"}
]}
```

**Citations** — Enable to get exact source references back from Claude:
```python
client.messages.create(..., citations={"enabled": True})
```

---

### Module 16 — Prompt Caching

Caching saves Claude's processing work and reuses it on identical follow-up requests. Results in faster responses and lower costs.

```python
# Add cache_control to content you want cached (must be ≥ 1024 tokens)
system_prompt = [{"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}}]

# Check usage to see if cache was hit
response.usage.cache_read_input_tokens   # > 0 means cache was used
response.usage.cache_creation_input_tokens  # > 0 means cache was written
```

**Rules:**
- Cache lasts 1 hour
- Max 4 breakpoints per request
- Processing order for cache: tools → system prompt → messages
- Any change to cached content invalidates the cache

---

### Module 17 — Files API & Code Execution

**Files API** — Upload files once, reference by ID instead of re-encoding every request:
```python
file = client.beta.files.upload(file=open("data.csv", "rb"))
# Use file.id in future requests
```

**Code Execution Tool** — Claude writes and runs Python in an isolated Docker container:
```python
tools = [{"type": "computer_use_20250124", ...}]
# Claude generates code, executes it, interprets output, responds
```

---

## Exercises Index

All hands-on exercises are in the `exercises/` folder:

| Notebook | Topics Covered |
|----------|----------------|
| [01_api_basics.ipynb](exercises/01_api_basics.ipynb) | First API call, multi-turn chat, system prompts, temperature |
| [02_streaming_output_control.ipynb](exercises/02_streaming_output_control.ipynb) | Streaming, pre-filling, stop sequences, structured JSON extraction |
| [03_prompt_engineering_eval.ipynb](exercises/03_prompt_engineering_eval.ipynb) | Eval pipeline, dataset generation, model grading, code grading |
| [04_tool_use_reminder_bot.ipynb](exercises/04_tool_use_reminder_bot.ipynb) | Tool schemas, tool functions, multi-turn tool loop, reminder bot |
| [05_advanced_tools.ipynb](exercises/05_advanced_tools.ipynb) | Batch tool, structured extraction, web search tool |
| [06_rag_pipeline.ipynb](exercises/06_rag_pipeline.ipynb) | Chunking, embeddings, vector DB, BM25, hybrid search, reranking |
| [07_advanced_features.ipynb](exercises/07_advanced_features.ipynb) | Extended thinking, images, PDFs, citations, prompt caching |

---

## Key Concepts Quick Reference

| Concept | One-line summary |
|---------|-----------------|
| `max_tokens` | Upper limit on generation, not a target length |
| `stop_reason` | Why Claude stopped: `"end_turn"`, `"tool_use"`, `"max_tokens"` |
| `temperature` | 0 = deterministic, 1 = creative |
| Pre-fill | Append partial assistant message to steer response direction |
| Stop sequences | Force Claude to stop at a specific string |
| Tool use | Claude requests function calls; your code executes and returns results |
| RAG | Chunk → embed → store → retrieve relevant chunks → prompt |
| Cosine similarity | -1 to 1; closer to 1 = more similar vectors |
| BM25 | Scores documents by term frequency, down-weights common words |
| RRF | Merges ranked lists from multiple search systems into one score |
| Prompt caching | Reuse processed input work for 1 hour, saves cost + latency |
| Extended thinking | Claude reasons internally before answering, better accuracy |
| MCP | Standard protocol so Claude can connect to external tool servers |

