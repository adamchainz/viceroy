import warnings
from slimit.ast import String
from slimit.parser import Parser


class UnsupportedIdentifier(Warning):
    pass


class BaseScanner(object):
    test_methods = {}

    def __init__(self, source):
        self.tree = Parser().parse(source)

    def __iter__(self):
        for node in self.tree:
            yield from self.visit(node)

    def visit(self, node):
        method_name = 'visit_{}'.format(node.__class__.__name__)
        handler = getattr(self, method_name, self.visit_children)
        yield from handler(node)

    def visit_children(self, node):
        for child in node:
            yield from self.visit(child)

    def visit_FunctionCall(self, node):
        key = node.identifier.to_ecma()
        if key in self.test_methods:
            argument = self.test_methods[key]
            if callable(argument):
                yield argument(node)
            else:
                yield self.extract_name(node.args[argument])
        yield from self.visit_children(node)

    def extract_name(self, node):
        if isinstance(node, String):
            s = node.to_ecma()
            if s[0] == s[-1] and s[0] in ["'", '"']:
                return s[1:-1]
            else:
                return s
        else:
            warnings.warn(
                "Unsupported test name type {!r}, "
                "only strings are supported".format(
                    node
                ),
                UnsupportedIdentifier
            )
            raise StopIteration()
