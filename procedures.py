from sqlalchemy import text
from models import db

def inserir_jogo_com_versao(nome, nome_plataforma, versao, data_lancamento_jogo, fase_jogo):
    sql = text("""
        CALL jogo_versao(:nome, :nome_plataforma, :versao, :data_lancamento_jogo, :fase_jogo)
    """)
    try:
        db.session.execute(sql, {
            'nome': nome,
            'nome_plataforma': nome_plataforma,
            'versao': versao,
            'data_lancamento_jogo': data_lancamento_jogo,
            'fase_jogo': fase_jogo
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao executar stored procedure: {e}")
        raise

    
def atualizar_feedbacks_lote(id_status_anterior, id_status_novo):
    sql = text("""
        CALL feedbacks_lote(:id_status_anterior, :id_status_novo)
    """)
    try:
        db.session.execute(sql, {
            'id_status_anterior': id_status_anterior,
            'id_status_novo': id_status_novo
        })
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
