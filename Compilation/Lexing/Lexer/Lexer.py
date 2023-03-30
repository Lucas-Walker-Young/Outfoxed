# --------------------------------------------------------------------------------------------------
# ----------------------------------- LEXING :: Lexical Analyzer -----------------------------------
# --------------------------------------------------------------------------------------------------
from .. Tokens.Tokentype import Tokentype
from .. Tokens.Token     import Token

from typing import Iterator
from typing import NoReturn

import collections
import pathlib
import inspect


# --------------------------------------------------------------------------------------------------
# ----------------------------------- CLASS :: Lexical Analyzer ------------------------------------
# --------------------------------------------------------------------------------------------------
class Lexer(object):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    tokenizer : Iterator[Token]

    origin : str
    source : str
    length : int

    start  : int
    end    : int
    line   : int
    column : int

    indentation : list[int]
    parentheses : list[str]
    stringstack : list[str]


    # ------------------------------------------------------------------------------------------
    # ------------------------------- CONSTRUCTOR :: Constructor -------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, origin: str, source: str = '') -> None:

        length = len(source := source or pathlib.Path(origin).read_text())

        self.origin = origin
        self.source = source
        self.length = length

        self.start   = 0
        self.end     = 0
        self.line    = 1
        self.column  = 1

        self.indentation = [ 0 ]
        self.quotes      = ['|']
        self.parentheses = ['|']

        self.tokenizer   = self.lex()


    # ------------------------------------------------------------------------------------------
    # ------------------------- ERRORS :: Assorted Tokenization Errors -------------------------
    # ------------------------------------------------------------------------------------------
    def indentation_error(self) -> NoReturn:
        raise SyntaxError(f"indentation decreased to inconsistent depth")

    def parenthesis_error(self) -> NoReturn:
        raise SyntaxError(f"mismatched parenthetical: {repr(self.observe(-1))}")

    def backslash_error(self) -> NoReturn:
        raise SyntaxError(f"backslashes must be followed immediately by newlines")

    def tab_error(self) -> NoReturn:
        raise SyntaxError(f"leading tabs are prohibited (use spaces instead)")


    # ------------------------------------------------------------------------------------------
    # --------------------------------- METHOD :: Create Tokens ---------------------------------
    # ------------------------------------------------------------------------------------------
    def token(self, type: Tokentype) -> Iterator[Token]:

        literal    = self.source[(start := self.start) : self.end]
        self.start = self.end

        yield Token(type, literal, self.start, self.end, self.line, self.column, self.origin)


    # ------------------------------------------------------------------------------------------
    # -------------------- UTILITY :: Advance Start Marker by Some Distance --------------------
    # ------------------------------------------------------------------------------------------
    def consume(self) -> Iterator[Token]:

        self.start = self.end

        if False:
            yield  # must be generator to be consistent w other tokenizers


    # ------------------------------------------------------------------------------------------
    # --------------------- UTILITY :: Advance End Marker by Some Distance ---------------------
    # ------------------------------------------------------------------------------------------
    def advance(self, distance: int = 1) -> None:

        self.end    += distance
        self.column += distance

        return True


    # ------------------------------------------------------------------------------------------
    # ------------------- UTILITY :: Observe a Character some Distance Ahead -------------------
    # ------------------------------------------------------------------------------------------
    def observe(self, distance: int = 0) -> None:

        if (offset := self.end + distance) < self.length:
            return self.source[offset]

        return ''


    # ------------------------------------------------------------------------------------------
    # ---------------------- TOKENIZER :: Create Tokens and Update Markers ----------------------
    # ------------------------------------------------------------------------------------------
    def token(self, type: Tokentype) -> Iterator[Token]:

        literal = self.source[(start := self.start): self.end]
        self.start = self.end

        yield Token(type, literal, start, self.end, self.line, self.column, self.origin)


    # ------------------------------------------------------------------------------------------
    # ------------------------ TOKENIZER :: Create a Comment Meta-Tokens ------------------------
    # ------------------------------------------------------------------------------------------
    def comment(self) -> Iterator[Token]:

        characters = {
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
            'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
            'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '`', '~',
            '!', '@', '#', '$', '%', '^', '^', '&', '*', '(', ')', '-', '_', '+', '=', '|',
            '[', ']', '{', '}', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/', ' ', '\t'
        }

        while (observed := self.observe()) and observed != '\n' and observed != '\r' :

            if observed not in characters:
                raise SyntaxError(f"unrecognized character: {repr(observed)}")

            self.advance()

        self.token(Tokentype.COMMENT); yield  # consume w/o generating token


    # ------------------------------------------------------------------------------------------
    # ---------------------- TOKENIZER :: Create Indent and Dedent Tokens ----------------------
    # ------------------------------------------------------------------------------------------
    def indents_and_dedents(self, indentation: int) -> Iterator[Token]:

        if indentation < self.indentation[-1] and indentation not in self.indentation:
            self.indentation_error()

        if indentation > self.indentation[-1]:

            self.indentation.append(indentation)
            yield from self.token(Tokentype.INDENT)

        while indentation < self.indentation[-1]:

            self.indentation.pop()
            yield from self.token(Tokentype.DEDENT)

        yield from self.consume() # consume leading ws in cases where indentation hasn't changed


    # ------------------------------------------------------------------------------------------
    # ----------------- TOKENIZER :: Create a Newline and Indent/Dedent Tokens -----------------
    # ------------------------------------------------------------------------------------------
    def newline(self, indentation: int = 0) -> Iterator[Token]:

        if len(self.parentheses) == 1: # ignore indentation rules if in parentheses

            newline_token = next(self.token(Tokentype.NEWLINE))

            while self.observe() == ' ' and self.advance():
                indentation += 1

            match self.observe():

                case '\n':
                    yield from self.consume() # ignore

                case '\r':
                    yield from self.consume()  # ignore

                case  '#':
                    yield from self.comment()  # ignore

                case '\t':
                    self.tab_error()

                case   _ :
                    yield newline_token
                    yield from self.indents_and_dedents(indentation)


    # ------------------------------------------------------------------------------------------
    # ------------ TOKENIZER :: Reclassify an Identifier Tokens as Keyword if Needed ------------
    # ------------------------------------------------------------------------------------------
    def or_keyword(self, token: Token) -> Iterator[Token]:

        keywords = {
            'public', 'restricted', 'private', 'protected', 'restricted', 'static', 'async',
            'class', 'operator', 'def', 'for', 'in', 'while', 'until', 'continue', 'break',
            'pass', 'finally', 'return', 'yield', 'from', 'if', 'else', 'and', 'not', 'or',
            'match', 'case', 'default', 'try', 'suppress', 'catch', 'with', 'as', 'import',
            'await', 'broken', 'exit', 'true', 'false', 'null',
        }

        if token.literal in keywords:
            yield token.reclassify(Tokentype.KEYWORD)

        else:
            yield token


    # ------------------------------------------------------------------------------------------
    # ------------------- TOKENIZER :: Create an Identifier or Keyword Tokens -------------------
    # ------------------------------------------------------------------------------------------
    def identifier_or_keyword(self) -> Iterator[Token]:

        characters = {
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',
            'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
            'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
            'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '_',
        }

        while self.observe() in characters:
            self.advance()

        yield from self.or_keyword(next(self.token(Tokentype.IDENTIFIER)))


    # ------------------------------------------------------------------------------------------
    # ---------- UTILITY :: Get Numerals and Command Characters for Numeric Tokenizer ----------
    # ------------------------------------------------------------------------------------------
    def get_numeric_context(self, type: Tokentype) -> tuple[frozenset[str], str, str]:

        if type & (Tokentype.BASE36 | Tokentype.BASE16):

            numerals = {
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
                'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
            }

            return numerals, 'ε', 'ι'

        return {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}, 'e', 'i'


    # ------------------------------------------------------------------------------------------
    # --------------------------- TOKENIZER :: Create a Number Tokens ---------------------------
    # ------------------------------------------------------------------------------------------
    def numeric(self, type: Tokentype) -> Iterator[Token]:

        charset, e, i = self.get_numeric_context(type)

        while self.observe() in charset and self.advance():
            pass  # consume digits preceding the radix

        if self.observe() == '.':

            type |= Tokentype.NUMBER | Tokentype.FLOAT
            self.advance()

        else:
            type |= Tokentype.NUMBER | Tokentype.INTEGER

        while self.observe() in charset and self.advance():
            pass  # consume digits following the radix

        if self.observe().lower() == i:
            type |= Tokentype.COMPLEX
            self.advance()

        if self.observe().lower() == e:
            type |= Tokentype.EPSILON
            self.advance()

        while self.observe() in charset and self.advance():
            pass  # consume digits preceding the radix

        if self.observe().lower() == '.':
            self.advance()

        while self.observe() in charset and self.advance():
            pass  # consume digits following the radix

        yield from self.token(type)


    # ------------------------------------------------------------------------------------------
    # ---------------- TOKENIZER :: Create Double or Triple-Double Quotes Tokens ----------------
    # ------------------------------------------------------------------------------------------
    def double_quote(self) -> Iterator[Token]:

        if self.source[self.end : self.end + 2] == '""':

            self.advance(2)
            yield from self.token(Tokentype.DOUBLE_QUOTE | Tokentype.TRIPLE_QUOTE)

        else:
            yield from self.token(Tokentype.DOUBLE_QUOTE)


    # ------------------------------------------------------------------------------------------
    # ---------------- TOKENIZER :: Create Single or Triple-Single Quotes Tokens ----------------
    # ------------------------------------------------------------------------------------------
    def single_quote(self) -> Iterator[Token]:

        if self.source[self.end : self.end + 2] == "''":

            self.advance(2)
            yield from self.token(Tokentype.SINGLE_QUOTE | Tokentype.TRIPLE_QUOTE)

        else:
            yield from self.token(Tokentype.SINGLE_QUOTE)


    # ------------------------------------------------------------------------------------------
    # -------------------- TOKENIZER :: Apply String-Prefix to Quotes Tokens --------------------
    # ------------------------------------------------------------------------------------------
    def fstring(self, tokenizer: Iterator[Token]) -> Iterator[Token]:
        yield next(tokenizer).reclassify(Tokentype.F_STRING)

    def rstring(self, tokenizer: Iterator[Token]) -> Iterator[Token]:
        yield next(tokenizer).reclassify(Tokentype.R_STRING)


    # ------------------------------------------------------------------------------------------
    # ------------------- TOKENIZER :: Handle Parentheses and Generate Tokens -------------------
    # ------------------------------------------------------------------------------------------
    def parenthetical(self, open: str, close: str = '') -> Iterator[Token]:

        if close:

            if self.parentheses.pop() != open:
                self.parenthesis_error()

        else:
            self.parentheses.append(open)

        yield from self.token(Tokentype.OPERATOR)


    # ------------------------------------------------------------------------------------------
    # ------------------ TOKENIZER :: Generate an EOF and Final Dedent Tokens ------------------
    # ------------------------------------------------------------------------------------------
    def eof(self) -> Iterator[Token]:

        while self.indentation.pop():
            yield from self.token(Tokentype.DEDENT)

        yield from self.token(Tokentype.EOF)


    # ------------------------------------------------------------------------------------------
    # ------------------ PREFIX MAP :: Regular Fox-Source-Code Tokens Prefixes ------------------
    # ------------------------------------------------------------------------------------------
    Fox_Prefix_Map = collections.defaultdict(lambda : None, {

        'FR"': lambda self : self.fstring(self.rstring(self.double_quote())),
        'Fr"': lambda self : self.fstring(self.rstring(self.double_quote())),
        'fr"': lambda self : self.fstring(self.rstring(self.double_quote())),
        'fR"': lambda self : self.fstring(self.rstring(self.double_quote())),
        'RF"': lambda self : self.fstring(self.rstring(self.double_quote())),
        'Rf"': lambda self : self.fstring(self.rstring(self.double_quote())),
        'rf"': lambda self : self.fstring(self.rstring(self.double_quote())),
        'rF"': lambda self : self.fstring(self.rstring(self.double_quote())),
        "FR'": lambda self : self.fstring(self.rstring(self.single_quote())),
        "Fr'": lambda self : self.fstring(self.rstring(self.single_quote())),
        "fr'": lambda self : self.fstring(self.rstring(self.single_quote())),
        "fR'": lambda self : self.fstring(self.rstring(self.single_quote())),
        "RF'": lambda self : self.fstring(self.rstring(self.single_quote())),
        "Rf'": lambda self : self.fstring(self.rstring(self.single_quote())),
        "rf'": lambda self : self.fstring(self.rstring(self.single_quote())),
        "rF'": lambda self : self.fstring(self.rstring(self.single_quote())),
        'F"' : lambda self : self.fstring(self.double_quote()),
        'f"' : lambda self : self.fstring(self.double_quote()),
        'R"' : lambda self : self.rstring(self.double_quote()),
        'r"' : lambda self : self.rstring(self.double_quote()),
        "F'" : lambda self : self.fstring(self.single_quote()),
        "f'" : lambda self : self.fstring(self.single_quote()),
        "R'" : lambda self : self.rstring(self.single_quote()),
        "r'" : lambda self : self.rstring(self.single_quote()),
        '"'  : lambda self : self.double_quote(),
        "'"  : lambda self : self.single_quote(),

        '::=': lambda self : self.token(Tokentype.OPERATOR),
        '...': lambda self : self.token(Tokentype.OPERATOR),
        '>>=': lambda self : self.token(Tokentype.OPERATOR),
        '<<=': lambda self : self.token(Tokentype.OPERATOR),
        '=>' : lambda self : self.token(Tokentype.OPERATOR),
        '->' : lambda self : self.token(Tokentype.OPERATOR),
        '==' : lambda self : self.token(Tokentype.OPERATOR),
        '++' : lambda self : self.token(Tokentype.OPERATOR),
        '+=' : lambda self : self.token(Tokentype.OPERATOR),
        '--' : lambda self : self.token(Tokentype.OPERATOR),
        '-=' : lambda self : self.token(Tokentype.OPERATOR),
        '**' : lambda self : self.token(Tokentype.OPERATOR),
        '*=' : lambda self : self.token(Tokentype.OPERATOR),
        '/=' : lambda self : self.token(Tokentype.OPERATOR),
        '<<' : lambda self : self.token(Tokentype.OPERATOR),
        '<=' : lambda self : self.token(Tokentype.OPERATOR),
        '>>' : lambda self : self.token(Tokentype.OPERATOR),
        '>=' : lambda self : self.token(Tokentype.OPERATOR),
        '^=' : lambda self : self.token(Tokentype.OPERATOR),
        '&=' : lambda self : self.token(Tokentype.OPERATOR),
        '|=' : lambda self : self.token(Tokentype.OPERATOR),
        '::' : lambda self : self.token(Tokentype.OPERATOR),
        ':=' : lambda self : self.token(Tokentype.OPERATOR),
        '!=' : lambda self : self.token(Tokentype.OPERATOR),
        '='  : lambda self : self.token(Tokentype.OPERATOR),
        '+'  : lambda self : self.token(Tokentype.OPERATOR),
        '-'  : lambda self : self.token(Tokentype.OPERATOR),
        '*'  : lambda self : self.token(Tokentype.OPERATOR),
        '/'  : lambda self : self.token(Tokentype.OPERATOR),
        '<'  : lambda self : self.token(Tokentype.OPERATOR),
        '>'  : lambda self : self.token(Tokentype.OPERATOR),
        '~'  : lambda self : self.token(Tokentype.OPERATOR),
        '^'  : lambda self : self.token(Tokentype.OPERATOR),
        '&'  : lambda self : self.token(Tokentype.OPERATOR),
        '|'  : lambda self : self.token(Tokentype.OPERATOR),
        '@'  : lambda self : self.token(Tokentype.OPERATOR),
        '%'  : lambda self : self.token(Tokentype.OPERATOR),
        ':'  : lambda self : self.token(Tokentype.OPERATOR),
        ';'  : lambda self : self.token(Tokentype.OPERATOR),
        ','  : lambda self : self.token(Tokentype.OPERATOR),
        '.'  : lambda self : self.token(Tokentype.OPERATOR),

        '('  : lambda self : self.parenthetical('('),
        ')'  : lambda self : self.parenthetical('(', ')'),
        '['  : lambda self : self.parenthetical('['),
        ']'  : lambda self : self.parenthetical('[', ']'),
        '{'  : lambda self : self.parenthetical('{'),
        '}'  : lambda self : self.parenthetical('{', '}'),

        'A'  : lambda self : self.identifier_or_keyword(),
        'B'  : lambda self : self.identifier_or_keyword(),
        'C'  : lambda self : self.identifier_or_keyword(),
        'D'  : lambda self : self.identifier_or_keyword(),
        'E'  : lambda self : self.identifier_or_keyword(),
        'F'  : lambda self : self.identifier_or_keyword(),
        'G'  : lambda self : self.identifier_or_keyword(),
        'H'  : lambda self : self.identifier_or_keyword(),
        'I'  : lambda self : self.identifier_or_keyword(),
        'J'  : lambda self : self.identifier_or_keyword(),
        'K'  : lambda self : self.identifier_or_keyword(),
        'L'  : lambda self : self.identifier_or_keyword(),
        'M'  : lambda self : self.identifier_or_keyword(),
        'N'  : lambda self : self.identifier_or_keyword(),
        'O'  : lambda self : self.identifier_or_keyword(),
        'P'  : lambda self : self.identifier_or_keyword(),
        'Q'  : lambda self : self.identifier_or_keyword(),
        'R'  : lambda self : self.identifier_or_keyword(),
        'S'  : lambda self : self.identifier_or_keyword(),
        'T'  : lambda self : self.identifier_or_keyword(),
        'U'  : lambda self : self.identifier_or_keyword(),
        'V'  : lambda self : self.identifier_or_keyword(),
        'W'  : lambda self : self.identifier_or_keyword(),
        'X'  : lambda self : self.identifier_or_keyword(),
        'Y'  : lambda self : self.identifier_or_keyword(),
        'Z'  : lambda self : self.identifier_or_keyword(),
        'a'  : lambda self : self.identifier_or_keyword(),
        'b'  : lambda self : self.identifier_or_keyword(),
        'c'  : lambda self : self.identifier_or_keyword(),
        'd'  : lambda self : self.identifier_or_keyword(),
        'e'  : lambda self : self.identifier_or_keyword(),
        'f'  : lambda self : self.identifier_or_keyword(),
        'g'  : lambda self : self.identifier_or_keyword(),
        'h'  : lambda self : self.identifier_or_keyword(),
        'i'  : lambda self : self.identifier_or_keyword(),
        'j'  : lambda self : self.identifier_or_keyword(),
        'k'  : lambda self : self.identifier_or_keyword(),
        'l'  : lambda self : self.identifier_or_keyword(),
        'm'  : lambda self : self.identifier_or_keyword(),
        'n'  : lambda self : self.identifier_or_keyword(),
        'o'  : lambda self : self.identifier_or_keyword(),
        'p'  : lambda self : self.identifier_or_keyword(),
        'q'  : lambda self : self.identifier_or_keyword(),
        'r'  : lambda self : self.identifier_or_keyword(),
        's'  : lambda self : self.identifier_or_keyword(),
        't'  : lambda self : self.identifier_or_keyword(),
        'u'  : lambda self : self.identifier_or_keyword(),
        'v'  : lambda self : self.identifier_or_keyword(),
        'w'  : lambda self : self.identifier_or_keyword(),
        'x'  : lambda self : self.identifier_or_keyword(),
        'y'  : lambda self : self.identifier_or_keyword(),
        'z'  : lambda self : self.identifier_or_keyword(),
        '_'  : lambda self : self.identifier_or_keyword(),

        '0Δ' : lambda self : self.numeric(Tokentype.BASE36),
        '0δ' : lambda self : self.numeric(Tokentype.BASE36),
        '0X' : lambda self : self.numeric(Tokentype.BASE16),
        '0x' : lambda self : self.numeric(Tokentype.BASE16),
        '0O' : lambda self : self.numeric(Tokentype.BASE08),
        '0o' : lambda self : self.numeric(Tokentype.BASE08),
        '0B' : lambda self : self.numeric(Tokentype.BASE02),
        '0b' : lambda self : self.numeric(Tokentype.BASE02),
        '.0' : lambda self : self.numeric(Tokentype.BASE10),
        '.1' : lambda self : self.numeric(Tokentype.BASE10),
        '.2' : lambda self : self.numeric(Tokentype.BASE10),
        '.3' : lambda self : self.numeric(Tokentype.BASE10),
        '.4' : lambda self : self.numeric(Tokentype.BASE10),
        '.5' : lambda self : self.numeric(Tokentype.BASE10),
        '.6' : lambda self : self.numeric(Tokentype.BASE10),
        '.7' : lambda self : self.numeric(Tokentype.BASE10),
        '.8' : lambda self : self.numeric(Tokentype.BASE10),
        '.9' : lambda self : self.numeric(Tokentype.BASE10),
        '0'  : lambda self : self.numeric(Tokentype.BASE10),
        '1'  : lambda self : self.numeric(Tokentype.BASE10),
        '2'  : lambda self : self.numeric(Tokentype.BASE10),
        '3'  : lambda self : self.numeric(Tokentype.BASE10),
        '4'  : lambda self : self.numeric(Tokentype.BASE10),
        '5'  : lambda self : self.numeric(Tokentype.BASE10),
        '6'  : lambda self : self.numeric(Tokentype.BASE10),
        '7'  : lambda self : self.numeric(Tokentype.BASE10),
        '8'  : lambda self : self.numeric(Tokentype.BASE10),
        '9'  : lambda self : self.numeric(Tokentype.BASE10),

        '#'  : lambda self : self.comment(),

        ' '  : lambda self : self.consume(), # ignore
        '\t' : lambda self : self.consume(), # ignore

        '\\\r\n' : lambda self : self.consume(),
        '\\\n'   : lambda self : self.consume(),
        '\r\n'   : lambda self : self.newline(),
        '\n'     : lambda self : self.newline(),
        '\\'     : lambda self : self.backslash_error(),

    })


    # ------------------------------------------------------------------------------------------
    # --------------- TOKENIZER :: Generate Tokens from Raw Outfoxed Source Code ---------------
    # ------------------------------------------------------------------------------------------
    def lex(self) -> Iterator[Token]:

        while self.end < self.length:

            prefix = self.source[self.start : self.start + 3]

            if tokenizer := self.Fox_Prefix_Map[prefix[:3]]:

                self.advance(3)
                yield from tokenizer(self); continue

            if tokenizer := self.Fox_Prefix_Map[prefix[:2]]:

                self.advance(2)
                yield from tokenizer(self); continue

            if tokenizer := self.Fox_Prefix_Map[prefix[:1]]:

                self.advance(1)
                yield from tokenizer(self); continue

            raise SyntaxError(f"unrecognized character: {repr(self.observe())}")

        yield from self.eof()
