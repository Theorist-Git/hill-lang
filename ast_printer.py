from expr import Visitor, Expr, BinaryExpr, UnaryExpr, GroupExpr, LiteralExpr
from hill_token import Token, TokenType


class AstPrinter(Visitor):
    def __init__(self, reverse_polish_notation=False):
        self.reverse_polish_notation = reverse_polish_notation

    def print(self, expr: Expr):
        return expr.accept(self)

    def visit_binaryexpr(self, expr: BinaryExpr):
        return self.parenthesize(expr.operator.lexeme, expr.expr_left, expr.expr_right)

    def visit_unaryexpr(self, expr: UnaryExpr):
        return self.parenthesize(expr.operator.lexeme, expr.expr_right)

    def visit_groupexpr(self, expr: GroupExpr):
        return self.parenthesize("group", expr.expr)

    def visit_literalexpr(self, expr: LiteralExpr):
        if expr.value is None:
            return "nil"

        return str(expr.value)

    def parenthesize(self, name: str, *expressions: Expr) -> str:
        final_str = ""

        if not self.reverse_polish_notation:
            final_str += f"({name}"
        else:
            final_str += f"("

        for expr in expressions:
            final_str += " "
            final_str += str(expr.accept(self))

        if self.reverse_polish_notation:
            final_str += f" {name})"
        else:
            final_str += ")"

        return final_str

if __name__ == '__main__':
    expression = BinaryExpr(
        UnaryExpr(
            Token(token_type=TokenType.MINUS, lexeme="-", literal=None, line=1),
            LiteralExpr(123)
        ),
        Token(token_type=TokenType.STAR, lexeme="*", literal=None, line=1),
        GroupExpr(
            LiteralExpr(45.67)
        )
    )

    printer = AstPrinter(reverse_polish_notation=True)
    print(printer.print(expression))
