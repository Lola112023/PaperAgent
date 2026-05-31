import ast
import operator


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculator(expression: str) -> str:
    """
    安全计算数学表达式。

    支持：
    1. 加法 +
    2. 减法 -
    3. 乘法 *
    4. 除法 /
    5. 幂运算 **
    6. 取余 %
    7. 括号
    8. 小数

    示例：
        calculator("12 * (3 + 4)")
    """

    expression = expression.strip()

    if not expression:
        return "计算失败：表达式不能为空。"

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_ast(tree.body)
        return f"计算结果：{result}"
    except ZeroDivisionError:
        return "计算失败：除数不能为 0。"
    except Exception as e:
        return f"计算失败：非法表达式。错误信息：{e}"


def _eval_ast(node):
    """
    递归计算 AST 节点。
    """

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("只允许数字常量。")

    if isinstance(node, ast.BinOp):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"不支持的运算符：{operator_type}")

        return _ALLOWED_OPERATORS[operator_type](left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _eval_ast(node.operand)
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"不支持的一元运算符：{operator_type}")

        return _ALLOWED_OPERATORS[operator_type](operand)

    raise ValueError(f"不支持的表达式类型：{type(node).__name__}")