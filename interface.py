from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import requests
import base64
import click
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
)
import time
from rich.console import Console


BACKEND_URL = "http://172.18.0.2:8080/dalle"

cons = Console(
    highlight=False,
)


def find_path(prompt: str) -> Path:
    """
    Takes a prompt, returning a path to a new image file in a directory named after the prompt

    :param prompt: The prompt

    :return: A path to a file that doesn't exist yet.
    """

    # Creates a new directory if it isn't already there
    basepath = Path(f"results/{prompt.replace(' ' , '_').lower()}")
    if not basepath.is_dir():
        basepath.mkdir(parents=True)
    # Selects a path for the new image to be in, one that's not yet occupied
    i = 0
    path = basepath / f"{i}.jpg"
    while path.exists():
        i += 1
        path = basepath / f"{i}.jpg"
    return path


def post_prompt(prompt: str, progcons: Console, verbose: bool = False) -> Path | None:
    path = find_path(prompt)
    # Posts the prompt to the backend
    if verbose:
        before = time.time()
        progcons.print(
            f"Sent request for prompt [yellow italic not bold]{prompt}[/]!",
        )
    r = requests.post(BACKEND_URL, json={"text": prompt, "num_images": 1})
    if verbose:
        progcons.print(
            f"Got response for prompt [yellow italic not bold]{prompt}[/] in [bold white]{time.time()-before:0.3f}s[/]!",  # type: ignore
            highlight=False,
        )
    if not r.ok:
        print("Error sending prompt")
    with open(path, "wb") as f:
        f.write(base64.b64decode(r.json()[0]))
        if verbose:
            progcons.print(f"Wrote image to [red underline bold]{path}[/]!")
    return path


@click.group()
def cli():
    pass


@cli.command()
@click.argument("prompts", nargs=-1, required=True)
@click.option("-n", default=1, help="Number of images to generate")
@click.option("--verbose", is_flag=True, default=False)
def oneshot(prompts: list[str], n: int, verbose: bool):
    cons.print(
        f"Generating: [yellow italic]{', '.join(prompts)}[/], [red bold]{n}[/] times each, with DALL-E mini on [blue italic underline]{BACKEND_URL}[/].\n",
    )
    with Progress(
        SpinnerColumn("bounce", "red"),
        TextColumn("[yellow italic]{task.description}[/]"),
        BarColumn(bar_width=30, complete_style="magenta", finished_style="magenta"),
        TextColumn("[green]{task.percentage:>3.0f}%[/]"),
        TimeRemainingColumn(True, True),
        speed_estimate_period=10,
    ) as progress:
        if len(prompts) > 1:
            allprompts = progress.add_task(
                "[red not italic]All", total=len(prompts) * n
            )
        for p in prompts:
            curr = progress.add_task(f"{p}", total=n)
            for _ in range(n):
                post_prompt(p, progress.console, verbose)
                progress.advance(curr)
                if len(prompts) > 1:
                    progress.advance(allprompts)  # type: ignore


@cli.command()
@click.argument("prompts", nargs=-1, required=True)
@click.option("--verbose", is_flag=True, default=False)
def collage(prompts: list[str], verbose: bool):
    cons.print("Generating collages...")
    with Progress(
        SpinnerColumn("bounce", "red"),
        TextColumn("[yellow italic]{task.description}[/]"),
        BarColumn(bar_width=30, complete_style="magenta", finished_style="magenta"),
        TextColumn("[green]{task.percentage:>3.0f}%[/]"),
        TimeRemainingColumn(True, True),
        speed_estimate_period=10,
    ) as progress:
        if len(prompts) > 1:
            allprompts = progress.add_task(
                "[red not italic]All", total=len(prompts) * 9
            )
        for p in prompts:
            coll_images: list[Path] = []
            curr = progress.add_task(f"{p}", total=9)
            for _ in range(9):
                respath = post_prompt(p, progress.console, verbose)
                if respath:
                    coll_images.append(respath)
                progress.advance(curr)
                if len(prompts) > 1:
                    progress.advance(allprompts)  # type: ignore
            if coll_images:
                collage_path = (
                    Path(f"results/{p.replace(' ' , '_').lower()}") / "collage.jpg"
                )
                collage_path.touch()
                new = Image.new("RGB", (798, 820))
                for i, img in enumerate(coll_images):
                    # images are 256x256
                    im = Image.open(img)
                    bordered = ImageOps.expand(im, border=5, fill="black")
                    new.paste(bordered, ((i % 3) * 266, (i // 3) * 266))
                draw = ImageDraw.Draw(new)
                w, _ = draw.textsize(p[:20])
                draw.text(((798 - w) // 2, 805), p[:100], fill="white")
                new.save(collage_path)


if __name__ == "__main__":
    cli()
