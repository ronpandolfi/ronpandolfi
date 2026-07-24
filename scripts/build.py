# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "jinja2", "pyyaml"]
# ///
"""Build the profile README: fetch data, draw SVG panels, render the template."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[1]
LOGIN = "ronpandolfi"
ORCID = "0000-0003-0824-8548"


def render_readme(profile: dict, activity: dict, publications: list, updated: str) -> str:
    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      keep_trailing_newline=True, trim_blocks=False)
    tpl = env.get_template("README.md.j2")
    return tpl.render(profile=profile, activity=activity,
                      publications=publications, updated=updated)
