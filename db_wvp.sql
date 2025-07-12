-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS wvp;
USE wvp;

-- ------------------------------------------------------
-- Tabela: usuario
-- ------------------------------------------------------
CREATE TABLE usuario (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(100) NOT NULL UNIQUE,
  genero CHAR(1) NOT NULL CHECK (genero IN ('M', 'F')),
  data_nascimento DATE NOT NULL
);

-- ------------------------------------------------------
-- Tabela: categoria_feedback
-- ------------------------------------------------------
CREATE TABLE categoria_feedback (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  categoria VARCHAR(30) NOT NULL
);

-- ------------------------------------------------------
-- Tabela: status_feedback
-- ------------------------------------------------------
CREATE TABLE status_feedback (
  id_status INT AUTO_INCREMENT PRIMARY KEY,
  status_fb VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------
-- Tabela: plataforma
-- ------------------------------------------------------
CREATE TABLE plataforma (
  id_plataforma INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(30) NOT NULL UNIQUE
);

-- ------------------------------------------------------
-- Tabela: jogo
-- ------------------------------------------------------
CREATE TABLE jogo (
  id_jogo INT AUTO_INCREMENT PRIMARY KEY,
  nome_jogo VARCHAR(50) NOT NULL,
  id_plataforma INT NOT NULL,
  CONSTRAINT fk_plataforma FOREIGN KEY (id_plataforma) REFERENCES plataforma(id_plataforma)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ------------------------------------------------------
-- Tabela: versao_jogo
-- ------------------------------------------------------
CREATE TABLE versao_jogo (
  id_versao INT AUTO_INCREMENT PRIMARY KEY,
  id_jogo INT NOT NULL,
  numero VARCHAR(10) NOT NULL,
  data_lancamento DATE NOT NULL,
  fase ENUM('alpha','beta','gold') NOT NULL,
  CONSTRAINT fk_versao_jogo FOREIGN KEY (id_jogo) REFERENCES jogo (id_jogo)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT unique_jogo_versao UNIQUE (id_jogo, numero)
);

-- ------------------------------------------------------
-- Tabela: feedback
-- ------------------------------------------------------
CREATE TABLE feedback (
  id_feedback INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT NOT NULL,
  id_categoria INT NOT NULL,
  id_status INT NOT NULL,
  id_jogo INT NOT NULL,
  descricao TEXT NOT NULL,
  nota DECIMAL(3,1) NOT NULL CHECK (nota BETWEEN 0 AND 10),
  CONSTRAINT fk_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_categoria FOREIGN KEY (id_categoria) REFERENCES categoria_feedback (id_categoria)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_status FOREIGN KEY (id_status) REFERENCES status_feedback (id_status)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_feedback_jogo FOREIGN KEY (id_jogo) REFERENCES jogo (id_jogo)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- ------------------------------------------------------
-- Inserir dados
-- ------------------------------------------------------

-- Tabela: plataforma
INSERT INTO plataforma (nome) VALUES
('PC'),
('PlayStation'),
('Xbox');

-- Tabela: usuario
INSERT INTO usuario (email, genero, data_nascimento) VALUES
('alice@example.com', 'F', '1990-05-12'),
('bob@example.com', 'M', '1985-11-23'),
('carol@example.com', 'F', '2000-07-15'),
('anamaria@gmail.com', 'F', '1995-06-15'),
('joaomeliodaspvp03@gmail.com', 'M', '2010-09-03'),
('carimbomiguel123@gmail.com', 'M','1998-10-05');

-- Tabela: categoria_feedback
INSERT INTO categoria_feedback (categoria) VALUES
('Bug'),
('Sugestão'),
('Elogio');

-- Tabela: status_feedback
INSERT INTO status_feedback (status_fb) VALUES
('Aberto'),
('Pendente'),
('Resolvido'),
('Fechado');

-- Tabela: jogo
INSERT INTO jogo (nome_jogo, id_plataforma) VALUES
('Jogo A', 1), -- PC
('Jogo B', 2), -- PlayStation
('Jogo C', 3); -- Xbox

-- Tabela: versao_jogo
INSERT INTO versao_jogo (id_jogo, numero, data_lancamento, fase) VALUES
(1, '1.0', '2022-01-10', 'gold'),
(1, '1.1', '2022-06-15', 'gold'),
(2, '0.9', '2023-02-01', 'beta'),
(3, '0.5', '2024-05-20', 'alpha');

-- Tabela: feedback
INSERT INTO feedback (id_usuario, id_categoria, id_status, id_jogo, descricao, nota) VALUES
(1, 1, 1, 1, 'O personagem trava se agachar, levantar e atirar.', 4.0),
(2, 2, 1, 1, 'Podia ter mais sangue quando o personagem leva um golpe.', 2.0),
(3, 3, 1, 1, 'Gostei dos sons, particulas e vfx.', 5.0);

-- ------------------------------------------------------
-- Views
-- ------------------------------------------------------
-- View para: Resumo de avaliação do jogo --
CREATE VIEW resumo_avaliacao_jogo AS
SELECT 
  j.nome_jogo,
  v.numero AS versao,
  COUNT(f.id_feedback) AS total_feedbacks,
  AVG(f.nota) AS media_avaliacao
FROM jogo j
JOIN versao_jogo v ON j.id_jogo = v.id_jogo
LEFT JOIN feedback f ON j.id_jogo = f.id_jogo
GROUP BY j.id_jogo, v.numero;

-- View para: ranking de usuarios --
CREATE VIEW ranking_usuarios AS
SELECT 
  u.id_usuario,
  u.email,
  COUNT(f.id_feedback) AS total_feedbacks
FROM usuario u
LEFT JOIN feedback f ON u.id_usuario = f.id_usuario
GROUP BY u.id_usuario
ORDER BY total_feedbacks DESC;

-- View para: Listar feedback por categoria e plataforma
CREATE VIEW feedback_categoria_plataforma AS
SELECT
  cf.categoria AS categoria_feedback,
  p.nome AS plataforma,
  j.nome_jogo,
  f.descricao,
  f.nota
FROM feedback f
JOIN categoria_feedback cf ON f.id_categoria = cf.id_categoria
JOIN jogo j ON f.id_jogo = j.id_jogo
JOIN plataforma p ON j.id_plataforma = p.id_plataforma;

-- View para: Listar jogos por plataforma
CREATE VIEW jogos_por_plataforma AS
SELECT
  p.nome AS plataforma,
  j.nome_jogo
FROM jogo j
JOIN plataforma p ON j.id_plataforma = p.id_plataforma
ORDER BY p.nome, j.nome_jogo;

-- View para: Relacionar gêneros de usuários com categorias de jogos
CREATE VIEW genero_categoria_feedback AS
SELECT
  u.genero,
  cf.categoria AS categoria_feedback,
  COUNT(*) AS total_feedbacks
FROM feedback f
JOIN usuario u ON f.id_usuario = u.id_usuario
JOIN categoria_feedback cf ON f.id_categoria = cf.id_categoria
GROUP BY u.genero, cf.categoria
ORDER BY u.genero, cf.categoria;

-- View para: Relacionar gêneros de usuários com tipos de feedback
CREATE VIEW genero_status_feedback AS
SELECT
  u.genero,
  sf.status_fb AS tipo_feedback,
  COUNT(*) AS total_feedbacks
FROM feedback f
JOIN usuario u ON f.id_usuario = u.id_usuario
JOIN status_feedback sf ON f.id_status = sf.id_status
GROUP BY u.genero, sf.status_fb
ORDER BY u.genero, sf.status_fb;

-- teste das views --
SELECT * FROM resumo_avaliacao_jogo;
SELECT * FROM ranking_usuarios;
SELECT * FROM feedback_categoria_plataforma;
SELECT * FROM jogos_por_plataforma;
SELECT * FROM genero_categoria_feedback;
SELECT * FROM genero_status_feedback;

-- ------------------------------------------------------
-- Transações
-- ------------------------------------------------------
-- Transação: Ao inserir novo jogo adicionar versão.
START TRANSACTION;
	INSERT INTO jogo (nome_jogo, plataforma)
	VALUES 
		('Jogo D', 'PC');
	-- Recuperar o último id_jogo gerado para o novo jogo inserido --
	SET @id_jogo_novo = LAST_INSERT_ID();
	INSERT INTO versao_jogo (id_jogo, numero, data_lancamento, fase)
	VALUES (@id_jogo_novo, '1.0', '2011-09-11', 'alpha');
COMMIT;
-- Caso algum erro na transação --
ROLLBACK;

-- Testes Transação --
SELECT * FROM jogo;
SELECT * FROM versao_jogo;
-- Ignorem: verificar dados --

-- Transação: Atualização em lote dos status de feedbacks.
START TRANSACTION;
	UPDATE feedback
	SET id_status = 2
	WHERE id_status = 1;
COMMIT;
-- Caso algum erro na transação --
ROLLBACK;

-- Teste Transação --
SELECT * FROM feedback;
-- Ignorem: verificar dados --

SELECT * FROM jogo;