"""
calculator.py
Core math engine. Safely evaluates arithmetic and scientific expressions
without using Python's raw eval() on untrusted input.
"""

import ast
import math
import operator


class CalculatorError(Exception):
    pass


class Calculator:
    """Safe expression evaluator supporting basic + scientific operations."""

    # Supported binary/unary operators
    _BIN_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.FloorDiv: operator.floordiv,
    }
    _UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    # Supported function calls, e.g. sin(90), sqrt(16), log(100)
    _FUNCTIONS = {
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "asin": lambda x: math.degrees(math.asin(x)),
        "acos": lambda x: math.degrees(math.acos(x)),
        "atan": lambda x: math.degrees(math.atan(x)),
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "log": math.log10,
        "ln": math.log,
        "exp": math.exp,
        "abs": abs,
        "fact": lambda x: math.factorial(int(x)),
    }

    # Supported constants, e.g. pi, e
    _CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    def evaluate(self, expression: str, variables: dict | None = None) -> float:
        """Evaluate a math expression string and return a numeric result.

        `variables` optionally maps names (e.g. 'x') to numeric values, used
        by the graphing feature to sample a function at many points.
        """
        if not expression or not expression.strip():
            raise CalculatorError("Empty expression")

        # Convenience replacements so the UI can use familiar symbols
        expr = (
            expression.replace("×", "*")
            .replace("÷", "/")
            .replace("^", "**")
            .replace("π", "pi")
        )

        try:
            tree = ast.parse(expr, mode="eval")
            result = self._eval_node(tree.body, variables or {})
        except ZeroDivisionError:
            raise CalculatorError("Cannot divide by zero")
        except CalculatorError:
            raise
        except Exception:
            raise CalculatorError("Invalid expression")

        if isinstance(result, complex):
            raise CalculatorError("Invalid expression")

        return result

    def evaluate_at(self, expression: str, var_name: str, value: float) -> float:
        """Convenience wrapper for graphing: evaluate expr with one variable set."""
        return self.evaluate(expression, {var_name: value})

    def _eval_node(self, node, variables: dict):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise CalculatorError("Invalid expression")

        if isinstance(node, ast.BinOp):
            op_func = self._BIN_OPS.get(type(node.op))
            if op_func is None:
                raise CalculatorError("Unsupported operator")
            left = self._eval_node(node.left, variables)
            right = self._eval_node(node.right, variables)
            return op_func(left, right)

        if isinstance(node, ast.UnaryOp):
            op_func = self._UNARY_OPS.get(type(node.op))
            if op_func is None:
                raise CalculatorError("Unsupported operator")
            return op_func(self._eval_node(node.operand, variables))

        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            if node.id in self._CONSTANTS:
                return self._CONSTANTS[node.id]
            raise CalculatorError(f"Unknown identifier: {node.id}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise CalculatorError("Invalid function call")
            func_name = node.func.id
            if func_name not in self._FUNCTIONS:
                raise CalculatorError(f"Unknown function: {func_name}")
            args = [self._eval_node(arg, variables) for arg in node.args]
            return self._FUNCTIONS[func_name](*args)

        raise CalculatorError("Invalid expression")
