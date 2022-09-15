import inspect
from codes.utils import fileModel


def paramPreprocess(input_data, param):
    if param.annotation == list:
        required_input_data = input_data.split(' ')
        if len(input_data) == 0: required_input_data = []
    elif type(input_data) != param.annotation:
        required_input_data = param.annotation(input_data)
    else:
        required_input_data = input_data
    return required_input_data


def read_default_param(strategy_name, main_path, paramFile):
    text = fileModel.read_text(main_path, paramFile)
    strategy_param_text = [t for t in text.split('~') if len(t) > 0 and t.find(strategy_name) >= 0][0].strip()
    strategy_param_dict = {}
    for param_text in strategy_param_text.split('\n')[1:]:
        param_name, value = param_text.split(':', 1)
        strategy_param_dict[param_name.strip()] = value.strip()
    return strategy_param_dict


def input_param(param, strategy_param_dict):
    input_data = input("{}({})\nDefault: {}: ".format(param.name, param.annotation.__name__, strategy_param_dict[param.name]))
    if len(input_data) == 0:
        input_data = strategy_param_dict[param.name]
    return input_data


def ask_params(class_object, main_path, paramFile):
    # read the default params text
    strategy_param_dict = read_default_param(class_object.__name__, main_path, paramFile)

    # asking the params
    sig = inspect.signature(class_object)
    params = {}
    for param in sig.parameters.values():
        if (param.kind == param.KEYWORD_ONLY) and (param.default == param.empty):
            input_data = input_param(param, strategy_param_dict)
            input_data = paramPreprocess(input_data, param)
            params[param.name] = input_data
    return params
