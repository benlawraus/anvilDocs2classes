from typing import List, Dict

from prodict.prodict import Prodict

ClassAttrType = Dict[str, Dict[str, str]]


class OutInfo(Prodict):
    filename: str
    imports: str


class FileInfo(Prodict):
    in_file: str
    module_name: str
    out_file_info: List[OutInfo]
    primary_classes: List[str]


class FileCatalog(Prodict):
    anvil: FileInfo
    GoogleMap: FileInfo
    Users: FileInfo


COMMON_IMPORT = """from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict
"""
ModuleSettings = [
    dict(
        module_name='anvil',
        out_file_info=[
            dict(filename='component.py',
                 imports=COMMON_IMPORT),
            dict(filename='anvil_ui.py',
                 imports=COMMON_IMPORT + """
from _anvil_designer.componentsUI.GoogleMap import GoogleMap
from _anvil_designer.componentsUI.anvil import $primary_classes
from math import pi as PI

""")
        ],
        primary_classes=['Component', 'Container', 'Media']
    ),
    dict(
        module_name='anvil.GoogleMap',
        out_file_info=[
            dict(filename='GoogleMap.py',
                 imports=COMMON_IMPORT + """
import _anvil_designer.componentsUI.anvil.component as anvil
"""),
        ],
        primary_classes=[]
    ),
    dict(
        module_name='anvil.users',
        out_file_info=[
            dict(filename='Users.py',
                 imports=COMMON_IMPORT + """
import _anvil_designer.componentsUI.anvil.component as anvil
"""),
        ],
        primary_classes=[]
    )
]

