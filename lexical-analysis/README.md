# Lexical analysis

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
* Whitespace (WS)
* Arrow 
* String Literal (LIT)

## Lexical Grammar/Token Rules
* Identifier: Any contiguous sequence of alphabetical characters
  * Regex: `[a-zA-z]+`
* Number: Any contiguous sequence of digits (0-9) 
   * Regex: `[0-9]+`
* Left parenthesis: "("
  * Regex: `\(`
* Right parenthesis: ")"
  * Regex: `\)`
* Left brace: "{"
  * Regex: `\{`
* Right brace: "}"
  * Regex: `\}`
* Colon: ":"
  * Regex: `:`
* Comma: ","
  * Regex: `,`
* Whitespace: Any contiguous sequence of spaces
  * Regex: `[ ]+`
* Arrow: "->"
  * Regex: `\-\>`
* String literal: Either ' or ", followed by any sequence of characters, followed by ' or "
  * Regex: `['"].*?['"]`

## Finite State Machine Diagram
![FSM](./FSM.png)

## Installation
With Docker: 
1. Run `lexical-analysis % docker build --tag lexical-analyzer .` in this folder
2. Run `docker run lexical-analyzer <input file name>`

Straight with Python (if Python is installed and the interpreter is in PATH):
1. Run `python main.py <input file name>` in this folder

## Test file names
* `test.txt`: A properly formatted program
* `test-2.txt`: Adding garbage characters to `test.txt` to test error checking
* `test-3.txt`: Testing incomplete arrow (a hyphen without a ">") error checking
* `test-4.txt`: Testing arrow token further and other identifier/character formats
* `test-5.txt`: Another properly formatted program

## Program Description
* The main function opens the file passed in and passes the content text into tokenize()
* 