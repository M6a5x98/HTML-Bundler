from xml.etree.ElementTree import parse, Element
from sys import argv
from os import path
from pathlib import Path


def get_xpath(element, root):
    path = []
    while element is not None:
        parent = find_parent(root, element)
        if parent is not None:
            siblings = parent.findall(element.tag)
            if len(siblings) == 1:
                path.append(element.tag)
            else:
                index = siblings.index(element) + 1
                path.append(f"{element.tag}[{index}]")
        else:
            path.append(element.tag)
        element = parent
    return '/'.join(path[::-1])


def find_parent(root, child):
    for parent in root.iter():
        if child in parent:
            return parent
    return None


scripts, styles = [], []
tree = parse(argv[1])
root = tree.getroot()
mainFilePath = str(Path(path.dirname(argv[1])).resolve())

for el in tree.findall(".//script[@src]"):
    scripts.append({
        "element": el,
        "path": path.normpath(path.join(mainFilePath, el.attrib.get('src'))),
        "type": "module" if el.attrib.get('type') == "module" else "script",
        "xpath": get_xpath(el, root)
    })

for el in tree.findall(".//link[@rel='stylesheet'][@href]"):
    styles.append({
        "element": el,
        "path": path.normpath(path.join(mainFilePath, el.attrib.get('href'))),
        "xpath": get_xpath(el, root)
    })

for script in scripts:
    parent = find_parent(root, script['element'])
    if parent is not None:
        parent.remove(script['element'])

for style in styles:
    parent = find_parent(root, style['element'])
    if parent is not None:
        parent.remove(style['element'])

for el in root:
    if el.tag.lower() == "head":
        for style in styles:
            style_tag = Element("style", {"type": "text/css"})
            with open(style['path'], 'r') as file:
                style_tag.text = file.read()
            el.append(style_tag)
    elif el.tag.lower() == "body":
        for script in scripts:
            script_tag = Element(
                "script", {"type": "module"}) if script["type"] == "module" else Element("script")
            with open(script['path'], 'r') as file:
                script_tag.text = file.read()
            el.append(script_tag)

try:
    tree.write(f'{argv[2]}.html')
except:
    tree.write('index.html')
