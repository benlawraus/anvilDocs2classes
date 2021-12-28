from prodict_0_8_18.prodict import Prodict

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

class Param(Prodict):
    attr: str
    of_type: str
    description: str

