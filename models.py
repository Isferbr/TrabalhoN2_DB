from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Enum, func
from datetime import date

db = SQLAlchemy()

# ------------------------------
# Modelo: Usuario
# ------------------------------
class Usuario(db.Model):
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=True)
    genero = db.Column(db.String(1), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)

    feedbacks = db.relationship('Feedback', backref='usuario', lazy=True)

# ------------------------------
# Modelo: CategoriaFeedback
# ------------------------------
class CategoriaFeedback(db.Model):
    __tablename__ = 'categoria_feedback'

    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria = db.Column(db.String(30), nullable=False)

    feedbacks = db.relationship('Feedback', backref='categoria', lazy=True)

# ------------------------------
# Modelo: StatusFeedback
# ------------------------------
class StatusFeedback(db.Model):
    __tablename__ = 'status_feedback'

    id_status = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status_fb = db.Column(db.String(100), nullable=False)

    feedbacks = db.relationship('Feedback', backref='status', lazy=True)

# ------------------------------
# Modelo: Jogo
# ------------------------------
class Jogo(db.Model):
    __tablename__ = 'jogo'

    id_jogo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_jogo = db.Column(db.String(50), nullable=False)
    id_plataforma = db.Column(db.Integer, db.ForeignKey('plataforma.id_plataforma'), nullable=False)

    plataforma = db.relationship('Plataforma', backref='jogos', lazy=True)
    versoes = db.relationship('VersaoJogo', backref='jogo', lazy=True)
    feedbacks = db.relationship('Feedback', backref='jogo', lazy=True)

class Plataforma(db.Model):
    __tablename__ = 'plataforma'

    id_plataforma = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(30), nullable=False, unique=True)

# ------------------------------
# Modelo: VersaoJogo
# ------------------------------
class VersaoJogo(db.Model):
    __tablename__ = 'versao_jogo'

    id_jogo = db.Column(db.Integer, db.ForeignKey('jogo.id_jogo'), primary_key=True)
    numero = db.Column(db.String(10), primary_key=True)
    data_lancamento = db.Column(db.Date, nullable=True)
    fase = db.Column(Enum('alpha', 'beta', 'gold'), nullable=True)

# ------------------------------
# Modelo: Feedback
# ------------------------------
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id_feedback = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria_feedback.id_categoria'), nullable=True)
    id_status = db.Column(db.Integer, db.ForeignKey('status_feedback.id_status'), nullable=True)
    id_jogo = db.Column(db.Integer, db.ForeignKey('jogo.id_jogo'), nullable=True)
    descricao = db.Column(db.Text, nullable=False)
    nota = db.Column(db.Float, nullable=False)

    __table_args__ = (
        CheckConstraint('nota >= 0 AND nota <= 10', name='nota_range'),
    )

# ------------------------------
# Consultas Utilitárias
# ------------------------------
def listar_feedbacks():
    return db.session.query(Feedback).join(Usuario).join(Jogo).join(CategoriaFeedback).join(StatusFeedback).all()

def contar_feedbacks_por_categoria():
    return db.session.query(
        CategoriaFeedback.categoria,
        func.count(Feedback.id_feedback).label("total")
    ).join(Feedback).group_by(CategoriaFeedback.categoria).all()

def listar_versoes_por_jogo():
    return db.session.query(
        Jogo.nome_jogo,
        VersaoJogo.numero,
        VersaoJogo.fase,
        VersaoJogo.data_lancamento
    ).join(VersaoJogo).order_by(Jogo.nome_jogo, VersaoJogo.numero).all()

# Função de consulta
def resumo_avaliacao_jogo():
    return db.session.query(
        Jogo.nome_jogo,
        VersaoJogo.numero.label("versao"),
        func.count(Feedback.id_feedback).label("total_feedbacks"),
        func.avg(Feedback.nota).label("media_avaliacao")
    ).join(
        VersaoJogo, Jogo.id_jogo == VersaoJogo.id_jogo
    ).outerjoin(
        Feedback, Feedback.id_jogo == VersaoJogo.id_jogo
    ).group_by(
        Jogo.nome_jogo, VersaoJogo.numero
    ).order_by(
        Jogo.nome_jogo, VersaoJogo.numero
    ).all()

def obter_ranking_usuarios():
    total_feedbacks = func.coalesce(func.count(Feedback.id_feedback), 0).label("total_feedbacks")

    return db.session.query(
        Usuario.id_usuario,
        Usuario.email,
        total_feedbacks
    ).outerjoin(
        Feedback, Usuario.id_usuario == Feedback.id_usuario
    ).group_by(
        Usuario.id_usuario,
        Usuario.email
    ).order_by(
        total_feedbacks.desc()
    ).all()

def get_feedbacks_categoria_plataforma():
    return (
        db.session.query(
            CategoriaFeedback.categoria.label('categoria_feedback'),
            Plataforma.nome.label('plataforma'),
            Jogo.nome_jogo,
            Feedback.descricao,
            Feedback.nota
        )
        .join(Feedback, Feedback.id_categoria == CategoriaFeedback.id_categoria)
        .join(Jogo, Feedback.id_jogo == Jogo.id_jogo)
        .join(Plataforma, Jogo.id_plataforma == Plataforma.id_plataforma)
        .all()
    )

def get_jogos_por_plataforma():
    return (
        db.session.query(
            Plataforma.nome.label('plataforma'),
            Jogo.nome_jogo
        )
        .join(Jogo, Jogo.id_plataforma == Plataforma.id_plataforma)
        .order_by(Plataforma.nome, Jogo.nome_jogo)
        .all()
    )

def get_feedbacks_por_genero_e_categoria():
    return (
        db.session.query(
            Usuario.genero.label('genero'),
            CategoriaFeedback.categoria.label('categoria_feedback'),
            db.func.count().label('total_feedbacks')
        )
        .join(Feedback, Feedback.id_usuario == Usuario.id_usuario)
        .join(CategoriaFeedback, Feedback.id_categoria == CategoriaFeedback.id_categoria)
        .group_by(Usuario.genero, CategoriaFeedback.categoria)
        .order_by(Usuario.genero, CategoriaFeedback.categoria)
        .all()
    )

def get_feedbacks_por_genero_e_status():
    return (
        db.session.query(
            Usuario.genero.label('genero'),
            StatusFeedback.status_fb.label('tipo_feedback'),
            db.func.count().label('total_feedbacks')
        )
        .join(Feedback, Feedback.id_usuario == Usuario.id_usuario)
        .join(StatusFeedback, Feedback.id_status == StatusFeedback.id_status)
        .group_by(Usuario.genero, StatusFeedback.status_fb)
        .order_by(Usuario.genero, StatusFeedback.status_fb)
        .all()
    )

def buscar_versoes_por_nome_jogo(nome_jogo):
    return (
        db.session.query(
            Jogo.nome_jogo,
            VersaoJogo.numero,
            VersaoJogo.data_lancamento,
            VersaoJogo.fase
        )
        .join(VersaoJogo, Jogo.id_jogo == VersaoJogo.id_jogo)
        .filter(Jogo.nome_jogo == nome_jogo)
        .order_by(VersaoJogo.numero)
        .all()
    )

def buscar_feedbacks_por_status(id_status):
    return Feedback.query.filter_by(id_status=id_status).all()
