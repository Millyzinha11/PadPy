from flask import Flask, redirect, render_template, request
from datetime import datetime, timedelta
from flask_mysqldb import MySQL

# Endereço raiz do shortlink
root_link = 'http://localhost:5000'

app = Flask(__name__)

# Configurações de acesso ao MySQL
app.config['MYSQL_HOST'] = 'localhost'              # Servidor do MySQL
app.config['MYSQL_USER'] = 'root'                   # Usuário do MySQL
app.config['MYSQL_PASSWORD'] = ''                   # Senha do MySQL
app.config['MYSQL_DB'] = 'redirpydb'                # Nome da base de dados
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'      # Retorna dados como DICT
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'    # CRUD em UTF-8

# Variável de conexão com o MySQL
mysql = MySQL(app)


# Configura a conexão com o MySQL para usar utf8mb4 e português do Brasil
@app.before_request
def before_request():
    cur = mysql.connection.cursor()
    cur.execute("SET NAMES utf8mb4")                    # MySQL com UTF-8
    cur.execute("SET character_set_connection=utf8mb4")  # MySQL com UTF-8
    cur.execute("SET character_set_client=utf8mb4")     # MySQL com UTF-8
    cur.execute("SET character_set_results=utf8mb4")    # MySQL com UTF-8
    # Configura os nomes dos dias da semana e meses para português do Brasil
    cur.execute("SET lc_time_names = 'pt_BR'")
    cur.close()


@app.route('/<short>')  # Rota principal que recebe um parâmetro 'short'
def home(short):

    sql = '''
        SELECT link
        FROM redir
        WHERE short = %s AND status = 'on';
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (short,))
    link = cur.fetchone()
    cur.close()

    print('\n\n\n', link, '\n\n\n')

    if link == None:
        return page_not_found(404)

    return redirect(link['link'])


@app.route('/edit/<id>')  # Rota para editar um registro com base no 'id'
def edit(id):
    return f'Editando {id}'


@app.route('/del/<id>')  # Rota para deletar um registro com base no 'id'
def delete(id):

    sql = '''
        UPDATE redir SET status = 'del'
        WHERE id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql)
    link = cur.fetchone()
    cur.close()



    return f'Apagando {id}'


@app.route('/admin')  # Rota para a página de administração
def admin():
    sql = '''
        SELECT id, name, link, short, views,
            DATE_FORMAT(date, '%d/%m/%Y %H:%i') AS datebr,
            DATE_FORMAT(expire, '%d/%m/%Y %H:%i') AS expirebr
        FROM redir
        WHERE status = 'on'
        ORDER BY name, short, date DESC, expire DESC;
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql)
    shortlinks = cur.fetchall()
    cur.close()

    print('\n\n\n', shortlinks, '\n\n\n')

    page = {
        'root_link': root_link,
        'shortlinks': shortlinks
    }

    return render_template('admin.html', page=page)

# Rota para criar um novo shortlink


@app.route('/new', methods=['GET', 'POST'])
def new():
    sended = False  # Variável para indicar se o formulário foi enviado com sucesso
    error = False   # Variável para indicar se houve um erro

    if request.method == 'POST':  # Processa o formulário enviado
        # Converte os dados do formulário para um dicionário
        form = dict(request.form)

        # Consulta SQL para verificar se já existe um shortlink com o mesmo nome ou short
        sql = '''
            SELECT COUNT(id) AS total FROM redir
            WHERE (name = %s OR short = %s)
                AND status = 'on' AND expire > NOW();
        '''
        cur = mysql.connection.cursor()  # Cria um cursor para executar a consulta
        # Executa a consulta com os parâmetros do formulário
        cur.execute(sql, (form['name'], form['short'],))
        total = cur.fetchone()  # Obtém o resultado da consulta

        if int(total['total']) > 0:  # Verifica se já existe um shortlink com o mesmo nome ou short
            error = True  # Define a variável de erro como True
        else:
            # Consulta SQL para inserir um novo shortlink
            sql = '''
                INSERT INTO redir (name, link, short, expire)
                VALUES (%s, %s, %s, %s)
            '''
            # Executa a consulta de inserção
            cur.execute(sql, (form['name'], form['link'],
                              form['short'], form['expire'],))
            mysql.connection.commit()  # Confirma a transação no banco de dados
            sended = True  # Define a variável de sucesso como True

        cur.close()  # Fecha o cursor

    data_atual = datetime.now()  # Obtém a data e hora atuais
    # Calcula a data futura adicionando 1 ano
    data_futura = data_atual + timedelta(days=365)
    one_year = data_futura.strftime(
        "%Y-%m-%d %H:%M:%S")  # Formata a data futura

    page = {
        'expire_sugest': one_year,  # Sugestão de data de expiração
        'sended': sended,  # Indica se o formulário foi enviado com sucesso
        'error': error  # Indica se houve um erro
    }

    # Renderiza o template 'new.html' com os dados da página
    return render_template('new.html', page=page)


# Rota para a página "Sobre"
@app.route('/about')
def about():
    return 'Sobre...'

# Manipulador de erro 404


@app.errorhandler(404)
def page_not_found(e):
    return 'Oooops! Erro 404', 404


# Roda o servidor de desenvolvimento local
if __name__ == '__main__':
    app.run(debug=True)
