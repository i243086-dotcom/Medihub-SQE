"""Draw the deployed booking handler CFG and count nodes/edges explicitly."""

import argparse
import ast
from pathlib import Path


class Graph:
    def __init__(self, split_booleans):
        self.nodes = []
        self.edges = []
        self.split_booleans = split_booleans
        self.entry = self.node("entry")
        self.exit = self.node("exit")

    def node(self, text):
        self.nodes.append(text)
        return len(self.nodes)

    def connect(self, origin, destination, label=""):
        self.edges.append((origin, destination, label))

    def condition(self, test, yes, no):
        if self.split_booleans and isinstance(test, ast.BoolOp):
            final = self.condition(test.values[-1], yes, no)
            for part in reversed(test.values[:-1]):
                values = (final, no) if isinstance(test.op, ast.And) else (yes, final)
                final = self.condition(part, *values)
            return final
        n = self.node(f"L{test.lineno} {ast.unparse(test)}")
        self.connect(n, yes, "true")
        self.connect(n, no, "false")
        return n

    def body(self, stmts, follow):
        for stmt in reversed(stmts):
            if isinstance(stmt, ast.If):
                follow = self.condition(stmt.test, self.body(stmt.body, follow), self.body(stmt.orelse, follow))
            elif isinstance(stmt, ast.Try):
                if stmt.finalbody:
                    raise ValueError("This CFG does not model finally")
                n = self.node(f"L{stmt.lineno} try")
                self.connect(n, self.body(stmt.body, self.body(stmt.orelse, follow)), "normal")
                for handler in stmt.handlers:
                    self.connect(n, self.body(handler.body, follow), "handled exception")
                follow = n
            else:
                n = self.node(f"L{stmt.lineno} {ast.unparse(stmt)}")
                self.connect(n, self.exit if isinstance(stmt, (ast.Return, ast.Raise)) else follow)
                follow = n
        return follow

    @property
    def complexity(self):
        return len(self.edges) - len(self.nodes) + 2


def build(function, split=False):
    graph = Graph(split)
    graph.connect(graph.entry, graph.body(function.body, graph.exit))
    return graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = Path("backend/routes/patient.py")
    function = next(node for node in ast.parse(source.read_text(encoding="utf-8")).body
                    if isinstance(node, ast.FunctionDef) and node.name == "book_appointment")
    graph = build(function)
    split = build(function, True)
    header = ["# Booking control-flow graph", "",
              f"`{source.as_posix()}:{function.lineno}` through line {function.end_lineno}. Each explicit return joins one exit. "
              "One decision is counted per condition, with an explicit handled-exception edge per handler. "
              "Uncaught runtime exceptions and framework decorators are outside the function CFG.", "",
              f"- Concrete graph: E = {len(graph.edges)}, N = {len(graph.nodes)}, P = 1. M = **{graph.complexity}**.",
              f"- Short-circuit variant: E = {len(split.edges)}, N = {len(split.nodes)}, P = 1. M = **{split.complexity}**.",
              "", "```mermaid", "flowchart TD"]
    for n, label in enumerate(graph.nodes, 1):
        compact = label.replace('"', "'").replace("\n", " ")
        if len(compact) > 90:
            compact = compact[:87] + "..."
        header.append(f'    N{n}["{n}. {compact}"]')
    for i, (origin, dest, label) in enumerate(graph.edges, 1):
        header.append(f'    N{origin} -->|{i} {label}| N{dest}')
    header.extend(["```", ""])
    args.output.write_text("\n".join(header), encoding="utf-8")
    print(f"Manual CFG M={graph.complexity}; short-circuit M={split.complexity}")


if __name__ == "__main__":
    main()
