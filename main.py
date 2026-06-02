from rich.console import Console

from config import settings
from agent.core import PaperAgent
from tools.registry import list_tools, run_tool

console = Console()


def show_help():
    """
    显示帮助信息。
    """

    console.print("\n[bold yellow]可用命令：[/bold yellow]")
    console.print("/help      查看帮助")
    console.print("/tools     查看当前可用工具")
    console.print("/calc      手动调用计算器，例如：/calc 12 * (3 + 4)")
    console.print("/read      手动读取文件，例如：/read data/example.md")
    console.print("/load      加载文档并预览，例如：/load data/example.md")
    console.print("/chunk     加载并切分文档，例如：/chunk data/example.md")
    console.print("/embed     生成文档 embedding 预览，例如：/embed data/example.md")
    console.print("/index     为文档建立索引，例如：/index data/uploaded/test.pdf")
    console.print("/search    检索索引内容，例如：/search 论文的方法是什么")
    console.print("/ask       通过 Agent 提问，例如：/ask 这篇论文的主要方法是什么")

    console.print("/history   查看当前对话历史")
    console.print("/clear     清空当前对话历史")
    console.print("exit       退出程序")
    console.print("quit       退出程序")


def show_tools():
    """
    显示工具列表。
    """

    tools = list_tools()

    console.print("\n[bold yellow]当前可用工具：[/bold yellow]")
    for index, tool in enumerate(tools, start=1):
        console.print(
            f"{index}. [bold]{tool['name']}[/bold]：{tool['description']}"
        )


def show_history(agent: PaperAgent):
    """
    显示对话历史。
    """

    history = agent.get_history()

    if not history:
        console.print("[yellow]当前没有对话历史。[/yellow]")
        return

    console.print("\n[bold yellow]当前对话历史：[/bold yellow]")

    for index, message in enumerate(history, start=1):
        role = message.get("role", "unknown")
        content = message.get("content", "")

        console.print(f"\n[bold]{index}. {role}[/bold]")
        console.print(content)


def main():
    console.rule("[bold blue]PaperAgent")
    console.print(f"[green]项目名称：[/green]{settings.project_name}")
    console.print("[bold green]PaperAgent 初始化成功！[/bold green]")
    console.print("输入 /help 查看帮助。")

    try:
        agent = PaperAgent()
    except Exception as e:
        console.print(f"[bold red]Agent 初始化失败：[/bold red]{e}")
        return

    while True:
        user_input = console.input("\n[bold cyan]User > [/bold cyan]").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            console.print("[yellow]已退出 PaperAgent。[/yellow]")
            break

        if user_input == "/help":
            show_help()
            continue

        if user_input == "/tools":
            show_tools()
            continue

        if user_input == "/history":
            show_history(agent)
            continue

        if user_input == "/clear":
            agent.clear_memory()
            console.print("[yellow]对话历史已清空。[/yellow]")
            continue

        if user_input.startswith("/calc "):
            expression = user_input.removeprefix("/calc ").strip()

            result = run_tool("calculator", expression=expression)
            console.print(f"\n[bold magenta]Tool > [/bold magenta]{result}")

            continue

        if user_input.startswith("/read "):
            file_path = user_input.removeprefix("/read ").strip()

            result = run_tool("read_file", file_path=file_path)
            console.print(f"\n[bold magenta]Tool > [/bold magenta]\n{result}")

            continue

        if user_input.startswith("/load "):
            file_path = user_input.removeprefix("/load ").strip()

            result = run_tool("load_document", file_path=file_path)
            console.print(f"\n[bold magenta]Tool > [/bold magenta]\n{result}")

            continue

        if user_input.startswith("/chunk "):
            file_path = user_input.removeprefix("/chunk ").strip()

            result = run_tool("chunk_document", file_path=file_path)
            console.print(f"\n[bold magenta]Tool > [/bold magenta]\n{result}")

            continue
        if user_input.startswith("/embed "):
            file_path = user_input.removeprefix("/embed ").strip()

            result = run_tool("embedding_preview", file_path=file_path)
            console.print(f"\n[bold magenta]Tool > [/bold magenta]\n{result}")

            continue

        if user_input.startswith("/index "):
            file_path = user_input.removeprefix("/index ").strip()

            result = run_tool("build_index", file_path=file_path)
            console.print(f"\n[bold magenta]Tool > [/bold magenta]\n{result}")

            continue

        if user_input.startswith("/search "):
            query = user_input.removeprefix("/search ").strip()

            result = run_tool("search_index", query=query)
            console.print(f"\n[bold magenta]Tool > [/bold magenta]\n{result}")

            continue
        
        if user_input.startswith("/ask "):
            question = user_input.removeprefix("/ask ").strip()

            response = agent.run(question)
            console.print(f"\n[bold magenta]PaperAgent > [/bold magenta]{response}")

            continue


        response = agent.run(user_input)
        console.print(f"\n[bold magenta]PaperAgent > [/bold magenta]{response}")


if __name__ == "__main__":
    main()