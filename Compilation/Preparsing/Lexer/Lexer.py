# --------------------------------------------------------------------------------------------------
# -------------------------------- PRE-PARSING :: Lexical Analyzer ---------------------------------
# --------------------------------------------------------------------------------------------------
from . Tokentype import Tokentype
from . Token     import Token

from typing import Iterator
from typing import Optional
from typing import NoReturn


# --------------------------------------------------------------------------------------------------
# ----------------------------------- CHARSETS :: Character Sets -----------------------------------
# --------------------------------------------------------------------------------------------------
ASCII_SYMBOLS = {
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
    'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
    'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'g', 'h', 'i', 't', 'u', 'v',
    'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', '~',
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '{', '}', '<', '>',
    '-', '=', '+', '|', ':', ';', '"', "'", ',', '.', '?', '/', ' ', '\\'
}

ALNUM_SYMBOLS = {
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
    'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
    'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'g', 'h', 'i', 't', 'u', 'v',
    'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_'
}

DIGIT_SYMBOLS = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
}


# --------------------------------------------------------------------------------------------------
# ----------------------------------- CLASS :: Lexical Analyzer ------------------------------------
# --------------------------------------------------------------------------------------------------
class Lexer(object):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    parentheses : list[str]

    origin : str
    source : str
    length : int

    start  : int
    end    : int
    line   : int
    column : int

    token     : Optional[Token]
    tokenizer : Iterator[Token]


    # ------------------------------------------------------------------------------------------
    # ------------------------------- CONSTRUCTOR :: Constructor -------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, origin: str, source: str = '') -> None:

        length = len( source := source or open(origin).read() )

        self.parentheses = ['|']

        self.origin = origin
        self.source = source
        self.length = length

        self.start  = 0
        self.end    = 0
        self.line   = 1
        self.column = 1

        self.token = None
        self.tokenizer = self.tokenize()
        self.next()


    # ------------------------------------------------------------------------------------------
    # ------------------------- UTILITY :: Observe the Next Character --------------------------
    # ------------------------------------------------------------------------------------------
    def observe(self) -> str:

        if (offset := self.end) < self.length:
            return self.source[offset]

        return ''


    # ------------------------------------------------------------------------------------------
    # ------------------------- UTILITY :: Consume the Next Character --------------------------
    # ------------------------------------------------------------------------------------------
    def advance(self) -> str:

        if (offset := self.end) < self.length:

            self.end += 1
            return self.source[offset]

        return ''


    # ------------------------------------------------------------------------------------------
    # ------------------- UTILITY :: Advance Start to End and Return Literal -------------------
    # ------------------------------------------------------------------------------------------
    def consume(self) -> str:

        literal, self.start = self.source[self.start : self.end], self.end

        return literal


    # ------------------------------------------------------------------------------------------
    # ----------------------------- TOKENIZER :: Ignore Whitespace -----------------------------
    # ------------------------------------------------------------------------------------------
    def ignore(self) -> Iterator[Token]:

        self.start = self.end

        if False:
            yield # must be generator to be consistent with other tokenizers


    # ------------------------------------------------------------------------------------------
    # --------------------------- TOKENIZER :: Create Operator Token ---------------------------
    # ------------------------------------------------------------------------------------------
    def operator(self, tokentype: Tokentype) -> Iterator[Token]:
        yield Token(tokentype, self.consume(), *self.context)


    # ------------------------------------------------------------------------------------------
    # -------------------------- TOKENIZER :: Create Identifier Token --------------------------
    # ------------------------------------------------------------------------------------------
    def identifier(self) -> Iterator[Token]:

        while self.observe() in ALNUM_SYMBOLS:
            self.advance()

        yield Token(Tokentype.IDENTIFIER, self.consume(), *self.context)


    # ------------------------------------------------------------------------------------------
    # ---------------------------- TOKENIZER :: Create Number Token ----------------------------
    # ------------------------------------------------------------------------------------------
    def number(self) -> Iterator[Token]:
        yield Token(Tokentype.NUMBER, self.consume(), *self.context)


    # ------------------------------------------------------------------------------------------
    # ---------------------------- TOKENIZER :: Create String Token ----------------------------
    # ------------------------------------------------------------------------------------------
    def string(self, quote: str) -> Iterator[Token]:

        while (character := self.observe()) != quote:

            if character in ASCII_SYMBOLS:
                self.advance()

            else:
                raise SyntaxError(f"unrecognized character: '{character}'")

        if self.observe() == quote:
            self.advance()

        else:
            raise SyntaxError(f"unterminated string literal")

        yield Token(Tokentype.STRING, self.consume(), *self.context)


    # ------------------------------------------------------------------------------------------
    # ------------------------- TOKENIZER :: Ignore Comment Characters -------------------------
    # ------------------------------------------------------------------------------------------
    def comment(self) -> None:

        while (character := self.observe()) not in '\r\n':

            if character in ASCII_SYMBOLS:
                self.advance()

            else:
                raise SyntaxError(f"unrecognized character: '{character}'")

        yield from self.ignore()


    # ------------------------------------------------------------------------------------------
    # -------------- TOKENIZER :: Match Parentheses and Create Parenthesis Token ---------------
    # ------------------------------------------------------------------------------------------
    def parenthetical(self, tokentype: Tokentype, open: str, close: str = '') -> Iterator[Token]:

        if close:

            if self.parentheses.pop() != open:
                raise SyntaxError(f"mismatched parenthetical: '{close}'")

        else:
            self.parentheses.append(open)

        yield Token(tokentype, self.consume(), *self.context)


    # ------------------------------------------------------------------------------------------
    # ---------------------- TOKENIZER :: Raise Erroneous Character Error ----------------------
    # ------------------------------------------------------------------------------------------
    def erroneous(self) -> NoReturn:
        raise SyntaxError(f"erroneous character '{self.source[self.start]}'")


    # ------------------------------------------------------------------------------------------
    # --------------------------------- PREFIXES :: Prefix Map ---------------------------------
    # ------------------------------------------------------------------------------------------
    Prefix_Map = {
        '**': lambda self : self.operator(Tokentype.STAR_STAR),
        '++': lambda self : self.operator(Tokentype.PLUS_PLUS),
        ':=': lambda self : self.operator(Tokentype.WALRUS),

        ')' : lambda self : self.parenthetical(Tokentype.R_PAREN, '(', ')'),
        ']' : lambda self : self.parenthetical(Tokentype.R_BRACK, '[', ']'),
        '}' : lambda self : self.parenthetical(Tokentype.R_BRACE, '{', '}'),
        '(' : lambda self : self.parenthetical(Tokentype.L_PAREN, '('),
        '[' : lambda self : self.parenthetical(Tokentype.L_BRACK, '['),
        '{' : lambda self : self.parenthetical(Tokentype.L_BRACE, '{'),

        '|' : lambda self : self.operator(Tokentype.PIPE),
        '*' : lambda self : self.operator(Tokentype.STAR),
        '+' : lambda self : self.operator(Tokentype.PLUS),
        ',' : lambda self : self.operator(Tokentype.COMMA),
        '=' : lambda self : self.operator(Tokentype.ASSIGN),

        '#' : lambda self : self.comment(),

        "'" : lambda self : self.string("'"),
        '"' : lambda self : self.string('"'),

        '&' : lambda self : self.erroneous(),
        '!' : lambda self : self.erroneous(),
        '~' : lambda self : self.erroneous(),
        '@' : lambda self : self.erroneous(),
        '$' : lambda self : self.erroneous(),
        '%' : lambda self : self.erroneous(),
        '^' : lambda self : self.erroneous(),
        '-' : lambda self : self.erroneous(),
        ';' : lambda self : self.erroneous(),
        '<' : lambda self : self.erroneous(),
        '>' : lambda self : self.erroneous(),
        '?' : lambda self : self.erroneous(),
        '/' : lambda self : self.erroneous(),
        '\\': lambda self : self.erroneous(),

        'A' : lambda self : self.identifier(),
        'B' : lambda self : self.identifier(),
        'C' : lambda self : self.identifier(),
        'D' : lambda self : self.identifier(),
        'E' : lambda self : self.identifier(),
        'F' : lambda self : self.identifier(),
        'G' : lambda self : self.identifier(),
        'H' : lambda self : self.identifier(),
        'I' : lambda self : self.identifier(),
        'J' : lambda self : self.identifier(),
        'K' : lambda self : self.identifier(),
        'L' : lambda self : self.identifier(),
        'M' : lambda self : self.identifier(),
        'N' : lambda self : self.identifier(),
        'O' : lambda self : self.identifier(),
        'P' : lambda self : self.identifier(),
        'Q' : lambda self : self.identifier(),
        'R' : lambda self : self.identifier(),
        'S' : lambda self : self.identifier(),
        'T' : lambda self : self.identifier(),
        'U' : lambda self : self.identifier(),
        'V' : lambda self : self.identifier(),
        'W' : lambda self : self.identifier(),
        'X' : lambda self : self.identifier(),
        'Y' : lambda self : self.identifier(),
        'Z' : lambda self : self.identifier(),
        'a' : lambda self : self.identifier(),
        'b' : lambda self : self.identifier(),
        'c' : lambda self : self.identifier(),
        'd' : lambda self : self.identifier(),
        'e' : lambda self : self.identifier(),
        'f' : lambda self : self.identifier(),
        'g' : lambda self : self.identifier(),
        'h' : lambda self : self.identifier(),
        'i' : lambda self : self.identifier(),
        'j' : lambda self : self.identifier(),
        'k' : lambda self : self.identifier(),
        'l' : lambda self : self.identifier(),
        'm' : lambda self : self.identifier(),
        'n' : lambda self : self.identifier(),
        'o' : lambda self : self.identifier(),
        'p' : lambda self : self.identifier(),
        'q' : lambda self : self.identifier(),
        'r' : lambda self : self.identifier(),
        's' : lambda self : self.identifier(),
        't' : lambda self : self.identifier(),
        'u' : lambda self : self.identifier(),
        'v' : lambda self : self.identifier(),
        'w' : lambda self : self.identifier(),
        'x' : lambda self : self.identifier(),
        'y' : lambda self : self.identifier(),
        'z' : lambda self : self.identifier(),

        '0' : lambda self : self.number(),
        '1' : lambda self : self.number(),
        '2' : lambda self : self.number(),
        '3' : lambda self : self.number(),
        '4' : lambda self : self.number(),
        '5' : lambda self : self.number(),
        '6' : lambda self : self.number(),
        '7' : lambda self : self.number(),
        '8' : lambda self : self.number(),
        '9' : lambda self : self.number(),
        ' ' : lambda self : self.ignore(),
        '\t': lambda self : self.ignore(),

        '\n'  : lambda self : self.operator(Tokentype.EOL),
        '\r\n': lambda self : self.operator(Tokentype.EOL),
    }


    # ------------------------------------------------------------------------------------------
    # ------------------------------ TOKENIZER :: Create a Token -------------------------------
    # ------------------------------------------------------------------------------------------
    def tokenize(self) -> Iterator[Token]:

        while self.end < self.length:

            double_prefix = self.source[self.start : self.start + 2]
            single_prefix = self.source[self.start : self.start + 1]

            if tokenizer := Lexer.Prefix_Map.get(double_prefix):

                self.advance()
                self.advance()
                yield from tokenizer(self); continue

            if tokenizer := Lexer.Prefix_Map.get(single_prefix):

                self.advance()
                yield from tokenizer(self); continue

            raise SyntaxError(f"unrecognized character '{single_prefix}'")

        yield from self.operator(Tokentype.EOF)


    # ------------------------------------------------------------------------------------------
    # ----------------------------- UTILITY :: Observe Next Token ------------------------------
    # ------------------------------------------------------------------------------------------
    def peek(self) -> Token:
        return self.token


    # ------------------------------------------------------------------------------------------
    # ----------------------------- UTILITY :: Consume Next Token ------------------------------
    # ------------------------------------------------------------------------------------------
    def next(self) -> Token:

        try:
            next_token = next(self.tokenizer)

        except StopIteration:
            next_token = None

        prev_token = self.token
        self.token = next_token

        return prev_token


    # ------------------------------------------------------------------------------------------
    # ------------------------------- PROPERTY :: Token Context --------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def context(self) -> tuple[int, int, int, int, str]:
        return self.start, self.end, self.line, self.column, self.source