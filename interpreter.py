import re

# Tokenizer to break the expression into tokens
token_specification = [
    ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
    ('ADD',      r'\+'),           # Addition
    ('SUB',      r'-'),            # Subtraction
    ('MUL',      r'\*'),           # Multiplication
    ('DIV',      r'/'),            # Division
    ('LPAREN',   r'\('),           # Left Parenthesis
    ('RPAREN',   r'\)'),           # Right Parenthesis
    ('SKIP',     r'[ \t]+'),       # Skip spaces and tabs
    ('MISMATCH', r'.'),            # Any other character
]

tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)

def tokenize(code):
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group(kind)
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'SKIP':
            continue
        yield (kind, value)

class SimpleInterpreter:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token[0]}")

    def factor(self):
        """Parse a number or a parenthesized expression."""
        token = self.current_token
        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return token[1]
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            result = self.expr()
            if self.current_token[0] == 'RPAREN':
                self.eat('RPAREN')
                return result
            else:
                raise SyntaxError("Expected ')'")
        else:
            raise SyntaxError("Expected a number or '('")

    def expr(self):
        """Handle addition and subtraction with higher precedence than multiplication/division."""
        result = self.term()
        while self.current_token and self.current_token[0] in ('MUL', 'DIV'):
            token_type = self.current_token[0]
            if token_type == 'MUL':
                self.eat('MUL')
                result *= self.term()
            elif token_type == 'DIV':
                self.eat('DIV')
                result /= self.term()
        return result

    def term(self):
        """Handle multiplication and division with lower precedence."""
        result = self.factor()
        while self.current_token and self.current_token[0] in ('ADD', 'SUB'):
            token_type = self.current_token[0]
            if token_type == 'ADD':
                self.eat('ADD')
                result += self.factor()
            elif token_type == 'SUB':
                self.eat('SUB')
                result -= self.factor()
        return result

# Example usage
code = "(3 + 4) * 2"  # Parentheses override precedence
tokens = tokenize(code)
interpreter = SimpleInterpreter(tokens)
result = interpreter.expr()

print(f"The result of the expression '{code}' with custom precedence is: {result}")
