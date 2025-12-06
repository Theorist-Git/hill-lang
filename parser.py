from hill_token import Token, TokenType
from expr import Expr, BinaryExpr, UnaryExpr, GroupExpr, LiteralExpr
from typing import List

import errors

"""
expression     → comma ;
comma          → equality ( "," equality )* 
equality       → comparison ( ( "!=" | "==" ) comparison )* ;
comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           → factor ( ( "-" | "+" ) factor )* ;
factor         → unary ( ( "/" | "*" ) unary )* ;
unary          → ( "!" | "-" ) unary | primary ;
primary        → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" ;

expression:
  An expression allows equality-type operations.

equality:
  Equality allows a comparison expression followed by any number of
  '!=' and '==' operators, each applied between additional comparison
  expressions.
  Example:
      comparison_expr != comparison_expr == comparison_expr != comparison_expr

comparison:
  Each comparison_expr consists of a term_expr followed by any number
  of comparison operators between further term_exprs.

evaluation notes:
  This structure repeats until we reach a non-recursive atomic expression,
  i.e., the highest-precedence form, which is just a literal. Once something
  is reduced to a literal, we start climbing back up the hierarchy,
  plugging its computed value into the higher-level expression forms.
"""

N_LITERAL_TYPE = 5

class ParserError(Exception):
    def __init__(self, token: Token, message: str):
        errors.error(token, message)
        super().__init__(message)

class Parser:
    current: int = 0

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def peek(self) -> Token:
        return self.tokens[self.current]

    def prvs(self, rewind=1) -> Token:
        if self.current - rewind < 0:
            raise IndexError("Tried to access token before index 0")

        return self.tokens[self.current - rewind]

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1

        return self.prvs()

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self.peek().token_type == token_type

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def expression(self) -> Expr:
        """expression     → comma ;"""
        return self.comma()

    def comma(self) -> Expr:
        """equality ( "," equality )* """
        expr: Expr = self.equality()

        while self.match(TokenType.COMMA):
            operator: Token = self.prvs()
            right: Expr = self.comparison()

            expr = BinaryExpr(
                expr_left=expr,
                operator=operator,
                expr_right=right
            )

        return expr

    def equality(self) -> Expr:
        """equality       → comparison ( ( "!=" | "==" ) comparison )* ;"""
        expr: Expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.prvs()
            right: Expr = self.comparison()
            expr = BinaryExpr(
                expr_left=expr,
                operator=operator,
                expr_right=right
            )

        return expr


    def comparison(self) -> Expr:
        """comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;"""
        expr: Expr = self.term()

        while self.match(
            TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.LESS, TokenType.LESS_EQUAL,
        ):
            operator: Token = self.prvs()
            right: Expr = self.term()

            expr = BinaryExpr(
                expr_left=expr,
                operator=operator,
                expr_right=right
            )

        return expr

    def term(self) -> Expr:
        """term           → factor ( ( "-" | "+" ) factor )* ;"""
        expr: Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.prvs()
            right: Expr = self.factor()

            expr = BinaryExpr(
                expr_left=expr,
                operator=operator,
                expr_right=right
            )

        return expr

    def factor(self) -> Expr:
        """factor         → unary ( ( "/" | "*" ) unary )* ;"""
        expr: Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.prvs()
            right: Expr = self.unary()

            expr = BinaryExpr(
                expr_left=expr,
                operator=operator,
                expr_right=right
            )

        return expr

    def unary(self) -> Expr:
        """unary          → ( "!" | "-" ) unary | primary ;"""
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.prvs()
            right: Expr = self.unary()

            expr = UnaryExpr(
                operator=operator,
                expr_right=right
            )

            return expr

        return self.primary()

    def primary(self) -> Expr:
        """primary        → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" ;"""
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.prvs().literal)

        elif self.match(TokenType.FALSE):
            return LiteralExpr(False)

        elif self.match(TokenType.TRUE):
            return LiteralExpr(True)

        elif self.match(TokenType.NIL):
            return LiteralExpr(None)

        elif self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")

            return GroupExpr(expr)

        else:
            raise ParserError(self.peek(), "Unexpected token.")


    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()

        raise ParserError(self.peek(), message)

    def sync_parser(self):
        self.advance()

        while not self.is_at_end():
            if self.prvs().token_type == TokenType.SEMICOLON:
                return

            if self.peek().token_type in {
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            }:
                return

            self.advance()

    def parse(self):
        try:
            return self.expression()
        except ParserError:
            return None
