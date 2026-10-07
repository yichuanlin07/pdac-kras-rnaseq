import sys
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

source, target = map(Path, sys.argv[1:3])
assert source.resolve() != target.resolve(), "Use a separate output path."
reader = PdfReader(source)
writer = PdfWriter()
writer.clone_document_from_reader(reader)
writer.root_object.pop(NameObject("/Outlines"), None)
writer.root_object.pop(NameObject("/PageMode"), None)
writer.add_metadata({str(k): str(v) for k, v in reader.metadata.items()})
target.parent.mkdir(parents=True, exist_ok=True)
with target.open("wb") as stream:
    writer.write(stream)
final = PdfReader(target)
assert len(final.pages) == len(reader.pages) and (not final.outline)
assert all(
    (
        a.get_contents().get_data() == b.get_contents().get_data()
        for a, b in zip(reader.pages, final.pages)
    )
)
print(f"{len(final.pages)} pages; no outline navigation; page content preserved.")
