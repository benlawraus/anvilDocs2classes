# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import pathlib
from dataclasses import dataclass

from prodict_0_8_18.prodict import *
from functions import convert_soup, text2class, classes2string, types2string, import_string, readfile, text2functions

class OutFile(Prodict):
    primary: str
    secondary: str


class FileInfo(Prodict):
    in_file: str
    module_name: str
    out_file_postfix: OutFile


class FileCatalog(Prodict):
    anvil:FileInfo
    GoogleMap:FileInfo



AnvilFileInfo = dict(
    in_file='anvil.html',
    out_file_postfix=dict(primary='1', secondary='2')
)
GoogleFileInfo = dict(
    in_file='GoogleMap.html',
    out_file_postfix=dict(primary='a', secondary='b')
)

HomePath = pathlib.Path(__file__).parent


def convert_module(file_info:FileInfo):
    html_doc, n = readfile(file_info.in_file, HomePath / 'webpages')

    soup = convert_soup(html_doc)
    title = soup.title.get_text()
    module_name = title[title.find('anvil'):]
    print(f"Module name:{module_name}")

    class_, type_catalog = text2class(soup, module_name)
    class_files = classes2string(class_, type_catalog)
    class_files['primary'] += text2functions(soup, module_name)
    type_string = types2string(type_catalog)
    for key in class_files:
        import_str = import_string(module_name)
        out_path = pathlib.Path(__file__).parent/ 'out' / f"{module_name}_{file_info.out_file_postfix[key]}.py"
        out_path.write_text(import_str + type_string + class_files[key])

if __name__ == '__main__':
    file_catalog:FileCatalog=FileCatalog.from_dict({'anvil':AnvilFileInfo, 'GoogleMap':GoogleFileInfo})
    for module_name,item in file_catalog.items():
        convert_module(item)