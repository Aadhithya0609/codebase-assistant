import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser
from typing import List, Dict

PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())

def get_parser(language: str):
    parser = Parser()
    if language == "py":
        parser.language = PY_LANGUAGE
    elif language in ("js", "ts"):
        parser.language = JS_LANGUAGE
    else:
        return None
    return parser

def parse_with_ast(file_path: str, language: str) -> List[Dict]:
    parser = get_parser(language)
    if not parser:
        return []
    try:
        with open(file_path, "rb") as f:
            source = f.read()
    except Exception:
        return []

    tree = parser.parse(source)
    chunks = []

    py_types = ("function_definition", "class_definition")
    js_types = (
        "function_declaration",
        "class_declaration",
        "method_definition",
        "arrow_function",
        "function_expression",
    )

    target_types = py_types if language == "py" else js_types

    def extract_nodes(node):
        if node.type in target_types:
            name_node = node.child_by_field_name("name")
            if not name_node and node.parent:
                if node.parent.type == "variable_declarator":
                    name_node = node.parent.child_by_field_name("name")
            name = name_node.text.decode("utf-8") if name_node else "anonymous"
            chunk_text = source[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
            if len(chunk_text.strip()) > 20:
                chunks.append({
                    "function_name": name,
                    "line_number": node.start_point[0] + 1,
                    "chunk_text": chunk_text,
                    "type": node.type
                })
        for child in node.children:
            extract_nodes(child)

    extract_nodes(tree.root_node)
    return chunks

def parse_sql_file(file_path: str) -> List[Dict]:
    try:
        with open(file_path, "r", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    chunks = []
    current = []
    start_line = 1

    for i, line in enumerate(lines):
        upper = line.strip().upper()
        if upper.startswith(("CREATE ", "ALTER ", "INSERT ", "SELECT ", "DROP ")):
            if current:
                chunks.append({
                    "function_name": current[0].strip()[:60],
                    "line_number": start_line,
                    "chunk_text": "".join(current),
                    "type": "sql_statement"
                })
            current = [line]
            start_line = i + 1
        else:
            current.append(line)

    if current:
        chunks.append({
            "function_name": current[0].strip()[:60],
            "line_number": start_line,
            "chunk_text": "".join(current),
            "type": "sql_statement"
        })

    return chunks

def parse_file(file_path: str, language: str) -> List[Dict]:
    if language == "sql":
        return parse_sql_file(file_path)
    return parse_with_ast(file_path, language)