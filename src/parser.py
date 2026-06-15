
"""
Parses a MERN stack codebase 

Pipeline: scan .js files → classify → split into logical blocks → wrap as CustomDocuments
"""

import re
from pathlib import Path
from src.schemas import CustomDocument



# Block-boundary patterns
# Each regex matches the first line of a distinct logical code block.

BLOCK_PATTERNS: dict[str, re.Pattern] = {
    # Express
    "route_handler":    re.compile(r'router\.(get|post|put|patch|delete|use)\s*\('),
    "app_route":        re.compile(r'app\.(get|post|put|patch|delete|use)\s*\('),

    # Functions
    "async_arrow":      re.compile(r'(const|let|var)\s+\w+\s*=\s*async\s*[\(\[]'),
    "async_function":   re.compile(r'async\s+function\s+\w+'),
    "regular_function": re.compile(r'function\s+\w+\s*\('),
    "arrow_function":   re.compile(r'(const|let|var)\s+\w+\s*=\s*\(.*\)\s*=>'),

    # Classes
    "class_def":        re.compile(r'class\s+[A-Z]\w+'),

    # Mongoose
    "schema_def":       re.compile(r'(const|let|var)\s+\w+\s*=\s*new\s+(mongoose\.)?Schema\s*\('),
    "model_create":     re.compile(r'mongoose\.model\s*\('),
    "schema_hook":      re.compile(r'\w+Schema\.(pre|post)\s*\('),
    "schema_method":    re.compile(r'\w+Schema\.(methods|statics)\.\w+\s*='),
    "schema_virtual":   re.compile(r'\w+Schema\.virtual\s*\('),

    # Exports
    "module_export":    re.compile(r'module\.exports\s*='),
    "named_export":     re.compile(r'export\s+(const|function|class|default)'),

    # React
    "react_component":  re.compile(r'(function|const)\s+[A-Z]\w+\s*[\(=]'),
    "custom_hook":      re.compile(r'(function|const)\s+use[A-Z]\w+\s*[\(=]'),
    "context":          re.compile(r'createContext|useContext'),

    # Middleware & async handlers
    "middleware":       re.compile(r'(const|let|var)\s+\w+\s*=\s*(async\s*)?\(\s*req\s*,\s*res\s*(,\s*next)?\s*\)'),
    "async_handler":    re.compile(r'asyncHandler\s*\('),
}



# File-level classification 

FILE_TYPE_PATTERNS: dict[str, re.Pattern] = {
    "model":      re.compile(r'mongoose\.model\s*\('),
    "controller": re.compile(r'asyncHandler|module\.exports\s*=\s*\{'),
    "route":      re.compile(r'express\.Router\(\)|router\.(get|post|put|patch|delete)'),
    "middleware": re.compile(r'\(\s*req\s*,\s*res\s*,\s*next\s*\)'),
    "component":  re.compile(r'from\s+[\'"]react[\'"]'),
    "hook":       re.compile(r'(function|const)\s+use[A-Z]'),
    "config":     re.compile(r'dotenv|mongoose\.connect|cloudinary\.config'),
    "utility":    re.compile(r'module\.exports|export\s+(const|function|default)'),
}

def _classify_file(content: str) -> str:
    for file_type, pattern in FILE_TYPE_PATTERNS.items():
        if pattern.search(content):
            return file_type
    return "general_source"



# Metadata helpers

def _is_comment_or_blank(line: str) -> bool:
    stripped = line.strip()
    return stripped == "" or stripped.startswith(("//", "/*", "*/", "*"))


def _extract_imports(lines: list[str]) -> list[str]:
    import_pattern = re.compile(
        r'^\s*(import |const .+ = require)'
    )

    imports = []
    for line in lines:
        if import_pattern.match(line):
            imports.append(line.strip())

    return imports


def _extract_function_name(content: str) -> str | None:
    function_pattern = re.compile(
        r'(const|function)\s+(\w+)\s*=?\s*(async\s*)?\('
    )

    match = function_pattern.search(content)
    if match is not None:
        function_name = match.group(2)
        return function_name
    
    return None


def _extract_http_method(content: str) -> str | None:
    route_pattern = re.compile(
        r'router\.(get|post|put|patch|delete)'
    )

    match = route_pattern.search(content)
    if match is not None:
        http_method = match.group(1)
        return http_method.upper()

    return None


def _extract_route_path(content: str) -> str | None:
    route_pattern = re.compile(
        r'router\.\w+\s*\(\s*["\']([^"\']+)["\']'
    )

    match = route_pattern.search(content)
    if match:
        route_path = match.group(1)
        return route_path
    
    return None


def _extract_model_name(content: str) -> str | None:
    model_pattern = re.compile(
        r'mongoose\.model\s*\(\s*["\'](\w+)["\']'
    )

    match = model_pattern.search(content)
    if match is not None:
        model_name = match.group(1)
        return model_name
    
    return None


def _build_block(lines: list[str], chunk_type: str) -> dict:
    return {
        "content":    "\n".join(lines).strip(),
        "chunk_type": chunk_type,
    }

# Main parser

class codebaseParser: 
    """
    Scans a MERN codebase and splits every .js file into semantic chunks
    wrapped as CustomDocuments for embedding into a vector database.
    """

    def __init__(self, directory_path: str):
        self.directory_path = Path(directory_path)
        self.ignore_dirs = {"node_modules", ".git", "build", "dist", ".venv", ".env"}

    def _split_into_blocks(self, content: str) -> list[dict]:
        """
        Splits a JS file into logical blocks 
        """
        lines = content.splitlines()
        blocks: list[dict] = []

        current_lines: list[str] = []
        current_type = 'unknown'
        brace_depth = 0

        import_lines = _extract_imports(lines)
        if import_lines:
            blocks.append(_build_block(import_lines, "imports"))
        
        for line in lines:
            brace_depth += line.count("{") - line.count("}")
        
            matched_type = None

            #seatching for pattern
            for name,pattern in BLOCK_PATTERNS.items():
                if pattern.search(line):
                    matched_type = name
                    break
            
            if matched_type and current_lines and brace_depth <= 0:
                #Peel trailing comments off the current block and carry them into the next one

                trailing_comments: list[str] = []
                #current_lines[-1] this gives last item from currlines -1 means last in python
                while current_lines and _is_comment_or_blank(current_lines[-1]):
                    trailing_comments.insert(0, current_lines.pop())#yes python has pop function on a list

                if len("\n".join(current_lines).strip()) > 40:
                    blocks.append(_build_block(current_lines, current_type))
                
                current_lines = trailing_comments
                current_type = matched_type

            current_lines.append(line)
        
        if len("\n".join(current_lines).strip()) > 40:
            blocks.append(_build_block(current_lines, current_type))

        return blocks
    
    def load_documents(self) -> list[CustomDocument]:
        """Scans the codebase and returns all chunks as CustomDocuments."""
        documents: list[CustomDocument] = []

        for file_path in self.directory_path.rglob("*.js"):
            should_ignore = False

            for part in file_path.parts:
                if part in self.ignore_dirs:
                    should_ignore = True
                    break

            if should_ignore:
                continue

            try: 
                raw_code = file_path.read_text(encoding="utf-8")
                file_type = _classify_file(raw_code)
                blocks  = self._split_into_blocks(raw_code)

                for block in blocks:
                    content = block["content"]

                    raw_metadata = {
                        "file_path" : str(file_path),
                        "file_name" : file_path.name,#pathlib has a function to return file name
                        "file_type": file_type,
                        "chunk_type": block["chunk_type"],
                        "function_name": _extract_function_name(content),
                        "http_method": _extract_http_method(content),
                        "route_path": _extract_route_path(content),
                        "model_name": _extract_model_name(content)
                    }

                    clean_metadata = {}

                    for key, value in raw_metadata.items():
                        if value is not None:
                            clean_metadata[key] = value
                    
                    doc = CustomDocument(
                        content = content,
                        metadata = clean_metadata
                    )
                    documents.append(doc)
            
            except Exception as e:
                print(f"[CodebaseParser] Skipping '{file_path.name}': {e}")
        
        return documents