import sys
from tokens import token_validators

def tokenize(string: str):
    in_comment = False
    token_type = None
    token_val = None
    
    index = 0
    
    while index < len(string):
        c = string[index]
        # print(f"c=[{c}]")
        
        if c == '\n':
            if in_comment:
                in_comment = False
            index += 1
            continue

        if in_comment:
            index += 1
            continue
        
        if c == '#':
            in_comment = True
            index += 1
            continue
        
        if token_type is not None:
            # Currently parsing token
            
            if token_validators[token_type].is_valid_content(c, token_val):
                token_val += c
                #print("token val is:", token_val)
                index += 1
                if token_type == "Arrow":
                    print(f'<{token_type}, "{token_val}">')
                    token_type = None
                    token_val = None
                    continue
            elif token_type == "Arrow" and c != ">":
                print(':: LEXICAL ERROR :: broken arrow')
                token_type = None
                token_val = None
            else:
                print(f'<{token_type}, "{token_val}">')
                token_type = None
                token_val = None
                continue
        if token_type is None:
            # New token
            token_val = c
            index += 1
            for typename, validator in token_validators.items():
                if validator.is_valid_start(c):
                    token_type = typename
                    break
            else: # I actually like that Python for loops have an else clause
                print(f':: LEXICAL ERROR :: Invalid character: {c}')
                continue
                
    if token_type is not None and token_type != "Arrow":
        if token_type == 'LIT' and token_val[-1] != token_val[0]:
            print(':: LEXICAL ERROR :: Unterminated literal')
        
        print(f'<{token_type}, "{token_val}">')

def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py <file>')
        sys.exit(1)

    file_path = sys.argv[1]
    
    with open(file_path, 'r') as f:
        tokenize(f.read())
        
if __name__ == '__main__':
    main()
