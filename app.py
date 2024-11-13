from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Define token specifications for each element in expressions
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

# Combine token specifications into a single regex pattern
tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)

# Tokenizer function to break the code into tokens
def tokenize(code):
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group(kind)
        if kind == 'NUMBER':
            # Convert numeric strings to actual numbers
            value = float(value) if '.' in value else int(value)
        elif kind == 'SKIP':
            # Skip whitespace
            continue
        yield (kind, value)

# Interpreter class to parse and evaluate expressions
class SimpleInterpreter:
    def __init__(self, tokens):
        # Initialize with token list and set the starting position
        self.tokens = list(tokens)
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    # Consume a token of a specified type
    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None  # End of tokens
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token[0]}")

    # Parse a number or a parenthesized expression
    def factor(self):
        token = self.current_token
        if token[0] == 'NUMBER':
            # Return the number value if the token is a number
            self.eat('NUMBER')
            return token[1]
        elif token[0] == 'LPAREN':
            # If we encounter '(', evaluate the expression within parentheses
            self.eat('LPAREN')
            result = self.expr()  # Evaluate inner expression
            if self.current_token[0] == 'RPAREN':
                self.eat('RPAREN')
                return result
            else:
                raise SyntaxError("Expected ')'")
        else:
            raise SyntaxError("Expected a number or '('")

    # Handle multiplication and division (higher precedence)
    def expr(self):
        result = self.term()
        # Continue to evaluate as long as there are '*' or '/' tokens
        while self.current_token and self.current_token[0] in ('MUL', 'DIV'):
            token_type = self.current_token[0]
            if token_type == 'MUL':
                self.eat('MUL')
                result *= self.term()
            elif token_type == 'DIV':
                self.eat('DIV')
                result /= self.term()
        return result

    # Handle addition and subtraction (lower precedence)
    def term(self):
        result = self.factor()
        # Continue to evaluate as long as there are '+' or '-' tokens
        while self.current_token and self.current_token[0] in ('ADD', 'SUB'):
            token_type = self.current_token[0]
            if token_type == 'ADD':
                self.eat('ADD')
                result += self.factor()
            elif token_type == 'SUB':
                self.eat('SUB')
                result -= self.factor()
        return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate_expression():
    data = request.json
    code = data.get('expression', '')
    try:
        tokens = tokenize(code)  # Tokenize the user input
        interpreter = SimpleInterpreter(tokens)  # Initialize interpreter with tokens
        result = interpreter.expr()  # Evaluate the expression
        return jsonify({'result': result})
    except SyntaxError as e:
        return jsonify({'error': f"Syntax error: {e}"}), 400
    except ZeroDivisionError:
        return jsonify({'error': "Error: Division by zero is not allowed."}), 400

if __name__ == '__main__':
    app.run(debug=True)
