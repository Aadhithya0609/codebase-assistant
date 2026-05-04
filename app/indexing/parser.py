import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from typing import List, Dict

PY_LANGUAGE = Language(tspython.language())

def get_parser(language: str) -> Parser:
    if language == 'py':
        parser = Parser(PY_LANGUAGE)
        return parser
    return None

def parse_python_file(file_path: str) -> List[Dict]:
    parser = get_parser('py')
    if not parser:
        return []

    with open(file_path, 'rb') as f:
        source = f.read()

    tree = parser.parse(source)
    chunks = []

    def extract_nodes(node):
        if node.type in ('function_definition', 'class_definition'):
            name_node = node.child_by_field_name('name')
            name = name_node.text.decode('utf-8') if name_node else 'unknown'
            chunk_text = source[node.start_byte:node.end_byte].decode('utf-8')
            chunks.append({
                'function_name': name,
                'line_number': node.start_point[0] + 1,
                'chunk_text': chunk_text,
                'type': node.type
            })
        for child in node.children:
            extract_nodes(child)

    extract_nodes(tree.root_node)
    return chunks

def parse_file(file_path: str, language: str) -> List[Dict]:
    if language == 'py':
        return parse_python_file(file_path)
    return []