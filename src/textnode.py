from enum import Enum
import re


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url
    
    def __eq__(self, other):
        return (
            self.text == other.text and
            self.text_type == other.text_type and
            self.url == other.url
        )
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Split text nodes based on a delimiter and create new nodes with the specified text type.
    
    Args:
        old_nodes: List of TextNode objects to process
        delimiter: String delimiter to split on (e.g., "`", "**", "*")
        text_type: TextType enum value for the delimited text
        
    Returns:
        List of TextNode objects with delimited text split into separate nodes
    """
    new_nodes = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            # Only process TEXT type nodes
            new_nodes.append(node)
            continue
            
        text = node.text
        if not text:
            # Empty text, skip
            continue
            
        if delimiter not in text:
            # No delimiter found, keep original node
            new_nodes.append(node)
            continue
            
        # Split the text by delimiter
        parts = text.split(delimiter)
        
        # Check if we have an odd number of parts (delimiter pairs must be complete)
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown syntax: unclosed delimiter '{delimiter}' in text '{text}'")
        
        # Process parts alternately: text, delimited, text, delimited, ...
        for i, part in enumerate(parts):
            if part:  # Only add non-empty parts
                if i % 2 == 0:
                    # Even index: regular text
                    new_nodes.append(TextNode(part, TextType.TEXT))
                else:
                    # Odd index: delimited text
                    new_nodes.append(TextNode(part, text_type))
    
    return new_nodes


def extract_markdown_images(text):
    """
    Extract markdown images from text and return a list of tuples (alt_text, url).
    
    Args:
        text: String containing markdown text
        
    Returns:
        List of tuples where each tuple contains (alt_text, url)
    """
    pattern = r"!\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    """
    Extract markdown links from text and return a list of tuples (anchor_text, url).
    
    Args:
        text: String containing markdown text
        
    Returns:
        List of tuples where each tuple contains (anchor_text, url)
    """
    pattern = r"(?<!!)\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches
