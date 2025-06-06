#!/usr/bin/env python3
import os
import re

# pip install atlassian-python-api
from atlassian import Confluence

confluence = Confluence(
            url=os.environ['CONFLUENCE_URL'],
            username=os.environ['CONFLUENCE_USER'],
            token=os.environ['CONFLUENCE_TOKEN'])

# Confluence Page ID and Title is derived from README.md
parent_id_pattern = re.compile(r"<!-- confluence-parent-id: (\d+) -->")
page_id_pattern = re.compile(r"<!-- confluence-page-id: (\d+) -->")
space_pattern = re.compile(r"<!-- confluence-space-key: (\w+) -->")
page_id = None
title = None
space = None
with open('README.md', 'r') as f:
    while page_id is None or title is None:
        line = f.readline()
        # confluence-parent-id
        match = parent_id_pattern.match(line)
        if match:
            parent_id = match.group(1)
            continue
        # confluence-page-id
        match = page_id_pattern.match(line)
        if match:
            page_id = match.group(1)
            continue
        # confluence-space-key
        match = space_pattern.match(line)
        if match:
            space = match.group(1)
            continue
        # confluence-title
        if line.startswith('# '):
            title = line[1:].strip()

print(f"Using Parent ID: {parent_id}")
print(f"Using Page ID: {page_id}")
print(f"Using Space: {space}")
print(f"Using Title: {title}")

with open("README.md", mode='r') as markdown_file:
    body = markdown_file.read()

if confluence.page_exists(space, title, type=None) is False:
    print("Creating page")
    confluence.create_page(
        space,
        title,
        body,
        parent_id='421855570',
        type='page',
        representation='storage',
        editor='v2',
        full_width=False
    )
else:
    print("Updating existing page")
    confluence.update_page(
        page_id,
        title,
        body,
        parent_id=None,
        type='page',
        representation='storage',
        minor_edit=False,
        full_width=False
    )
