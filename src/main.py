import os
import shutil
from textnode import TextNode, TextType, markdown_to_html_node, extract_title


def copy_static_to_public(src_dir, dest_dir):
    """
    Recursively copy all contents from source directory to destination directory.
    First deletes all contents of the destination directory to ensure a clean copy.
    
    Args:
        src_dir: Source directory path
        dest_dir: Destination directory path
    """
    # Delete destination directory if it exists
    if os.path.exists(dest_dir):
        print(f"Deleting existing directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create destination directory
    print(f"Creating directory: {dest_dir}")
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy all contents recursively
    _copy_directory_contents(src_dir, dest_dir)


def _copy_directory_contents(src_dir, dest_dir):
    """
    Helper function to recursively copy directory contents.
    
    Args:
        src_dir: Source directory path
        dest_dir: Destination directory path
    """
    if not os.path.exists(src_dir):
        print(f"Source directory does not exist: {src_dir}")
        return
    
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.isdir(src_path):
            # Create directory and recursively copy its contents
            print(f"Creating directory: {dest_path}")
            os.makedirs(dest_path, exist_ok=True)
            _copy_directory_contents(src_path, dest_path)
        else:
            # Copy file
            print(f"Copying file: {src_path} -> {dest_path}")
            shutil.copy2(src_path, dest_path)


def generate_page(from_path, template_path, dest_path):
    """
    Generate an HTML page from a markdown file using a template.
    
    Args:
        from_path: Path to the markdown file to convert
        template_path: Path to the HTML template file
        dest_path: Path where the generated HTML will be written
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown file
    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract the title
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace('{{ Title }}', title)
    final_html = final_html.replace('{{ Content }}', html_content)
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    # Write the final HTML to the destination
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    """
    Recursively generate HTML pages from all markdown files in a content directory.
    
    Args:
        dir_path_content: Path to the content directory containing markdown files
        template_path: Path to the HTML template file
        dest_dir_path: Path to the destination directory for generated HTML files
    """
    for item in os.listdir(dir_path_content):
        src_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item)
        
        if os.path.isdir(src_path):
            # Create corresponding directory in destination
            os.makedirs(dest_path, exist_ok=True)
            # Recursively process subdirectory
            generate_pages_recursive(src_path, template_path, dest_path)
        elif item.endswith('.md'):
            # Convert .md extension to .html
            html_filename = item[:-3] + '.html'
            html_dest_path = os.path.join(dest_dir_path, html_filename)
            # Generate the HTML page
            generate_page(src_path, template_path, html_dest_path)


def main():
    # Get the root directory (parent of src)
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Define paths
    static_dir = os.path.join(root_dir, "static")
    public_dir = os.path.join(root_dir, "public")
    content_dir = os.path.join(root_dir, "content")
    template_path = os.path.join(root_dir, "template.html")
    
    # Delete anything in the public directory
    if os.path.exists(public_dir):
        print(f"Deleting existing public directory: {public_dir}")
        shutil.rmtree(public_dir)
    
    # Copy static files to public directory
    print("Starting static file copy...")
    copy_static_to_public(static_dir, public_dir)
    print("Static file copy completed!")
    
    # Generate all pages recursively
    print("Generating all pages...")
    generate_pages_recursive(content_dir, template_path, public_dir)
    print("Page generation completed!")


if __name__ == "__main__":
    main()
