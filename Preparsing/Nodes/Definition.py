# --------------------------------------------------------------------------------------------------
# --------------------------------- PRE-PARSING :: Definition Node ---------------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token

from .  Signature import Signature
from .  Sequence  import Sequence
from .  Node      import Node
from .  Error     import Error

from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# ------------------------------------ CLASS :: Definition Node ------------------------------------
# --------------------------------------------------------------------------------------------------
class Definition(Node):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    signature   : Error | Signature
    productions : Error | Sequence


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, signature: Error | Signature, productions: Error | Sequence) -> None:

        self.signature   = signature
        self.productions = productions


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Definition('{self.signature.identifier.token.literal}')"

    def __str__(self) -> str:
        return f"Definition('{self.signature.identifier.token.literal}')"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_definition(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.signature.start

    @property
    def end(self) -> Token:
        return self.productions.end