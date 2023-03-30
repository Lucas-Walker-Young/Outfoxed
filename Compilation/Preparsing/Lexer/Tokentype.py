# --------------------------------------------------------------------------------------------------
# --------------------------------- PRE-PARSING :: Tokentype Enum ----------------------------------
# --------------------------------------------------------------------------------------------------
from enum import IntFlag
from enum import auto


# --------------------------------------------------------------------------------------------------
# ------------------------------------- ENUM :: Tokentype Enum -------------------------------------
# --------------------------------------------------------------------------------------------------
class Tokentype(IntFlag):

    IDENTIFIER     = auto()
    STRING         = auto()
    NUMBER         = auto()

    L_PAREN        = auto()
    R_PAREN        = auto()
    L_BRACK        = auto()
    R_BRACK        = auto()
    L_BRACE        = auto()
    R_BRACE        = auto()

    WALRUS         = auto()
    ASSIGN         = auto()
    COMMA          = auto()
    PIPE           = auto()
    PLUS           = auto()
    STAR           = auto()
    PLUS_PLUS      = auto()
    STAR_STAR      = auto()

    ASSIGNMENT     = auto()
    ALTERNATION    = auto()
    QUANTIFICATION = auto()
    CONCATENATION  = auto()

    EOL = auto()
    EOF = auto()


