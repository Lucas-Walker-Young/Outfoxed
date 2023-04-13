# --------------------------------------------------------------------------------------------------
# -------------------------------- PRE-PARSING :: Lexical Analyzer ---------------------------------
# --------------------------------------------------------------------------------------------------
from . Tokentype import Tokentype
from . Token     import Token
from . Codec     import Codec

from typing import Iterator
from typing import Optional
from typing import NoReturn


# --------------------------------------------------------------------------------------------------
# ----------------------------------- CLASS :: Lexical Analyzer ------------------------------------
# --------------------------------------------------------------------------------------------------
class Lexer(object):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    parentheses : list[int]
    literal     : list[int]

    origin : str
    start  : int
    end    : int
    line   : int
    column : int

    codec  : Codec

    token     : Optional[Token]
    tokenizer : Iterator[Token]


    # ------------------------------------------------------------------------------------------
    # ------------------------------- CONSTRUCTOR :: Constructor -------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, origin: str) -> None:

        self.parentheses = ['|']
        self.literal     = [   ]

        self.origin = origin
        self.start  = 0
        self.end    = 0
        self.line   = 1
        self.column = 1

        self.codec  = Codec(origin)

        self.token = None
        self.tokenizer = self.tokenize()

        self.next()


    # ------------------------------------------------------------------------------------------
    # ------------------------- UTILITY :: Observe the Next Character --------------------------
    # ------------------------------------------------------------------------------------------
    def observe(self) -> str:
        return self.codec.peek()[0]


    # ------------------------------------------------------------------------------------------
    # ------------------------- UTILITY :: Consume the Next Character --------------------------
    # ------------------------------------------------------------------------------------------
    def advance(self) -> str:

        self.literal.append(self.observe())

        self.end += 1
        return self.codec.next()


    # ------------------------------------------------------------------------------------------
    # ------------------- UTILITY :: Advance Start to End and Return Literal -------------------
    # ------------------------------------------------------------------------------------------
    def consume(self) -> str:

        literal = bytes(self.literal).decode(encoding='utf-8')

        self.start   = self.end
        self.literal = []

        return literal


    # ------------------------------------------------------------------------------------------
    # ----------------------------- TOKENIZER :: Ignore Whitespace -----------------------------
    # ------------------------------------------------------------------------------------------
    def ignore(self) -> Iterator[Token]:

        self.start   = self.end
        self.literal = []

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

        while True:

            if 65 <= self.observe() <= 90: # A-Z
                self.advance(); continue

            if 97 <= self.observe() <= 122: # a-z
                self.advance(); continue

            if 95 == self.observe(): # underscore
                self.advance(); continue

            break

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

        while (character := self.observe()) and character != ord(quote):
            self.advance()

        if self.observe() == ord(quote):
            self.advance()

        else:
            raise SyntaxError(f"unterminated string literal")

        yield Token(Tokentype.STRING, self.consume(), *self.context)


    # ------------------------------------------------------------------------------------------
    # ------------------------- TOKENIZER :: Ignore Comment Characters -------------------------
    # ------------------------------------------------------------------------------------------
    def comment(self) -> None:

        while (codepoint := self.observe()) not in (ord('\r'), ord('\n')):
            self.advance()

        yield from self.ignore()


    # ------------------------------------------------------------------------------------------
    # -------------- TOKENIZER :: Match Parentheses and Create Parenthesis Token ---------------
    # ------------------------------------------------------------------------------------------
    def parenthetical(self, tokentype: Tokentype, open: str, close: str = '') -> Iterator[Token]:

        if close:

            if self.parentheses.pop() != ord(open):
                raise SyntaxError(f"mismatched parenthetical: '{close}'")

        else:
            self.parentheses.append(ord(open))

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
        (ord('*'), ord('*')): lambda self : self.operator(Tokentype.STAR_STAR),
        (ord('+'), ord('+')): lambda self : self.operator(Tokentype.PLUS_PLUS),
        (ord(':'), ord('=')): lambda self : self.operator(Tokentype.WALRUS),

        (ord(')'), ) : lambda self : self.parenthetical(Tokentype.R_PAREN, '(', ')'),
        (ord(']'), ) : lambda self : self.parenthetical(Tokentype.R_BRACK, '[', ']'),
        (ord('}'), ) : lambda self : self.parenthetical(Tokentype.R_BRACE, '{', '}'),
        (ord('('), ) : lambda self : self.parenthetical(Tokentype.L_PAREN, '('),
        (ord('['), ) : lambda self : self.parenthetical(Tokentype.L_BRACK, '['),
        (ord('{'), ) : lambda self : self.parenthetical(Tokentype.L_BRACE, '{'),

        (ord('|'), ) : lambda self : self.operator(Tokentype.PIPE),
        (ord('*'), ) : lambda self : self.operator(Tokentype.STAR),
        (ord('+'), ) : lambda self : self.operator(Tokentype.PLUS),
        (ord(','), ) : lambda self : self.operator(Tokentype.COMMA),
        (ord('='), ) : lambda self : self.operator(Tokentype.ASSIGN),

        (ord('#'), ) : lambda self : self.comment(),

        (ord("'"), ) : lambda self : self.string("'"),
        (ord('"'), ) : lambda self : self.string('"'),

        (ord('&'), ) : lambda self : self.erroneous(),
        (ord('!'), ) : lambda self : self.erroneous(),
        (ord('!'), ) : lambda self : self.erroneous(),
        (ord('@'), ) : lambda self : self.erroneous(),
        (ord('$'), ) : lambda self : self.erroneous(),
        (ord('%'), ) : lambda self : self.erroneous(),
        (ord('^'), ) : lambda self : self.erroneous(),
        (ord('-'), ) : lambda self : self.erroneous(),
        (ord(';'), ) : lambda self : self.erroneous(),
        (ord('<'), ) : lambda self : self.erroneous(),
        (ord('>'), ) : lambda self : self.erroneous(),
        (ord('?'), ) : lambda self : self.erroneous(),
        (ord('/'), ) : lambda self : self.erroneous(),
        (ord('/'), ) : lambda self : self.erroneous(),

        (ord('A'), ) : lambda self : self.identifier(),
        (ord('B'), ) : lambda self : self.identifier(),
        (ord('C'), ) : lambda self : self.identifier(),
        (ord('D'), ) : lambda self : self.identifier(),
        (ord('E'), ) : lambda self : self.identifier(),
        (ord('F'), ) : lambda self : self.identifier(),
        (ord('G'), ) : lambda self : self.identifier(),
        (ord('H'), ) : lambda self : self.identifier(),
        (ord('I'), ) : lambda self : self.identifier(),
        (ord('J'), ) : lambda self : self.identifier(),
        (ord('K'), ) : lambda self : self.identifier(),
        (ord('L'), ) : lambda self : self.identifier(),
        (ord('M'), ) : lambda self : self.identifier(),
        (ord('N'), ) : lambda self : self.identifier(),
        (ord('O'), ) : lambda self : self.identifier(),
        (ord('P'), ) : lambda self : self.identifier(),
        (ord('Q'), ) : lambda self : self.identifier(),
        (ord('R'), ) : lambda self : self.identifier(),
        (ord('S'), ) : lambda self : self.identifier(),
        (ord('T'), ) : lambda self : self.identifier(),
        (ord('U'), ) : lambda self : self.identifier(),
        (ord('V'), ) : lambda self : self.identifier(),
        (ord('W'), ) : lambda self : self.identifier(),
        (ord('X'), ) : lambda self : self.identifier(),
        (ord('Y'), ) : lambda self : self.identifier(),
        (ord('Z'), ) : lambda self : self.identifier(),
        (ord('a'), ) : lambda self : self.identifier(),
        (ord('b'), ) : lambda self : self.identifier(),
        (ord('c'), ) : lambda self : self.identifier(),
        (ord('d'), ) : lambda self : self.identifier(),
        (ord('e'), ) : lambda self : self.identifier(),
        (ord('f'), ) : lambda self : self.identifier(),
        (ord('g'), ) : lambda self : self.identifier(),
        (ord('h'), ) : lambda self : self.identifier(),
        (ord('i'), ) : lambda self : self.identifier(),
        (ord('j'), ) : lambda self : self.identifier(),
        (ord('k'), ) : lambda self : self.identifier(),
        (ord('l'), ) : lambda self : self.identifier(),
        (ord('m'), ) : lambda self : self.identifier(),
        (ord('n'), ) : lambda self : self.identifier(),
        (ord('o'), ) : lambda self : self.identifier(),
        (ord('p'), ) : lambda self : self.identifier(),
        (ord('q'), ) : lambda self : self.identifier(),
        (ord('r'), ) : lambda self : self.identifier(),
        (ord('s'), ) : lambda self : self.identifier(),
        (ord('t'), ) : lambda self : self.identifier(),
        (ord('u'), ) : lambda self : self.identifier(),
        (ord('v'), ) : lambda self : self.identifier(),
        (ord('w'), ) : lambda self : self.identifier(),
        (ord('x'), ) : lambda self : self.identifier(),
        (ord('y'), ) : lambda self : self.identifier(),
        (ord('z'), ) : lambda self : self.identifier(),
        (ord('_'), ): lambda self: self.identifier(),

        (ord('0'), ) : lambda self : self.number(),
        (ord('1'), ) : lambda self : self.number(),
        (ord('2'), ) : lambda self : self.number(),
        (ord('3'), ) : lambda self : self.number(),
        (ord('4'), ) : lambda self : self.number(),
        (ord('5'), ) : lambda self : self.number(),
        (ord('6'), ) : lambda self : self.number(),
        (ord('7'), ) : lambda self : self.number(),
        (ord('8'), ) : lambda self : self.number(),
        (ord('9'), ) : lambda self : self.number(),

        (ord(' '), ) : lambda self : self.ignore(),
        (ord('\t'),) : lambda self : self.ignore(),

        (ord('\n'),) : lambda self : self.operator(Tokentype.EOL),
        (ord('\n'), ord('\r')): lambda self : self.operator(Tokentype.EOL),
    }


    # ------------------------------------------------------------------------------------------
    # ------------------------------ TOKENIZER :: Create a Token -------------------------------
    # ------------------------------------------------------------------------------------------
    def tokenize(self) -> Iterator[Token]:

        while self.observe():

            double_prefix = self.codec.peek(2)
            single_prefix = self.codec.peek(1)

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
    def peek(self) -> None | Token:
        return self.token


    # ------------------------------------------------------------------------------------------
    # ----------------------------- UTILITY :: Consume Next Token ------------------------------
    # ------------------------------------------------------------------------------------------
    def next(self) -> None | Token:

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
        return self.start, self.end, self.line, self.column, self.origin