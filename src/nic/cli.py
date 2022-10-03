from pathlib import Path
from typing import Optional

import typer

import nic

app = typer.Typer(no_args_is_help=True, add_completion=False)
STATE = {"verbose": False}


def _show_version_and_exit(value: bool) -> None:
    if value:
        typer.echo(f"nictool v{nic.__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    version: Optional[bool] = typer.Option(
        None,
        "-v",
        "--version",
        callback=_show_version_and_exit,
        help="Show version and exit.",
    ),
) -> None:
    """Command line tool for the Nikon Imaging Center at HMS.

    v{version}
    """


_main.__doc__ = typer.style(
    (_main.__doc__ or "").format(version=nic.__version__), fg="bright_yellow"
)


@app.command()
def update() -> None:
    """Update nictool itself."""
    import subprocess

    url = "https://github.com/tlambert03/nictool/archive/refs/heads/main.zip"
    subprocess.run(
        ["pip", "install", "--upgrade", "--force-reinstall", url],
        stderr=subprocess.DEVNULL,
    )


@app.command()
def clean(
    directory: str = typer.Argument(
        ...,
        help="The directory to cleanup",
    ),
    days: float = typer.Option(
        60,
        "-d",
        "--days",
        metavar="FLOAT",
        help="Number of days old a file must be to be deleted",
    ),
    dry_run: bool = typer.Option(
        False,
        "-n",
        "--dry-run",
        help="Don't delete anything. Just print what would be deleted and exit",
    ),
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Delete without confirmation (otherwise a prompt is shown with "
        "the number of files that would be deleted)",
    ),
    delete_empty_dirs: bool = typer.Option(True, help="Delete empty directories."),
    skip: str = typer.Option("delete", help="Don't delete files with this string."),
) -> None:
    """✨ Delete files in a given directory older than a certain age."""
    context = None
    if directory.startswith("smb://"):
        from nic.remote import mount_smb

        server, *rest = directory[6:].split("/")
        share = rest[0] if rest else "data"
        user = "Admin"
        if "@" in server:
            user, server = server.split("@")
        if ":" in user:
            raise ValueError("Usernames with ':' are not supported")

        context = mount_smb(server, share, user)
        _directory = Path(context.__enter__())
        typer.secho("loaded remote directory")
    else:
        _directory = Path(directory).resolve()
        if not _directory.is_dir():
            if _directory.exists():
                typer.secho(f"Path is not a directory: {directory!r}", fg="red")
            else:
                typer.secho(f"Directory does not exist: {directory!r}", fg="red")
            raise typer.Exit(0)

    try:
        # grab list of old files
        old_files = list(nic.iter_old_files(_directory, days, skip=skip))

        # if there are no old files, exit
        if not old_files:
            typer.secho(
                f"No files found in {directory!r} older than {days} days!",
                fg="green",
                bold=True,
            )
            raise typer.Exit(0)

        # if dry_run, just print what would be deleted
        if dry_run:
            for old_file, age in old_files:
                name_age = f"{old_file} ({age:.1f} days old)"
                typer.secho(f"Would delete {name_age}", fg=(140, 140, 140))
            raise typer.Exit(0)

        # if force was not specified, ask for confirmation
        if not force:
            msg = typer.style(
                f"This will delete {len(old_files)} files (use '--dry-run' to show them"
                "). Are you sure?",
                fg=typer.colors.BRIGHT_MAGENTA,
                bold=True,
            )
            typer.confirm(msg, abort=True)

        # actually delete files
        for old_file, age in old_files:
            name_age = f"{old_file} ({age:.1f} days old)"
            count = 0
            errs = 0
            try:
                old_file.unlink()
                typer.secho(f"Deleted {name_age}", fg="green")
                count += 1
            except Exception as e:
                typer.secho(f"Failed to delete {name_age}: {e}", err=True, fg="red")
                errs += 1

        if delete_empty_dirs:
            typer.secho("---------------------------------------", fg=(110, 110, 110))
            for empty in nic.iter_empty_dirs(_directory, skip=skip):
                try:
                    empty.rmdir()
                    typer.secho(f"📂 Deleted empty directory {empty}", fg="green")
                except Exception as e:
                    typer.secho(
                        f"Failed to delete empty directory {empty}: {e}",
                        err=True,
                        fg="red",
                    )

        typer.secho("---------------------------------------", fg=(160, 160, 160))

        # print summary and exit
        if count:
            typer.secho(f"Deleted {count} files", fg="green", bold=True)
        if errs:
            typer.secho(f"Unabled to delete {errs} files.", fg="red", bold=True)
        raise typer.Exit(1 if errs else 0)
    finally:
        if context:
            context.__exit__(None, None, None)


def main() -> None:
    """Run main app."""
    app()
