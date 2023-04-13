# --------------------------------------------------------------------------------------------------
# --------------------------------- PRE-PARSING :: Production Node ---------------------------------
# --------------------------------------------------------------------------------------------------
from .. Visitors.Visitor import Visitor
from .. Lexer.Token      import Token

from .  Expression  import Expression
from .  Error       import Error

from typing import Optional
from typing import TypeVar
R = TypeVar('R')


# --------------------------------------------------------------------------------------------------
# ------------------------------------ CLASS :: Production Node ------------------------------------
# --------------------------------------------------------------------------------------------------
class Production(Expression):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    lookahead  : Error | Expression | None
    expression : Error | Expression
    output     : Error | Expression | None


    # ------------------------------------------------------------------------------------------
    # ------------------------------ CONSTRUCTION :: Construction ------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self,
        expression: Error | Expression, output : Optional[Error | Expression] = None,
    ) -> None:

        self.expression = expression
        self.output     = output


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def stringify(self) -> str:

        expression = self.expression.__class__.__name__
        output     = self.output.__class__.__name__

        return f"Production('{expression}', '{output}')"

    def __repr__(self) -> str:
        return self.stringify()

    def __str__(self) -> str:
        return self.stringify()


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITATION :: Accept Visitor ------------------------------
    # ------------------------------------------------------------------------------------------
    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_production(self)


    # ------------------------------------------------------------------------------------------
    # ------------------------------ PROPERTIES :: Bounds of Node ------------------------------
    # ------------------------------------------------------------------------------------------
    @property
    def start(self) -> Token:
        return self.expression.start

    @property
    def end(self) -> Token:
        return self.output.end if self.output else self.expression.end