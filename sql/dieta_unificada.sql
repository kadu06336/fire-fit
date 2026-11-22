CREATE TABLE IF NOT EXISTS alimentos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    kcal_100g NUMERIC(8,2) NOT NULL,
    proteina_100g NUMERIC(8,2) DEFAULT 0,
    carbo_100g NUMERIC(8,2) DEFAULT 0,
    gordura_100g NUMERIC(8,2) DEFAULT 0,
    unidade VARCHAR(10) NOT NULL DEFAULT 'g', -- 'g', 'ml' ou 'un'
    usuario_id INTEGER NULL -- NULL = alimento padrão do sistema
);

CREATE TABLE IF NOT EXISTS refeicoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    tipo_refeicao VARCHAR(40) NOT NULL, -- 'Café da Manhã', 'Almoço', 'Lanche', 'Jantar'
    data_refeicao DATE NULL,            -- Preenchido quando for prato do dia
    dia_semana INTEGER NULL,            -- 0=Seg .. 6=Dom quando for cardápio semanal
    is_template BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (usuario_id, tipo_refeicao, data_refeicao, is_template),
    UNIQUE (usuario_id, tipo_refeicao, dia_semana, is_template)
);

CREATE TABLE IF NOT EXISTS refeicao_itens (
    id SERIAL PRIMARY KEY,
    refeicao_id INTEGER NOT NULL REFERENCES refeicoes(id) ON DELETE CASCADE,
    alimento_id INTEGER NOT NULL REFERENCES alimentos(id),
    quantidade NUMERIC(8,2) NOT NULL,
    kcal_calculada NUMERIC(8,2) NOT NULL,
    proteina_calculada NUMERIC(8,2) DEFAULT 0,
    carbo_calculada NUMERIC(8,2) DEFAULT 0,
    gordura_calculada NUMERIC(8,2) DEFAULT 0
);

INSERT INTO alimentos (nome, kcal_100g, proteina_100g, carbo_calculada, gordura_100g, unidade, usuario_id)
SELECT * FROM (VALUES
    ('Arroz Branco Cozido', 128.0, 2.5, 28.1, 0.2, 'g', NULL),
    ('Peito de Frango Grelhado', 159.0, 32.0, 0.0, 2.5, 'g', NULL),
    ('Ovo Cozido', 146.0, 13.0, 0.6, 10.0, 'g', NULL),
    ('Batata Doce Cozida', 77.0, 0.6, 18.4, 0.1, 'g', NULL),
    ('Pão de Forma Integral', 253.0, 9.4, 49.9, 3.7, 'g', NULL),
    ('Banana Prata', 98.0, 1.3, 26.0, 0.1, 'g', NULL),
    ('Aveia em Flocos', 394.0, 13.9, 66.6, 8.5, 'g', NULL),
    ('Whey Protein Concentrado', 400.0, 80.0, 10.0, 5.0, 'g', NULL),
    ('Azeite de Oliva', 884.0, 0.0, 0.0, 100.0, 'ml', NULL)
) AS v(nome, kcal_100g, proteina_100g, carbo_100g, gordura_100g, unidade, usuario_id)
WHERE NOT EXISTS (SELECT 1 FROM alimentos WHERE usuario_id IS NULL);
