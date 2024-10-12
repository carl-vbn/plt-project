import sys
from tokens import token_validators

def tokenize(string: str):
    token_type = None
    token_val = None
    
    index = 0
    
    while index < len(string):
        c = string[index]
        
        if token_type is not None:
            # Currently parsing token
            
            if token_validators[token_type].is_valid_content(c):
                token_val += c
                index += 1
            else:
                print(f'<{token_type}, "{token_val}">')
                token_type = None
                token_val = None
        else:
            # New token
            token_val = ''
            for typename, validator in token_validators.items():
                if validator.is_valid_start(c):
                    token_type = typename
                    break
                
    if token_type is not None:
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
