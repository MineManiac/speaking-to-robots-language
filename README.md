# Speaking-to-Robots-Language

Lógica da Computação APS

Este repositório implementa uma **DSL de Controle de Robô**, com suporte a:

* Declaração de variáveis
* Atribuições
* Comandos de movimento
* Estruturas de controle (`if`, `for`, `while`)
* Acesso a sensores do robô

---

## Gramática em EBNF

```ebnf
(* Programa = sequência de sentenças *)
<program> ::= { <statement> }

(* Sentenças *)
<statement> ::=
    <var_decl>
  | <assignment>
  | <if_stmt>
  | <for_stmt>
  | <while_stmt>
  | <command_stmt>

(* Declaração de variável *)
<var_decl> ::= "var" <identifier> ":" <type> ";"

(* Atribuição *)
<assignment> ::= <identifier> "=" <expression> ";"

(* If-then[-else] *)
<if_stmt> ::=
    "if" "(" <expression> ")" <block>
  [ "else" <block> ]

(* Laço for i = expr1 to expr2 { … } *)
<for_stmt> ::=
    "for" <identifier> "=" <expression>
    "to" <expression> <block>

(* Laço while (expr) { … } *)
<while_stmt> ::=
    "while" "(" <expression> ")" <block>

(* Chamada de comando *)
<command_stmt> ::= <command> ";"

(* Bloco de sentenças *)
<block> ::= "{" { <statement> } "}"

(* Comandos de movimento e manipulação *)
<command> ::=
    "moveForward" "(" ")"
  | "turnLeft"    "(" ")"
  | "turnRight"   "(" ")"
  | "pick"        "(" ")"
  | "drop"        "(" ")"

(* Expressões: lógicas, relacionais e aritméticas *)
<expression> ::=
    <expression> <logical_op>       <expression>
  | <expression> <relational_op>   <expression>
  | <expression> <additive_op>     <expression>
  | <expression> <multiplicative_op> <expression>
  | "!" <expression>
  | "(" <expression> ")"
  | <sensor_access>
  | <literal>
  | <identifier>

(* Acesso a sensor ex: sensor.front *)
<sensor_access> ::= "sensor" "." <sensor_pos>
<sensor_pos>   ::= "front" | "left" | "right" | "back"

(* Literais *)
<literal>    ::= <number> | <string> | <boolean>
<number>     ::= digit { digit }
<string>     ::= '"' { caractere } '"'
<boolean>    ::= "true" | "false"

(* Operadores *)
<logical_op>        ::= "&&" | "||"
<relational_op>     ::= "==" | "!=" | "<" | ">" | "<=" | ">="
<additive_op>       ::= "+" | "-"
<multiplicative_op> ::= "*" | "/" | "%"

(* Identificadores e tipos *)
<identifier> ::= letter { letter | digit | "_" }
<type>       ::= "int" | "bool" | "string"
```

## Exemplos de Programas

### Exemplo 1: Movimento Básico

```rbt
var passos: int;
passos = 4;

for i = 1 to passos {
    moveForward();
    turnLeft();
}
```

### Exemplo 2: Coletar e Depositar Objetos

```rbt
var coletados: int;
coletados = 0;

while (coletados < 3) {
    moveForward();
    if (sensor.front != "wall") {
        pick();
        coletados = coletados + 1;
    }
}

for i = 1 to coletados {
    moveForward();
    drop();
}
```

---

## Compilação e Execução

Para gerar o analisador e o interpretador sintático:

```bash
bison -d parser.y       # gera parser.tab.c e parser.tab.h
flex scanner.l          # gera lex.yy.c
gcc -o robolang parser.tab.c lex.yy.c -lfl
```

Para executar um programa `.rbt`:

```bash
./robolang < programa.rbt
```

## Testes

* **Validados**: entradas que seguem a EBNF devem retornar exit code `0` e nenhuma mensagem de erro.
* **Inválidos**: entradas fora da gramática devem imprimir `Erro: syntax error` e retornar código diferente de `0`.

Exemplo de teste inválido:

```rbt
for i = to 5 { moveForward(); }
```

---

## Estrutura de Arquivos

```
README.md
parser.y      # Definição da gramática Bison
scanner.l     # Definição do scanner Flex
programa.rbt  # Arquivo Robot
```

> **Observação**: arquivos gerados (`lex.yy.c`, `parser.tab.c`, `parser.tab.h`, `robolang`) não devem ser commitados.
