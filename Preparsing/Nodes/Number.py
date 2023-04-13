# --------------------------------------------------------------------------------------------------
# ----------------------------------- PRE-PARSING :: Number Node -----------------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token
from .  Literal  import Literal

from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# -------------------------------------- CLASS :: Number Node --------------------------------------
# --------------------------------------------------------------------------------------------------
class Number(Literal):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    token : Token


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, token: Token) -> None:
        self.token  =  token


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Number('{self.token.literal}')"

    def __str__(self) -> str:
        return f"Number('{self.token.literal}')"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_number(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.token

    @property
    def end(self) -> Token:
        return self.token