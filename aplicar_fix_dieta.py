import os
import re

caminho = os.path.join("templates", "index.html")
with open(caminho, "r", encoding="utf-8") as f:
    html = f.read()

# 1. No menu <nav>, remove o botao separado de Alim. para unificar na aba Cardapio
html = re.sub(
    r'\s*<button[^>]*onclick="abrirAba\(\x27alimentos\x27,\s*this\)"[^>]*>.*?</button>',
    '',
    html,
    flags=re.DOTALL
)

# 2. Se existir <section id="aba-alimentos" ...>...</section>, move seu conteudo para dentro de <section id="aba-cardapio" ...>
m_alim = re.search(r'(<section\s+id="aba-alimentos"[^>]*>)(.*?)(</section>)', html, flags=re.DOTALL)
m_card = re.search(r'(<section\s+id="aba-cardapio"[^>]*>)(.*?)(</section>)', html, flags=re.DOTALL)

if m_alim and m_card:
    conteudo_alim_extra = m_alim.group(2)
    # Remove a secao antiga aba-alimentos
    html = html[:m_alim.start()] + html[m_alim.end():]
    # Rebusca aba-cardapio e anexa o bloco de alimentos/pesagem rapida dentro dela
    m_card = re.search(r'(<section\s+id="aba-cardapio"[^>]*>)(.*?)(</section>)', html, flags=re.DOTALL)
    if m_card:
        bloco_unificado_extra = (
            '\n      <div class="card" style="border-color:#f97316;">'
            '\n        <div style="font-weight:700; font-size:1rem; margin-bottom:8px;">Registro Rapido de Alimentos (Mesma Aba)</div>'
            + conteudo_alim_extra +
            '\n      </div>\n'
        )
        novo_card = m_card.group(1) + m_card.group(2) + bloco_unificado_extra + m_card.group(3)
        html = html[:m_card.start()] + novo_card + html[m_card.end():]

# 3. Garante que abrirAba('alimentos') abra 'cardapio' caso algum clique antigo chame 'alimentos'
if "function abrirAba(" in html:
    html = re.sub(
        r'(function abrirAba\([^)]*\)\s*\{)',
        r"\1 if (nomeAba === 'alimentos') nomeAba = 'cardapio';",
        html,
        count=1
    )

# 4. Injeta script definitivo no final para forcar calculo exato (gramas / 100) * kcal100g e sincronizar totais
script_fix = """
<script id="firefit-fix-gramas-unificado">
(function() {
  function numBR(v) {
    if (v === null || v === undefined) return NaN;
    var s = String(v).trim().replace(",", ".");
    if (!s) return NaN;
    var n = parseFloat(s);
    return isNaN(n) ? NaN : n;
  }

  window.calcGramas100 = function(gramas, kcal100) {
    var g = numBR(gramas);
    var k = numBR(kcal100);
    if (isNaN(g) || g <= 0 || isNaN(k) || k < 0) return 0;
    return Math.round((g / 100.0) * k);
  };

  // Sobrescreve calcularAutoKcalGramas para usar sempre (gramas / 100) * base100
  window.calcularAutoKcalGramas = function(nome, gramasVal) {
    var base100 = (typeof buscarKcal100g === "function") ? buscarKcal100g(nome) : null;
    var g = numBR(gramasVal);
    if (base100 !== null && !isNaN(base100) && !isNaN(g) && g > 0) {
      return Math.round((g / 100.0) * Number(base100));
    }
    if (base100 !== null && !isNaN(base100)) return Math.round(Number(base100));
    return 0;
  };

  // Ajusta addLinhaExcel para mostrar o valor calórico e somar corretamente
  window.addLinhaExcel = function() {
    var nomeEl = document.getElementById("ex-alimento");
    var gramasEl = document.getElementById("ex-gramas");
    var kcal100El = document.getElementById("ex-kcal100");
    var tbody = document.getElementById("excel-linhas-body");
    if (!nomeEl || !gramasEl || !kcal100El || !tbody) return;

    var alimento = (nomeEl.value || "").trim();
    var gramas = numBR(gramasEl.value);
    var kcal100 = numBR(kcal100El.value);
    if (!alimento || isNaN(gramas) || gramas <= 0 || isNaN(kcal100) || kcal100 < 0) {
      alert("Preencha alimento, quantidade em gramas e kcal por 100g.");
      return;
    }

    var kcalItem = window.calcGramas100(gramas, kcal100);
    var tr = document.createElement("tr");
    tr.className = "linha-prato-calc";
    tr.setAttribute("data-gramas", String(gramas));
    tr.setAttribute("data-kcal", String(kcalItem));
    tr.innerHTML =
      "<td>" + alimento + "</td>" +
      "<td>" + gramas + "g</td>" +
      "<td>" + kcalItem + " kcal (" + kcal100 + "/100g)</td>" +
      "<td><button type='button' class='btn-del' onclick='this.closest(\"tr\").remove(); window.recalcularTabelaPrato();'>Tirar</button></td>";

    var totalRow = tbody.querySelector("tr.total-row");
    if (totalRow) {
      tbody.insertBefore(tr, totalRow);
    } else {
      tbody.innerHTML = "";
      tbody.appendChild(tr);
    }

    nomeEl.value = "";
    gramasEl.value = "";
    kcal100El.value = "";
    nomeEl.focus();
    window.recalcularTabelaPrato();
  };

  window.recalcularTabelaPrato = function() {
    var tbody = document.getElementById("excel-linhas-body");
    if (!tbody) return;
    var linhas = tbody.querySelectorAll("tr.linha-prato-calc");
    var totG = 0;
    var totK = 0;
    linhas.forEach(function(tr) {
      totG += numBR(tr.getAttribute("data-gramas")) || 0;
      totK += numBR(tr.getAttribute("data-kcal")) || 0;
    });

    var totalRow = tbody.querySelector("tr.total-row");
    if (!linhas.length) {
      tbody.innerHTML = "<tr><td colspan='4'>Nenhuma linha adicionada ainda.</td></tr>";
      return;
    }
    var htmlTotal =
      "<tr class='total-row'>" +
      "<td><b>Total no prato</b></td>" +
      "<td><b>" + Math.round(totG * 10) / 10 + "g</b></td>" +
      "<td>-</td>" +
      "<td><b>" + Math.round(totK * 10) / 10 + " kcal</b></td>" +
      "</tr>";
    if (totalRow) {
      totalRow.outerHTML = htmlTotal;
    } else {
      tbody.insertAdjacentHTML("beforeend", htmlTotal);
    }
  };

  window.limparLinhasExcel = function() {
    var tbody = document.getElementById("excel-linhas-body");
    if (tbody) {
      tbody.innerHTML = "<tr><td colspan='4'>Nenhuma linha adicionada ainda.</td></tr>";
    }
  };
})();
</script>
"""

html = re.sub(r'<script id="firefit-fix-gramas-unificado">.*?</script>', '', html, flags=re.DOTALL)
if "</body>" in html:
    html = html.replace("</body>", script_fix + "\n</body>", 1)
else:
    html = html + "\n" + script_fix

with open(caminho, "w", encoding="utf-8") as f:
    f.write(html)

print("templates/index.html atualizado com sucesso.")
