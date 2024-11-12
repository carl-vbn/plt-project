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
        if self.index >= len(self.tokens):
            raise StopIteration
        
        return self.tokens[self.index]
    
    def skip(self, n=1):
        self.index += n
    
    def back(self, n=1):
        self.index -= n
        
    def hasnext(self):
        return self.index < len(self.tokens)
    
    def clone(self):
        return TokenStream(self.tokens, self.index)
    
class ParsingError(Exception):
    pass

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
    '''
    Returns the number of INDENT tokens in the stream and advances the stream to the next non-INDENT token
    '''
    
    indent_level = 0
    while token_stream.peek().type == 'INDENT':
        indent_level += 1
        next(token_stream)
        
    return indent_level

def get_indent_level(token_stream: TokenStream) -> int:
    '''
    Returns the number of INDENT tokens in the stream without advancing the stream
    '''
    
    return next_indent_level(token_stream.clone())
           
def expect(token_stream: TokenStream, token_type: str):
    token = next(token_stream)
    if token.type != token_type:
        raise ParsingError(f'Expected {token_type}, got {token.type}')
    
    return token

def parse_param_value(token_stream: TokenStream) -> Node:
    '''
    Parses the value of a parameter, like 5 or (1, 2, 3)
    For named parameters, like width: 5, this is the value part (5)
    For anonymous parameters, this is the entire parameter
    '''
    
    token = next(token_stream)
    if token.type == 'ID':
        # Param is new node
        param_node = Node(token.value)
        next_token = token_stream.peek()
        if next_token.type == 'LPAR':
            param_node.children = parse_params(token_stream)
        elif next_token.type not in ['COMMA', 'RPAR']:
            raise ParsingError(f'Expected LPAR, COMMA or RPAR, got {next_token.type}')
        
        return param_node
    elif token.type == 'LPAR': # Tuple
        tuple_node = Node('Tuple')
        while True:
            num = expect(token_stream, 'NUM')
            tuple_node.children.append(Node(num.value))
            
            tok = next(token_stream)
            if tok.type == 'COMMA':
                continue
            elif tok.type == 'RPAR':
                break
            else:
                raise ParsingError(f'Expected COMMA or RPAR, got {tok.type}')
        return tuple_node
    elif token.type == 'LBRACE': # Dict
        dict_node = Node('Dict')
        while True:
            entry_node = Node('DictEntry')
            key = expect(token_stream, 'ID')
            entry_node.children.append(Node(key.value))
            
            expect(token_stream, 'COLON')
            
            value_node = parse_param_value(token_stream)
            entry_node.children.append(value_node)
            
            dict_node.children.append(entry_node)
            
            tok = next(token_stream)
            if tok.type == 'COMMA':
                continue
            elif tok.type == 'RBRACE':
                break
            else:
                raise ParsingError(f'Expected COMMA or RBRACE, got {tok.type}')
            
        return dict_node
    else:
        return Node(token.value)

def parse_param(token_stream: TokenStream) -> Node:
    '''
    Parses a single parameter, like "hello" or width: 5
    '''
    
    node = Node('AnonymousParameter')
    token = next(token_stream)

    if token.type == 'RPAR':
        return None
    elif token.type == 'ID':
        next_token = next(token_stream)
        if next_token.type == 'COLON':
            node.name = 'NamedParameter'
            node.children.append(Node(token.value))
            node.children.append(parse_param_value(token_stream))
        elif next_token.type == 'LPAR':
            # Param is new node
            token_stream.back(2) # Go back before the parameter started
            node.children.append(parse_param_value(token_stream))
        else:
            raise ParsingError(f'Expected COLON or LPAR, got {next_token.type}')          
        
    else:
        token_stream.back()
        node.children.append(parse_param_value(token_stream))
    
    return node
     
def parse_params(token_stream: TokenStream) -> List[Node]:
    '''
    Parses a list of parameters, like (1, 2, 3) or (width: 5, height: 10)
    '''
    
    params = []
    
    expect(token_stream, 'LPAR')
    
    while token_stream.hasnext():
        param = parse_param(token_stream)
        if param is None:
            break
        
        params.append(param)
        
        next_token = next(token_stream)
        if next_token.type == 'COMMA':
            continue
        elif next_token.type == 'RPAR':
            break
        else:
            raise ParsingError(f'Expected COMMA or RPAR, got {next_token}')
    
    return params

def parse_node(token_stream: TokenStream):
    '''
    Parses a layer node, like Canvas(width: 100, height: 100) and its possible exports
    Does not parse children (stops after one layer node)
    '''
    
    token = expect(token_stream, 'ID')
    node = Node(token.value)
    params = parse_params(token_stream)
    
    if len(params) > 0:
        params_node = Node('parameters')
        params_node.children = params
        node.children.append(params_node)
    
    if token_stream.hasnext() and token_stream.peek().type == 'ARROW':
        # Exports
        next(token_stream)
        expect(token_stream, 'LPAR')
        exports = []
        while True:
            export = expect(token_stream, 'ID')
            exports.append(Node(export.value))
            next_token = next(token_stream)
            if next_token.type == 'COMMA':
                continue
            elif next_token.type == 'RPAR':
                break
            else:
                raise ParsingError(f'Expected COMMA or RPAR, got {next_token.type}')
            
        exports_node = Node('exports')
        exports_node.children = exports
        node.children.append(exports_node)
    
    return node
    
def parse_children(token_stream: TokenStream, indent_level: int) -> List[Node]:
    '''
    Recursively parses all children from the current position in the token stream at the given indent level
    '''
    
    nodes = []
    while token_stream.hasnext():
        try:
            indent = get_indent_level(token_stream)
        except StopIteration:
            break
        if indent == indent_level:
            token_stream.skip(indent)
            
            node = parse_node(token_stream)
            children = parse_children(token_stream, indent_level + 1)
            if len(children) > 0:
                children_node = Node('children')
                children_node.children = children
                node.children.append(children_node)
            nodes.append(node)
        elif indent < indent_level:
            break
        else:
            raise ParsingError(f'Unexpected indent')
        
    return nodes
            
def parse(token_stream: TokenStream):
    root = Node('root')
    root.children = parse_children(token_stream, 0)
    print_tree(root)
        
def main():
    try:
        parse(TokenStream(read_token_stream()))
    except ParsingError as e:
        # print(f':: PARSER ERROR :: {e}')
        raise e
    
    
if __name__ == '__main__':
    main()