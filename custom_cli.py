from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.traceback import install
import time
console = Console()
install()

def stream_print(text, delay=0.05):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

while True:
    # Show a bordered input box with "> " inside

    query = Prompt.ask("", default="Write Prompt")  
    console.print(Panel.fit(
        f"[bold cyan]>[/bold cyan] {query}", 
        title="User Input",  # acts like hover text
        border_style="bright_magenta",  
    ))

    
    if query.lower() in ["exit", "quit"]:
        console.print("[red]Exiting GeminiCLI look...[/red]")
        break
    with console.status("Generating ..."):
        time.sleep(5)

        console.rule(query)

    # except Exception as e:
    #     error_console = Console(stderr=True, style="bold red")
    #     error_console.print()
    #     error_console.print("Error !!! --> ", e)