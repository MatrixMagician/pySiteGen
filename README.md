# pySiteGen

A Python-based static site generator that processes inline text elements and converts them to HTML. This project provides a foundation for building static websites by representing different types of text content through a structured node system.

## Features

- **Text Node System**: Represents different types of inline text elements including:
  - Plain text
  - Bold text
  - Italic text
  - Code snippets
  - Links
  - Images

- **Type Safety**: Uses Python enums for text type definitions
- **Extensible Architecture**: Easy to add new text types and processing capabilities
- **Unit Testing**: Comprehensive test suite for core functionality

## Project Structure

```
pySiteGen/
├── src/
│   ├── main.py          # Main application entry point
│   ├── textnode.py      # Core TextNode and TextType classes
│   └── test_textnode.py # Unit tests for TextNode functionality
├── public/              # Output directory for generated static files
├── main.sh              # Script to run the application
├── test.sh              # Script to run all unit tests
└── README.md            # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.x

### Running the Application

Execute the main application:
```bash
./main.sh
```

Or run directly with Python:
```bash
python3 src/main.py
```

### Running Tests

Run the complete test suite:
```bash
./test.sh
```

Or run tests directly:
```bash
python3 -m unittest discover -s src
```

## Usage Example

```python
from textnode import TextNode, TextType

# Create a link node
node = TextNode("This is some anchor text", TextType.LINK, "https://github.com")
print(node)  # TextNode(This is some anchor text, TextType.LINK, https://github.com)
```

## Development

The project is currently in early development. The core `TextNode` class provides the foundation for representing inline text elements with support for various text types and optional URL attributes for links and images.

### Core Classes

- **`TextType`**: Enum defining supported text types (TEXT, BOLD, ITALIC, CODE, LINK, IMAGE)
- **`TextNode`**: Main class for representing text elements with type and optional URL

## Contributing

This project follows standard Python development practices. When contributing:

1. Run tests before submitting changes
2. Follow existing code style and conventions
3. Add tests for new functionality
