import ast
import operator
from typing import Any, Callable

SAFE_OPERATORS = {
    ast.Lt:     operator.lt,
    ast.Gt:     operator.gt,
    ast.LtE:    operator.le,
    ast.GtE:    operator.ge,
    ast.Eq:     operator.eq,
    ast.NotEq:  operator.ne,
    ast.And:    operator.and_,
    ast.Or:     operator.or_,
    ast.In:     lambda a, b: operator.contains(b, a),      # a in b
    ast.NotIn:  lambda a, b: not operator.contains(b, a),  # a not in b
}

def compile_expr(expr: str) -> Callable[[dict], bool]:
    tree = ast.parse(expr, mode="eval")

    def _compile(node: ast.AST) -> Callable[[dict], Any]:
        # Разворачиваем корень
        if isinstance(node, ast.Expression):
            return _compile(node.body)

        # len(var)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "len"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)
        ):
            var = node.args[0].id
            return lambda ctx: len(ctx.get(var, []))

        # переменная
        if isinstance(node, ast.Name):
            return lambda ctx: ctx.get(node.id)

        # литерал (число, строка)
        if isinstance(node, ast.Constant):
            return lambda ctx: node.value

        # контейнерные литералы: list, tuple, set
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            # собираем Python-объект из констант
            consts = [elt.value for elt in node.elts if isinstance(elt, ast.Constant)]
            container = (
                set(consts) if isinstance(node, ast.Set)
                else tuple(consts) if isinstance(node, ast.Tuple)
                else list(consts)
            )
            return lambda ctx, c=container: c

        # сравнения (включая in / not in)
        if isinstance(node, ast.Compare):
            left_fn  = _compile(node.left)
            right_fn = _compile(node.comparators[0])
            op_type  = type(node.ops[0])
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type}")
            op_fn = SAFE_OPERATORS[op_type]
            return lambda ctx: op_fn(left_fn(ctx), right_fn(ctx))

        # булевы операции and/or
        if isinstance(node, ast.BoolOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported boolean op: {op_type}")
            op_fn = SAFE_OPERATORS[op_type]
            value_fns = [_compile(v) for v in node.values]
            return lambda ctx: op_fn(*(vf(ctx) for vf in value_fns))

        raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    return _compile(tree)
