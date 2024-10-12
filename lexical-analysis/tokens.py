from collections import namedtuple

TokenValidator = namedtuple('TokenType', ['is_valid_start', 'is_valid_content'])

token_validators = {
    'ID': TokenValidator(
        is_valid_start=lambda c: c.isalpha(),
        is_valid_content=lambda c: c.isalpha()
    ),
    'NUM': TokenValidator(
        is_valid_start=lambda c: c.isdigit(),
        is_valid_content=lambda c: c.isdigit()
    ),
    'WS': TokenValidator(
        is_valid_start=lambda c: c == ' ',
        is_valid_content=lambda c: c == ' '
    )
}