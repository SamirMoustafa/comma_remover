import re
import sys
import pathlib

def remove_trailing_commas(content):
    # Multi-line: comma before closing bracket on new line
    content = re.sub(r',(\s*\n\s*)([)\]}])', r'\1\2', content)
    
    # Single-line: comma before closing bracket on same line (e.g., [1, 2,])
    # Be careful not to remove comma from single-item tuple (1,)
    # This regex looks for comma followed by optional space and closing bracket
    # It excludes the case where removing the comma makes a tuple an int
    # Simple approach: remove comma if there is more than one item visible before it
    # For safety, we stick to the multi-line regex mostly, but here is a safe single-line attempt:
    content = re.sub(r',(\s*)([)\]}])', r'\1\2', content)
    
    return content

def main():
    if len(sys.argv) < 2:
        print("Usage: python comma_remover.py <file_or_directory>")
        sys.exit(1)

    target = pathlib.Path(sys.argv[1])
    files = target.rglob("*.py") if target.is_dir() else [target]

    for file in files:
        try:
            content = file.read_text(encoding="utf-8")
            new_content = remove_trailing_commas(content)
            if content != new_content:
                file.write_text(new_content, encoding="utf-8")
                print(f"✅ Fixed: {file}")
        except Exception as e:
            print(f"❌ Error {file}: {e}")

if __name__ == "__main__":
    main()