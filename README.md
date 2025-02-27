# Agent Saloon

A collaborative AI writing system using OpenAI's Swarm framework to orchestrate multiple AI agents for creative writing at scale.

## Overview

Agent Saloon is a Python-based system that allows multiple AI agents to collaborate on writing comprehensive books. The system follows a structured approach:

1. **Title Generation**: Agents collaborate to create an engaging book title
2. **Table of Contents Creation**: Agents design a coherent structure for the book
3. **Section Writing**: Agents work together to write each section with thoughtful debates and iterations

The key feature is the multi-agent collaboration, where each agent brings a unique perspective:

* **Zero**: The enthusiastic creative writer, making initial proposals
* **Gustave**: The thoughtful editor, refining and polishing content

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/agent_saloon.git
   cd agent_saloon
   ```

2. Install the package:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```
   Or create a `.env` file with the key.

## Usage

# Multi-Provider CLI Examples

The Agent Saloon now supports multiple AI providers and agent types. Here are examples of how to use the enhanced CLI:

## Basic Usage with Default Agents

```bash
# Create a book with default agents (Zero and Gustave via OpenAI)
agent-saloon create "The History of Artificial Intelligence"
```

## Using Multiple Agent Types

```bash
# Create a book with all three agents (Zero, Gustave, and Camille)
agent-saloon create "Machine Learning Ethics" --agents zero,gustave,camille

# Create a book with just Zero and Camille
agent-saloon create "Introduction to Python" --agents zero,camille
```

## Specifying Providers

```bash
# Use OpenAI for all agents
agent-saloon create "Data Science Fundamentals" --agents zero,gustave,camille --providers openai

# Use Anthropic for all agents
agent-saloon create "Web Development Basics" --agents zero,gustave,camille --providers anthropic

# Mix providers (Zero: OpenAI, Camille: Anthropic, Gustave: OpenAI)
agent-saloon create "Quantum Computing" --agents zero,camille,gustave --providers openai,anthropic,openai
```

## Advanced Configuration

```bash
# Generate a technical book with more detailed settings
agent-saloon create "Deep Learning Fundamentals" \
  --agents zero,camille,gustave \
  --providers openai,anthropic,openai \
  --min-chapters 8 \
  --max-chapters 12 \
  --min-words 800 \
  --max-words 2500
```

## Continuing Existing Books

```bash
# Continue a book with specific sections using Camille
agent-saloon continue your-book-id \
  --sections 3,3.1,3.2 \
  --agents camille \
  --providers anthropic
```

## Listing Available Agents

```bash
# View information about available agents and providers
agent-saloon agents
```

The output will show:

```
Available Agents:
  - zero:    Enthusiastic and creative writer
  - gustave: Refined and eloquent editor
  - camille: Balanced and insightful reviewer

Available Providers:
  - openai:    OpenAI GPT models (default for Zero and Gustave)
  - anthropic: Anthropic Claude models (default for Camille)

Default Models:
  - OpenAI:    gpt-4
  - Anthropic: claude-3-opus-20240229
```

## Examples

The `examples` directory contains sample scripts demonstrating how to use Agent Saloon:

- `simple_book.py`: Generate a book with default settings
- `advanced_book.py`: Generate a book with custom structure and selective section generation

## Project Structure

```
agent_saloon/
├── agents/           # Agent definitions
├── collaboration/    # Collaboration protocols
├── generators/       # Content generation
├── prompts/          # Prompt templates
├── config/           # Configuration
├── utils/            # Utility functions
└── book/             # Book management
```

## Advanced Features

### Customizing Agent Personalities

You can customize the agent personalities by modifying the prompt templates in the `prompts` directory.

### Custom Table of Contents

You can provide a custom table of contents structure:

```python
custom_toc = [
    {
        "title": "Introduction",
        "sections": [
            {"title": "Background", "subsections": []},
            {"title": "Key Concepts", "subsections": []}
        ]
    },
    # Additional chapters...
]

book = manager.generate_book(
    topic="Machine Learning",
    toc=custom_toc
)
```

### Exporting to Different Formats

Books can be exported to multiple formats:

```python
from agent_saloon.book.exporter import BookExporter

exporter = BookExporter()
exporter.export_markdown(book, "output.md")
exporter.export_html(book, "output.html")
exporter.export_plaintext(book, "output.txt")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
