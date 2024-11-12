import sys
from collections import namedtuple
from typing import Iterable, Generator, List, Tuple
from ast import Node, print_tree

Token = namedtuple('Token', ['type', 'value'])

class TokenStream(Iterable[Token]):
    def __init__(self, tokens: Iterable[Token], index=0):
        self.tokens = list(tokens)
        self.index = index
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.tokens):
            raise StopIteration
        token = self.tokens[self.index]
        self.index += 1
        return token
    
    def peek(self):
        return self.tokens[self.index]
    
    def skip(self, n=1):
        self.index += n
    
    def back(self, n=1):
        self.index -= n
        
    def hasnext(self):
        return self.index < len(self.tokens)
    
    def clone(self):
        return TokenStream(self.tokens, self.index)

def parse_token_repr(token_repr: str) -> Token:
    # Convert <type, "value"> to Token(type, value)
    token_repr = token_repr.lstrip('<').rstrip('>\n').split(',')
    token_type = token_repr[0].strip()
    token_value = token_repr[1].strip()[1:-1] # Remove quotes
    
    return Token(token_type, token_value)
    

def read_token_stream() -> Generator[Token, None, None]:
    for line in sys.stdin:
        yield parse_token_repr(line.strip())
        
def next_indent_level(token_stream: TokenStream) -> int:    
    indent_level = 0
    while token_stream.peek().type == 'INDENT':
        indent_level += 1
        next(token_stream)
        
    return indent_level

def get_indent_level(token_stream: TokenStream) -> int:
    return next_indent_level(token_stream.clone())
            
def parse_node(token_stream: TokenStream):
    token = next(token_stream)
    if token.type == 'ID':
        return Node(token.value)
    else:
        printerr(f'Expected ID, got {token.type}')
        return None
    
def parse_children(token_stream: TokenStream, indent_level: int) -> List[Node]:
    nodes = []
    while token_stream.hasnext():
        indent = get_indent_level(token_stream)
        if indent == indent_level:
            token_stream.skip(indent)
            
            node = parse_node(token_stream)
            node.children = parse_children(token_stream, indent_level + 1)
            nodes.append(node)
        elif indent < indent_level:
            break
        else:
            printerr(f'Unexpected indent')
            break
        
    return nodes
            
def parse(token_stream: TokenStream):
    root = Node('root')
    root.children = parse_children(token_stream, 0)
    print_tree(root)
    

def printerr(msg: str):
    print(f':: PARSER ERROR :: {msg}')
        
def main():
    parse(TokenStream(read_token_stream()))
    
    
if __name__ == '__main__':
    main()