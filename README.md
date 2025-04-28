# Speaking-to-Robots-Language
Lógica da Computação APS

Este documento define, em EBNF, uma gramática de **Controle de Robô**, com suporte a:

- Declaração de variáveis  
- Atribuições  
- Comandos de movimento  
- Estruturas de controle (`if`, `for`, `while`)  
- Acesso a sensores do robô  

---

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
