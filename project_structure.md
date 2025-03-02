# Agent Saloon

A collaborative AI writing system using OpenAI's Swarm framework to orchestrate multiple AI agents for creative writing at scale.

## Overview

Agent Saloon is a Python-based system that allows multiple AI agents to collaborate on writing comprehensive books. The system follows a structured approach:

1. **Title Generation**: Agents collaborate to create an engaging book title
2. **Table of Contents Creation**: Agents design a coherent structure for the book
3. **Section Writing**: Agents work together to write each section with thoughtful debates and iterations

## Project Structure

### Core Components

#### 1. Agents

The `agents` module defines the different AI personalities that collaborate on content creation:

- **Base Agent**: Abstract base class defining common agent properties and methods
- **Zero**: The enthusiastic creative writer, making initial proposals
- **Gustave**: The thoughtful editor, refining and polishing content
- **Factory**: Creates different types of agents with appropriate configurations

#### 2. Collaboration

The `collaboration` module manages how agents work together:

- **Coordinator**: Orchestrates the collaboration process between agents
- **Consensus**: Detects when agents have reached agreement or handles forced consensus
- **Handoff**: Manages the transition between agents during collaboration

#### 3. Generators

The `generators` module handles the content creation pipeline:

- **Base Generator**: Common functionality for all generators
- **Title Generator**: Coordinates title creation between agents
- **TOC Generator**: Manages table of contents generation
- **Section Generator**: Handles section content generation

#### 4. Prompts

The `prompts` module contains structured instructions for the agents:

- **Title Prompts**: Guidelines for title creation
- **TOC Prompts**: Instructions for structure planning
- **Section Prompts**: Directives for content writing

#### 5. Book

The `book` module manages the state and structure of the generated book:

- **Book**: Main class representing a book and its complete state
- **Section**: Represents a section within the book
- **Exporter**: Handles exporting the book to various formats

#### 6. Utils

The `utils` module provides supporting functionality:

- **Logger**: IRC-style logging for visibility into agent interactions
- **IO**: File and storage operations
- **Parsing**: Content extraction and parsing utilities
- **Formatting**: Content formatting utilities

### Configuration

The `config` module handles global settings:

- **Settings**: Configuration parameters for the application

## Usage Flow

1. User provides a book topic
2. System initializes agents with appropriate instructions
3. Title generation process begins
   - Zero proposes an initial title
   - Gustave refines the proposal
   - Agents iterate until consensus
4. Table of contents generation follows a similar pattern
5. For each section in the table of contents:
   - Zero drafts initial content
   - Gustave refines and improves
   - Agents iterate until consensus
6. Final book is assembled and exported

## Key Design Principles

1. **Clear Separation of Concerns**: Each component has a defined responsibility
2. **Extensibility**: Easy to add new agents or modify existing ones
3. **Robustness**: Error handling and recovery strategies are in place
4. **Visibility**: Comprehensive logging to track agent interactions
5. **Modularity**: Components can be reused or replaced independently

## Examples

See the `examples` directory for sample usage scripts:

- `simple_book.py`: Basic book generation
- `advanced_book.py`: Demonstrates advanced features

```console
agent_saloon/
├── README.md                 # Project documentation
├── pyproject.toml            # Dependencies and build configuration
├── .gitignore                # Git ignore file
├── .env.example              # Example environment variables
│
├── agent_saloon/             # Main package
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Entry point for CLI
│   │
│   ├── agents/               # Agent definitions
│   │   ├── __init__.py
│   │   ├── base.py           # Base agent class
│   │   ├── zero.py           # Zero agent implementation
│   │   ├── gustave.py        # Gustave agent implementation
│   │   └── factory.py        # Agent factory for creating agents
│   │
│   ├── collaboration/        # Collaboration protocols
│   │   ├── __init__.py
│   │   ├── coordinator.py    # Manages agent collaboration
│   │   ├── consensus.py      # Consensus detection and management
│   │   └── handoff.py        # Agent handoff mechanisms
│   │
│   ├── generators/           # Content generation
│   │   ├── __init__.py
│   │   ├── base_generator.py # Base generator class
│   │   ├── title.py          # Title generation
│   │   ├── toc.py            # Table of contents generation
│   │   └── section.py        # Section content generation
│   │
│   ├── prompts/              # Prompt templates
│   │   ├── __init__.py
│   │   ├── title_prompts.py  # Title generation prompts
│   │   ├── toc_prompts.py    # TOC generation prompts
│   │   └── section_prompts.py# Section generation prompts
│   │
│   ├── config/               # Configuration
│   │   ├── __init__.py
│   │   └── settings.py       # Global settings
│   │
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py         # IRC-style logging
│   │   ├── io.py             # File I/O operations
│   │   ├── parsing.py        # Content parsing utilities
│   │   └── formatting.py     # Content formatting utilities
│   │
│   └── book/                 # Book management
│       ├── __init__.py
│       ├── book.py           # Book class for managing state
│       ├── section.py        # Section class
│       └── exporter.py       # Export to various formats
│
├── examples/                 # Example usage scripts
│   ├── simple_book.py        # Basic book generation
│   └── advanced_book.py      # Advanced features example
│
└── tests/                    # Unit and integration tests
    ├── __init__.py
    ├── test_agents.py
    ├── test_collaboration.py
    ├── test_generators.py
    └── test_book.py
```
