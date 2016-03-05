import ast
import astor

class Variable(object):
    def __init__(self, name, original_name=None):
        self.name = name
        self.original_name = original_name
        self.in_nodes = []
        self.out_nodes = []

class ObjectVariable(Variable):
    def __init__(self, name, original_name=None):
        super(ObjectVariable, self).__init__(name, original_name)
        self.children = {}

    def extend_from_variable(self, var):
        self.in_nodes = var.in_nodes
        self.out_nodes = var.out_nodes


class VariableCollector(ast.NodeVisitor):
    def __init__(self):
        self.variables = {}
        self.var_rename_map = {}
        self.assignments = []
        self.is_collecting_var = False
        self.current_mode = None
        self.current_variable_list = []

        self._setup_sys_arg() # TODO: better handle importing and func def

    def _setup_sys_arg(self):
        obj_var = ObjectVariable(name="sys.arg")
        self.variables["sys.arg"] = obj_var
        self.var_rename_map["sys.arg"] = { "var": obj_var, "count": 1 }

    def get_var(self, var_name, var_cls=Variable):
        var_item = self.var_rename_map.get(var_name)
        if var_item is None:
            var_item = self.add_var_item(var_name, var_cls)
        return var_item["var"]

    def add_var_item(self, var_name, var_cls=Variable):
        var = self.var_rename_map.get(var_name)
        if var is None:
            var = var_cls(name=var_name)
            self.variables[var_name] = var
            self.var_rename_map[var_name] = {
                "count": 1,
                "var": var
            }
        else:
            new_var_name = "%s_%d" % (var_name, self.var_rename_map[var_name]["count"] + 1)
            var = Variable(name=new_var_name, original_name=var_name)
            self.variables[new_var_name] = var
            self.var_rename_map[var_name]["count"] += 1
            self.var_rename_map[var_name]["var"] = var
        return self.var_rename_map[var_name]

    def set_var(self, var_name, var):
        self.var_rename_map[var_name]["var"] = var
        self.variables[var.name] = var

    def get_obj_var(self, obj_var_name):
        var = self.get_var(obj_var_name, var_cls=ObjectVariable)
        if isinstance(var, Variable):
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
            if obj_var.children.get(src) is None:
                obj_var.children[src] = var
        return var

    def visit_Subscript(self, node):
        if self.is_collecting_var:
            var = self.get_subscript_or_attribute(node)
            self.current_variable_list.append(var)

    def visit_Attribute(self, node):
        if self.is_collecting_var:
            var = self.get_subscript_or_attribute(node)
            self.current_variable_list.append(var)

    def visit_Call(self, node):
        for arg in node.args:
            self.visit(arg)
        for keyword in node.keywords:
            self.visit(keyword)

    def visit_Assign(self, node):
        self.assignments.append(node)

        self.is_collecting_var = True
        self.current_mode = "targets"
        self.current_variable_list = []
        for target in node.targets:
            self.visit(target)
        targets = self.current_variable_list
        self.current_mode = None
        self.is_collecting_var = False

        self.is_collecting_var = True
        self.current_mode = "value"
        self.current_variable_list = []
        self.visit(node.value)
        value = self.current_variable_list
        self.current_mode = None
        self.is_collecting_var = False

        for target_var in targets:
            for value_var in value:
                target_var.out_nodes.append({
                    "lineno": node.lineno,
                    "node": value_var
                })
                value_var.in_nodes.append({
                    "lineno": node.lineno,
                    "node": target_var
                })

    # record the var name
    def visit_Name(self, node):
        if self.is_collecting_var:
            var = None
            if self.current_mode == "targets":
                var_item = self.add_var_item(node.id)
                var = var_item["var"]
            elif self.current_mode == "value":
                var = self.get_var(node.id)
            self.current_variable_list.append(var)

    def generic_visit(self, node):
        #if self.current is not None:
        #    print "warning: {} node in function expression not supported".format(
        #        node.__class__.__name__)
        super(VariableCollector, self).generic_visit(node)
