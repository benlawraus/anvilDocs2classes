from bs4 import BeautifulSoup
from bs4.element import Tag
import pathlib
from typing import Tuple, List, Dict
from string import Template, whitespace

from src.anvilDocs2classes.types import TypeCatalog, GENERIC_ITEM
from defaults import defaults as defaults_py
from prodict.prodict import Prodict
from src.anvilDocs2classes.classes import FileInfo, ClassAttrType


def build_path(filename, directory) -> pathlib.Path:
    root = directory / filename
    return root


def readfile(filename: str, directory: pathlib.Path) -> Tuple[str, List[str]]:
    """Reads a file and outputs the text and an array of newline characters
    used at the end of each line.

    Parameters
    ----------
    filename : str
    directory : str, optional
        Directory of the file. The default is current directory.

    Returns
    -------
    text :
        File as a str
    n : TYPE
        List of strings that contain the types of new_line characters used in the file.
    """
    fn = build_path(filename, directory)
    n = []
    with fn.open("r") as f:
        lines = f.readlines()
        text = ''.join(lines)  # list(f))
        n.extend(f.newlines)
    return text, n


def convert_soup(html_doc):
    """Imports webpage as beautifulsoup object."""
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup


def translate_type(attr_method, type_catalog: Dict[str, str], module_name: str) -> str:
    seconds_list = ('duration', 'current_time', 'interval')
    objects_list = ('items',)
    int_list = ('rows_per_page',)
    attr, of_type, description, _ = list(attr_method.values())

    if 'list' in of_type:
        attr_method['of_type'] = of_type.replace('list(', '').replace(')', '')
        of_type = translate_type(attr_method, type_catalog, module_name)
        return 'List[' + of_type + ']'
    if attr in seconds_list:
        return 'Seconds'
    if attr in objects_list:
        return 'Items'
    if attr in int_list:
        return 'Integer'
    if attr == 'parent':
        return 'Object'
    if 'anvil' in of_type and of_type.count('.') == 1:
        class_name = of_type.replace(' instance', '')
        if module_name == 'anvil':
            # drop the `anvil.`
            class_name = class_name.replace('anvil.', '')
        type_catalog.update({class_name: class_name})
        return class_name
    if module_name in of_type:
        class_name = of_type.replace(' instance', '').split(module_name + '.')[1]
        type_catalog.update({class_name: class_name})
        return class_name
    if "in pixels" in description:
        return 'Pixels'
    if of_type == '':
        return 'String'
    if of_type.count('.') > 1:  # not sure what this is
        return 'Object'
    return of_type.capitalize()


def extract_class_inners(class_sec: Tag,
                         type_catalog: Dict[str, str],
                         module_name) -> Dict[str, Dict[str, str]]:
    """

    :param class_sec:
    :type class_sec:
    :param type_catalog:
    :type type_catalog:
    :param module_name:
    :type module_name:
    :return: `{name: dict(of_type=of_type, description=description, param_description=par)}`
        where `name` is the attribute or complete method definition.
    :rtype:
    """
    class_parts = dict()
    bs_class_parts = class_sec.next_sibling
    while bs_class_parts and bs_class_parts.name != 'hr':
        try:
            # name of attribute or function
            attr_name = bs_class_parts.strong.get_text()
            description = ''
            try:
                # description of attribute or method
                description = bs_class_parts.p.get_text()
            except AttributeError:
                try:
                    # description for methods
                    description = bs_class_parts.next_sibling.next_sibling.get_text()
                except AttributeError:
                    pass
                pass
            par: Dict[str, str] = dict()  # key: name of func arg, value: description of arg
            try:
                # sometimes the methods have parameters (GoogleMap) that have descriptions too
                # mostly for events
                params = bs_class_parts.ul
                for param in params.select('li'):
                    par.update({param.code.get_text(): list(param.stripped_strings)[1]})
            except AttributeError:
                pass
            of_t = ''
            try:
                # type of the attribute, not applicable for methods
                of_t = bs_class_parts.i.get_text()
            except AttributeError:
                pass
            attr_method = dict(attr=attr_name, of_type=of_t, description=description, param_description=par)
            attr_method['of_type'] = translate_type(attr_method, type_catalog, module_name)
            class_parts.update({attr_name: attr_method})
        except AttributeError:
            pass
        bs_class_parts = bs_class_parts.next_sibling
    return class_parts


def extract_class_outers(h3, module_name):
    try:
        div = h3.parent.div
        bs_class_name = h3.code
        class_name = bs_class_name.get_text()
        bs_constructor = div.code
        constructor = bs_constructor.get_text()
        base_class = ''
        try:
            bs_base_class = div.h5
            base_class = bs_base_class.get_text().split('Base class:')[1]
            base_class = base_class.replace(' ', '').replace(module_name + '.', '')
        except AttributeError:
            pass
        return {class_name: dict(base_class=base_class, constructor=constructor)}
    except AttributeError:
        pass
        return dict()


def one_space_only(text: str):
    disallowed_white = [_ix for _ix in whitespace if _ix != ' ']
    _tmp = [_ix for _ix in text if _ix not in disallowed_white]
    _v_list = [_v for ix, _v in enumerate(_tmp) if ix == 0 or not (_tmp[ix - 1] == ' ' and _v == ' ')]
    return ''.join(_v_list)


def assign_parent_default(module_name: str, class_attr: ClassAttrType) -> None:
    """Alters class_attr['parent'] by adding a default field."""
    if 'parent' in class_attr:
        parent_str = 'Container()'
        if 'anvil.' in module_name:
            parent_str = 'anvil.' + parent_str
        class_attr['parent'].update({'default': parent_str})


def assign_item_default(class_attr: ClassAttrType) -> None:
    """Alters class_attr['item'] by adding a default field."""
    if 'item' in class_attr:
        class_attr['item'].update({'default': 'defaultdict(default_val(None))',
                                   'of_type': None})
    return


def assign_defaults(module_name: str, class_name: str, class_attr: ClassAttrType):
    """Retrieves the default value and assigns to the attribute of class."""
    assign_parent_default(module_name, class_attr)
    assign_item_default(class_attr)
    try:
        defaults = getattr(defaults_py, class_name)
    except AttributeError:
        # no defaults there
        return
    for attr_name, attr_value in class_attr.items():
        if attr_name in defaults:
            default_val = defaults.get(attr_name)
            if isinstance(default_val, str):
                default_val = f'"{default_val}"'
            else:
                default_val = str(default_val)
            attr_value.update({'default': default_val})
    return


def text2class(soup, module_name) -> Tuple[Dict, Dict]:
    h3_list = soup.select('.class-header')
    class_ = dict()
    type_catalog = TypeCatalog.copy()
    for h3 in h3_list:
        latest_class = extract_class_outers(h3, module_name)
        class_name = list(latest_class.keys())
        if len(class_name) == 0:
            continue
        name = class_name[0]
        class_.update(latest_class)
        class_sections = h3.parent.div.find_all('h4')
        if len(class_sections) > 1:
            for class_sec in class_sections[1:]:
                if "Properties" in class_sec.get_text():
                    attributes = extract_class_inners(class_sec, type_catalog, module_name)
                    # there might be defaults for this class
                    assign_defaults(module_name, name, attributes)
                    class_[name].update({"attributes": attributes})
                if "Methods" in class_sec.get_text():
                    class_[name].update({"methods": extract_class_inners(class_sec, type_catalog, module_name)})
                if "Events" in class_sec.get_text():
                    class_[name].update({"events": extract_class_inners(class_sec, type_catalog, module_name)})
    return class_, type_catalog


def extract_params(name: str) -> Tuple[str, str]:
    """Extracts method name and arguments from a string taken from the webpage."""
    name_split = name.split('(')
    method_name = name_split[0]
    try:
        params = name_split[1].split(')')[0]
        if params:
            params = params + ')'  # for the case `,properties=)`
            params = ', ' + params.replace('[', '').replace('=)', ')') \
                .replace('=]', '=None').replace('=,', ', ').replace(']', '').replace(')', '')
    except IndexError:
        params = ''
    return method_name, params


def combine_para_description(param_description: Dict) -> str:
    """
    :param param_description:
    :type param_description:
    :return:
    :rtype:
    """
    par = "\n\n"
    param_template = Template("\t\t:param $key: $key_description\n")
    for key, item in param_description.items():
        description = one_space_only(item.replace('- ', ''))
        par += param_template.substitute(key=key, key_description=description)
    if par.strip() == '':
        par = ''
    return par


def method_string(method_dict):
    """Formats the `method_dict` into a string."""
    doc_string_template = Template('''\n\t\t"""$description$param_description\t\t"""''')
    method_template = Template("\tdef $name(self$params):$description\n\t\tpass\n")
    methods = ""
    for name, attr in method_dict.items():
        method_name, params = extract_params(name)
        description = one_space_only(attr['description'])
        param_des = combine_para_description(attr['param_description'])
        doc_string = doc_string_template.substitute(description=description, param_description=param_des)
        if doc_string.replace('"', '').strip() == '':
            doc_string = ''
        methods += method_template.substitute(name=method_name,
                                              params=params,
                                              of_type=attr.get('of_type', ''),
                                              description=doc_string
                                              )
    return methods


def attr_string(attr_dict):
    attrs = ""
    attr_template = Template("\t$name$type_not_none$of_type$default\t\t#  $description\n")
    for name, attr in attr_dict.items():
        type_not_none = ':'
        of_type = attr.get('of_type', '')
        if of_type is None:
            type_not_none = ''
            of_type = ''
        attrs += attr_template.substitute(name=name,
                                          type_not_none=type_not_none,
                                          of_type=of_type,
                                          description=attr.get('description', ''),
                                          default="=" + attr.get('default', 'None')
                                          )
    return attrs


def class2string(key, item):
    class_template = Template("\n@dataclass\nclass $class_name($base_class):\n$attrs$methods$events\tpass\n")
    attrs = attr_string(item.get('attributes', {}))
    methods = method_string(item.get('methods', {}))
    events = method_string(item.get('events', {}))
    master_string = class_template.substitute(class_name=key,
                                              base_class=item.get('base_class', ''),
                                              attrs=attrs,
                                              methods=methods,
                                              events='')  # events)
    return master_string


def text2functions(soup, module_name: str) -> str:
    function_str = ""
    function_template = Template('''def $name($param):\n$tab"""$description"""\n${tab}pass\n''')
    try:
        bs_marker = soup.find(id="functions").next_sibling
    except AttributeError:
        # no functions
        return ''
    func_catalog = Prodict()
    while bs_marker and bs_marker.name != 'h2':
        if bs_marker.name == 'h4':
            func_str = bs_marker.code.get_text()
            while bs_marker.name != 'p':
                bs_marker = bs_marker.next_sibling
            doc_str = bs_marker.get_text()
            func_name, params = extract_params(func_str)
            func_catalog[func_name] = params
            description = one_space_only(doc_str)
            function_str += function_template.substitute(name=func_name, tab="    ", param=params[2:],
                                                         description=description)
        bs_marker = bs_marker.next_sibling

    if module_name == 'anvil' and 'set_url_hash' not in func_catalog:
        function_str += '''
def set_url_hash(*args, **kwargs):
    """This is added for `anvil_extras`. for some reason it is not in the anvil documentation."""
    pass
'''
        func_catalog['set_url_hash'] = '*args, **kwargs'

    return function_str


def classes2string(class_: dict, type_catalog: dict, file_info: FileInfo) -> List[str]:
    # primary_classes = ('Component', 'Container', 'Media')
    class_files = [''] * len(file_info.out_file_info)
    ix = 0
    counter = 0
    for class_name in file_info.primary_classes:
        if class_name not in class_:
            continue
        counter += 1
        class_files[ix] += class2string(class_name, class_[class_name])

    if counter > 0:
        ix = 1

    for class_name in type_catalog:
        if class_name in file_info.primary_classes:
            continue
        if class_name not in class_:
            continue
        class_files[ix] += class2string(class_name, class_[class_name])

    for class_name in class_:
        if class_name in file_info.primary_classes:
            continue
        if class_name in type_catalog:
            continue
        class_files[ix] += class2string(class_name, class_[class_name])

    return class_files


def types2string(type_catalog: Dict):
    types_string = GENERIC_ITEM
    for key, item in TypeCatalog.items():
        types_string += f"{key} = {item}\n"
    return types_string
