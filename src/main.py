import shutil
import sys
import logging
from pathlib import Path
from typing import Optional
from textnode import TextNode, TextType, markdown_to_html_node, extract_title

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('site_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def validate_path(path: str, must_exist: bool = True) -> Path:
    """
    Validate and normalize a file path, preventing path traversal attacks.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If path is invalid or contains path traversal attempts
        FileNotFoundError: If path doesn't exist and must_exist is True
    """
    if not path or not isinstance(path, str):
        raise ValueError("Path must be a non-empty string")
    
    # Convert to Path object and resolve
    path_obj = Path(path).resolve()
    
    # Check for path traversal attempts
    if '..' in str(path_obj) or str(path_obj).startswith('/'):
        # Allow absolute paths but log them
        logger.warning(f"Absolute path used: {path_obj}")
    
    # Check if path exists when required
    if must_exist and not path_obj.exists():
        raise FileNotFoundError(f"Path does not exist: {path_obj}")
    
    return path_obj


def copy_static_to_public(src_dir: str, dest_dir: str) -> None:
    """
    Recursively copy all contents from source directory to destination directory.
    First deletes all contents of the destination directory to ensure a clean copy.
    
    Args:
        src_dir: Source directory path
        dest_dir: Destination directory path
        
    Raises:
        ValueError: If paths are invalid
        OSError: If file operations fail
    """
    try:
        src_path = validate_path(src_dir, must_exist=True)
        dest_path = validate_path(dest_dir, must_exist=False)
        
        # Delete destination directory if it exists
        if dest_path.exists():
            logger.info(f"Deleting existing directory: {dest_path}")
            shutil.rmtree(dest_path)
        
        # Create destination directory
        logger.info(f"Creating directory: {dest_path}")
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all contents recursively
        _copy_directory_contents(src_path, dest_path)
        
    except Exception as e:
        logger.error(f"Error copying static files: {e}")
        raise


def _copy_directory_contents(src_dir: Path, dest_dir: Path) -> None:
    """
    Helper function to recursively copy directory contents.
    
    Args:
        src_dir: Source directory Path object
        dest_dir: Destination directory Path object
    """
    if not src_dir.exists():
        logger.warning(f"Source directory does not exist: {src_dir}")
        return
    
    try:
        for item in src_dir.iterdir():
            dest_path = dest_dir / item.name
            
            if item.is_dir():
                # Create directory and recursively copy its contents
                logger.info(f"Creating directory: {dest_path}")
                dest_path.mkdir(parents=True, exist_ok=True)
                _copy_directory_contents(item, dest_path)
            else:
                # Copy file with validation
                logger.info(f"Copying file: {item} -> {dest_path}")
                shutil.copy2(item, dest_path)
                
    except Exception as e:
        logger.error(f"Error copying directory contents: {e}")
        raise


def sanitize_basepath(basepath: str) -> str:
    """
    Sanitize and validate basepath.
    
    Args:
        basepath: Base path string
        
    Returns:
        Sanitized basepath
        
    Raises:
        ValueError: If basepath is invalid
    """
    if not basepath or not isinstance(basepath, str):
        raise ValueError("Basepath must be a non-empty string")
    
    # Ensure basepath starts and ends with /
    if not basepath.startswith('/'):
        basepath = '/' + basepath
    if not basepath.endswith('/') and basepath != '/':
        basepath = basepath + '/'
    
    # Remove any dangerous characters
    basepath = basepath.replace('..', '').replace('//', '/')
    
    return basepath


# Template cache for performance
_template_cache: Optional[str] = None


def get_template_content(template_path: str) -> str:
    """
    Get template content with caching for performance.
    
    Args:
        template_path: Path to the HTML template file
        
    Returns:
        Template content as string
    """
    global _template_cache
    
    if _template_cache is None:
        template_path_obj = validate_path(template_path, must_exist=True)
        try:
            with open(template_path_obj, 'r', encoding='utf-8') as f:
                _template_cache = f.read()
        except UnicodeDecodeError:
            logger.error(f"Invalid UTF-8 encoding in template: {template_path_obj}")
            raise
    
    return _template_cache


def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str) -> None:
    """
    Generate an HTML page from a markdown file using a template.
    
    Args:
        from_path: Path to the markdown file to convert
        template_path: Path to the HTML template file
        dest_path: Path where the generated HTML will be written
        basepath: Base path for the site (e.g., "/" or "/pySiteGen/")
        
    Raises:
        ValueError: If paths are invalid
        FileNotFoundError: If input files don't exist
        OSError: If file operations fail
    """
    try:
        # Validate paths
        from_path_obj = validate_path(from_path, must_exist=True)
        dest_path_obj = validate_path(dest_path, must_exist=False)
        
        # Sanitize basepath
        clean_basepath = sanitize_basepath(basepath)
        
        logger.info(f"Generating page from {from_path_obj} to {dest_path_obj}")
        
        # Read markdown file with error handling
        try:
            with open(from_path_obj, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except UnicodeDecodeError:
            logger.error(f"Invalid UTF-8 encoding in file: {from_path_obj}")
            raise
        
        # Get cached template content
        template_content = get_template_content(template_path)
        
        # Convert markdown to HTML
        html_node = markdown_to_html_node(markdown_content)
        html_content = html_node.to_html()
        
        # Extract the title
        title = extract_title(markdown_content)
        
        # Sanitize title to prevent XSS
        title = title.replace('<', '&lt;').replace('>', '&gt;')
        
        # Replace placeholders in template
        final_html = template_content.replace('{{ Title }}', title)
        final_html = final_html.replace('{{ Content }}', html_content)
        
        # Replace href and src paths with basepath
        final_html = final_html.replace('href="/', f'href="{clean_basepath}')
        final_html = final_html.replace('src="/', f'src="{clean_basepath}')
        
        # Create destination directory if it doesn't exist
        dest_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the final HTML to the destination
        with open(dest_path_obj, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
    except Exception as e:
        logger.error(f"Error generating page: {e}")
        raise


def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str) -> None:
    """
    Recursively generate HTML pages from all markdown files in a content directory.
    
    Args:
        dir_path_content: Path to the content directory containing markdown files
        template_path: Path to the HTML template file
        dest_dir_path: Path to the destination directory for generated HTML files
        basepath: Base path for the site (e.g., "/" or "/pySiteGen/")
        
    Raises:
        ValueError: If paths are invalid
        OSError: If file operations fail
    """
    try:
        content_path = validate_path(dir_path_content, must_exist=True)
        template_path_obj = validate_path(template_path, must_exist=True)
        dest_path = validate_path(dest_dir_path, must_exist=False)
        
        # Ensure destination directory exists
        dest_path.mkdir(parents=True, exist_ok=True)
        
        for item in content_path.iterdir():
            item_dest_path = dest_path / item.name
            
            if item.is_dir():
                # Create corresponding directory in destination
                item_dest_path.mkdir(parents=True, exist_ok=True)
                # Recursively process subdirectory
                generate_pages_recursive(str(item), str(template_path_obj), str(item_dest_path), basepath)
            elif item.suffix == '.md':
                # Convert .md extension to .html
                html_filename = item.stem + '.html'
                html_dest_path = dest_path / html_filename
                # Generate the HTML page
                generate_page(str(item), str(template_path_obj), str(html_dest_path), basepath)
                
    except Exception as e:
        logger.error(f"Error generating pages recursively: {e}")
        raise


def main() -> None:
    """
    Main function to build the static site.
    
    Raises:
        SystemExit: If critical errors occur
    """
    try:
        # Get basepath from command line argument, default to "/"
        basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
        
        # Validate basepath
        try:
            basepath = sanitize_basepath(basepath)
        except ValueError as e:
            logger.error(f"Invalid basepath: {e}")
            sys.exit(1)
        
        # Get the root directory (parent of src)
        root_dir = Path(__file__).parent.parent
        
        # Define paths
        static_dir = root_dir / "static"
        public_dir = root_dir / "docs"
        content_dir = root_dir / "content"
        template_path = root_dir / "template.html"
        
        # Validate required directories exist
        for path, name in [(static_dir, "static"), (content_dir, "content"), (template_path, "template.html")]:
            if not path.exists():
                logger.error(f"Required {name} not found: {path}")
                sys.exit(1)
        
        # Delete anything in the public directory
        if public_dir.exists():
            logger.info(f"Deleting existing public directory: {public_dir}")
            shutil.rmtree(public_dir)
        
        # Copy static files to public directory
        logger.info("Starting static file copy...")
        copy_static_to_public(str(static_dir), str(public_dir))
        logger.info("Static file copy completed!")
        
        # Generate all pages recursively
        logger.info("Generating all pages...")
        generate_pages_recursive(str(content_dir), str(template_path), str(public_dir), basepath)
        logger.info("Page generation completed!")
        
    except KeyboardInterrupt:
        logger.info("Site generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error during site generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
