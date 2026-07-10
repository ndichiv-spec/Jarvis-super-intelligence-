uv lock; uv run python -c ""import pathlib;print(len([p for p in pathlib.Path('packages').iterdir() if p.is_dir()]))""
