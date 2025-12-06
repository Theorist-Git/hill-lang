from sys import argv, exit
from pathlib import Path
from scanner import Scanner
from parser import Parser
from ast_printer import AstPrinter

import errors

class Hill:
    def main(self):
        args = argv[1:]
        print(args)

        if len(args) > 1:
            print("Usage: hill.py <script>")
            exit(64)
        elif len(args) == 1:
            self.run_program(Path(args[0]))
        else:
            self.run_prompt()

    @staticmethod
    def run(source: str):
        scanner = Scanner(source=source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens=tokens)
        expression = parser.parse()

        if errors.had_error:
            return

        printer = AstPrinter(reverse_polish_notation=True)
        print(printer.print(expression))


    def run_program(self, file_path: Path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                self.run(source)

                if errors.had_error:
                    exit(1)
        except FileNotFoundError:
            print(f"[Error]: Could not open file: {file_path}")

    def run_prompt(self):
        print("Hill Language REPL (Python Implementation)")
        print("Press Ctrl+D to exit")

        while True:
            try:
                line = input(">>> ")
                if line.strip() == "exit":
                    break

                self.run(line)
                errors.had_error = False

            except EOFError:
                # Ctrl+D
                print("\nExiting.")
                break
            except KeyboardInterrupt:
                # Ctrl+C
                print("\nKeyboardInterrupt")
                break

    # @classmethod
    # def error(cls, line, message):
    #     cls.report(line, "", message)
    #
    # @classmethod
    # def report(cls, line, where, message):
    #     print(f"[line {line}] Error{where}: {message}", file=stderr)
    #     cls.had_error = True

if __name__ == '__main__':
    Hill().main()
