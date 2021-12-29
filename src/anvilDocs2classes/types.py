TypeCatalog = dict(
    String='str',
    Number='float',
    Integer='int',
    Color='str',
    Boolean='bool',
    Themerole='str',
    Object='object',
    Seconds='float',
    Items='List[Dict]',
    Datagridcolumns='List[str]',
    Pixels='int',
    Uri='str',
    Html='str',
    Icon='str',
    Form='object'
)

GENERIC_ITEM = """
def default_val(val):
    return lambda: val
"""
