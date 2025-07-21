from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager
from datetime import timedelta
import MySQLdb.cursors
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
app.secret_key= 'Rodrigues@2025@'
app.permanent_session_lifetime = timedelta(minutes=30)
UPLOAD_FOLDER = 'comprovantes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'site_lojas'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha =  request.form['senha']
        cursor = mysql.connect.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND senha=%s", (email, senha))
        usuario = cursor.fetchone()
        if usuario: 
            session['logado'] = True
            session['nome'] = usuario['nome']
            return redirect('/dashboard')
    else:
        flash("Credenciais inválidas!", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logado'):
        return redirect('/')
    return render_template('dashboard.html', nome=session.get('nome'))

@app.route('/cadastro_loja', methods=['GET', 'POST'])
def cadastro_loja():
    if not session.get('logado'):
        return redirect('/')
    
    if request.method == 'POST':
        nome = request.form['nome']
        fornecedor_internet = request.form['fornecedor_internet']
        fornecedor_alarme = request.form['fornecedor_alarme']
        vencimento = request.form['vencimento']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO lojas (nome, fornecedor_internet, fornecedor_alarme, vencimento)
            VALUES (%s, %s, %s, %s)
        """, (nome, fornecedor_internet, fornecedor_alarme, vencimento))
        mysql.connection.commit()
        flash('Loja cadastrada com sucesso!', 'success')
        return redirect('/dashboard')

    return render_template('cadastro_loja.html')

@app.route('/registrar-fatura', methods=['GET', 'POST'])
def registrar_faturas():
    if not  session.get('logado'):
        return redirect('/')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, nome FROM lojas")
    lojas = cursor.fetchall()

    if request.method == 'POST' :
        loja_id = request.form['loja']
        data_envio = request.form['data_envio']
        arquivo = request.files['comprovante']

        if arquivo:
            nome_arquivo = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
            arquivo.save(caminho)

            cursor.execute("""
                INSERT INTO faturas (loja_id, data_envio, comprovante)
                VALUES (%s, %s, %s)
            """, (loja_id, data_envio, nome_arquivo))
            mysql.connection.commit()

            flash("Fatura foi registrada!", "success")
            return redirect('/dashboard')
        
        return render_template('registrar_fatura.html', lojas= lojas)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
    