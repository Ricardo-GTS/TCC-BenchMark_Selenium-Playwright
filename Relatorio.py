import pandas as pd
import json
from tabulate import tabulate

from Structs import *
from Util import *
from Config import *

# ─────────────────────────────────────────────────────────
# RELATÓRIO
# ─────────────────────────────────────────────────────────
def gerar_relatorio(resultados: list[ResultadoCenario]):
    """Imprime e salva o relatório final de comparação."""

    # Organizar por cenário
    por_cenario: dict[int, dict] = {}
    for r in resultados:
        if r.cenario_id not in por_cenario:
            por_cenario[r.cenario_id] = {}
        por_cenario[r.cenario_id][r.ferramenta] = r

    # ── Tabela principal ──────────────────────────────────
    linhas = []
    for cid in sorted(por_cenario):
        sel = por_cenario[cid].get("Selenium")
        pw  = por_cenario[cid].get("Playwright")
        if not sel or not pw:
            continue

        if sel.tempo_medio > 0 and pw.tempo_medio > 0:
            diff_pct = ((pw.tempo_medio - sel.tempo_medio) / sel.tempo_medio) * 100
            diff_str = f"{diff_pct:+.1f}%"
            vencedor = "Playwright" if pw.tempo_medio < sel.tempo_medio else "Selenium"
        else:
            diff_str = "—"
            vencedor = "—"

        linhas.append([
            cid,
            (sel.nome[:38] + "…") if len(sel.nome) > 39 else sel.nome,
            f"{sel.tempo_medio:.2f}s",
            f"{pw.tempo_medio:.2f}s",
            diff_str,
            f"{sel.taxa_sucesso:.0f}%",
            f"{pw.taxa_sucesso:.0f}%",
            vencedor,
        ])

    cabecalho = [
        "Cen.", "Cenário",
        "Sel. (s)", "PW (s)", "Δ Tempo",
        "Sel. %OK", "PW %OK", "Vencedor"
    ]

    print("\n")
    log("═" * 88, "head")
    log("  RELATÓRIO FINAL – Selenium vs. Playwright  │  TCC 2026", "head")
    log("═" * 88, "head")
    print(tabulate(linhas, headers=cabecalho, tablefmt="rounded_outline",
                   stralign="center", numalign="center"))

    # ── Resumo estatístico ────────────────────────────────
    tempos_sel = [r.tempo_medio for r in resultados
                  if r.ferramenta == "Selenium" and r.tempo_medio > 0]
    tempos_pw  = [r.tempo_medio for r in resultados
                  if r.ferramenta == "Playwright" and r.tempo_medio > 0]
    tx_sel     = [r.taxa_sucesso for r in resultados if r.ferramenta == "Selenium"]
    tx_pw      = [r.taxa_sucesso for r in resultados if r.ferramenta == "Playwright"]

    if tempos_sel and tempos_pw:
        media_sel = sum(tempos_sel) / len(tempos_sel)
        media_pw  = sum(tempos_pw) / len(tempos_pw)
        ganho     = ((media_pw - media_sel) / media_sel) * 100

        print()
        log("─" * 60, "head")
        log("  RESUMO ESTATÍSTICO", "head")
        log("─" * 60, "head")
        print(f"  Tempo médio geral  →  Selenium: {media_sel:.2f}s  |  Playwright: {media_pw:.2f}s")
        print(f"  Diferença média    →  {ganho:+.1f}%  ({'Playwright mais rápido' if ganho < 0 else 'Selenium mais rápido'})")
        print(f"  Taxa sucesso média →  Selenium: {sum(tx_sel)/len(tx_sel):.1f}%  |  "
              f"Playwright: {sum(tx_pw)/len(tx_pw):.1f}%")


    # ── Salvar CSV ────────────────────────────────────────
    registros = [asdict(r) for r in resultados]
    df = pd.DataFrame(registros)
    csv_path = OUTPUT_DIR / "resultados_benchmark.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    log(f"\n  ✓ CSV salvo em: {csv_path}", "ok")

    # ── Salvar JSON detalhado ─────────────────────────────
    json_path = OUTPUT_DIR / "resultados_benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    log(f"  ✓ JSON salvo em: {json_path}", "ok")

    # ── Recomendação automática ───────────────────────────
    print()
    log("─" * 60, "head")
    log("  RECOMENDAÇÃO", "head")
    log("─" * 60, "head")
    if tempos_pw and tempos_sel:
        if sum(tempos_pw) < sum(tempos_sel):
            log("  → Playwright apresentou melhor desempenho geral.", "ok")
        else:
            log("  → Selenium apresentou melhor desempenho geral.", "ok")
        pw_ok  = sum(tx_pw) / len(tx_pw)
        sel_ok = sum(tx_sel) / len(tx_sel)
        if pw_ok >= sel_ok:
            log(f"    Playwright: taxa de sucesso {pw_ok:.1f}% ≥ "
                f"Selenium: {sel_ok:.1f}%", "ok")
        else:
            log(f"    Selenium: taxa de sucesso {sel_ok:.1f}% ≥ "
                f"Playwright: {pw_ok:.1f}%", "warn")
    log("═" * 88, "head")
