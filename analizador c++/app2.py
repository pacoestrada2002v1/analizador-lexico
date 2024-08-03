import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, render_template, request

# Lista de palabras reservadas
reserved = {
    'int': 'INT',
    'main': 'MAIN',
    'return': 'RETURN',
    'include': 'INCLUDE',
    'std': 'STD',
    'cout': 'COUT',
    'iostream': 'IOSTREAM'
}

# Lista de tokens
tokens = [
    'HASH', 'LT', 'GT', 'ID', 'NUMBER', 'STRING', 'SEMI', 'COLON', 'DOUBLECOLON',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'PLUS', 'ASSIGN', 'ERROR'
] + list(reserved.values())

# Expresiones regulares para tokens simples
t_HASH = r'\#'
t_LT = r'\<'
t_GT = r'\>'
t_SEMI = r';'
t_COLON = r':'
t_DOUBLECOLON = r'::'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_PLUS = r'\+'
t_ASSIGN = r'='
t_STRING = r'\"([^\\"]|\\.)*\"'

# Ignorar espacios en blanco y nuevas líneas
t_ignore = ' \t\n'

# Lista para almacenar caracteres ilegales
caracteres_ilegales = []

# Definir las reglas para identificar tokens
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')    # Verificar palabras reservadas
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Manejo de errores léxicos
def t_error(t):
    global caracteres_ilegales
    caracteres_ilegales.append(t.value[0])
    t.lexer.skip(1)

# Construir el analizador léxico
lexer = lex.lex()

# Reglas de la gramática
def p_includes(p):
    'includes : HASH INCLUDE LT IOSTREAM GT INT MAIN LPAREN RPAREN LBRACE STD DOUBLECOLON COUT LT LT STRING SEMI RETURN NUMBER SEMI RBRACE'

def p_error(p):
    global sintactic_errors
    if p:
        sintactic_errors.append(f"Error sintáctico en '{p.value}'")
    else:
        sintactic_errors.append("Error sintáctico en EOF")

# Construir el analizador sintáctico
parser = yacc.yacc()

# Función para analizar una cadena de entrada
# Función para analizar una cadena de entrada
def analizar(data):
    global caracteres_ilegales, sintactic_errors
    caracteres_ilegales = []  # Reiniciar la lista de caracteres ilegales
    sintactic_errors = []  # Reiniciar la lista de errores sintácticos
    lexer.input(data)
    tokens_reconocidos = []
    token_category_counts = {
        'Palabras reservadas': [],
        'Identificadores': [],
        'Números': [],
        'Cadenas': [],
        'Símbolos': [],  # For symbols like +, -, =, etc.
        'Errores': []
    }

    # Initialize counts for all reserved words as well
    for res in reserved.values():
        token_category_counts[res] = []

    # Analizar tokens léxicos
    while True:
        tok = lexer.token()
        if not tok:
            break
        if tok.type in reserved.values():
            category = 'Palabras reservadas'
        elif tok.type == 'ID':
            category = 'Identificadores'
        elif tok.type == 'NUMBER':
            category = 'Números'
        elif tok.type == 'STRING':
            category = 'Cadenas'
        elif tok.type in ['HASH', 'LT', 'GT', 'SEMI', 'COLON', 'DOUBLECOLON', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'PLUS', 'ASSIGN']:
            category = 'Símbolos'
        else:
            category = 'Errores'

        tokens_reconocidos.append((tok.type, tok.value, tok.lineno, tok.lexpos, category))
        token_category_counts[category].append(tok.value)

    # Realizar el análisis sintáctico
    parser.parse(data)

    return tokens_reconocidos, caracteres_ilegales, token_category_counts, sintactic_errors


# Crear la aplicación Flask
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    tokens_reconocidos = []
    caracteres_ilegales = []
    tokens_clasificados = {
        'Palabras reservadas': [],
        'Identificadores': [],
        'Números': [],
        'Cadenas': [],
        'Simbolos': [],
        'Errores': []
    }
    errores_sintacticos = []

    if request.method == 'POST':
        input_text = request.form['input_text']
        tokens_reconocidos, caracteres_ilegales, tokens_clasificados, errores_sintacticos = analizar(input_text)

    return render_template('index.html', tokens_reconocidos=tokens_reconocidos, caracteres_ilegales=caracteres_ilegales, tokens_clasificados=tokens_clasificados, errores_sintacticos=errores_sintacticos)

if __name__ == '__main__':
    app.run(debug=True)
