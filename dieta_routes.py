from datetime import date
import os
from flask import Blueprint, jsonify, render_template, request, send_from_directory, session

dieta_bp = Blueprint("dieta_bp", __name__)

TIPOS_REFEICAO = ["Café da Manhã", "Almoço", "Lanche", "Jantar"]
DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def get_usuario_id():
    return session.get("user_id", 1)


def calcular_kcal_por_gramas(kcal_100g, gramas):
    k = float(kcal_100g or 0)
    g = float(gramas or 0)
    if k <= 0 or g <= 0:
        return 0.0
    return round((k / 100.0) * g, 1)


def _pg_url():
    return os.environ.get("DATABASE_URL", "").strip()


def _usar_postgres():
    url = _pg_url()
    if not url:
        return False
    try:
        import psycopg2  # noqa: F401
        return True
    except ImportError:
        return False


def _pg_conn():
    import psycopg2
    return psycopg2.connect(_pg_url())


def _garantir_tabelas_pg(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS dieta_pratos_pg (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            modo VARCHAR(20) NOT NULL DEFAULT 'hoje',
            chave_data VARCHAR(20) NOT NULL,
            alimento VARCHAR(160) NOT NULL,
            gramas NUMERIC(10, 2) NOT NULL,
            kcal_100g NUMERIC(10, 2) NOT NULL DEFAULT 0,
            kcal_calculada NUMERIC(10, 2) NOT NULL DEFAULT 0
        );
        """
    )


def _garantir_estado_json(dados):
    if not isinstance(dados, dict):
        dados = {}
    if "dieta_pratos" not in dados or not isinstance(dados["dieta_pratos"], dict):
        dados["dieta_pratos"] = {}
    pratos = dados["dieta_pratos"]
    pratos.setdefault("por_dia", {})
    pratos.setdefault("semanal", {"0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": []})
    return dados


def _listar_itens(usuario_id, modo, chave):
    if _usar_postgres():
        conn = _pg_conn()
        try:
            with conn.cursor() as cur:
                _garantir_tabelas_pg(cur)
                cur.execute(
                    """
                    SELECT id, alimento, gramas, kcal_100g, kcal_calculada
                    FROM dieta_pratos_pg
                    WHERE usuario_id = %s AND modo = %s AND chave_data = %s
                    ORDER BY id ASC
                    """,
                    (usuario_id, modo, str(chave)),
                )
                rows = cur.fetchall()
                conn.commit()
                return [
                    {
                        "id": r[0],
                        "alimento": r[1],
                        "gramas": float(r[2]),
                        "kcal_100g": float(r[3]),
                        "kcal": float(r[4]),
                    }
                    for r in rows
                ]
        finally:
            conn.close()

    from app import carregar_dados
    dados = _garantir_estado_json(carregar_dados())
    if modo == "semanal":
        return list(dados["dieta_pratos"]["semanal"].get(str(chave), []))
    return list(dados["dieta_pratos"]["por_dia"].get(str(chave), []))


def _adicionar_item(usuario_id, modo, chave, alimento, gramas, kcal_100g):
    kcal = calcular_kcal_por_gramas(kcal_100g, gramas)

    if _usar_postgres():
        conn = _pg_conn()
        try:
            with conn.cursor() as cur:
                _garantir_tabelas_pg(cur)
                cur.execute(
                    """
                    INSERT INTO dieta_pratos_pg
                        (usuario_id, modo, chave_data, alimento, gramas, kcal_100g, kcal_calculada)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (usuario_id, modo, str(chave), alimento, gramas, kcal_100g, kcal),
                )
                novo_id = cur.fetchone()[0]
                conn.commit()
                return {
                    "id": novo_id,
                    "alimento": alimento,
                    "gramas": float(gramas),
                    "kcal_100g": float(kcal_100g),
                    "kcal": kcal,
                }
        finally:
            conn.close()

    from app import carregar_dados, salvar_dados
    dados = _garantir_estado_json(carregar_dados())
    novo_item = {
        "id": int(date.today().strftime("%Y%m%d")) * 100000 + len(dados["dieta_pratos"]["por_dia"]) + len(dados["dieta_pratos"]["semanal"].get(str(chave), [])) + 1,
        "alimento": alimento,
        "gramas": float(gramas),
        "kcal_100g": float(kcal_100g),
        "kcal": kcal,
    }
    if modo == "semanal":
        bucket = dados["dieta_pratos"]["semanal"].setdefault(str(chave), [])
    else:
        bucket = dados["dieta_pratos"]["por_dia"].setdefault(str(chave), [])
    bucket.append(novo_item)
    salvar_dados(dados)
    return novo_item


def _remover_item(usuario_id, item_id):
    if _usar_postgres():
        conn = _pg_conn()
        try:
            with conn.cursor() as cur:
                _garantir_tabelas_pg(cur)
                cur.execute(
                    "DELETE FROM dieta_pratos_pg WHERE id = %s AND usuario_id = %s",
                    (item_id, usuario_id),
                )
                conn.commit()
                return
        finally:
            conn.close()

    from app import carregar_dados, salvar_dados
    dados = _garantir_estado_json(carregar_dados())
    for k, lista in list(dados["dieta_pratos"]["por_dia"].items()):
        dados["dieta_pratos"]["por_dia"][k] = [i for i in lista if str(i.get("id")) != str(item_id)]
    for k, lista in list(dados["dieta_pratos"]["semanal"].items()):
        dados["dieta_pratos"]["semanal"][k] = [i for i in lista if str(i.get("id")) != str(item_id)]
    salvar_dados(dados)


def _limpar_itens(usuario_id, modo, chave):
    if _usar_postgres():
        conn = _pg_conn()
        try:
            with conn.cursor() as cur:
                _garantir_tabelas_pg(cur)
                cur.execute(
                    "DELETE FROM dieta_pratos_pg WHERE usuario_id = %s AND modo = %s AND chave_data = %s",
                    (usuario_id, modo, str(chave)),
                )
                conn.commit()
                return
        finally:
            conn.close()

    from app import carregar_dados, salvar_dados
    dados = _garantir_estado_json(carregar_dados())
    if modo == "semanal":
        dados["dieta_pratos"]["semanal"][str(chave)] = []
    else:
        dados["dieta_pratos"]["por_dia"][str(chave)] = []
    salvar_dados(dados)


def _resumo_itens(itens):
    total_gramas = round(sum(float(i.get("gramas") or 0) for i in itens), 1)
    total_kcal = round(sum(calcular_kcal_por_gramas(i.get("kcal_100g"), i.get("gramas")) for i in itens), 1)
    return {
        "itens": itens,
        "total_gramas": total_gramas,
        "total_kcal": total_kcal,
    }


@dieta_bp.route("/")
@dieta_bp.route("/dieta")
def index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "index.html")
    if os.path.exists(template_path):
        return render_template("index.html")
    return send_from_directory(base_dir, "index.html")


@dieta_bp.get("/api/dieta/prato")
def api_get_prato():
    usuario_id = get_usuario_id()
    modo = request.args.get("modo", "hoje")
    chave = request.args.get("chave") or (
        str(date.today().weekday()) if modo == "semanal" else date.today().isoformat()
    )
    itens = _listar_itens(usuario_id, modo, chave)
    return jsonify({"ok": True, "modo": modo, "chave": chave, **_resumo_itens(itens)})


@dieta_bp.post("/api/dieta/prato")
def api_add_prato():
    usuario_id = get_usuario_id()
    payload = request.get_json(force=True) or {}

    modo = payload.get("modo", "hoje")
    chave = payload.get("chave") or (
        str(date.today().weekday()) if modo == "semanal" else date.today().isoformat()
    )
    alimento = (payload.get("alimento") or "").strip()
    gramas = float(payload.get("gramas") or 0)
    kcal_100g = float(payload.get("kcal_100g") or 0)

    if not alimento or gramas <= 0:
        return jsonify({"ok": False, "erro": "Informe alimento e quantidade em gramas."}), 400

    _adicionar_item(usuario_id, modo, chave, alimento, gramas, kcal_100g)
    itens = _listar_itens(usuario_id, modo, chave)
    return jsonify({"ok": True, "modo": modo, "chave": chave, **_resumo_itens(itens)}), 201


@dieta_bp.delete("/api/dieta/prato/<item_id>")
def api_del_prato(item_id):
    usuario_id = get_usuario_id()
    modo = request.args.get("modo", "hoje")
    chave = request.args.get("chave") or (
        str(date.today().weekday()) if modo == "semanal" else date.today().isoformat()
    )
    _remover_item(usuario_id, item_id)
    itens = _listar_itens(usuario_id, modo, chave)
    return jsonify({"ok": True, "modo": modo, "chave": chave, **_resumo_itens(itens)})


@dieta_bp.post("/api/dieta/prato/limpar")
def api_limpar_prato():
    usuario_id = get_usuario_id()
    payload = request.get_json(force=True) or {}
    modo = payload.get("modo", "hoje")
    chave = payload.get("chave") or (
        str(date.today().weekday()) if modo == "semanal" else date.today().isoformat()
    )
    _limpar_itens(usuario_id, modo, chave)
    itens = _listar_itens(usuario_id, modo, chave)
    return jsonify({"ok": True, "modo": modo, "chave": chave, **_resumo_itens(itens)})


@dieta_bp.post("/api/dieta/prato/aplicar-semanal")
def api_aplicar_semanal():
    usuario_id = get_usuario_id()
    payload = request.get_json(force=True) or {}
    chave_hoje = payload.get("chave_hoje") or date.today().isoformat()
    dia_idx = int(payload.get("dia_idx", date.today().weekday()))

    itens_semana = _listar_itens(usuario_id, "semanal", str(dia_idx))
    _limpar_itens(usuario_id, "hoje", chave_hoje)
    for item in itens_semana:
        _adicionar_item(
            usuario_id,
            "hoje",
            chave_hoje,
            item["alimento"],
            item["gramas"],
            item["kcal_100g"],
        )

    itens_hoje = _listar_itens(usuario_id, "hoje", chave_hoje)
    return jsonify({"ok": True, "modo": "hoje", "chave": chave_hoje, **_resumo_itens(itens_hoje)})
