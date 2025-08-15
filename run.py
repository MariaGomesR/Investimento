from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_aleatoria'

TAXAS = {'cdb': 1.2, 'tesouro_direto': 0.9, 'acoes': 2.5}
DATABASE = os.path.join(os.path.dirname(__file__), 'models/investimento.db')

app.config['dados_login'] = []  # Variável global para armazenar os dados do login

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/seguranca')
def seguranca():
    return render_template('seguranca.html')

@app.route('/quemsomos')   
def quemsomos():
    return render_template('quemsomos.html')

@app.route('/comoinvestir')
def comoinvestir():
    return render_template('comoinvestir.html')

@app.route('/investimentos')
def investimentos():
    return render_template('investimentos.html')

@app.route('/simulador', methods=['GET', 'POST'])
def simulador():
    taxa_juros = None
    tipo_investimento = None
    valor_inicial = None
    periodo = None
    resultado = None
 
    if request.method == 'POST':
        tipo_investimento = request.form['tipo_investimento']
        valor_inicial = float(request.form['valor_inicial'])
        periodo = int(request.form['periodo'])
       
        # Determina a taxa de juros com base no tipo de investimento
        taxa_juros = TAXAS.get(tipo_investimento, 0)
       
        # Calcula o valor futuro
        valor_final = valor_inicial * ((1 + (taxa_juros / 100)) ** periodo)
        resultado = f"Valor Futuro: R$ {valor_final:,.2f}"
 
    return render_template('simulador.html', taxa_juros=taxa_juros, tipo_investimento=tipo_investimento, valor_inicial=valor_inicial, periodo=periodo, resultado=resultado)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # Conectar ao banco de dados e verificar o login
        conexao = sqlite3.connect(DATABASE)
        cursor = conexao.cursor()
        
        # Corrigindo a consulta SQL
        sql = "SELECT * FROM tb_usuario WHERE usuario = ? AND senha = ?"
        cursor.execute(sql, (usuario, senha))
        
        login_usuario = cursor.fetchone()
        
        if login_usuario:
            app.config['dados_login'] = login_usuario
            return redirect('/')
        else:
            return redirect('/login')
    
    return render_template('login.html')  # Renderiza a página de login para o método GET

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
     if request.method == 'POST':
        nome_completo = request.form.get('nome_usuario')
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        
        # Verificar se o usuário já existe
        conexao = sqlite3.connect(DATABASE)
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM tb_usuario WHERE usuario = ?", (usuario,))
        if cursor.fetchone():
            return "Usuário já existe. Tente outro."

        # Inserir novo usuário
        cursor.execute("INSERT INTO tb_usuario (nome_completo, usuario, senha) VALUES (?, ?, ?)", (nome_completo, usuario, senha))
        conexao.commit()
        conexao.close()

        return redirect('/login')  # Redireciona para a página de login
     
     return render_template('cadastro.html')  # Retorna o formulário de cadastro

@app.route('/logout')
def logout():
    
    app.config['dados_login'] = []
    return redirect('/')



app.run(host='0.0.0.0', port=80, debug=True)
