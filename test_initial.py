import re
import os
import tempfile
import pytest
from syrupy.extensions.single_file import SingleFileSnapshotExtension
import remarks
import functools

def run_once(func):
    """Decorator to run a function only once."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper

def with_remarks(input_name):
    """Decorator to run remarks for a specific input directory."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            input_dir = input_name
            output_dir = "tests/out"

            # Run remarks if it hasn't been run for this input directory
            if not getattr(with_remarks, f"run_{input_name}", False):
                remarks.run_remarks(input_dir, output_dir, **default_args)
                setattr(with_remarks, f"run_{input_name}", True)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class JPEGImageExtension(SingleFileSnapshotExtension):
    _file_extension = "jpg"


@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(JPEGImageExtension)


default_args = {
    "file_name": None,
    "ann_type": ["scribbles", "highlights"],
    "combined_pdf": True,
    "modified_pdf": False,
    "per_page_targets": [],
    "assume_malformed_pdfs": False,
    "avoid_ocr": False,
}

def snapshot_test_pdf(filename: str, snapshot):
    """Snapshots a pdf by converting all pages to jpeg images and collecting their hashes.
    Makes a snapshot for each page"""
    assert os.path.isfile(f"tests/out/{filename}")
    with tempfile.TemporaryDirectory() as tempDir:
        os.system(
            f'convert -density 150 "tests/out/{filename}" -quality 100 {tempDir}/output-%3d.jpg'
        )
        page_images = os.listdir(tempDir)
        for i, image in enumerate(page_images):
            name = f"{filename}:page-{i}"
            with open(f"{tempDir}/{image}", "rb") as f:
                assert f.read() == snapshot(name=name)


@with_remarks("tests/in/pdf_with_multiple_added_pages")
def test_pdf_with_inserted_pages(snapshot):
    snapshot_test_pdf("pdf_longer _remarks.pdf", snapshot)


@with_remarks("tests/in/highlighter-test")
def test_pdf_with_glyphrange_highlights(snapshot):
    snapshot_test_pdf("docsfordevelopers _remarks.pdf", snapshot)


@with_remarks("demo/on-computable-numbers/xochitl")
def test_can_process_demo_with_default_args():
    assert os.path.isfile(
        "tests/out/1936 On Computable Numbers, with an Application to the Entscheidungsproblem - A. M. Turing _remarks.pdf"
    )

@with_remarks("tests/in/v2_notebook_complex")
def test_can_handle_drawing_with_many_scribbles():
    assert os.path.isfile("tests/out/Gosper _remarks.pdf")

@with_remarks("tests/in/v2_book_with_ann")
def test_can_handle_book():
    assert os.path.isfile("tests/out/Gosper _remarks.pdf")

@with_remarks("tests/in/highlighter-test")
@pytest.mark.markdown
def test_generated_markdown_has_autogeneration_warning():
    autogeneration_warning = """> [!WARNING] **Do not modify** this file
> This file is automatically generated by Scrybble and will be overwritten whenever this file in synchronized.
> Treat it as a reference."""
    with open("tests/out/docsfordevelopers _obsidian.md") as f:
        assert autogeneration_warning in f.read()

@with_remarks("tests/in/v3_markdown_tags")
@with_remarks("tests/in/highlighter-test")
@pytest.mark.markdown
def test_generated_markdown_heading_is_positioned_correctly():
    with open("tests/out/docsfordevelopers _obsidian.md") as f:
        assert f.readline()[0] == "#"
    with open("tests/out/tags test _obsidian.md") as f:
        content = f.read()
        # Make sure that the title is on its own line
        match = re.search(r"^# tags test$", content, re.MULTILINE)
        assert match, "Title '# tags test' not found on its own line in the file"

@with_remarks("tests/in/v3_markdown_tags")
@pytest.mark.markdown
def test_yaml_frontmatter_is_valid():
    with open('tests/out/tags test _obsidian.md') as f:
        content = f.read()
        assert content.startswith("---")
        assert content.count("---") == 2
        assert """tags:
- '#remarkable/obsidian'""" in content


