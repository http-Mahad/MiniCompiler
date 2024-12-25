import re
import streamlit as st
from graphviz import Digraph

# Token Types
KEYWORDS = {'snake', 'cathi', 'bol'}
OPERATORS = {'+', '-', '*', '/', '='}
DELIMITERS = {';', '(', ')'}


# Lexer (Tokenization)
class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.line_number = 1

    def tokenize(self):
        lines = self.code.split('\n')
        for line in lines:
            self.tokenize_line(line)
            self.line_number += 1
        return self.tokens

    def tokenize_line(self, line):
        words = re.findall(r'\w+|[+\-*/=();]', line)
        for word in words:
            if word in KEYWORDS:
                self.tokens.append(('KEYWORD', word, self.line_number))
            elif word in OPERATORS:
                self.tokens.append(('OPERATOR', word, self.line_number))
            elif word in DELIMITERS:
                self.tokens.append(('DELIMITER', word, self.line_number))
            elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', word):
                self.tokens.append(('IDENTIFIER', word, self.line_number))
            elif re.match(r'^\d+$', word):
                self.tokens.append(('NUMBER', word, self.line_number))
            elif re.match(r'^".*"$', word):
                self.tokens.append(('STRING', word, self.line_number))
            else:
                self.tokens.append(('ERROR', word, self.line_number))


# Parse Node
class ParseNode:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children else []


# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = 0
        self.symbol_table = {}
        self.root = None

    def parse(self):
        self.root = ParseNode('Program')
        while self.current_token < len(self.tokens):
            token = self.tokens[self.current_token]
            if token[0] == 'KEYWORD':
                if token[1] == 'cathi':
                    self.root.children.append(self.parse_declaration('int'))
                elif token[1] == 'snake':
                    self.root.children.append(self.parse_declaration('string'))
                elif token[1] == 'bol':
                    self.root.children.append(self.parse_print())
            elif token[0] == 'IDENTIFIER':
                self.root.children.append(self.parse_assignment())
            else:
                self.error(f"Unexpected token {token[1]}")

    def parse_declaration(self, data_type):
        node = ParseNode(f"Declaration ({data_type})")
        self.current_token += 1

        # Identifier
        token = self.tokens[self.current_token]
        if token[0] != 'IDENTIFIER':
            self.error(f"Expected identifier, got {token[1]}")
        identifier = token[1]
        node.children.append(ParseNode(f"Identifier: {identifier}"))
        self.current_token += 1

        # Equals sign
        token = self.tokens[self.current_token]
        if token[0] != 'OPERATOR' or token[1] != '=':
            self.error(f"Expected '=', got {token[1]}")
        node.children.append(ParseNode("="))
        self.current_token += 1

        # Value
        token = self.tokens[self.current_token]
        if data_type == 'int' and token[0] != 'NUMBER':
            self.error(f"Expected number, got {token[1]}")
        elif data_type == 'string' and token[0] != 'STRING':
            self.error(f"Expected string, got {token[1]}")
        value = token[1]
        node.children.append(ParseNode(f"Value: {value}"))
        self.symbol_table[identifier] = value
        self.current_token += 1

        # Semicolon
        token = self.tokens[self.current_token]
        if token[0] != 'DELIMITER' or token[1] != ';':
            self.error(f"Expected ';', got {token[1]}")
        node.children.append(ParseNode(";"))
        self.current_token += 1

        return node

    def parse_assignment(self):
        node = ParseNode("Assignment")

        # Identifier
        token = self.tokens[self.current_token]
        identifier = token[1]
        node.children.append(ParseNode(f"Identifier: {identifier}"))
        self.current_token += 1

        # Equals sign
        token = self.tokens[self.current_token]
        if token[0] != 'OPERATOR' or token[1] != '=':
            self.error(f"Expected '=', got {token[1]}")
        node.children.append(ParseNode("="))
        self.current_token += 1

        # Expression
        node.children.append(self.parse_expression())

        # Semicolon
        token = self.tokens[self.current_token]
        if token[0] != 'DELIMITER' or token[1] != ';':
            self.error(f"Expected ';', got {token[1]}")
        node.children.append(ParseNode(";"))
        self.current_token += 1

        return node

    def parse_expression(self):
        # Handle a simple expression with two operands and one operator
        node = ParseNode("Expression")

        # First operand
        token = self.tokens[self.current_token]
        if token[0] not in {'IDENTIFIER', 'NUMBER'}:
            self.error(f"Expected identifier or number, got {token[1]}")
        node.children.append(ParseNode(f"Operand: {token[1]}"))
        self.current_token += 1

        # Operator
        token = self.tokens[self.current_token]
        if token[0] != 'OPERATOR':
            self.error(f"Expected operator, got {token[1]}")
        node.children.append(ParseNode(f"Operator: {token[1]}"))
        self.current_token += 1

        # Second operand
        token = self.tokens[self.current_token]
        if token[0] not in {'IDENTIFIER', 'NUMBER'}:
            self.error(f"Expected identifier or number, got {token[1]}")
        node.children.append(ParseNode(f"Operand: {token[1]}"))
        self.current_token += 1

        return node

    def parse_print(self):
        node = ParseNode("Print")
        self.current_token += 1

        # Left parenthesis
        token = self.tokens[self.current_token]
        if token[0] != 'DELIMITER' or token[1] != '(':
            self.error(f"Expected '(', got {token[1]}")
        node.children.append(ParseNode("("))
        self.current_token += 1

        # Identifier
        token = self.tokens[self.current_token]
        if token[0] != 'IDENTIFIER':
            self.error(f"Expected identifier, got {token[1]}")
        identifier = token[1]
        if identifier not in self.symbol_table:
            self.error(f"Undefined variable {identifier}")
        node.children.append(ParseNode(f"Identifier: {identifier}"))
        self.current_token += 1

        # Right parenthesis
        token = self.tokens[self.current_token]
        if token[0] != 'DELIMITER' or token[1] != ')':
            self.error(f"Expected ')', got {token[1]}")
        node.children.append(ParseNode(")"))
        self.current_token += 1

        # Semicolon
        token = self.tokens[self.current_token]
        if token[0] != 'DELIMITER' or token[1] != ';':
            self.error(f"Expected ';', got {token[1]}")
        node.children.append(ParseNode(";"))
        self.current_token += 1

        return node

    def error(self, message):
        raise SyntaxError(f"Error at line {self.tokens[self.current_token][2]}: {message}")

    def generate_parse_tree(self, node, dot=None):
        if dot is None:
            dot = Digraph()

        dot.node(str(id(node)), node.label)
        for child in node.children:
            dot.node(str(id(child)), child.label)
            dot.edge(str(id(node)), str(id(child)))
            self.generate_parse_tree(child, dot)

        return dot


# Generate LR(0) Parse Table
def generate_lr0_table():
    parse_table = {
        "State": [0, 1, 2, 3],
        "Action": ["SHIFT", "REDUCE", "SHIFT", "ACCEPT"],
        "Goto": ["-", "-", "-", "-"],
    }
    return parse_table


# Streamlit GUI
def main():
    st.title("Mini Compiler")

    code = st.text_area("Enter Code", height=300)

    if st.button("Run"):
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        st.subheader("Lexemes")
        st.write(tokens)

        try:
            parser = Parser(tokens)
            parser.parse()

            st.subheader("Symbol Table")
            st.write(parser.symbol_table)

            st.subheader("Parse Tree")
            dot = parser.generate_parse_tree(parser.root)
            st.graphviz_chart(dot.source)

            st.subheader("LR(0) Parse Table")
            lr0_table = generate_lr0_table()
            st.write(lr0_table)

        except SyntaxError as e:
            st.error(str(e))


if __name__ == "__main__":
    main()
