# Anthropic Claude API — Learning Repository

A structured, hands-on learning repository for the **Anthropic Academy: Building with the Claude API** course.

---

## What's Inside

| Folder | Contents |
|--------|----------|
| `docs/` | 28 topic-by-topic markdown reference guides |
| `notebooks/` | 15 Jupyter notebooks with live code examples |
| `exercises/` | 10 standalone Python exercises |
| `datasets/` | Sample evaluation datasets |
| `projects/` | 3 production-ready backend projects |
| `utils/` | Shared client helpers used across everything |

---

## Repository Structure

```
anthropic-claude-api-learning/
├── README.md
├── requirements.txt
├── .env.example
│
├── docs/                          # 28 topic reference guides
│   ├── 01_claude_models.md
│   ├── 02_anthropic_api_basics.md
│   └── ... (see docs/ for full list)
│
├── notebooks/                     # 15 interactive notebooks
│   ├── 01_claude_models.ipynb
│   ├── 02_api_basics.ipynb
│   └── ... (see notebooks/ for full list)
│
├── exercises/                     # 10 standalone Python scripts
│   ├── exercise_01_basic_api_call.py
│   └── ...
│
├── datasets/
│   └── eval_dataset.json
│
├── projects/
│   ├── claude_chat_server/        # FastAPI streaming chat server
│   ├── rag_document_search/       # Full RAG pipeline
│   └── tool_agent_reminder/       # Tool-using Claude agent
│
└── utils/
    ├── anthropic_client.py        # Shared client setup
    ├── message_helpers.py         # Conversation history helpers
    └── streaming_helpers.py       # Streaming output helpers
```

---

## Setup

```bash
# 1. Clone / open the repo
cd anthropic-claude-api-learning

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

---

## Learning Path

Follow the topics in order for a structured progression:

### Foundations
1. [Claude Models](docs/01_claude_models.md) — model families, pricing, context windows
2. [API Basics](docs/02_anthropic_api_basics.md) — authentication, SDK setup, first call
3. [Messages API](docs/03_messages_api.md) — request/response structure
4. [Multi-Turn Conversations](docs/04_multi_turn_conversations.md) — message history pattern
5. [System Prompts](docs/05_system_prompts.md) — personas, rules, restrictions
6. [Temperature & Sampling](docs/06_temperature_and_sampling.md) — controlling randomness

### Output Control
7. [Streaming](docs/07_streaming_responses.md) — real-time token delivery
8. [Controlling Output](docs/08_controlling_output.md) — pre-filling, stop sequences
9. [Structured Outputs](docs/09_structured_outputs.md) — reliable JSON extraction

### Prompt Engineering
10. [Prompt Engineering](docs/10_prompt_engineering.md) — techniques and patterns
11. [Prompt Evaluation](docs/11_prompt_evaluation.md) — building eval pipelines
12. [Dataset Generation](docs/12_dataset_generation.md) — synthetic data with Claude
13. [Model-Based Grading](docs/13_model_based_grading.md) — LLM-as-judge
14. [Code-Based Grading](docs/14_code_based_grading.md) — deterministic evaluation

### Tool Use
15. [Tool Use Basics](docs/15_tool_use_basics.md) — schemas, dispatcher pattern
16. [Tool Chaining](docs/16_tool_chaining.md) — multi-step tool calls
17. [Batch Tool Execution](docs/17_batch_tool_execution.md) — parallel tool calls
18. [Streaming with Tools](docs/18_streaming_with_tools.md)

### RAG
19. [RAG Introduction](docs/19_rag_intro.md)
20. [Chunking Strategies](docs/20_chunking_strategies.md)
21. [Embeddings](docs/21_embeddings.md)
22. [Vector Databases](docs/22_vector_databases.md)
23. [Hybrid Search & BM25](docs/23_hybrid_search_bm25.md)
24. [Reranking](docs/24_reranking.md)
25. [Contextual Retrieval](docs/25_contextual_retrieval.md)

### Advanced
26. [Prompt Caching](docs/26_prompt_caching.md)
27. [Model Context Protocol](docs/27_mcp_intro.md)
28. [Agents vs Workflows](docs/28_agents_vs_workflows.md)

---

## Projects

### 1. Claude Chat Server
A production FastAPI backend with streaming multi-turn chat.

```bash
cd projects/claude_chat_server
uvicorn main:app --reload
# POST /chat          — single response
# POST /chat/stream   — streaming SSE response
```

### 2. RAG Document Search
Full RAG pipeline: ingest → chunk → embed → hybrid search → rerank → answer.

```bash
cd projects/rag_document_search
python ingest.py --path /path/to/your/docs
python main.py
```

### 3. Tool Agent — Reminder Bot
A Claude agent that uses tools to manage reminders with natural language.

```bash
cd projects/tool_agent_reminder
python main.py
```

---

## Key Concepts Quick Reference

| Concept | API Parameter | When to Use |
|---------|--------------|-------------|
| Temperature | `temperature=0.0–1.0` | 0 for facts/extraction, 1 for creative tasks |
| Streaming | `client.messages.stream()` | All user-facing interfaces |
| Pre-filling | `assistant` turn in messages | Force output format |
| Stop sequences | `stop_sequences=[...]` | Precise extraction |
| Tool use | `tools=[...]` | External actions, structured data |
| Prompt caching | `cache_control` | Repeated long contexts |
| Extended thinking | `thinking={...}` | Hard reasoning tasks |

---

## Models Reference

| Model | Speed | Cost | Best For |
|-------|-------|------|---------- |
| `claude-haiku-4-5` | Fastest | Lowest | Exercises, classification, grading |
| `claude-sonnet-4-5` | Balanced | Medium | General use, production APIs |
| `claude-opus-4` | Slower | Highest | Complex reasoning, long documents |

---

## Running the Notebooks

```bash
pip install jupyter
jupyter lab
```

Open any notebook in `notebooks/` and run cells top to bottom. All notebooks load the API key from `../.env`.

---

## Running Individual Exercises

Each exercise in `exercises/` is a self-contained Python script:

```bash
python exercises/exercise_01_basic_api_call.py
python exercises/exercise_02_multi_turn_chat.py
# etc.
```

---

*Based on the Anthropic Academy "Building with the Claude API" course.*
