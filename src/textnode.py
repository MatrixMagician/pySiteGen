from enum import Enum
import re


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


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


def split_nodes_image(old_nodes):
    """
    Split text nodes based on markdown image syntax and create new nodes.
    
    Args:
        old_nodes: List of TextNode objects to process
        
    Returns:
        List of TextNode objects with image markdown split into separate nodes
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
            
        # Extract all images from the text
        images = extract_markdown_images(text)
        
        if not images:
            # No images found, keep original node
            new_nodes.append(node)
            continue
        
        # Process each image in order
        current_text = text
        for image_alt, image_url in images:
            # Split on the full image markdown
            image_markdown = f"![{image_alt}]({image_url})"
            sections = current_text.split(image_markdown, 1)
            
            if len(sections) != 2:
                # Image not found in current text, skip
                continue
                
            # Add text before the image (if not empty)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
                
            # Add the image node
            new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_url))
            
            # Continue with text after the image
            current_text = sections[1]
        
        # Add any remaining text after the last image
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes


def split_nodes_link(old_nodes):
    """
    Split text nodes based on markdown link syntax and create new nodes.
    
    Args:
        old_nodes: List of TextNode objects to process
        
    Returns:
        List of TextNode objects with link markdown split into separate nodes
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
            
        # Extract all links from the text
        links = extract_markdown_links(text)
        
        if not links:
            # No links found, keep original node
            new_nodes.append(node)
            continue
        
        # Process each link in order
        current_text = text
        for link_text, link_url in links:
            # Split on the full link markdown
            link_markdown = f"[{link_text}]({link_url})"
            sections = current_text.split(link_markdown, 1)
            
            if len(sections) != 2:
                # Link not found in current text, skip
                continue
                
            # Add text before the link (if not empty)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
                
            # Add the link node
            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            
            # Continue with text after the link
            current_text = sections[1]
        
        # Add any remaining text after the last link
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes


def text_to_textnodes(text):
    """
    Convert markdown text into a list of TextNode objects.
    
    This function processes markdown text and splits it into nodes based on:
    - Bold text (**text**)
    - Italic text (*text*)
    - Code blocks (`code`)
    - Images (![alt](url))
    - Links ([text](url))
    
    Args:
        text: String containing markdown text
        
    Returns:
        List of TextNode objects representing the parsed markdown
    """
    # Start with a single TEXT node containing the entire text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply all splitting functions in sequence
    # Order matters: images and links first, then delimiters
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes


def markdown_to_blocks(markdown):
    """
    Split markdown text into block-level elements.
    
    Blocks are separated by double newlines (\n\n) and represent distinct
    structural elements like headings, paragraphs, lists, etc.
    
    Args:
        markdown: String containing markdown text
        
    Returns:
        List of block strings with leading/trailing whitespace stripped
    """
    # Split on double newlines to get potential blocks
    blocks = markdown.split('\n\n')
    
    # Strip whitespace from each block and filter out empty blocks
    result = []
    for block in blocks:
        stripped_block = block.strip()
        if stripped_block:  # Only add non-empty blocks
            result.append(stripped_block)
    
    return result


def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    
    Args:
        block: String representing a single markdown block (whitespace already stripped)
        
    Returns:
        BlockType enum value representing the type of block
    """
    lines = block.split('\n')
    
    # Check for heading (1-6 # characters, followed by space)
    if block.startswith('#'):
        # Count leading # characters
        hash_count = 0
        for char in block:
            if char == '#':
                hash_count += 1
            else:
                break
        
        # Must be 1-6 # characters followed by a space
        if 1 <= hash_count <= 6 and hash_count < len(block) and block[hash_count] == ' ':
            return BlockType.HEADING
    
    # Check for code block (starts and ends with ```)
    if block.startswith('```') and block.endswith('```'):
        return BlockType.CODE
    
    # Check for quote block (every line starts with >)
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE
    
    # Check for unordered list (every line starts with - followed by space)
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list (every line starts with number. followed by space, incrementing from 1)
    if all(line and len(line) >= 3 for line in lines):  # Minimum "1. " is 3 characters
        expected_num = 1
        is_ordered_list = True
        
        for line in lines:
            # Check if line starts with expected number followed by '. '
            expected_start = f"{expected_num}. "
            if not line.startswith(expected_start):
                is_ordered_list = False
                break
            expected_num += 1
        
        if is_ordered_list:
            return BlockType.ORDERED_LIST
    
    # Default to paragraph if no other conditions are met
    return BlockType.PARAGRAPH


def text_to_children(text):
    """
    Convert text containing inline markdown to a list of HTMLNode children.
    
    Args:
        text: String containing inline markdown
        
    Returns:
        List of HTMLNode objects representing the parsed inline markdown
    """
    from htmlnode import text_node_to_html_node
    
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def markdown_to_html_node(markdown):
    """
    Convert a full markdown document into a single parent HTMLNode.
    
    Args:
        markdown: String containing markdown text
        
    Returns:
        HTMLNode representing the markdown document as a div containing all blocks
    """
    from htmlnode import LeafNode, ParentNode
    
    blocks = markdown_to_blocks(markdown)
    block_nodes = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            # Replace newlines with spaces for paragraphs
            paragraph_text = block.replace('\n', ' ')
            children = text_to_children(paragraph_text)
            block_nodes.append(ParentNode("p", children))
            
        elif block_type == BlockType.HEADING:
            # Count leading # characters to determine heading level
            hash_count = 0
            for char in block:
                if char == '#':
                    hash_count += 1
                else:
                    break
            
            # Extract text after "# " (hash_count + 1 characters)
            heading_text = block[hash_count + 1:]
            children = text_to_children(heading_text)
            block_nodes.append(ParentNode(f"h{hash_count}", children))
            
        elif block_type == BlockType.CODE:
            # Remove surrounding ``` and create code block
            code_text = block[3:-3]  # Remove first and last 3 characters (```)
            # Strip leading newline only
            code_text = code_text.lstrip('\n')
            code_node = LeafNode("code", code_text)
            block_nodes.append(ParentNode("pre", [code_node]))
            
        elif block_type == BlockType.QUOTE:
            # Remove > from each line and join with newlines
            lines = block.split('\n')
            quote_lines = []
            for line in lines:
                # Remove the '>' character and any following space
                if line.startswith('> '):
                    quote_lines.append(line[2:])  # Remove '> '
                else:
                    quote_lines.append(line[1:])  # Remove just '>'
            quote_text = '\n'.join(quote_lines)
            children = text_to_children(quote_text)
            block_nodes.append(ParentNode("blockquote", children))
            
        elif block_type == BlockType.UNORDERED_LIST:
            # Split into list items and create ul with li elements
            lines = block.split('\n')
            list_items = []
            for line in lines:
                # Remove "- " from the beginning
                item_text = line[2:]
                item_children = text_to_children(item_text)
                list_items.append(ParentNode("li", item_children))
            block_nodes.append(ParentNode("ul", list_items))
            
        elif block_type == BlockType.ORDERED_LIST:
            # Split into list items and create ol with li elements
            lines = block.split('\n')
            list_items = []
            for line in lines:
                # Find the ". " pattern and remove everything before it
                dot_index = line.find(". ")
                item_text = line[dot_index + 2:]
                item_children = text_to_children(item_text)
                list_items.append(ParentNode("li", item_children))
            block_nodes.append(ParentNode("ol", list_items))
    
    # Return all blocks wrapped in a div
    return ParentNode("div", block_nodes)
