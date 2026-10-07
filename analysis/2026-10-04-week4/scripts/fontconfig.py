import sys
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

fonts, config, cache = map(lambda x: Path(x).resolve(), sys.argv[1:4])
assert fonts.is_dir() and list(
    fonts.glob("*.TTF")
), "Provide an authorized Times New Roman font directory."
cache.mkdir(parents=True, exist_ok=True)
config.parent.mkdir(parents=True, exist_ok=True)
root = Element("fontconfig")
SubElement(root, "cachedir").text = str(cache)
SubElement(root, "include", ignore_missing="no").text = "/etc/fonts/fonts.conf"
SubElement(root, "dir").text = str(fonts)
config.write_text(
    '<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">'
    + tostring(root, encoding="unicode")
)
print(config)
