from src.anvilDocs2classes.classes import FileCatalog, AnvilFileInfo, GoogleFileInfo
from src.anvilDocs2classes.entry import convert_module

if __name__ == '__main__':
    file_catalog: FileCatalog = FileCatalog.from_dict({'anvil': AnvilFileInfo, 'GoogleMap': GoogleFileInfo})
    for module_name, item in file_catalog.items():
        convert_module(item)
