import os
from bs4 import BeautifulSoup

def inject_keyboard_navigation(file_path):
    """Parses an HTML file and injects the arrow key listeners."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Guard clause: Avoid duplicating the injection if script runs twice
        if "ArrowRight" in html_content and "nextStep" in html_content:
            print(f"Skipped (already injected): {file_path}")
            return

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Plain JavaScript to trigger your existing nextStep() and prevStep() functions
        js_code = """
        document.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowRight') {
                if (typeof nextStep === 'function') nextStep();
            } else if (event.key === 'ArrowLeft') {
                if (typeof prevStep === 'function') prevStep();
            }
        });
        """
        
        # Create a new script tag and inject the JS code
        new_script_tag = soup.new_tag("script")
        new_script_tag.string = js_code
        
        # Append to </body> if it exists, otherwise fallback to safely appending at the end
        if soup.body:
            soup.body.append(new_script_tag)
        elif soup.head:
            soup.head.append(new_script_tag)
        else:
            soup.append(new_script_tag)
            
        # Overwrite the file with modified HTML content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        print(f"Successfully updated: {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_parent_folder(parent_directory):
    """Walks through the parent directory and targets all HTML files."""
    if not os.path.exists(parent_directory):
        print(f"Error: The directory '{parent_directory}' does not exist.")
        return

    # os.walk automatically digs into all child subfolders deeply
    for root, dirs, files in os.walk(parent_directory):
        for file in files:
            if file.lower().endswith('.html') or file.lower().endswith('.htm'):
                full_path = os.path.join(root, file)
                inject_keyboard_navigation(full_path)

if __name__ == "__main__":
    # Target directory relative to this script. Use '.' for current folder.
    TARGET_DIR = "." 
    
    print(f"Starting HTML modification in: {os.path.abspath(TARGET_DIR)}")
    process_parent_folder(TARGET_DIR)
    print("Process complete!")
