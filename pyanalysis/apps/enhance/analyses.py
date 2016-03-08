import json
import ast
import astor

class Variable(object):
    def __init__(self, name, original_name=None):
        self.name = name
        self.original_name = original_name
        self.in_nodes = []
        self.out_nodes = []
        self.lines = []

    def to_dict(self):
        return {
            "name": self.name,
            "original_name": self.original_name,
            "lines": self.lines
        }

class ObjectVariable(Variable):
    def __init__(self, name, original_name=None):
        super(ObjectVariable, self).__init__(name, original_name)
        self.children = {}

    def extend_from_variable(self, var):
        self.in_nodes = var.in_nodes
        self.out_nodes = var.out_nodes
        self.lines = var.lines


class VariableCollector(ast.NodeVisitor):
    def __init__(self):
        self.variables = {}
        self.var_rename_map = {}
        self.assignments = []
        self.is_collecting_var = False
        self.current_old_mode = None
        self.current_mode = None
        self.current_variable_list = []
        self.value = []

        self._setup_sys_argv() # TODO: better handle importing and func def

    def _setup_sys_argv(self):
        obj_var = ObjectVariable(name="sys.argv")
        self.variables["sys.argv"] = obj_var
        self.var_rename_map["sys.argv"] = { "var": obj_var, "count": 1 }

    def is_exist(self, var_name):
        return self.var_rename_map.get(var_name)

    def get_var(self, var_name, var_cls=Variable):
        var_item = self.var_rename_map.get(var_name)
        if var_item is None:
            var_item = self.add_var_item(var_name, var_cls)
        return var_item["var"]

    def add_var_item(self, var_name, var_cls=Variable):
        var_item = self.var_rename_map.get(var_name)
        if var_item is None:
            var = var_cls(name=var_name)
            self.variables[var_name] = var
            self.var_rename_map[var_name] = {
                "count": 1,
                "var": var
            }
        else:
            new_var_name = "%s_%d*" % (var_name, self.var_rename_map[var_name]["count"] + 1)
            cls = var_item["var"].__class__
            try:
                var = cls(name=new_var_name, original_name=var_name)
            except:
                import pdb
                pdb.set_trace()
            self.variables[new_var_name] = var
            self.var_rename_map[var_name]["count"] += 1
            self.var_rename_map[var_name]["var"] = var
        return self.var_rename_map[var_name]

    def set_var(self, var_name, var):
        self.var_rename_map[var_name]["var"] = var
        self.variables[var.name] = var

    def get_obj_var(self, obj_var_name):
        var = self.get_var(obj_var_name, var_cls=ObjectVariable)
        if not isinstance(var, ObjectVariable):
            obj_var = ObjectVariable(name=var.name)
            obj_var.extend_from_variable(var)
            self.set_var(obj_var_name, obj_var)
            var = obj_var
        return var

    def get_subscript_or_attribute(self, node):
        var = None
        if isinstance(node, ast.Subscript) or isinstance(node, ast.Attribute):
            src = astor.to_source(node)
            idx = src.rfind('[') if isinstance(node, ast.Subscript) else src.rfind('.')
            var_name = src[:idx]
            obj_var = self.get_obj_var(var_name)
            var = self.get_var(src)
            obj_var.lines.append(node.lineno)
            var.lines.append(node.lineno)
            if obj_var.children.get(src) is None:
                obj_var.children[src] = var
        return var

    def visit_Subscript(self, node):
        if self.is_collecting_var:
            if self.current_mode == "targets" or self.current_mode == "value":
                var = self.get_subscript_or_attribute(node)
                self.current_variable_list.append(var)
            else:
                self.visit(node.value)

    def visit_Attribute(self, node):
        if self.is_collecting_var:
            if self.current_mode == "targets" or self.current_mode == "value" or self.current_mode == "params":
                var = self.get_subscript_or_attribute(node)
                self.current_variable_list.append(var)
            else:
                self.visit(node.value)

    def visit_Call(self, node):
        if self.current_mode == "targets" or self.current_mode == "value" or self.current_mode == "params":
            if isinstance(node.func, ast.Name) and self.is_exist(node.func.id):
                self.visit(node.func)

            for arg in node.args:
                self.visit(arg)
            for keyword in node.keywords:
                self.visit(keyword)
        else:
            self.is_collecting_var = True
            self.current_old_mode = self.current_mode
            self.current_mode = "func"
            self.current_variable_list = []
            self.visit(node.func)
            func = self.current_variable_list
            self.current_mode = self.current_old_mode
            self.is_collecting_var = False

            if len(func) == 1:
                var = func[0]
                self.is_collecting_var = True
                self.current_old_mode = self.current_mode
                self.current_mode = "params"
                self.current_variable_list = []
                for arg in node.args:
                    self.visit(arg)
                for keyword in node.keywords:
                    self.visit(keyword)
                params = self.current_variable_list
                self.current_mode = self.current_old_mode
                self.is_collecting_var = False

                for param_var in params:
                    var.in_nodes.append({
                        "lineno": node.lineno,
                        "node": param_var,
                        "type": "call"
                    })
                    param_var.out_nodes.append({
                        "lineno": node.lineno,
                        "node": var,
                        "type": "call"
                    })

    def visit_Assign(self, node):
        self.assignments.append(node)

        self.is_collecting_var = True
        self.current_old_mode = self.current_mode
        self.current_mode = "value"
        self.current_variable_list = []
        self.visit(node.value)
        self.value = self.current_variable_list
        self.current_mode = self.current_old_mode
        self.is_collecting_var = False

        self.is_collecting_var = True
        self.current_old_mode = self.current_mode
        self.current_mode = "targets"
        self.current_variable_list = []
        for target in node.targets:
            self.visit(target)
        targets = self.current_variable_list
        self.current_mode = self.current_old_mode
        self.is_collecting_var = False



        for target_var in targets:
            for value_var in self.value:
                target_var.in_nodes.append({
                    "lineno": node.lineno,
                    "node": value_var,
                    "type": "assignment"
                })
                value_var.out_nodes.append({
                    "lineno": node.lineno,
                    "node": target_var,
                    "type": "assignment"
                })

    # record the var name
    def visit_Name(self, node):
        if self.is_collecting_var:
            var = None
            if self.current_mode == "targets":
                if self.is_exist(node.id):
                    var = self.get_var(node.id)
                    if var not in self.value:
                        var_item = self.add_var_item(node.id)
                        var = var_item["var"]
                else:
                    var_item = self.add_var_item(node.id)
                    var = var_item["var"]
            elif self.current_mode == "value" or self.current_mode == "params":
                var = self.get_var(node.id)
            elif self.current_mode == "func" and self.is_exist(node.id):
                var = self.get_var(node.id)

            if var:
                var.lines.append(node.lineno)
                self.current_variable_list.append(var)

    def generic_visit(self, node):
        #if self.current is not None:
        #    print "warning: {} node in function expression not supported".format(
        #        node.__class__.__name__)
        super(VariableCollector, self).generic_visit(node)


def get_script_var_graph(src):
    tree = ast.parse(src)
    cc = VariableCollector()
    cc.visit(tree)
    return cc.variables

def convert_format(variables):
    nodes = []
    node_id_map = {}
    links = []

    for idx, key in enumerate(variables):
        var = variables[key]
        node_id_map[var.name] = idx
        node = var.to_dict()
        node["id"] = idx
        nodes.append(node)

    for idx, key in enumerate(variables):
        var = variables[key]
        for out_node in var.out_nodes:
            src_id = node_id_map[var.name]
            tar_id = node_id_map[out_node["node"].name]
            line_no = out_node["lineno"]
            link = {
                "source": src_id,
                "target": tar_id,
                "line_no": line_no,
                "type": out_node["type"]
            }
            links.append(link)

        if isinstance(var, ObjectVariable):
            for child in var.children:
                src_id = node_id_map[var.name]
                tar_id = node_id_map[child]
                link = {
                    "source": src_id,
                    "target": tar_id,
                    "type": "scope"
                }
                links.append(link)

    return {"nodes": nodes, "links": links}