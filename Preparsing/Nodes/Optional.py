# --------------------------------------------------------------------------------------------------
# ---------------------------------- PRE-PARSING :: Optional Node ----------------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token

from .  Expression import Expression
from .  Error      import Error

from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# ------------------------------------ CLASS :: Assignment Node ------------------------------------
# --------------------------------------------------------------------------------------------------
class Optional(Expression):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    expression : Error | Expression
    output     : Error | Expression | None


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self,
              expression: Error | Expression, output: None | Error | Expression = None) -> None:

        self.expression = expression
        self.output     = output


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def stringify(self) -> str:

        expression = self.expression.__class__.__name__
        output     = self.output.__class__.__name__

        if self.output:
            return f"Optional('{expression}', '{output}')"

        return f"Optional('{expression}')"

    def __repr__(self) -> str:
        return self.stringify()

    def __str__(self) -> str:
        return self.stringify()


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_optional(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.expression.start

    @property
    def end(self) -> Token:
        return self.output.end if self.output else self.expression.end