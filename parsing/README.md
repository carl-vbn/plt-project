# Parser

## Team Members
* Carl von Bonin (cv2546)
* Adheesh Kadiresan (ak4907)

## Token types
* Identifier (ID)
* Left parenthesis (LPAR)
* Right parenthesis (RPAR)
* Left brace (LBRACE)
* Right brace (RBRACE)
* Number (NUM)
* Colon (COLON)
* Comma (COMMA)
* Indentation (INDENT) - Note: This replaces the whitespace token we had for the last part
* ARROW 
* String Literal (LIT)

# Context-Free Grammar
![CFG](./CFG-v2.png)


## Installation
With Docker: 
1. Ensure Docker daemon is running
2. `cd` into this folder `parsing`
3. Run `docker build -t scanner_and_parser .` in this folder
4. Run `docker run scanner_and_parser <input file name>`

Straight with Python (if Python is installed and the interpreter is in PATH):
1. `cd` into this folder `lexical-analysis`
2. Run `python lexical_analyser.py <input file name> | python parser.py` in this folder

## Video Link
https://youtu.be/ED1OrO2Rnno