import pathlib
import string
from typing import List

from src.anvilDocs2classes.classes import FileInfo, OutInfo
from src.anvilDocs2classes.functions import convert_soup, text2class, classes2string, types2string, readfile, \
    html2functions

HomePath = pathlib.Path(__file__).parent.parent.parent


def set_up_directory(module_name, out_file_info: List[OutInfo])->pathlib.Path:
    dir_name = module_name.replace('anvil.', '')
    dir_path = HomePath / 'out' / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)
    file__init = dir_path / "__init__.py"
    str__init = ""
    for info in out_file_info:
        if module_name == 'anvil.users':
            pass

        mod_name = info.filename.replace('.py', '')
        str__init += f"from .{mod_name} import *\n"
    file__init.write_text(str__init)
    return dir_path


def convert_module(file_info: FileInfo):
    html_doc, n = readfile(file_info.in_file, HomePath / 'webpages')

    soup = convert_soup(html_doc)
    title = soup.title.get_text()
    module_name = title[title.find('anvil'):]
    file_info.module_name = module_name
    print(f"Module name:{module_name}")

    class_, type_catalog = text2class(soup, module_name)
    class_files = classes2string(class_, type_catalog, file_info)
    class_files[0] += html2functions(soup, module_name)
    type_string = types2string(type_catalog)
    dir_path = set_up_directory(module_name,file_info.out_file_info)
    for ix, file_string in enumerate(class_files):
        tmp = file_info.out_file_info[ix].imports
        if '$primary_classes' in tmp:
            prim_clss_str = ','.join(file_info.primary_classes)
            import_str = string.Template(tmp).substitute(primary_classes=prim_clss_str)
        else:
            import_str = tmp
        filename = file_info.out_file_info[ix].filename
        out_path = dir_path / filename
        out_path.write_text(import_str + type_string + file_string)
