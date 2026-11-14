# Automated CoT Mini Project

A beginner-friendly Python project that demonstrates an iterative LLM workflow using structured JSON responses.

The application:
1. Accepts a task from the user.
2. Sends the conversation to an OpenAI model.
3. Processes `START`, `PLAN`, and `OUTPUT` steps.
4. Enforces a maximum number of iterations.
5. Handles API errors, invalid JSON, and unexpected response structures.
6. Executes only a small set of predefined Python tools. It never executes model-generated Python code.

> This is a learning project. The model's plan is not trusted as executable code.

## 1. Project structure

```text
automated_cot_mini_project/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── prompts/
│   └── system_prompt.txt
└── src/
    ├── __init__.py
    ├── main.py
    ├── llm_client.py
    ├── planner.py
    └── safe_tools.py
```

## 2. Concepts practised

- System and user messages
- Persona-based prompting
- Structured JSON responses
- `json.loads()` and JSON validation
- Message history and iterative API calls
- `while`, `continue`, and `break`
- Functions and allowlisted tool execution
- `try` / `except` error handling
- Maximum iteration limits
- Environment variables and `.env`

## 3. Setup

### Step 1 — Create and activate a virtual environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure your API key

Copy `.env.example` to `.env` and add your own OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
MAX_ITERATIONS=5
```

Keep `.env` private. It is excluded by `.gitignore`; never commit or share your API key.

### Step 4 — Run the project

Run this from the project root:

```bash
python -m src.main
```

## 4. How the loop works

```text
User enters a task
        |
        v
Create message_history
        |
        v
Call the LLM with message_history
        |
        v
Parse and validate JSON
        |
        +---- START ----> Display message ----> next iteration
        |
        +---- PLAN -----> Validate approved action
        |                       |
        |                       v
        |                Execute safe Python function
        |                       |
        |                       v
        |                Add result to history
        |                       |
        |                       v
        |                  next iteration
        |
        +---- OUTPUT ---> Display final answer ----> stop
        |
        +---- Invalid step / JSON / API error ---> handle safely
        |
        v
Stop if maximum iterations are reached
```

The Python application controls the loop. Appending a message to `message_history` does not itself call the API; the next API call happens when the loop reaches the next iteration.

## 5. Controlled execution

The model can request one of these actions:

| Action | What the Python application does |
|---|---|
| `count_words` | Counts words in the supplied text |
| `uppercase_text` | Converts supplied text to uppercase |
| `charcter_count` | Counts total no. of characters in the supplied text |
| `none` | Does not execute a tool |

The application checks the action against this allowlist in `safe_tools.py`.

It does **not** use `eval()`, `exec()`, shell commands, or model-generated Python code.

## 6. Example task

Try:

```text
Count the words in this sentence and then explain the result:
Python is useful for data engineering.
```

The model may return a `PLAN` asking for `count_words`. The application validates the action, executes the local Python function, adds the tool result to the conversation, and asks the model to continue.

The exact wording and number of planning iterations can vary because the model generates the responses.

## 7. Important safeguards in this project

- Maximum iteration count prevents an endless loop.
- API exceptions are caught and reported.
- JSON parsing errors are handled.
- Required response fields and step values are validated.
- Tool names are checked against an allowlist.
- Tool input is checked and limited in size.
- No arbitrary generated code is executed.

## 8. Suggested practice tasks

1. Change `MAX_ITERATIONS` and observe what happens.
2. Try a task that does not need a tool.
3. Try a task that needs `count_words`.
4. Add a new safe tool such as `character_count`.
5. Deliberately change a required JSON field in `planner.py` and observe the validation error.
6. Temporarily use an invalid API key to see the API error handling.
7. Explain why `continue` and `break` are used in `main.py`.

## 9. What this project does not cover yet

- Full autonomous agents or agent frameworks
- Database or file-system tool execution
- Parallel tool calls
- Persistent conversation storage
- Advanced retries and backoff
- Production authentication and authorisation

## 10. Code Output Samples

- Direct-answer scenarios
These should ideally return OUTPUT without executing a local tool.

<img width="994" height="286" alt="image" src="https://github.com/user-attachments/assets/59a63eeb-e901-4526-89c2-8f2307830664" />

- Tool execution scenarios
These should ideally trigger an approved tool.

<img width="1080" height="324" alt="image" src="https://github.com/user-attachments/assets/fbc8ae34-7b68-4b66-a7f8-b0f70455081b" />






