import os
import re
from typing import List
from antlr4 import *
from cobol_parser.CobolLexer import CobolLexer
from cobol_parser.CobolParser import CobolParser
from antlr4.tree.Trees import Trees


class CobolParserManager:
    def __init__(self, cobol_code: str, copybook_paths: list = None, extensions: List[str]=['.cpy', '.cbl', '']):
        """
        Initialize the parser manager with COBOL source code and copybook paths.

        Args:
            cobol_code (str): COBOL source code to parse.
            copybook_paths (list): List of directories to search for copybooks.
        """
        self.cobol_code = cobol_code
        self.copybook_paths = copybook_paths or []
        self.extensions = extensions

    def preprocess_input(self) -> str:
        """
        Preprocess COBOL code by removing comments and resolving copybooks.

        Returns:
            str: Preprocessed COBOL source code.
        """
        preprocessed_code = self._remove_comments(self.cobol_code)
        return self._remove_comments(self._resolve_copybooks(preprocessed_code))
        # return self._resolve_copybooks(preprocessed_code)

    def _remove_comments(self, input_text: str) -> str:
        """
        Remove comment lines from COBOL code.

        Args:
            input_text (str): Input COBOL code.

        Returns:
            str: COBOL code without comments.
        """
        # Step 1: Remove lines starting with an asterisk (*), even with leading spaces
        input_text = re.sub(r'^\s*\*.*$', '', input_text, flags=re.MULTILINE)
        # Step 2: Remove blank lines (optional, to clean up the result further)
        input_text = re.sub(r'^\s*$', '', input_text, flags=re.MULTILINE)
        return input_text

    def _resolve_copybooks(self, source_code: str) -> str:
        """
        Replace COPY statements in COBOL code with actual copybook contents.

        Args:
            source_code (str): COBOL source code.

        Returns:
            str: COBOL source code with embedded copybook content.
        """
        def locate_copybook(name):
            for path in self.copybook_paths:
                for ext in self.extensions:
                    file_path = os.path.join(path, name + ext)
                    if os.path.exists(file_path):
                        return file_path
            raise FileNotFoundError(f"Copybook '{name}' not found in paths: {self.copybook_paths} with extensions: {self.extensions}")

        def replace_copy_statements(match):
            copybook_name = match.group(1).strip()
            file_path = locate_copybook(copybook_name)
            with open(file_path, 'r') as f:
                return f.read()

        copy_regex = re.compile(r'COPY\s+(\S+)\s*\.', re.IGNORECASE)
        return copy_regex.sub(replace_copy_statements, source_code)

    def generate_parse_tree(self):
        """
        Parse the COBOL source code into a parse tree.

        Returns:
            ParseTree: Root node of the parse tree.
        """
        input_stream = InputStream(self.preprocess_input())
        lexer = CobolLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = CobolParser(token_stream)

        # Enable custom error handling
        from antlr4.error.ErrorListener import ErrorListener
        class CustomErrorListener(ErrorListener):
            def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
                print(f"Syntax Error at line {line}:{column} - {msg}")

        parser.removeErrorListeners()
        parser.addErrorListener(CustomErrorListener())

        # Parse the input and return the parse tree
        return parser.compilationUnit()

    def print_parse_tree(self, tree, parser):
        """
        Print the parse tree for debugging purposes.

        Args:
            tree (ParseTree): The root node of the parse tree.
            parser (CobolParser): The parser instance with rule names.
        """
        print(Trees.toStringTree(tree, None, parser))
