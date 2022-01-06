import pathlib
import string
from typing import List, Dict

import bs4

from src.anvilDocs2classes.classes import FileInfo, OutInfo, ModuleSettings, COMMON_IMPORT
from src.anvilDocs2classes.functions import convert_soup, text2class, classes2string, types2string, readfile, \
    html2functions

HomePath = pathlib.Path(__file__).parent.parent.parent


def get_file_names(directory: str) -> List[str]:
    """Returns file names in the `directory`."""
    paths = [file.name for file in pathlib.Path(directory).rglob('*.html')]
    return paths


def set_up_directory(file_info: FileInfo) -> pathlib.Path:
    """Assigns a directory of creates one, for the module specified by the input filename."""
    dir_name = file_info.in_file.replace('.html', '')
    dir_path = HomePath / 'out' / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)
    file__init = dir_path / "__init__.py"
    str__init = ""
    for info in file_info.out_file_info:
        mod_name = info.filename.replace('.py', '')
        str__init += f"from .{mod_name} import *\n"
    file__init.write_text(str__init)
    return dir_path


def default_outfile(fileinfo: FileInfo):
    """Sets default values for the `out_file_info` field."""
    out_name = fileinfo.in_file.replace('.html', '')
    if fileinfo.out_file_info is None:
        fileinfo.out_file_info = [OutInfo(filename=out_name + '.py', imports=COMMON_IMPORT)]
    else:
        for ix, out_file in enumerate(fileinfo.out_file_info):
            if out_file.filename is None:
                add_on = '' if ix == 0 else str(ix)
                out_file.filename = out_name + add_on + '.py'
            if out_file.imports is None:
                out_file.imports = COMMON_IMPORT
    return


def get_module_settings(module_name: str, filename: str) -> FileInfo:
    """Uses the dictionaries defined in `ModuleSettings` to initialize a `FileInfo` class for the module."""
    fileinfo = FileInfo()
    for settings in ModuleSettings:
        if module_name == settings['module_name']:
            fileinfo = FileInfo.from_dict(settings)
    fileinfo.in_file = filename
    default_outfile(fileinfo)
    if fileinfo.primary_classes is None:
        fileinfo.primary_classes = []
    return fileinfo


def html2modulename(soup: bs4.BeautifulSoup) -> str:
    """Parses for the module name."""
    title = soup.title.get_text()
    return title[title.find('|') + 2:].strip()


def string2file(file_info: FileInfo, type_string: str, class_files: List[str], dir_path: pathlib.Path):
    """Writes `type_string` and `class_files to a file designated by `file_info`. The file will be used
    to import in pyDALAnvilWorks."""
    for ix, file_string in enumerate(class_files):
        tmp = file_info.out_file_info[ix].imports
        if '$primary_classes' in tmp:
            prim_clss_str = ','.join(file_info.primary_classes)
            import_str = string.Template(tmp).substitute(primary_classes=prim_clss_str)
        else:
            import_str = tmp
        out_path = dir_path / file_info.out_file_info[ix].filename
        out_path.write_text(import_str + type_string + file_string)
    return


def convert_module(file_name: str):
    """Reads html file, parses it to produce a long string to write to a file. The string will describe
    class and function definitions of the anvil sdk described in the html file."""
    html_doc, n = readfile(file_name, HomePath / 'webpages')
    soup = convert_soup(html_doc)
    module_name = html2modulename(soup)
    file_info = get_module_settings(module_name, file_name)
    print(f"Module name:{module_name}")

    class_, type_catalog = text2class(soup, module_name)
    class_files = classes2string(class_, type_catalog, file_info)
    class_files[0] += html2functions(soup, module_name)
    type_string = types2string(type_catalog)
    dir_path = set_up_directory(file_info)
    string2file(file_info, type_string, class_files, dir_path)
    return


def process_directory():
    """Reads all the files in the directory anc converts them into empty class and function definitions."""
    filenames = get_file_names('webpages')
    for filename in filenames:
        convert_module(filename)
