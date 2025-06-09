import sys
from abc import ABC, abstractmethod

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.next = Token(None, None)
        self.select_next()

    def select_next(self):
        # 1) pular apenas espaços e quebras de linha
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

        # 2) fim de input?
        if self.position >= len(self.source):
            self.next = Token("EOF", None)
            return

        # 3) :, ; e operadores de tamanho 2
        if self.source[self.position] == ':':
            self.next = Token("COLON", ":")
            self.position += 1
            return
        if self.source[self.position] == ';':
            self.next = Token("SEMICOLON", ";")
            self.position += 1
            return

        for op in ["==", "!=", "<=", ">=", "&&", "||"]:
            if self.source.startswith(op, self.position):
                self.next = Token("OPERATOR", op)
                self.position += 2
                return

        # 4) single-char
        char = self.source[self.position]

        if char.isdigit():
            num = ""
            while self.position < len(self.source) and self.source[self.position].isdigit():
                num += self.source[self.position]
                self.position += 1
            self.next = Token("NUMBER", num)
            return

        if char == '"':
            self.position += 1
            s = ""
            while self.position < len(self.source) and self.source[self.position] != '"':
                s += self.source[self.position]
                self.position += 1
            self.position += 1
            self.next = Token("STRING", s)
            return

        if char.isalpha():
            ident = ""
            while self.position < len(self.source) and (
                self.source[self.position].isalnum() or self.source[self.position] == '_'
            ):
                ident += self.source[self.position]
                self.position += 1

            if ident in ("true", "false"):
                self.next = Token("BOOL", ident)
                return

            # keywords da DSL
            if ident == "var":
                self.next = Token("VAR", ident)
            elif ident in ("int", "bool", "string"):
                self.next = Token("TYPE", ident)
            elif ident == "if":
                self.next = Token("IF", ident)
            elif ident == "else":
                self.next = Token("ELSE", ident)
            elif ident == "for":
                self.next = Token("FOR", ident)
            elif ident == "while":
                self.next = Token("WHILE", ident)

            elif ident == "to":
                self.next = Token("TO", ident)

            # comandos de movimento
            elif ident in ("moveForward", "turnLeft", "turnRight", "pick", "drop"):
                self.next = Token("COMMAND", ident)

            # acesso a sensor
            elif ident == "sensor":
                self.next = Token("SENSOR", ident)
            elif ident in ("front", "left", "right", "back"):
                self.next = Token("SENSOR_POS", ident)

            # resto (identificador genérico)
            else:
                self.next = Token("IDENTIFIER", ident)
            return

        # parênteses, chaves, vírgula
        if char == '(':
            self.next = Token("LPAREN", char)
        elif char == ')':
            self.next = Token("RPAREN", char)
        elif char == '{':
            self.next = Token("LBRACE", char)
        elif char == '}':
            self.next = Token("RBRACE", char)
        elif char == ',':
            self.next = Token("COMMA", char)
        elif char == '.':
            self.next = Token("DOT", char)

        # operadores simples
        elif char in "+-*/<>!":
            self.next = Token("OPERATOR", char)
        elif char == '=':
            self.next = Token("ASSIGN", char)
        else:
            raise Exception(f"Invalid character found: '{char}'")

        self.position += 1
    
    def peek(self):
        # Salva estado
        pos, nxt = self.position, self.next
        self.select_next()
        result = self.next
        # Restaura estado
        self.position, self.next = pos, nxt
        return result

class Node(ABC):
    def __init__(self, value=None, children=None):
        self.value = value
        self.children = children if children is not None else []

    @abstractmethod
    def evaluate(self, symbol_table):
        pass

class IntVal(Node):
    def __init__(self, value):
        super().__init__(value=value)
    def evaluate(self, symbol_table):
        return ("int", self.value)

class StrVal(Node):
    def __init__(self, value):
        super().__init__(value=value)
    def evaluate(self, symbol_table):
        return ("string", self.value)

class BoolVal(Node):
    def __init__(self, value):
        super().__init__(value=value)
    def evaluate(self, symbol_table):
        return ("bool", self.value)

class Variable(Node):
    def evaluate(self, symbol_table):
        return symbol_table.get(self.value)

class Assignment(Node):
    def __init__(self, name, expr):
        super().__init__(value=name, children=[expr])
    def evaluate(self, symbol_table):
        # 1) exige que a variável já exista em algum escopo
        expected_type, _ = symbol_table.get(self.value)

        # 2) avalia a expressão
        var_type, var_value = self.children[0].evaluate(symbol_table)

        # 3) checa compatibilidade de tipo
        if var_type != expected_type:
            raise Exception(f"Incompatible types: expected {expected_type}, got {var_type}")

        # 4) atualiza o binding na tabela certa
        symbol_table.set(self.value, (var_type, var_value))

class BinOp(Node):
    def __init__(self, operator, left, right):
        super().__init__(value=operator, children=[left, right])
    def evaluate(self, symbol_table):
        # avalia recursivamente os operandos
        left_type, left_val = self.children[0].evaluate(symbol_table)
        right_type, right_val = self.children[1].evaluate(symbol_table)



        op = self.value
        # agora o seu código normal:
        if op == '+':
            if left_type == right_type:
                return (left_type, left_val + right_val)
            if left_type == "string" or right_type == "string":
                def normalize(val, typ):
                    if typ == "bool":
                        return "true" if val else "false"
                    return str(val)
                return ("string",
                        normalize(left_val, left_type) +
                        normalize(right_val, right_type))
        elif op == '-' and left_type == "int" and right_type == "int":
            return ("int", left_val - right_val)
        elif op == '*' and left_type == "int" and right_type == "int":
            return ("int", left_val * right_val)
        elif op == '/' and left_type == "int" and right_type == "int":
            return ("int", left_val // right_val if right_val != 0 else 0)
        elif op in ["==", "!=", ">", "<", ">=", "<="] and left_type == right_type:
            return ("bool", eval(f"left_val {op} right_val"))
        elif op == '&&' and left_type == "bool" and right_type == "bool":
            return ("bool", left_val and right_val)
        elif op == '||' and left_type == "bool" and right_type == "bool":
            return ("bool", left_val or right_val)
        else:
            raise Exception(f"Type mismatch in operation: {op}")

class UnOp(Node):
    def __init__(self, operator, operand):
        super().__init__(value=operator, children=[operand])
    def evaluate(self, symbol_table):
        typ, val = self.children[0].evaluate(symbol_table)
        if self.value == '+' and typ == "int":
            return ("int", +val)
        elif self.value == '-' and typ == "int":
            return ("int", -val)
        elif self.value == '!' and typ == "bool":
            return ("bool", not val)
        else:
            raise Exception(f"Invalid unary operation {self.value} on type {typ}")
class CommandStmt(Node):
    def __init__(self, name):
        super().__init__(value=name)
    def evaluate(self, symbol_table):
        # aqui você dispara a ação do robô
        print(f"[ROBOT CMD] {self.value}()")  # placeholder
    

class SensorAccess(Node):
    def __init__(self, pos):
        super().__init__(value=pos)
    def evaluate(self, symbol_table):
        # devolve uma string ou bool conforme seu simulador
        return ("string", symbol_table.read_sensor(self.value))

class Print(Node):
    def __init__(self, expr):
        super().__init__(children=[expr])

    def evaluate(self, symbol_table):
        typ, val = self.children[0].evaluate(symbol_table)
        if typ == "bool":
            print("true" if val else "false")
        else:
            print(val)

class Read(Node):
    def evaluate(self, symbol_table):
        return ("int", int(input()))

class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
    
    def declare(self, name):
        self.offsets[name] = 4  # ou incrementa seu contador

    def set(self, name, type_value):
        if name in self.variables:
            self.variables[name] = type_value
        elif self.parent:
            self.parent.set(name, type_value)
        else:
            self.variables[name] = type_value

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise Exception(f"Undefined variable: {name}")
    
    def read_sensor(self, pos):
        """
        Retorna um valor de sensor para a posição `pos` ("front", "left", etc.).
        Aqui você pode conectar ao seu simulador ou hardware; por enquanto,
        vamos devolver um valor padrão.
        """
        # Exemplo de stub: nunca há wall à frente
        # ou você pode implementar lógica real de leitura.
        return "none"



class Block(Node):
    def __init__(self, statements):
        super().__init__(children=statements)

    def evaluate(self, symbol_table):
        if symbol_table.parent is None:
            local_table = symbol_table
        else:
            local_table = SymbolTable(parent=symbol_table)

        for stmt in self.children:
            result = stmt.evaluate(local_table)
            if isinstance(result, tuple):
                return result
        return None

class If(Node):
    def __init__(self, condition, then_block, else_block=None):
        children = [condition, then_block]
        if else_block:
            children.append(else_block)
        super().__init__(children=children)

    def evaluate(self, symbol_table):
        cond_type, cond_val = self.children[0].evaluate(symbol_table)
        if cond_type != "bool":
            raise Exception("Condition in if must be boolean")

        if cond_val:
            # devolve o valor retornado pelo bloco 'then'
            return self.children[1].evaluate(symbol_table)
        elif len(self.children) == 3:
            # devolve o valor retornado pelo bloco 'else'
            return self.children[2].evaluate(symbol_table)
        # se não há else e a condição é falsa
        return None

class For(Node):
    def __init__(self, condition, block):
        super().__init__(children=[condition, block])

    def evaluate(self, symbol_table):
        iteration = 0
        while True:
            cond_type, cond_val = self.children[0].evaluate(symbol_table)
            iteration += 1

            if cond_type != "bool":
                raise Exception("Condition in for must be boolean")
            if not cond_val:
                break

            # executa o corpo do for
            self.children[1].evaluate(symbol_table)

class ForStmt(Node):
    def __init__(self, var_name, start_expr, end_expr, block):
        # var_name: nome da variável de iteração
        # start_expr, end_expr: nós que avaliam para inteiros
        # block: bloco a executar em cada iteração
        super().__init__(value=var_name, children=[start_expr, end_expr, block])

    def evaluate(self, symbol_table):
        # avalia limites
        start_type, start_val = self.children[0].evaluate(symbol_table)
        end_type,   end_val   = self.children[1].evaluate(symbol_table)
        if start_type != "int" or end_type != "int":
            raise Exception("For bounds must be integers")
        # loop inclusivo de start até end
        for i in range(start_val, end_val + 1):
            # atribui o índice na tabela
            symbol_table.set(self.value, ("int", i))
            # executa o corpo
            self.children[2].evaluate(symbol_table)
        return None

class While(Node):
    def __init__(self, condition, block):
        # guarda [condição, bloco]
        super().__init__(children=[condition, block])

    def evaluate(self, symbol_table):
        # repete enquanto a condição for verdadeira
        while True:
            cond_type, cond_val = self.children[0].evaluate(symbol_table)
            if cond_type != "bool":
                raise Exception("Condition in while must be boolean")
            if not cond_val:
                break
            self.children[1].evaluate(symbol_table)

class VarDec(Node):
    def __init__(self, name, var_type):
        super().__init__(value=name)
        self.var_type = var_type

    def evaluate(self, symbol_table):
        # declaração de parâmetro, não faz nada em tempo de execução
        pass

class FuncDec(Node):
    def __init__(self, name, params, ret_type, body):
        super().__init__(value=name, children=params + [body])
        self.ret_type = ret_type

    def evaluate(self, symbol_table):
        symbol_table.set(self.value, ("func", self, self.ret_type))


class FuncCall(Node):
    def __init__(self, name, args):
        super().__init__(value=name, children=args)

    def evaluate(self, symbol_table):
        # busca a declaração da função
        kind, func_node, ret_type = symbol_table.get(self.value)
        if kind != "func":
            raise Exception(f"{self.value} is not a function")

        # checa número de argumentos
        expected = len(func_node.children) - 1
        if len(self.children) != expected:
            raise Exception(f"Argument count mismatch: expected {expected}, got {len(self.children)}")

        # monta novo escopo só para a execução da função
        new_table = SymbolTable(parent=symbol_table)
        # avalia e atribui cada parâmetro NO ESCOPO DA PRÓPRIA FUNÇÃO
        for param_node, arg_node in zip(func_node.children[:-1], self.children):
            arg_type, arg_val = arg_node.evaluate(symbol_table)
            if arg_type != param_node.var_type:
                raise Exception(f"Type mismatch for parameter '{param_node.value}': expected {param_node.var_type}, got {arg_type}")
            # não propaga para o pai: só registra aqui dentro
            new_table.variables[param_node.value] = (arg_type, arg_val)

        # executa o corpo da função
        result = func_node.children[-1].evaluate(new_table)

        # se não há tipo de retorno declarado (void)
        if ret_type is None:
            # mas se houver return com valor, é inválido
            if result is not None:
                raise Exception("Invalid return in a void function")
            return None

        # se houve return explícito, result é uma tupla (tipo, valor)
        if result is not None:
            res_type, res_val = result
            # —— TESTE 109: verifica compatibilidade entre tipo declarado e tipo retornado
            if res_type != ret_type:
                raise Exception(f"Incompatible types: expected {ret_type}, got {res_type}")
            return result

        # se não houve return explícito, devolve (ret_type, None)
        return (ret_type, None)


class Return(Node):
    def __init__(self, expr):
        super().__init__(children=[expr])

    def evaluate(self, symbol_table):
        # avalia a expressão e devolve (tipo, valor)
        return self.children[0].evaluate(symbol_table)
    
# class ReturnException(Exception):
#     def __init__(self, type_val):
#         super().__init__()
#         self.type_val = type_val

class PrePro:
    @staticmethod
    def filter(code):
        lines = code.split('\n')
        no_comments = []
        for line in lines:
            if '//' in line:
                line = line.split('//')[0]
            no_comments.append(line)
        return '\n'.join(no_comments)

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer    = tokenizer
        self.symbol_table = SymbolTable()
        self.declared_vars = set()
    
    def expect(self, typ):
        tok = self.tokenizer.next
        if tok.type != typ:
            raise Exception(f"Expected {typ}, got {tok.type}")
        self.tokenizer.select_next()
        return tok

    def parse(self):
        prog = self.parse_program()
        if self.tokenizer.next.type != "EOF":
            raise Exception(f"Unexpected token {self.tokenizer.next.type}, expected EOF")
        return prog

    def parse_program(self):
        """
        Agora o parser lê todas as statements (var, assignments,
        if, for, while, comandos etc.) até encontrar EOF.
        """
        stmts = []
        while self.tokenizer.next.type != "EOF":
            stmts.append(self.parse_statement())
        return Block(stmts)
    
    def parse_func_declaration(self):
        # 1) consome o token 'func'
        self.tokenizer.select_next()

        # 2) nome da função
        if self.tokenizer.next.type != "IDENTIFIER":
            raise Exception("Expected function name after 'func'")
        name = self.tokenizer.next.value
        self.tokenizer.select_next()

        # 3) parâmetros entre parênteses
        if self.tokenizer.next.type != "LPAREN":
            raise Exception("Expected '(' after function name")
        self.tokenizer.select_next()

        params = []
        if self.tokenizer.next.type != "RPAREN":
            while True:
                if self.tokenizer.next.type != "IDENTIFIER":
                    raise Exception("Expected parameter name")
                pid = self.tokenizer.next.value
                self.tokenizer.select_next()

                if self.tokenizer.next.type != "TYPE":
                    raise Exception("Expected parameter type")
                ptype = self.tokenizer.next.value
                self.tokenizer.select_next()

                params.append(VarDec(pid, ptype))

                if self.tokenizer.next.type == "COMMA":
                    self.tokenizer.select_next()
                    continue
                break

        # 4) fecha ')'
        if self.tokenizer.next.type != "RPAREN":
            raise Exception("Expected ')' after parameters")
        self.tokenizer.select_next()

        # 5) tipo de retorno opcional
        if self.tokenizer.next.type == "TYPE":
            ret_type = self.tokenizer.next.value
            self.tokenizer.select_next()
        else:
            ret_type = None

        # ←── **AQUI**: Criamos o nodo FuncDec *sem* corpo ainda, e registramos
        fdec = FuncDec(name, params, ret_type, None)
        # registra assinatura imediatamente para que chamadas dentro do corpo
        # já encontrem 'fac', 'sum', etc.
        self.symbol_table.set(name, ("func", fdec, ret_type))

        # 6) corpo da função
        body = self.parse_block()
        # agora que temos o body, completamos o FuncDec
        fdec.children[-1] = body

        return fdec

    def parse_block(self):
        # espera abrir chaves
        if self.tokenizer.next.type != "LBRACE":
            raise Exception("Expected '{'")
        self.tokenizer.select_next()

        # —— salvamos o declarado do bloco pai e criamos um novo para este bloco
        outer_declared = self.declared_vars
        self.declared_vars = set()

        stmts = []
        # parse statements até fechar chaves
        while self.tokenizer.next.type != "RBRACE":
            if self.tokenizer.next.type == "EOF":
                raise Exception("Unclosed block")
            stmts.append(self.parse_statement())

        # consome '}'  
        self.tokenizer.select_next()

        if not stmts:
            raise Exception("Empty block is not allowed")

        # —— restauramos o contexto de variáveis do bloco pai
        self.declared_vars = outer_declared

        return Block(stmts)

    def parse_statement(self):
        tok = self.tokenizer.next

        # entrar num bloco "{ ... }" como statement
        if tok.type == "LBRACE":
            return self.parse_block()

        # var x: TYPE;
        if tok.type == "VAR":
            self.tokenizer.select_next()
            name = self.expect("IDENTIFIER").value
            self.expect("COLON")
            vartype = self.expect("TYPE").value
            self.expect("SEMICOLON")
            # aqui você deve DECLARAR e já inicializar na symbol_table
            return VarInit(name, vartype)

        # x = expr;
        if tok.type == "IDENTIFIER":
            name = tok.value
            self.tokenizer.select_next()
            self.expect("ASSIGN")
            expr = self.parse_bexpr()
            self.expect("SEMICOLON")
            return Assignment(name, expr)

        # if (cond) {…} [ else {…} ]
        if tok.type == "IF":
            self.tokenizer.select_next()
            self.expect("LPAREN")
            cond = self.parse_bexpr()
            self.expect("RPAREN")
            then_blk = self.parse_block()
            else_blk = None
            if self.tokenizer.next.type == "ELSE":
                self.tokenizer.select_next()
                else_blk = self.parse_block()
            return If(cond, then_blk, else_blk)

        # while (cond) {…}
        if tok.type == "WHILE":
            self.tokenizer.select_next()
            self.expect("LPAREN")
            cond = self.parse_bexpr()
            self.expect("RPAREN")
            body = self.parse_block()
            return WhileStmt(cond, body)

        # for i = start to end {…}
        if tok.type == "FOR":
            self.tokenizer.select_next()
            var = self.expect("IDENTIFIER").value
            self.expect("ASSIGN")
            start = self.parse_bexpr()
            self.expect("TO")
            end   = self.parse_bexpr()
            body  = self.parse_block()
            return ForStmt(var, start, end, body)

        # moveForward(); turnLeft(); pick(); drop();
        if tok.type == "COMMAND":
            cmd = tok.value
            self.tokenizer.select_next()
            self.expect("LPAREN")
            self.expect("RPAREN")
            self.expect("SEMICOLON")
            return CommandStmt(cmd)

        raise Exception(f"Unexpected token in statement: {tok.type}")
    
    def parse_funccall_statement(self):
        call = self.parse_funccall()
        if self.tokenizer.next.type == "SEMICOLON":
            self.tokenizer.select_next()
        return call

    def parse_bexpr(self):
        node = self.parse_bterm()
        while self.tokenizer.next.type == "OPERATOR" and self.tokenizer.next.value == "||":
            op = self.tokenizer.next.value
            self.tokenizer.select_next()
            node = BinOp(op, node, self.parse_bterm())
        return node

    def parse_bterm(self):
        node = self.parse_bfactor()
        while self.tokenizer.next.type == "OPERATOR" and self.tokenizer.next.value == "&&":
            op = self.tokenizer.next.value
            self.tokenizer.select_next()
            node = BinOp(op, node, self.parse_bfactor())
        return node

    def parse_bfactor(self):
        if self.tokenizer.next.type == "OPERATOR" and self.tokenizer.next.value == "!":
            self.tokenizer.select_next()
            return UnOp("!", self.parse_bfactor())
        else:
            return self.parse_relexpr()

    def parse_relexpr(self):
        node = self.parse_expression()
        if self.tokenizer.next.type == "OPERATOR" and self.tokenizer.next.value in ["==", "!=", ">", "<", ">=", "<="]:
            op = self.tokenizer.next.value
            self.tokenizer.select_next()
            node = BinOp(op, node, self.parse_expression())
        return node

    def parse_expression(self):
        node = self.parse_term()
        while self.tokenizer.next.type == "OPERATOR" and self.tokenizer.next.value in ("+", "-"):
            op = self.tokenizer.next.value
            self.tokenizer.select_next()
            node = BinOp(op, node, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.tokenizer.next.type == "OPERATOR" and self.tokenizer.next.value in ("*", "/", "%"):
            op = self.tokenizer.next.value
            self.tokenizer.select_next()
            node = BinOp(op, node, self.parse_factor())
        return node

    def parse_factor(self):
        tok = self.tokenizer.next

        # — Unário encadeado (+, -, !) —  
        if tok.type == "OPERATOR" and tok.value in ("+", "-", "!"):
            op = tok.value
            self.tokenizer.select_next()
            return UnOp(op, self.parse_factor())

        # — Literais —  
        elif tok.type == "NUMBER":
            self.tokenizer.select_next()
            return IntVal(int(tok.value))
        elif tok.type == "STRING":
            self.tokenizer.select_next()
            return StrVal(tok.value)
        elif tok.type == "BOOL":
            self.tokenizer.select_next()
            return BoolVal(tok.value == "true")
        
        # sensor.front
        if tok.type == "SENSOR":
            self.tokenizer.select_next()
            self.expect("DOT")
            pos = self.expect("SENSOR_POS").value
            return SensorAccess(pos)

        # — Identificador ou chamada de função —  
        elif tok.type == "IDENTIFIER":
            name = tok.value
            self.tokenizer.select_next()
            if self.tokenizer.next.type == "LPAREN":
                return self.parse_funccall(name)
            return Variable(name)

        # — Scan() —  
        elif tok.type == "SCAN":
            self.tokenizer.select_next()
            if self.tokenizer.next.type != "LPAREN":
                raise Exception("Expected '(' after Scan")
            self.tokenizer.select_next()
            if self.tokenizer.next.type != "RPAREN":
                raise Exception("Expected ')' after Scan")
            self.tokenizer.select_next()
            return Read()

        # — Parênteses —  
        elif tok.type == "LPAREN":
            self.tokenizer.select_next()
            expr = self.parse_bexpr()
            if self.tokenizer.next.type != "RPAREN":
                raise Exception("Expected closing parenthesis")
            self.tokenizer.select_next()
            return expr

        else:
            raise Exception("Unexpected token in factor")
    
    def parse_funccall(self, name=None):
        if name is None:
            name = self.tokenizer.next.value
            self.tokenizer.select_next()
        # consome '('
        self.tokenizer.select_next()
        args = []
        if self.tokenizer.next.type != "RPAREN":
            args.append(self.parse_bexpr())
            while self.tokenizer.next.type == "COMMA":
                self.tokenizer.select_next()
                args.append(self.parse_bexpr())
        if self.tokenizer.next.type != "RPAREN":
            raise Exception("Expected ')' in function call")
        self.tokenizer.select_next()
        return FuncCall(name, args)
    
class VarInit(Node):
    """
    Declaração de variável com ou sem inicialização.
    Fica no escopo corrente apenas.
    """
    def __init__(self, name, var_type, expr=None):
        super().__init__(value=name, children=[expr] if expr else [])
        self.var_type = var_type

    def evaluate(self, symbol_table):
        # obtém valor (ou default)
        if self.children:
            val_type, val = self.children[0].evaluate(symbol_table)
            # aqui o tipo já foi checado no parse
        else:
            if self.var_type == "int":
                val = 0
            elif self.var_type == "bool":
                val = False
            elif self.var_type == "string":
                val = ""
        # vincula **só** no escopo corrente
        symbol_table.variables[self.value] = (self.var_type, val)

class WhileStmt(Node):
    def __init__(self, cond, body):
        super().__init__(children=[cond, body])
    def evaluate(self, st):
        while True:
            t,v = self.children[0].evaluate(st)
            if t!="bool": raise Exception("Condition in while must be boolean")
            if not v: break
            self.children[1].evaluate(st)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 main.py <arquivo.go>\n")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        raw_code = f.read()

    clean_code = PrePro.filter(raw_code)

    tokenizer = Tokenizer(clean_code)
    
    parser = Parser(tokenizer)

    try:
        ast = parser.parse()
        ast.evaluate(parser.symbol_table)
        # só chama main se ela existir
        if "main" in parser.symbol_table.variables:
            FuncCall("main", []).evaluate(parser.symbol_table)
    except Exception as e:
        sys.stderr.write(f"Erro: {e}\n")
        sys.exit(1)