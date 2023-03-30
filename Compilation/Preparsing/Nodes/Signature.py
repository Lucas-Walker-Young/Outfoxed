# --------------------------------------------------------------------------------------------------
# --------------------------------- PRE-PARSING :: Signature Node ----------------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token

from .  Identifier import Identifier
from .  Annotation import Annotation
from .  Node  import Node
from .  Error import Error

from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# ------------------------------------ CLASS :: Signature Node -------------------------------------
# --------------------------------------------------------------------------------------------------
class Signature(Node):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    identifier : Error | Identifier
    annotation : Error | Annotation


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, identifier: Error | Identifier, annotation: Error | Annotation) -> None:

        self.identifier = identifier
        self.annotation = annotation


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Signature('{self.identifier.token.literal}')"

    def __str__(self) -> str:
        return f"Signature('{self.identifier.token.literal}')"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_signature(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.identifier.start

    @property
    def end(self) -> Token:
        return self.annotation.end