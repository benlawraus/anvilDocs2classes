from typing import List

from prodict.prodict import Prodict


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


AnvilFileInfo = dict(
    in_file='anvil.html',
    out_file_info=[
        dict(filename='component.py',
             imports="""
from dataclasses import dataclass
from typing import List, Dict
"""),
        dict(filename='anvil_ui.py',
             imports="""
from dataclasses import dataclass
from typing import List,Dict
from _anvil_designer.componentsUI.GoogleMap import GoogleMap
from _anvil_designer.componentsUI.anvil import $primary_classes
from math import pi as PI

""")
        ],
    primary_classes = ['Component', 'Container', 'Media']
    )

GoogleFileInfo = dict(
    in_file='GoogleMap.html',
    out_file_info=[
        dict(filename='GoogleMap.py',
             imports="""
from dataclasses import dataclass
from typing import List, Dict
import _anvil_designer.componentsUI.anvil.component as anvil
"""),
    ],
    primary_classes=[]
)
