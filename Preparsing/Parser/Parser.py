# --------------------------------------------------------------------------------------------------
# ------------------------------------- PRE-PARSING :: Parser --------------------------------------
# --------------------------------------------------------------------------------------------------
from .. Lexer.Tokentype     import Tokentype
from .. Lexer.Token         import Token
from .. Lexer.Lexer         import Lexer

from .. Nodes.Alternation   import Alternation
from .. Nodes.Annotation    import Annotation
from .. Nodes.Assignment    import Assignment
from .. Nodes.Call          import Call
from .. Nodes.Concatenation import Concatenation
from .. Nodes.Definition    import Definition
from .. Nodes.Error         import Error
from .. Nodes.Expression    import Expression
from .. Nodes.Identifier    import Identifier
from .. Nodes.Literal       import Literal
from .. Nodes.Node          import Node
from .. Nodes.Number        import Number
from .. Nodes.Optional      import Optional
from .. Nodes.Output        import Output
from .. Nodes.Parenthetical import Parenthetical
from .. Nodes.Plus          import Plus
from .. Nodes.Production    import Production
from .. Nodes.Pseudo        import Pseudo
from .. Nodes.Root          import Root
from .. Nodes.Sequence      import Sequence
from .. Nodes.Signature     import Signature
from .. Nodes.Star          import Star
from .. Nodes.String        import String

from .. Visitors.Printer    import Printer
from  . Fallback            import Fallback

from typing import TypeVar
from typing import Type

R = TypeVar('R', bound=Node)


# --------------------------------------------------------------------------------------------------
# ---------------------------------------- CLASS :: Parser -----------------------------------------
# --------------------------------------------------------------------------------------------------
class Parser(object):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    fallback : Fallback
    lexer    : Lexer

    origin   : str


    # ------------------------------------------------------------------------------------------
    # ------------------------------- CONSTRUCTOR :: Constructor -------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, origin: str) -> None:

        self.lexer    = Lexer(origin)
        self.fallback = Fallback()

        self.origin   = origin


    # ------------------------------------------------------------------------------------------
    # ---------------------------- HELPER :: Consume the Next Token ----------------------------
    # ------------------------------------------------------------------------------------------
    def advance(self) -> Token:
        return self.lexer.next()


    # ------------------------------------------------------------------------------------------
    # ---------------------------- HELPER :: Observe the Next Token ----------------------------
    # ------------------------------------------------------------------------------------------
    def observe(self) -> Token:
        return self.lexer.peek()


    # ------------------------------------------------------------------------------------------
    # ----------------------- HELPER :: Match and Consume the Next Token -----------------------
    # ------------------------------------------------------------------------------------------
    def consume(self, tokentype: Tokentype) ->  Token | None:

        if (token := self.observe()) and token.type & tokentype:
            return self.advance()

        return


    # ------------------------------------------------------------------------------------------
    # ---------------------------------- HELPER :: Lookaheads ----------------------------------
    # ------------------------------------------------------------------------------------------
    def positive_lookahead(self, tokentype: Tokentype) -> Token | None:
        return (token := self.observe()) and token.type & tokentype

    def negative_lookahead(self, tokentype: Tokentype) -> Token | None:
        return not self.positive_lookahead(tokentype)


    # ------------------------------------------------------------------------------------------
    # ----------------------------- PARSER :: Parse an Identifier ------------------------------
    # ------------------------------------------------------------------------------------------
    def identifier(self) -> Error | Identifier:
        return Identifier(self.consume(Tokentype.IDENTIFIER))


    # ------------------------------------------------------------------------------------------
    # -------------------------- PARSER :: Parse an Atomic Annotation --------------------------
    # ------------------------------------------------------------------------------------------
    def atom_annotation(self) -> Error | Expression:

        if self.positive_lookahead(Tokentype.L_PAREN):

            self.consume(Tokentype.L_PAREN)
            annotation = self.mult_annotation()
            self.consume(Tokentype.R_PAREN)

            return Parenthetical(annotation)

        return self.identifier()


    # ------------------------------------------------------------------------------------------
    # --------------------- PARSER :: Parse an Alternation of Annotations ----------------------
    # ------------------------------------------------------------------------------------------
    def star_annotation(self) -> Error | Expression:

        if self.consume(Tokentype.STAR):
            return Star(self.atom_annotation())

        return self.atom_annotation()


    # ------------------------------------------------------------------------------------------
    # --------------------- PARSER :: Parse an Alternation of Annotations ----------------------
    # ------------------------------------------------------------------------------------------
    def pipe_annotation(self) -> Error | Expression:

        annotations = [ annotation := self.star_annotation() ]

        if self.positive_lookahead(Tokentype.PIPE):

            while self.consume(Tokentype.PIPE):
                annotations.append(self.star_annotation())

            return Alternation(annotations)

        return annotation


    # ------------------------------------------------------------------------------------------
    # ----------------------- PARSER :: Parse a Sequence of Annotations ------------------------
    # ------------------------------------------------------------------------------------------
    def mult_annotation(self) -> Error | Expression:

        annotations = [ annotation := self.pipe_annotation() ]

        if self.positive_lookahead(Tokentype.COMMA):

            while self.consume(Tokentype.COMMA):
                annotations.append(self.pipe_annotation())

            return Sequence(*annotations)

        return annotation


    # ------------------------------------------------------------------------------------------
    # ----------------------------- PARSER :: Parse an Annotation ------------------------------
    # ------------------------------------------------------------------------------------------
    def annotation(self) -> Error | Annotation:

        self.consume(Tokentype.L_BRACK)
        annotation = Annotation(self.mult_annotation())
        self.consume(Tokentype.R_BRACK)

        return annotation


    # ------------------------------------------------------------------------------------------
    # -------------------------- PARSER :: Parse an Atomic Parameter ---------------------------
    # ------------------------------------------------------------------------------------------
    def atom_parameter(self) -> Error | Expression:

        identifier = self.identifier()

        if self.positive_lookahead(Tokentype.L_PAREN):

            self.consume(Tokentype.L_PAREN)
            parameters = self.mult_parameter()
            self.consume(Tokentype.R_PAREN)

            return Call(identifier, parameters)

        return identifier


    # ------------------------------------------------------------------------------------------
    # -------------------------- PARSER :: Parse a Starred Parameter ---------------------------
    # ------------------------------------------------------------------------------------------
    def star_parameter(self) -> Error | Expression:

        if self.consume(Tokentype.STAR):
            return Star(self.atom_parameter())

        return self.atom_parameter()


    # ------------------------------------------------------------------------------------------
    # ------------------------ PARSER :: Parse a Sequence of Parameters ------------------------
    # ------------------------------------------------------------------------------------------
    def mult_parameter(self) -> Error | Expression:

        parameters = [ parameter := self.star_parameter() ]

        if self.positive_lookahead(Tokentype.COMMA):

            while self.consume(Tokentype.COMMA):
                parameters.append(self.star_parameter())

            return Sequence(*parameters)

        return parameter


    # ------------------------------------------------------------------------------------------
    # ---------------------------- PARSER :: Parse an Atomic Output ----------------------------
    # ------------------------------------------------------------------------------------------
    def atom_output(self) -> Error | Expression:

        identifier = self.identifier()

        if self.positive_lookahead(Tokentype.L_PAREN):

            self.consume(Tokentype.L_PAREN)
            parameters = self.mult_parameter()
            self.consume(Tokentype.R_PAREN)

            return Call(identifier, parameters)

        return identifier


    # ------------------------------------------------------------------------------------------
    # ------------------------- PARSER :: Parse a Sequence of Outputs --------------------------
    # ------------------------------------------------------------------------------------------
    def mult_output(self) -> Error | Expression:

        outputs = [ output := self.atom_output() ]

        if self.positive_lookahead(Tokentype.COMMA):

            while self.consume(Tokentype.COMMA):
                outputs.append(self.atom_output())

            return Sequence(*outputs)

        return output


    # ------------------------------------------------------------------------------------------
    # ------------------------------- PARSER :: Parse an Output --------------------------------
    # ------------------------------------------------------------------------------------------
    def output(self) -> Error | Output:

        if self.positive_lookahead(Tokentype.L_BRACE):

            self.consume(Tokentype.L_BRACE)
            output = self.mult_output()
            self.consume(Tokentype.R_BRACE)

            return Output(output)


    # ------------------------------------------------------------------------------------------
    # ------------------------ PARSER :: Parse an Outfoxed Grammar File ------------------------
    # ------------------------------------------------------------------------------------------
    def signature(self) -> Error | Signature:

        identifier = self.identifier()
        annotation = self.annotation()

        return Signature(identifier, annotation)


    # ------------------------------------------------------------------------------------------
    # -------------------------- PARSER :: Parse an Atomic Expression --------------------------
    # ------------------------------------------------------------------------------------------
    def atomic(self) -> Error | Expression:

        if token := self.consume(Tokentype.IDENTIFIER):
            return Identifier(token)

        if token := self.consume(Tokentype.NUMBER):
            return Number(token)

        if token := self.consume(Tokentype.STRING):
            return String(token)


    # ------------------------------------------------------------------------------------------
    # ----------------------- PARSER :: Parse a Parenthetical Expression -----------------------
    # ------------------------------------------------------------------------------------------
    def parenthetical(self) -> Error | Expression:

        if self.positive_lookahead(Tokentype.L_PAREN):

            self.consume(Tokentype.L_PAREN)
            expression = self.expression()
            output     = self.output()
            self.consume(Tokentype.R_PAREN)

            return Parenthetical(expression)

        if self.positive_lookahead(Tokentype.L_BRACK):

            self.consume(Tokentype.L_BRACK)
            expression = self.expression()
            output     = self.output()
            self.consume(Tokentype.R_BRACK)

            return Optional(expression)

        return self.atomic()


    # ------------------------------------------------------------------------------------------
    # ------------------------ PARSER :: Parse an Assignment Expression ------------------------
    # ------------------------------------------------------------------------------------------
    def assignment(self) -> Error | Expression:

        if self.positive_lookahead(Tokentype.IDENTIFIER):

            identifier = self.identifier()

            if self.consume(Tokentype.ASSIGN):
                return Assignment(identifier, self.parenthetical())

            return identifier

        return self.parenthetical()


    # ------------------------------------------------------------------------------------------
    # ------------------------ PARSER :: Parse a Repetition Expression -------------------------
    # ------------------------------------------------------------------------------------------
    def repetition(self) -> Error | Expression:

        expression = self.assignment()

        if self.consume(Tokentype.STAR):
            return Star(expression)

        if self.consume(Tokentype.PLUS):
            return Plus(expression)

        return expression


    # ------------------------------------------------------------------------------------------
    # ----------------------- PARSER :: Parse a Concatenation Expression -----------------------
    # ------------------------------------------------------------------------------------------
    def concatenation(self) -> Error | Expression:

        expressions = [ expression := self.repetition() ]

        headtype  = Tokentype.IDENTIFIER
        headtype |= Tokentype.STRING
        headtype |= Tokentype.NUMBER
        headtype |= Tokentype.L_PAREN
        headtype |= Tokentype.L_BRACK

        if self.positive_lookahead(headtype):

            while self.positive_lookahead(headtype):
                expressions.append(self.repetition())

            return Concatenation(tuple(expressions))

        return expression


    # ------------------------------------------------------------------------------------------
    # --------------------- PARSER :: Parse an Alternation of Expressions ----------------------
    # ------------------------------------------------------------------------------------------
    def alternation(self) -> Error | Expression:

        expressions = [ expression := self.concatenation() ]

        if self.positive_lookahead(Tokentype.PIPE):

            while self.consume(Tokentype.PIPE):
                expressions.append(self.concatenation())

            return Alternation(tuple(expressions))

        return expression


    # ------------------------------------------------------------------------------------------
    # ----------------------------- PARSER :: Parse an Expression ------------------------------
    # ------------------------------------------------------------------------------------------
    def expression(self) -> Error | Expression:
        return self.alternation()


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PARSER :: Parse a Production ------------------------------
    # ------------------------------------------------------------------------------------------
    def production(self) -> Error | Production:
        return Production(self.expression(), self.output())


    # ------------------------------------------------------------------------------------------
    # ----------------------- PARSER :: Parse a Sequence of Productions ------------------------
    # ------------------------------------------------------------------------------------------
    def productions(self) -> Error | Sequence:

        if self.positive_lookahead(Tokentype.EOL):

            productions : list[ Error | Production ] = []

            while self.consume(Tokentype.EOL) and self.consume(Tokentype.PIPE):
                productions.append(self.production())

            return Sequence(*productions)

        return Sequence(self.production())


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PARSER :: Parse a Definition ------------------------------
    # ------------------------------------------------------------------------------------------
    def definition(self) -> Error | Definition:

        signature = self.signature()
        walrus = self.consume(Tokentype.WALRUS)
        productions = self.productions()

        return Definition(signature, productions)


    # ------------------------------------------------------------------------------------------
    # ------------------------ PARSER :: Parse an Outfoxed Grammar File ------------------------
    # ------------------------------------------------------------------------------------------
    def parse(self) -> Error | Root:

        definitions : list[Error | Definition, ...] = []

        while True:

            if self.consume(Tokentype.EOL):
                continue

            if self.consume(Tokentype.EOF):
                break

            definitions.append(self.definition())

        return Root(self.origin, Sequence(*definitions))
