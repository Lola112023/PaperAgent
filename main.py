from rich.console import Console
from config import settings
from agent.core import PaperAgent

console = Console()


def main():
    console.rule("[bold blue]PaperAgent")
    console.print(f"[green]项目名称：[/green]{settings.project_name}")
    console.print(f"[green]项目根目录：[/green]{settings.base_dir}")
    console.print(f"[green]上传目录：[/green]{settings.upload_dir}")
    console.print(f"[green]报告目录：[/green]{settings.report_dir}")
    console.print("[bold green]PaperAgent 初始化成功！[/bold green]")
    
    try:
        agent = PaperAgent()
    except Exception as e:
        console.print(f"[bold red]Agent 初始化失败：[/bold red]{e}")
        return
    
    while True:
        user_input = console.input("\n[bold cyan]User > [/bold cyan]")

        if user_input.lower() in ["exit", "quit"]:
            console.print("[yellow]已退出 PaperAgent。[/yellow]")
            break
        # if user_input in ["\\help"]:
        #     console.print("[blue]你需要一些帮助[/blue]")

        response = agent.run(user_input)
        console.print(f"\n[bold magenta]PaperAgent > [/bold magenta]{response}")


if __name__ == "__main__":
    main()