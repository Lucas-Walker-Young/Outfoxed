# --------------------------------------------------------------------------------------------------
# -------------------------- PRE-PARSING :: Pretty-Printer Visitor Class ---------------------------
# --------------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. Nodes.Alternation   import Alternation
    from .. Nodes.Annotation    import Annotation
    from .. Nodes.Assignment    import Assignment
    from .. Nodes.Call          import Call
    from .. Nodes.Concatenation import Concatenation
    from .. Nodes.Definition    import Definition
    from .. Nodes.Error         import Error
    from .. Nodes.Expression    import Expression
    from .. Nodes.Identifier    import Identifier
    from .. Nodes.Literal       import Literal
    from .. Nodes.Node          import Node
    from .. Nodes.Number        import Number
    from .. Nodes.Optional      import Optional
    from .. Nodes.Output        import Output
    from .. Nodes.Parenthetical import Parenthetical
    from .. Nodes.Plus          import Plus
    from .. Nodes.Production    import Production
    from .. Nodes.Pseudo        import Pseudo
    from .. Nodes.Root          import Root
    from .. Nodes.Sequence      import Sequence
    from .. Nodes.Signature     import Signature
    from .. Nodes.Star          import Star
    from .. Nodes.String        import String

from . Visitor import Visitor


# --------------------------------------------------------------------------------------------------
# ----------------------------- CLASS :: Pretty-Printer Visitor Class ------------------------------
# --------------------------------------------------------------------------------------------------
class Printer(Visitor[str]):

    # ------------------------------------------------------------------------------------------
    # -------------------------------- ATTRIBUTES :: Attributes --------------------------------
    # ------------------------------------------------------------------------------------------
    indentation : int


    # ------------------------------------------------------------------------------------------
    # ------------------------------- CONSTRUCTOR :: Constructor -------------------------------
    # ------------------------------------------------------------------------------------------
    def __init__(self, indentation: int = 0) -> None:
        self.indentation = indentation


    # ------------------------------------------------------------------------------------------
    # --------------------------- STRINGIFICATION :: Stringification ---------------------------
    # ------------------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Printer(indentation={self.indentation})"

    def __str__(self)  -> str:
        return f"Printer(indentation={self.indentation})"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ HELPER :: Get Head and Tail -------------------------------
    # ------------------------------------------------------------------------------------------
    def affixes(self, node: 'Node') -> tuple[str, str]:

        head = f"{'    ' * self.indentation}{node.__class__.__name__}("
        tail = f"{'    ' * self.indentation})"

        return head, tail


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITOR :: Visit Alternation ------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_alternation(self, node: 'Alternation') -> str:

        subprinter = Printer(self.indentation + 1)
        body = '\n'.join(child.accept(subprinter) for child in node.expressions)

        head, tail = self.affixes(node)

        return f"{head}\n{body}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITOR :: Visit Annotation -------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_annotation(self, node: 'Annotation') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        body = node.expression.accept(subprinter)

        return f"{head}\n{body}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITOR :: Visit Assignment -------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_assignment(self, node: 'Assignment') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        identifier = node.identifier.accept(subprinter)
        expression = node.expression.accept(subprinter)

        return f"{head}\n{identifier}\n{expression}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # --------------------------------- VISITOR :: Visit Call ----------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_call(self, node: 'Call') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        identifier = node.identifier.accept(subprinter)
        parameters = node.parameters.accept(subprinter)

        return f"{head}\n{identifier}\n{parameters}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # ----------------------------- VISITOR :: Visit Concatenation -----------------------------
    # ------------------------------------------------------------------------------------------
    def visit_concatenation(self, node: 'Concatenation') -> str:

        subprinter = Printer(self.indentation + 1)
        body = '\n'.join(child.accept(subprinter) for child in node.expressions)

        head, tail = self.affixes(node)

        return f"{head}\n{body}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITOR :: Visit Definition -------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_definition(self, node: 'Definition') -> str:

        head, tail  = self.affixes(node)

        subprinter  = Printer(self.indentation + 1)
        signature   = node.signature.accept(subprinter)
        productions = node.productions.accept(subprinter)

        return f"{head}\n{signature}\n{productions}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # --------------------------------- VISITOR :: Visit Error ---------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_error(self, node: 'Error') -> str:
        ...


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITOR :: Visit Expression -------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_generic(self, node: 'Node') -> str:
        ...
    

    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITOR :: Visit Identifier -------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_identifier(self, node: 'Identifier') -> str:
        return f"{'    ' * self.indentation}Identifier('{node.token.literal}')"


    # ------------------------------------------------------------------------------------------
    # -------------------------------- VISITOR :: Visit Number ---------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_number(self, node: 'Number') -> str:
        return f"{'    ' * self.indentation}Number('{node.token.literal}')"


    # ------------------------------------------------------------------------------------------
    # ------------------------------- VISITOR :: Visit Optional --------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_optional(self, node: 'Optional') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        expression = node.expression.accept(subprinter)

        if node.output and (output := node.output.accept(subprinter)):
            return f"{head}\n{expression}\n{output}\n{tail}"

        return f"{head}\n{expression}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # -------------------------------- VISITOR :: Visit Output ---------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_output(self, node: 'Output') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        body = node.expression.accept(subprinter)

        return f"{head}\n{body}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # ----------------------------- VISITOR :: Visit Parenthetical -----------------------------
    # ------------------------------------------------------------------------------------------
    def visit_parenthetical(self, node: 'Parenthetical') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        expression = node.expression.accept(subprinter)

        if node.output and (output := node.output.accept(subprinter)):
            return f"{head}\n{expression}\n{output}\n{tail}"

        return f"{head}\n{expression}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # --------------------------------- VISITOR :: Visit Plus ----------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_plus(self, node: 'Plus') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        body = node.expression.accept(subprinter)

        return f"{head}\n{body}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # ------------------------------ VISITOR :: Visit Production -------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_production(self, node: 'Production') -> str:

        subprinter  = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        expression = node.expression.accept(subprinter)

        if node.output and (output := node.output.accept(subprinter)):
            return f"{head}\n{expression}\n{output}\n{tail}"

        return f"{head}\n{expression}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # -------------------------------- VISITOR :: Visit Pseudo ---------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_pseudo(self, node: 'Pseudo') -> str:
        ...


    # ------------------------------------------------------------------------------------------
    # --------------------------------- VISITOR :: Visit Root ----------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_root(self, node: 'Root') -> str:

        subprinter  = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        body = node.definitions.accept(subprinter)

        return f"{head}\n{body}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # ------------------------------- VISITOR :: Visit Sequence --------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_sequence(self, node: 'Sequence') -> str:

        if node.elements:

            subprinter = Printer(self.indentation + 1)
            body = '\n'.join(element.accept(subprinter) for element in node.elements)

            head, tail = self.affixes(node)

            return f"{head}\n{body}\n{tail}"

        return f"{'    ' * self.indentation}Sequence()"


    # ------------------------------------------------------------------------------------------
    # ------------------------------- VISITOR :: Visit Sequence --------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_signature(self, node: 'Signature') -> str:

        subprinter  = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        identifier = node.identifier.accept(subprinter)
        annotation = node.annotation.accept(subprinter)

        return f"{head}\n{identifier}\n{annotation}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # --------------------------------- VISITOR :: Visit Star ----------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_star(self, node: 'Star') -> str:

        subprinter = Printer(self.indentation + 1)

        head, tail = self.affixes(node)
        body = node.expression.accept(subprinter)

        return f"{head}\n{body}\n{tail}"


    # ------------------------------------------------------------------------------------------
    # -------------------------------- VISITOR :: Visit String ---------------------------------
    # ------------------------------------------------------------------------------------------
    def visit_string(self, node: 'String') -> str:
        return f"{'    ' * self.indentation}String('{node.token.literal}')"


    # ------------------------------------------------------------------------------------------
    # ----------------------------- STATIC :: Pretty-Print an AST ------------------------------
    # ------------------------------------------------------------------------------------------
    @staticmethod
    def print(root: 'Node') -> str:
        print(root.accept(Printer(indentation=0)))