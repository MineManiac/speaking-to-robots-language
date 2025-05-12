%{
#include "parser.tab.h"
#include <stdlib.h>
#include <string.h>
%}

%%

"var"           { return VAR; }
"int"           { return TYPE_INT; }
"bool"          { return TYPE_BOOL; }
"string"        { return TYPE_STRING; }
"if"            { return IF; }
"else"          { return ELSE; }
"for"           { return FOR; }
"to"            { return TO; }
"while"         { return WHILE; }

"moveForward"   { return MOVEFORWARD; }
"turnLeft"      { return TURNLEFT; }
"turnRight"     { return TURNRIGHT; }
"pick"          { return PICK; }
"drop"          { return DROP; }

"sensor"        { return SENSOR; }
"front"         { return FRONT; }
"left"          { return LEFT; }
"right"         { return RIGHT; }
"back"          { return BACK; }

[0-9]+          { yylval.ival = atoi(yytext); return NUMBER; }
\"([^\\\"]|\\.)*\"  { yylval.sval = strndup(yytext+1, yyleng-2); return STRING_LITERAL; }
"true"|"false"  { yylval.bval = (strcmp(yytext, "true")==0); return BOOL_LITERAL; }

"=="            { return EQ; }
"!="            { return NEQ; }
"<="            { return LE; }
">="            { return GE; }
"<"             { return LT; }
">"             { return GT; }
"&&"            { return AND; }
"||"            { return OR; }
"!"             { return NOT; }

"+"             { return PLUS; }
"-"             { return MINUS; }
"*"             { return MUL; }
"/"             { return DIV; }
"%"             { return MOD; }
"="             { return ASSIGN; }

";"             { return SEMICOLON; }
":"             { return COLON; }
","             { return COMMA; }
"("             { return LPAREN; }
")"             { return RPAREN; }
"{"             { return LBRACE; }
"}"             { return RBRACE; }
"."             { return DOT; }

[a-zA-Z][a-zA-Z0-9_]*  { yylval.sval = strdup(yytext); return IDENTIFIER; }

[ \t\r\n]+      { /* ignora branco */ }

.               { fprintf(stderr, "Unexpected character: %s\n", yytext); }

%%
