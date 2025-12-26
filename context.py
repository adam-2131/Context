#!/usr/bin/env python3
"""
Context - A selection-based assistant that processes highlighted text
according to strict rules about using only the provided context.
"""

import sys
import argparse
import re
import os
from typing import Optional


def detect_language(text: str) -> str:
    """Detect the primary language of the text."""
    # Simple heuristic: check for common patterns
    if re.search(r'[一-龯]', text):  # Chinese characters
        return 'chinese'
    elif re.search(r'[あ-ん]|[ア-ン]', text):  # Japanese
        return 'japanese'
    elif re.search(r'[가-힣]', text):  # Korean
        return 'korean'
    elif re.search(r'[а-яё]', text, re.IGNORECASE):  # Cyrillic
        return 'russian'
    # Default to English
    return 'english'


def is_conversation(text: str) -> bool:
    """Determine if the text appears to be a conversation."""
    # Look for conversation indicators
    patterns = [
        r'^[A-Z][^:]+:\s',  # "Name: message" format
        r'^>\s',  # Quote/reply format
        r'^\[.*?\]\s',  # Timestamp or name in brackets
        r'^\d{1,2}:\d{2}',  # Time stamps
    ]
    
    lines = text.strip().split('\n')
    if len(lines) < 2:
        return False
    
    # Check if multiple lines match conversation patterns
    matches = sum(1 for line in lines[:5] if any(re.match(p, line) for p in patterns))
    return matches >= 2


def extract_last_message(text: str) -> str:
    """Extract the last message from a conversation."""
    lines = text.strip().split('\n')
    
    # Find the last substantial message
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if line and not line.startswith('>') and len(line) > 10:
            # Collect this message and any following context
            return '\n'.join(lines[i:])
    
    return text


def build_prompt(text: str, is_conv: bool, intent: Optional[str] = None, 
                style: Optional[str] = None, length: Optional[str] = None) -> str:
    """Build the system prompt for the LLM."""
    prompt = """You are Context, a selection-based assistant.

You are given text that the user has highlighted from their screen.
This text may come from:
- a conversation (chat, messages, email),
- a document or book,
- notes, code comments, or mixed content.

Assume the highlighted text is the ONLY context you are allowed to use.

Rules:
- Use ONLY the highlighted text. Do NOT invent facts, names, times, or details.
- If the text is a conversation, assume the LAST message is the one to respond to.
- If the text is informational (document, book, notes), answer or explain based strictly on it.
- Match the language of the highlighted text.
- Be natural, human, and paste-ready.
- Be concise by default.
- If crucial information is missing, ask exactly ONE short clarification question instead of guessing.
- Output ONLY the final result (reply, explanation, rewrite, etc.).
- Do NOT include explanations, meta-comments, labels, quotes, or formatting instructions.

If the user provides extra instructions (intent, style, length), follow them.
If nothing is specified, default to a concise, neutral response.

Now produce the result."""
    
    if intent:
        prompt += f"\n\nUser intent: {intent}"
    if style:
        prompt += f"\nStyle: {style}"
    if length:
        prompt += f"\nLength: {length}"
    
    if is_conv:
        prompt += "\n\nNote: This appears to be a conversation. Respond to the last message."
    else:
        prompt += "\n\nNote: This appears to be informational content. Explain or answer based strictly on it."
    
    prompt += f"\n\nHighlighted text:\n{text}"
    
    return prompt


def process_with_openai(text: str, intent: Optional[str] = None, style: Optional[str] = None, 
                       length: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """Process text using OpenAI API."""
    try:
        import openai
    except ImportError:
        return "Error: openai package not installed. Install with: pip install openai"
    
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable not set."
    
    is_conv = is_conversation(text)
    prompt = build_prompt(text, is_conv, intent, style, length)
    
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective default
            messages=[
                {"role": "system", "content": "You are Context, a selection-based assistant that processes highlighted text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error processing with OpenAI: {str(e)}"


def process_text(text: str, intent: Optional[str] = None, style: Optional[str] = None, 
                length: Optional[str] = None, use_llm: bool = True, 
                api_key: Optional[str] = None) -> str:
    """
    Process the highlighted text according to Context rules.
    
    Args:
        text: The highlighted text to process
        intent: Optional intent/instruction from user
        style: Optional style preference
        length: Optional length preference (short, medium, long)
        use_llm: Whether to use LLM for processing (default: True)
        api_key: OpenAI API key (or set OPENAI_API_KEY env var)
    """
    if not text or not text.strip():
        return ""
    
    text = text.strip()
    
    if use_llm:
        return process_with_openai(text, intent, style, length, api_key)
    else:
        # Fallback: return processed text structure
        is_conv = is_conversation(text)
        if is_conv:
            last_message = extract_last_message(text)
            return f"[Conversation detected. Last message: {last_message[:100]}...]"
        else:
            return f"[Informational content detected: {text[:100]}...]"


def get_input() -> str:
    """Get input from stdin, clipboard, or file."""
    # Try stdin first (piped input)
    if not sys.stdin.isatty():
        return sys.stdin.read()
    
    # Try clipboard
    try:
        import pyperclip
        clipboard_text = pyperclip.paste()
        if clipboard_text and clipboard_text.strip():
            return clipboard_text
    except ImportError:
        pass
    
    # Fallback: prompt for input
    print("Enter or paste the highlighted text (Ctrl+D or Ctrl+Z to finish):")
    try:
        return sys.stdin.read()
    except EOFError:
        return ""


def main():
    parser = argparse.ArgumentParser(
        description='Context - A selection-based assistant for processing highlighted text'
    )
    parser.add_argument('text', nargs='?', help='Text to process (optional if using clipboard or stdin)')
    parser.add_argument('-f', '--file', help='Read text from file')
    parser.add_argument('-c', '--clipboard', action='store_true', help='Read from clipboard')
    parser.add_argument('--intent', help='Specific intent or instruction')
    parser.add_argument('--style', help='Style preference')
    parser.add_argument('--length', choices=['short', 'medium', 'long'], help='Length preference')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM processing (fallback mode)')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Get input text
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
    elif args.clipboard:
        try:
            import pyperclip
            text = pyperclip.paste()
        except ImportError:
            print("Error: pyperclip not installed. Install with: pip install pyperclip", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading clipboard: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        text = get_input()
    
    if not text or not text.strip():
        print("Error: No text provided.", file=sys.stderr)
        sys.exit(1)
    
    # Process the text
    result = process_text(text, args.intent, args.style, args.length, 
                         use_llm=not args.no_llm, api_key=args.api_key)
    
    # Output only the result (no explanations)
    print(result)


if __name__ == '__main__':
    main()

