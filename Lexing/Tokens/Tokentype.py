# --------------------------------------------------------------------------------------------------
# ------------------------------------ LEXING :: Tokentype Enum ------------------------------------
# --------------------------------------------------------------------------------------------------
from enum import IntFlag
from enum import auto


# --------------------------------------------------------------------------------------------------
# --------------------------------------- ENUM :: Tokentype ----------------------------------------
# --------------------------------------------------------------------------------------------------
class Tokentype(IntFlag):

	IDENTIFIER 	 = auto()
	COMMENT 	 = auto()
	KEYWORD 	 = auto()
	OPERATOR 	 = auto()
	DELIMITER 	 = auto()

	SINGLE_QUOTE = auto()
	DOUBLE_QUOTE = auto()
	TRIPLE_QUOTE = auto()
	F_STRING 	 = auto()
	R_STRING 	 = auto()

	NUMBER  	 = auto()
	INTEGER 	 = auto()
	FLOAT 	 	 = auto()
	EPSILON 	 = auto()
	COMPLEX 	 = auto()
	BASE36 	  	 = auto()
	BASE16 	  	 = auto()
	BASE10 		 = auto()
	BASE08 		 = auto()
	BASE02 		 = auto()

	NEWLINE		 = auto()
	INDENT 		 = auto()
	DEDENT 		 = auto()

	EOF 		 = auto()