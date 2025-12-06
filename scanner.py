from typing import List, Union
from hill_token import Token, TokenType

import errors

class Scanner:
    # Scanning location tracking variables
    start       :int = 0
    current     :int = 0
    line        :int = 1 # lines start from index 1

    # token dict (single character)
    SINGLE_CHAR_MAP = {
        '(': TokenType.LEFT_PAREN,
        ')': TokenType.RIGHT_PAREN,
        '{': TokenType.LEFT_BRACE,
        '}': TokenType.RIGHT_BRACE,
        ',': TokenType.COMMA,
        '.': TokenType.DOT,
        '-': TokenType.MINUS,
        '+': TokenType.PLUS,
        ';': TokenType.SEMICOLON,
        '*': TokenType.STAR,
    }

    # Language keywords
    KEYWORD_MAP = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []

    def buffer_consumed(self) -> bool:
        """Checks if `current` pointer has read the entire source string"""
        return self.current >= len(self.source)

    def get_current_char_and_advance(self):
        """returns source[current] and increments `current` by 1. Essentially return source[current++]"""
        char = self.source[self.current]
        self.current += 1

        return char

    def match_next_token(self, expected: str) -> bool:
        """
        After having consumed a char using `get_current_char_and_advance(self)`
        `current` now points to the next character in source string
        If there are still characters left in the source buffer, `match_next_token(self, expected: str) -> bool`
        checks if the consumed character matches `expected` character pointed to by current ptr.
        """
        if self.buffer_consumed():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self, jump=0) -> str:
        """
        Peeks `jump` characters ahead of `current`. Defaults to returning `source[current]`
        Returns '\0' if jump moves past end of source string.
        """
        if jump < 0:
            raise ValueError("Jump must be Non Negative (>= 0)")
        if self.current + jump >= len(self.source):
            return '\0'

        return self.source[self.current + jump]

    def add_token(self, token_type: TokenType, literal=None):
        """
        Appends a Token to Token List.
        Also defines the lexeme.
        Literal is None by default.
        """
        lexeme = self.source[self.start: self.current]

        self.tokens.append(Token(
            token_type=token_type,
            lexeme=lexeme,
            literal=literal,
            line=self.line
        ))

    def read_in_string_literal(self):
        while self.peek() != '"' and not self.buffer_consumed():
            if self.peek() == '\n':
                self.line += 1

            self.get_current_char_and_advance()

        if self.buffer_consumed():
            # TODO: Fix this, create a new type or something that makes sense. EOF is just placeholder.
            errors.error(Token(TokenType.EOF, "", None, self.line), message='Unterminated string literal')
            return

        # Consume the closing `"`
        self.get_current_char_and_advance()

        #        `start ptr`--⌄           `current`--⌄
        # This is called when "source buffer literal"-
        # Therefore to get string literal we must do [start + 1, current - 1)
        string_literal: str = self.source[self.start + 1: self.current - 1]

        self.add_token(token_type=TokenType.STRING, literal=string_literal)

    @staticmethod
    def is_digit(c: str) -> bool:
        return '0' <= c <= '9'

    @staticmethod
    def is_alpha(c: str) -> bool:
        return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_'

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def read_in_number_literal(self):
        while self.is_digit(self.peek()):
            self.get_current_char_and_advance()

        if self.peek() == '.' and self.is_digit(self.peek(jump=1)):
            self.get_current_char_and_advance()

            while self.is_digit(self.peek()):
                self.get_current_char_and_advance()

        self.add_token(
            token_type=TokenType.NUMBER,
            literal=float(self.source[self.start: self.current])
        )

    def read_in_identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.get_current_char_and_advance()

        identifier = self.source[self.start: self.current]
        token_type: TokenType = self.KEYWORD_MAP.get(identifier)

        if not token_type:
            token_type = TokenType.IDENTIFIER

        self.add_token(token_type=token_type)

    def gen_token_list(self):
        char = self.get_current_char_and_advance()

        # Lexemes that can only ever be a single character
        if self.SINGLE_CHAR_MAP.get(char):
            self.add_token(token_type=self.SINGLE_CHAR_MAP.get(char))

            return
        # Lexemes with possible extension with `=`
        elif char == '!':
            extends: bool = self.match_next_token('=')
            self.add_token(
                token_type=TokenType.BANG if not extends else TokenType.BANG_EQUAL,
            )

            return
        elif char == '=':
            extends: bool = self.match_next_token('=')
            self.add_token(
                token_type=TokenType.EQUAL if not extends else TokenType.EQUAL_EQUAL,
            )

            return
        elif char == '<':
            extends: bool = self.match_next_token('=')
            self.add_token(
                token_type=TokenType.LESS if not extends else TokenType.LESS_EQUAL,
            )

            return
        elif char == '>':
            extends: bool = self.match_next_token('=')
            self.add_token(
                token_type=TokenType.GREATER if not extends else TokenType.GREATER_EQUAL,
            )

            return
        # Handling Comments
        elif char == '/':
            # Single line comments
            if self.match_next_token('/'):
                while self.peek() != '\n' and not self.buffer_consumed():
                    self.get_current_char_and_advance()

            # Multi Line comments
            elif self.match_next_token('*'):
                cnt = 1

                while cnt > 0 and not self.buffer_consumed():
                    if self.peek() == '\n':
                        self.line += 1

                    if self.peek() == '/' and self.peek(jump=1) == '*':
                        cnt += 1
                        self.get_current_char_and_advance()
                        self.get_current_char_and_advance()
                        continue

                    if self.peek() == '*' and self.peek(jump=1) == '/':
                        cnt -= 1
                        self.get_current_char_and_advance()
                        self.get_current_char_and_advance()
                        continue

                    self.get_current_char_and_advance()

                if cnt > 0:
                    # TODO: Fix this, create a new type or something that makes sense. EOF is just placeholder.
                    errors.error(
                        Token(TokenType.EOF, "", None, self.line),
                        message='Unterminated multi-line comment'
                    )
            else:
                self.add_token(token_type=TokenType.SLASH)

            return
        # New line
        elif char == '\n':
            self.line += 1

            return
        # Junk characters
        elif char == '\r' or char == '\t' or char == ' ':

            return
        elif char == '"':
            self.read_in_string_literal()

            return
        elif self.is_digit(char):
            self.read_in_number_literal()

            return
        elif self.is_alpha(char):
            self.read_in_identifier()

            return
        else:
            errors.error(
                Token(TokenType.EOF, "", None, self.line),
                message="Unexpected Character"
            )

            return

    def scan_tokens(self) -> List[Token]:
        while not self.buffer_consumed():
            self.start = self.current
            self.gen_token_list()

        eof_token = Token(
            token_type=TokenType.EOF,
            lexeme="",
            literal=None,
            line=self.line
        )

        self.tokens.append(
            eof_token
        )

        return self.tokens
