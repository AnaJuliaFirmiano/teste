from flask import Flask, request, render_template, redirect, url_for, send_file
import mysql.connector
import qrcode
from io import BytesIO

app = Flask(__name__)

# Função para conectar ao banco de dados local
def conectar_local():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="logistica",
        port=3306
    )

# Função para conectar ao banco de dados no Azure
def conectar_azure():
    return mysql.connector.connect(
        host="bdlogclass.mysql.database.azure.com",
        user="aj",
        password="sua_senha_azure",  # Substitua pela sua senha do Azure
        database="logistica",
        port=3306
    )

# Função para selecionar o banco de dados
def get_db_connection(ambiente='local'):
    if ambiente == 'azure':
        return conectar_azure()
    return conectar_local()


@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/salvar-produto', methods=['POST'])
def salvar_produto():
    nome_produto = request.form['nome-produto']
    descricao_produto = request.form['descricao-produto']
    nome_responsavel = request.form['nome-responsavel']
    
    cursor = db.cursor()

    # SQL para inserir os dados
    query = """
    INSERT INTO tb_cadastramento (nome, descri, responsavel)
    VALUES (%s, %s, %s)
    """
    
    # Executar a query com os dados do formulário
    cursor.execute(query, (nome_produto, descricao_produto, nome_responsavel))
    db.commit()

    # Pegar o ID do produto recém-cadastrado
    produto_id = cursor.lastrowid

    cursor.close()

    # Redirecionar para a rota de geração do QR Code
    return redirect(url_for('gerar_qr', codigo_produto=produto_id))

# Função para gerar QR Code com a URL do produto
def gerar_qr_code(produto_id):
    # Gerar a URL com o ID do produto --------------------------------------------------------------LINK
    dados_qr = f"http://127.0.0.1:5000/leitura/{produto_id}"
    
    # Gerar o QR Code com a URL
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(dados_qr)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Converter a imagem para um formato que possa ser enviado pelo Flask
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io

@app.route("/gerar_qr/<codigo_produto>")
def gerar_qr(codigo_produto):
    # Gerar o QR Code com o ID do produto
    qr_image = gerar_qr_code(codigo_produto)
    
    return send_file(qr_image, mimetype='image/png')

# Rota para exibir os dados do produto
@app.route("/produto/<produto_id>")
def exibir_produto(produto_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tb_cadastramento WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    if produto:
        return render_template('leitura.html', produto=produto)
    else:
        return "Produto não encontrado", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)