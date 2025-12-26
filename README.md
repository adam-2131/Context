# Context - Selection-Based Assistant

A program that processes highlighted/selected text according to strict rules about using only the provided context.

## Features

- **GUI Application**: Easy-to-use graphical interface with global hotkey support
- **Global Hotkey**: Press `Ctrl+Shift+X` from anywhere to activate
- **Auto Clipboard**: Automatically copies results to clipboard
- **Multiple Input Methods**: Clipboard, files, stdin, or command line
- **Conversation Detection**: Automatically detects and handles conversations
- **Language Detection**: Detects and matches the language of input text
- **Flexible Options**: Customize intent, style, and length of responses
- **LLM Integration**: Uses OpenAI API for intelligent text processing

## Installation

```bash
pip install -r requirements.txt
```

## Setup

Set your OpenAI API key as an environment variable:
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Windows (CMD)
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

Or pass it directly with `--api-key` flag.

## Usage

### GUI Application (Recommended)

Run the GUI application:
```bash
# Direct Python
python context_gui.py

# Or on Windows, use the batch file
run_context.bat
```

**Features:**
- Press `Ctrl+Shift+X` from anywhere to activate the window
- Automatically pastes text from clipboard when opened
- Configure style, intent, and length options
- Click "Process & Copy to Clipboard" to process and auto-copy result
- Results are automatically copied to your clipboard
- Window minimizes instead of closing (press hotkey to show again)

**Workflow:**
1. Highlight text anywhere on your screen
2. Copy it (Ctrl+C)
3. Press `Ctrl+Shift+X` to open Context Assistant
4. Text is automatically pasted from clipboard
5. Configure options (style, intent, length) if needed
6. Click "Process & Copy to Clipboard"
7. Result is automatically copied - just paste (Ctrl+V) wherever you need it!

**Note:** 
- On Windows, you may need to run as administrator for global hotkey support
- If hotkey doesn't work, right-click and "Run as Administrator"
- The window will minimize when closed - use Ctrl+Shift+X to show it again

### Command Line Interface

#### From clipboard:
```bash
python context.py --clipboard
```

#### From file:
```bash
python context.py -f input.txt
```

#### From command line:
```bash
python context.py "Your highlighted text here"
```

#### From stdin (piped input):
```bash
echo "Your text" | python context.py
```

#### With options:
```bash
python context.py --clipboard --intent "summarize" --length short
```

#### Without LLM (fallback mode):
```bash
python context.py --no-llm "Your text"
```

## Rules

- Uses ONLY the highlighted text (no invented facts)
- For conversations: responds to the last message
- For informational text: explains based strictly on it
- Matches the language of the input
- Outputs only the final result (no meta-comments)
- Asks exactly ONE clarification question if crucial info is missing

## Features

- **LLM Integration**: Uses OpenAI API for intelligent text processing
- **Multiple Input Methods**: Clipboard, files, stdin, or command line
- **Conversation Detection**: Automatically detects and handles conversations
- **Language Detection**: Detects and matches the language of input text
- **Flexible Options**: Customize intent, style, and length of responses
