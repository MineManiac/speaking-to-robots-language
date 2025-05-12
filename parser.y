%{
#include <stdio.h>
#include <stdlib.h>
void yyerror(const char *s) { fprintf(stderr, "Erro: %s\n", s); }
int yylex(void);
%}

/*--------------------------------------------------*
 * 1) Tipos de valor retornados pelos tokens (union)
 *--------------------------------------------------*/
%union {
  int    ival;
  char*  sval;
  int    bval;
}

/*--------------------------------------------------*
 * 2) Declaração de todos os tokens
 *--------------------------------------------------*/
%token <ival>         NUMBER
%token <sval>         STRING_LITERAL IDENTIFIER
%token <bval>         BOOL_LITERAL

%token VAR TYPE_INT TYPE_BOOL TYPE_STRING
%token IF ELSE FOR TO WHILE
%token MOVEFORWARD TURNLEFT TURNRIGHT PICK DROP
%token SENSOR FRONT LEFT RIGHT BACK

%token EQ NEQ LE GE LT GT AND OR NOT
%token PLUS MINUS MUL DIV MOD ASSIGN
%token SEMICOLON COLON COMMA LPAREN RPAREN LBRACE RBRACE DOT

/*--------------------------------------------------*
 * 3) Precedência e associatividade de operadores
 *--------------------------------------------------*/
%left OR
%left AND
%nonassoc EQ NEQ LT LE GT GE
%left PLUS MINUS
%left MUL DIV MOD
%right NOT UMINUS

/*--------------------------------------------------*
 * 4) Símbolo inicial da gramática
 *--------------------------------------------------*/
%start program

%%

/*==================================================*
 * 5) Regras de produção (implementando sua EBNF)
 *==================================================*/

program:
    /* vazio */
  | program statement
  ;

statement:
    var_decl
  | assignment
  | if_stmt
  | for_stmt
  | while_stmt
  | command_stmt
  ;

var_decl:
    VAR IDENTIFIER COLON type SEMICOLON
  ;

type:
    TYPE_INT
  | TYPE_BOOL
  | TYPE_STRING
  ;

assignment:
    IDENTIFIER ASSIGN expression SEMICOLON
  ;

if_stmt:
    IF LPAREN expression RPAREN block
  | IF LPAREN expression RPAREN block ELSE block
  ;

for_stmt:
    FOR IDENTIFIER ASSIGN expression TO expression block
  ;

while_stmt:
    WHILE LPAREN expression RPAREN block
  ;

command_stmt:
    command SEMICOLON
  ;

command:
    MOVEFORWARD LPAREN RPAREN
  | TURNLEFT    LPAREN RPAREN
  | TURNRIGHT   LPAREN RPAREN
  | PICK        LPAREN RPAREN
  | DROP        LPAREN RPAREN
  ;

block:
    LBRACE program RBRACE
  ;

expression:
    expression OR expression
  | expression AND expression
  | expression EQ expression
  | expression NEQ expression
  | expression LT expression
  | expression LE expression
  | expression GT expression
  | expression GE expression
  | expression PLUS expression
  | expression MINUS expression
  | expression MUL expression
  | expression DIV expression
  | expression MOD expression
  | NOT expression
  | MINUS expression             %prec UMINUS
  | LPAREN expression RPAREN
  | sensor_access
  | literal
  | IDENTIFIER
  ;

sensor_access:
    SENSOR DOT sensor_pos
  ;

sensor_pos:
    FRONT
  | LEFT
  | RIGHT
  | BACK
  ;

literal:
    NUMBER
  | STRING_LITERAL
  | BOOL_LITERAL
  ;

%%

/*==============================*
 * 6) Função main e erro
 *==============================*/
int main(void) {
    return yyparse();
}
