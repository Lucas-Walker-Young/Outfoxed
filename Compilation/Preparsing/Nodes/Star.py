# --------------------------------------------------------------------------------------------------
# --------------------------- PRE-PARSING :: Kleene-Star-Repetition Node ---------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token

from .  Expression  import Expression
from .  Error       import Error

from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# ---------------------------------- CLASS :: Concatenation Node -----------------------------------
# --------------------------------------------------------------------------------------------------
class Star(Expression):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    expression : Error | Expression


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, expression: Error | Expression) -> None:
        self.expression = expression


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Star('{self.expression.__class__.__name__}')"

    def __str__(self) -> str:
        return f"Star('{self.expression.__class__.__name__}')"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_star(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.expression.start

    @property
    def end(self) -> Token:
        return self.expression.end