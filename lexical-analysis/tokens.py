from collections import namedtuple

TokenValidator = namedtuple('TokenType', ['is_valid_start', 'is_valid_content'])

token_validators = {
    # c: character, tc: token content
    'ID': TokenValidator(
        is_valid_start=lambda c: c.isalpha(),
        is_valid_content=lambda c, tc: c.isalpha()
    ),
    'NUM': TokenValidator(
        is_valid_start=lambda c: c.isdigit(),
        is_valid_content=lambda c, tc: c.isdigit()
    ),
    'WS': TokenValidator(
        is_valid_start=lambda c: c == ' ',
        is_valid_content=lambda c, tc: c == ' '
    ),
    'LPAR': TokenValidator(
        is_valid_start=lambda c: c == '(',
        is_valid_content=lambda c, tc: False
    ),
    'RPAR': TokenValidator(
        is_valid_start=lambda c: c == ')',
        is_valid_content=lambda c, tc: False
    ),
    'COLON': TokenValidator(
        is_valid_start=lambda c: c == ':',
        is_valid_content=lambda c, tc: False
    ),
    'COMMA': TokenValidator(
        is_valid_start=lambda c: c == ',',
        is_valid_content=lambda c, tc: False
    ),
    'Arrow': TokenValidator(
        is_valid_start=lambda c: c == '-',
        is_valid_content=lambda c, tc: c == '>' and tc == '-'
    ),
    'LIT': TokenValidator(
        is_valid_start=lambda c: c == "'" or c == '"',
        is_valid_content=lambda c, tc: len(tc) == 1 or tc[-1] != tc[0] or tc[-1] == '\\'
    )
}