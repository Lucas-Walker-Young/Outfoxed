# --------------------------------------------------------------------------------------------------
# ------------------------------------ PRE-PARSING :: Call Node ------------------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token

from .  Expression  import Expression
from .  Identifier  import Identifier
from .  Sequence    import Sequence
from .  Error       import Error

from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# ------------------------------------ CLASS :: Assignment Node ------------------------------------
# --------------------------------------------------------------------------------------------------


class Call(Expression):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    identifier : Error | Identifier
    parameters : Error | Sequence


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, identifier: Error | Identifier, parameters: Error | Sequence) -> None:

        self.identifier = identifier
        self.parameters = parameters


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Call('{self.identifier.token.literal}')"

    def __str__(self) -> str:
        return f"Call('{self.identifier.token.literal}')"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_call(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.identifier.start

    @property
    def end(self) -> Token:
        return self.parameters[-1].end if self.parameters else self.identifier.end