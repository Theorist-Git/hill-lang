from abc import ABC, abstractmethod
from hill_token import Token


class Visitor(ABC):
    @abstractmethod
    def visit_binaryexpr(self, expr):
        pass

    @abstractmethod
    def visit_unaryexpr(self, expr):
        pass

    @abstractmethod
    def visit_groupexpr(self, expr):
        pass

    @abstractmethod
    def visit_literalexpr(self, expr):
        pass

class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

# Define BinaryExpr
class BinaryExpr(Expr):
    def __init__(self, expr_left: Expr, operator: Token, expr_right: Expr):
        self.expr_left = expr_left
        self.operator = operator
        self.expr_right = expr_right

    def accept(self, visitor: Visitor):
        return visitor.visit_binaryexpr(self)

# Define UnaryExpr
class UnaryExpr(Expr):
    def __init__(self, operator: Token, expr_right: Expr):
        self.operator = operator
        self.expr_right = expr_right

    def accept(self, visitor: Visitor):
        return visitor.visit_unaryexpr(self)

# Define GroupExpr
class GroupExpr(Expr):
    def __init__(self, expr: Expr):
        self.expr = expr

    def accept(self, visitor: Visitor):
        return visitor.visit_groupexpr(self)

# Define LiteralExpr
class LiteralExpr(Expr):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor: Visitor):
        return visitor.visit_literalexpr(self)
