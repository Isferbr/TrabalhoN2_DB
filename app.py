from flask import Flask, render_template, redirect, url_for, request
from models import db, Usuario, Jogo, Feedback, CategoriaFeedback, StatusFeedback, VersaoJogo, resumo_avaliacao_jogo, obter_ranking_usuarios, get_feedbacks_categoria_plataforma, get_jogos_por_plataforma, get_feedbacks_por_genero_e_categoria, get_feedbacks_por_genero_e_status
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://admin:1Km7Q5$S@db-wvp.cvemsq2gol4m.us-east-2.rds.amazonaws.com/wvp"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Inicializar o banco de dados
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resumo_jogos')
def resumo_jogos():
    dados = resumo_avaliacao_jogo()
    return render_template('resumo_jogos.html', resumo=dados)

@app.route("/ranking")
def ranking_usuarios():
    ranking = list(enumerate(obter_ranking_usuarios(), start=1))
    return render_template("ranking.html", ranking=ranking)

@app.route('/feedbacks_list')
def list_feedbacks():
    feedbacks = get_feedbacks_categoria_plataforma()
    return render_template('feedbacks_list.html', feedbacks=feedbacks)

@app.route('/jogos-plataforma')
def jogos_por_plataforma():
    jogos = get_jogos_por_plataforma()
    return render_template('jogos_por_plataforma.html', jogos=jogos)

@app.route('/feedbacks-genero-categoria')
def feedbacks_genero_categoria():
    dados = get_feedbacks_por_genero_e_categoria()
    return render_template('feedbacks_genero_categoria.html', dados=dados)

@app.route('/feedbacks-genero-status')
def feedbacks_genero_status():
    dados = get_feedbacks_por_genero_e_status()
    return render_template('feedbacks_genero_status.html', dados=dados)

# ------------------------------
# Usuários
# ------------------------------
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios/list.html', usuarios=usuarios)

@app.route('/usuarios/novo', methods=['GET', 'POST'])
def usuario_novo():
    if request.method == 'POST':
        novo = Usuario(
            email=request.form['email'],
            genero=request.form['genero'],
            data_nascimento=request.form['data_nascimento']
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('get_usuarios'))
    return render_template('usuarios/form.html', usuario=None)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def usuario_editar(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.email = request.form['email']
        usuario.genero = request.form['genero']
        usuario.data_nascimento = request.form['data_nascimento']
        db.session.commit()
        return redirect(url_for('get_usuarios'))
    return render_template('usuarios/form.html', usuario=usuario)

@app.route('/usuarios/excluir/<int:id>')
def usuario_excluir(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('get_usuarios'))

# ------------------------------
# Categorias de Feedback
# ------------------------------
@app.route('/categorias', methods=['GET'])
def get_categorias():
    categorias = CategoriaFeedback.query.all()
    return render_template('categorias/list.html', categorias=categorias)

@app.route('/categorias/novo', methods=['GET', 'POST'])
def create_categoria():
    if request.method == 'POST':
        nome_categoria = request.form.get('categoria')
        if not nome_categoria:
            flash('O campo categoria é obrigatório.', 'danger')
            return redirect(url_for('create_categoria'))
        nova_categoria = CategoriaFeedback(categoria=nome_categoria)
        db.session.add(nova_categoria)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('get_categorias'))
    return render_template('categorias/form.html', categoria=None)

@app.route('/categorias/editar/<int:id>', methods=['GET', 'POST'])
def edit_categoria(id):
    categoria = CategoriaFeedback.query.get_or_404(id)
    if request.method == 'POST':
        nome_categoria = request.form.get('categoria')
        if not nome_categoria:
            flash('O campo categoria é obrigatório.', 'danger')
            return redirect(url_for('edit_categoria', id=id))
        categoria.categoria = nome_categoria
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('get_categorias'))
    return render_template('categorias/form.html', categoria=categoria)

@app.route('/categorias/excluir/<int:id>')
def delete_categoria(id):
    categoria = CategoriaFeedback.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoria deletada com sucesso!', 'success')
    return redirect(url_for('get_categorias'))

# ------------------------------
# Status de Feedback
# ------------------------------
@app.route('/status')
def get_status():
    status_list = StatusFeedback.query.all()
    return render_template('status/list.html', status_list=status_list)

@app.route('/status/novo', methods=['GET', 'POST'])
def create_status():
    if request.method == 'POST':
        status_fb = request.form['status_fb']
        novo_status = StatusFeedback(status_fb=status_fb)
        db.session.add(novo_status)
        db.session.commit()
        return redirect(url_for('get_status'))
    return render_template('status/form.html', status=None)

@app.route('/status/editar/<int:id>', methods=['GET', 'POST'])
def edit_status(id):
    status = StatusFeedback.query.get_or_404(id)
    if request.method == 'POST':
        status.status_fb = request.form['status_fb']
        db.session.commit()
        return redirect(url_for('get_status'))
    return render_template('status/form.html', status=status)

@app.route('/status/excluir/<int:id>')
def delete_status(id):
    status = StatusFeedback.query.get_or_404(id)
    db.session.delete(status)
    db.session.commit()
    return redirect(url_for('get_status'))

# ------------------------------
# Jogos
# ------------------------------
@app.route('/jogos', methods=['GET'])
def get_jogos():
    jogos = Jogo.query.all()
    return render_template('jogos/list.html', jogos=jogos)

@app.route('/jogos/novo', methods=['GET', 'POST'])
def create_jogo():
    if request.method == 'POST':
        nome_jogo = request.form['nome_jogo']
        plataforma = request.form['plataforma']
        novo_jogo = Jogo(nome_jogo=nome_jogo, plataforma=plataforma)
        db.session.add(novo_jogo)
        db.session.commit()
        return redirect(url_for('get_jogos'))
    return render_template('jogos/form.html', jogo=None)

@app.route('/jogos/editar/<int:id>', methods=['GET', 'POST'])
def edit_jogo(id):
    jogo = Jogo.query.get_or_404(id)
    if request.method == 'POST':
        jogo.nome_jogo = request.form['nome_jogo']
        jogo.plataforma = request.form['plataforma']
        db.session.commit()
        return redirect(url_for('get_jogos'))
    return render_template('jogos/form.html', jogo=jogo)

@app.route('/jogos/excluir/<int:id>')
def delete_jogo(id):
    jogo = Jogo.query.get_or_404(id)
    db.session.delete(jogo)
    db.session.commit()
    return redirect(url_for('get_jogos'))

# ------------------------------
# Versões de Jogos
# ------------------------------
@app.route('/versoes', methods=['GET'])
def get_versoes():
    versoes = VersaoJogo.query.all()
    return render_template('versoes/list.html', versoes=versoes)

@app.route('/versoes/novo', methods=['GET', 'POST'])
def create_versao():
    if request.method == 'POST':
        versao = request.form['versao']
        id_jogo = request.form['id_jogo']
        nova_versao = VersaoJogo(versao=versao, id_jogo=id_jogo)
        db.session.add(nova_versao)
        db.session.commit()
        return redirect(url_for('get_versoes'))
    return render_template('versoes/form.html', versao=None)

@app.route('/versoes/editar/<int:id_jogo>/<string:numero>', methods=['GET', 'POST'])
def edit_versao(id_jogo, numero):
    versao = VersaoJogo.query.get_or_404((id_jogo, numero))
    if request.method == 'POST':
        versao.versao = request.form['versao']
        versao.id_jogo = request.form['id_jogo']
        db.session.commit()
        return redirect(url_for('get_versoes'))
    return render_template('versoes/form.html', versao=versao)

@app.route('/versoes/excluir/<int:id_jogo>/<string:numero>')
def delete_versao(id_jogo, numero):
    versao = VersaoJogo.query.get_or_404((id_jogo, numero))
    db.session.delete(versao)
    db.session.commit()
    return redirect(url_for('get_versoes'))

# ------------------------------
# Feedbacks
# ------------------------------
@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    feedbacks = Feedback.query.all()
    return render_template('feedbacks/list.html', feedbacks=feedbacks)


@app.route('/feedbacks/novo', methods=['GET', 'POST'])
def create_feedback():
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        id_jogo = request.form.get('id_jogo')
        id_categoria = request.form.get('id_categoria')
        id_status = request.form.get('id_status')
        descricao = request.form.get('descricao')
        nota = request.form.get('nota')

        novo_feedback = Feedback(
            id_usuario=id_usuario,
            id_jogo=id_jogo,
            id_categoria=id_categoria,
            id_status=id_status,
            descricao=descricao,
            nota=nota
        )
        db.session.add(novo_feedback)
        db.session.commit()
        return redirect(url_for('get_feedbacks'))
    return render_template('feedbacks/form.html', feedback=None)


@app.route('/feedbacks/editar/<int:id>', methods=['GET', 'POST'])
def edit_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if request.method == 'POST':
        feedback.id_usuario = request.form.get('id_usuario')
        feedback.id_jogo = request.form.get('id_jogo')
        feedback.id_categoria = request.form.get('id_categoria')
        feedback.id_status = request.form.get('id_status')
        feedback.descricao = request.form.get('descricao')
        feedback.nota = request.form.get('nota')
        db.session.commit()
        return redirect(url_for('get_feedbacks'))
    return render_template('feedbacks/form.html', feedback=feedback)


@app.route('/feedbacks/excluir/<int:id>')
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return redirect(url_for('get_feedbacks'))

if __name__ == "__main__":
    app.run(debug=True)
