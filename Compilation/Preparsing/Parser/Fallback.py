# --------------------------------------------------------------------------------------------------
# ---------------------------- PRE-PARSING :: Parser Exception Handler -----------------------------
# --------------------------------------------------------------------------------------------------
from .. Lexer.Tokentype import Tokentype
from .. Lexer.Token     import Token
from .. Lexer.Lexer     import Lexer


# --------------------------------------------------------------------------------------------------
# ------------------------------- CLASS :: Parser Exception Handler --------------------------------
# --------------------------------------------------------------------------------------------------
class Fallback(object):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------------------
    # ------------------------------- CONSTRUCTOR :: Constructor -------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self) -> None:
        ...