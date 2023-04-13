# --------------------------------------------------------------------------------------------------
# --------------------------------- PRE-PARSING :: Assignment Node ---------------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token

from .  Expression import Expression
from .  Identifier import Identifier
from .  Error      import Error

from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# ------------------------------------ CLASS :: Assignment Node ------------------------------------
# --------------------------------------------------------------------------------------------------
class Assignment(Expression):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    identifier : Error | Identifier
    expression : Error | Expression


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, identifier: Error | Identifier, expression: Error | Expression) -> None:

        self.identifier = identifier
        self.expression = expression


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def stringify(self) -> str:

        identifier = self.identifier.token.literal
        expression = self.expression.__class__.__name__

        return f"Assignment(Identifier('{identifier}'), '{expression}')"

    def __repr__(self) -> str:
        return self.stringify()

    def __str__(self) -> str:
        return self.stringify()


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_assignment(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.identifier.start

    @property
    def end(self) -> Token:
        return self.expression.end