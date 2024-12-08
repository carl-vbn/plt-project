import sys
import os
from lexical_analyser import tokenize
from parser import parse, TokenStream, parse_token_repr
from syntax_tree import print_tree
from layers import parse_ast, Context
from xml.etree.ElementTree import tostring as xml_to_string

def main():
    if len(sys.argv) != 2:
        print('Usage: python main.py <input_file>')
        sys.exit(1)
        
    input_file = sys.argv[1]
    with open(input_file, 'r') as f:
        tokens = TokenStream(map(parse_token_repr, tokenize(f.read())))
        
    ast = parse(tokens)
    print_tree(ast)
    
    if len(ast.children) != 1:
        print('Error: root node must have exactly one child')
        sys.exit(1)
    
    anim = parse_ast(ast.children[0])
    svg = anim.to_svg(Context('black', 'black', 1))
    print(xml_to_string(svg).decode())
    
if __name__ == '__main__':
    main()