"""
FastDEV CLI - Command line interface
"""

from pathlib import Path

import typer
from rich.console import Console

from . import __version__
from .server import FastDEVServer

app = typer.Typer(
    name="fastdev",
    help="FastDEV - Intelligent MCP server for FastAPI development",
    add_completion=False,
)
console = Console()


@app.command()
def serve(
    config: Path = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Start the FastDEV MCP server"""
    console.print(f"[bold green]FastDEV v{__version__}[/bold green]")
    console.print("Starting MCP server...")

    try:
        server = FastDEVServer(config_path=config)
        server.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show FastDEV version"""
    console.print(f"FastDEV version {__version__}")


@app.command()
def status():
    """Show status of all managed servers"""
    # This would connect to running FastDEV instance
    console.print("[yellow]This feature is coming soon![/yellow]")
    console.print("For now, use the MCP interface to query server status.")


@app.command()
def docs():
    """Open FastDEV documentation in browser"""
    import webbrowser

    url = "https://github.com/eagurin/fastdev"
    console.print(f"Opening documentation at {url}")
    webbrowser.open(url)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
