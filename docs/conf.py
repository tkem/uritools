import importlib.metadata

project = "uritools"
copyright = "2014-2026 Thomas Kemmer"
release = importlib.metadata.version(project)
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
]
exclude_patterns = ["_build"]
html_theme = "classic"
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
