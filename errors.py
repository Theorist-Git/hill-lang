import sys

had_error = False

def error(line, message):
    report(line, "", message)

def report(line, where, message):
    global had_error
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
    had_error = True
