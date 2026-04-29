"""
================================================================================
ANÁLISE COMPARATIVA DE FRAMEWORKS PARA AUTOMAÇÃO WEB: UM ESTUDO DE CASO ENTRE SELENIUM E PLAYWRIGHT
Benchmark completo com 10 cenários e métricas de avaliação
================================================================================
Dependências:
    pip install selenium playwright psutil requests pandas tabulate colorama
    playwright install chromium firefox
    playwright install-deps
================================================================================
Sites de teste utilizados (públicos, disponíveis para automação):
    Login              → https://the-internet.herokuapp.com/login
    Extração produtos  → https://books.toscrape.com
    Formulário         → https://demoqa.com/automation-practice-form
    SPA (React)        → https://angular.realworld.io/
    Download PDF       → https://the-internet.herokuapp.com/download
    XHR/Fetch          → https://reqres.in  (API pública)
    Screenshots        → https://books.toscrape.com
================================================================================
"""

import traceback

from Selenium_cenarios import *
from Playwright_cenarios import *
from Relatorio import *

init(autoreset=True)





# ─────────────────────────────────────────────────────────
# MAPEAMENTO DE CENÁRIOS
# ─────────────────────────────────────────────────────────
CENARIOS = [
    (1,  "Login em formulário simples",
         CenariosSelenium.c01_login,        CenariosPlaywright.c01_login),
    (2,  "Extração de 100 produtos paginados",
         CenariosSelenium.c02_extracao_produtos, CenariosPlaywright.c02_extracao_produtos),
    (3,  "Preenchimento de formulário complexo (10 campos)",
         CenariosSelenium.c03_formulario_complexo, CenariosPlaywright.c03_formulario_complexo),
    (4,  "Navegação em SPA React (5 rotas)",
         CenariosSelenium.c04_spa_navegacao, CenariosPlaywright.c04_spa_navegacao),
    (5,  "Download de arquivo com verificação",
         CenariosSelenium.c05_download_arquivo, CenariosPlaywright.c05_download_arquivo),
    (6,  f"Execução paralela ({PARALLEL_N} workers)",
         CenariosSelenium.c06_execucao_paralela, CenariosPlaywright.c06_execucao_paralela),
    (7,  "Testes cross-browser (múltiplos engines)",
         CenariosSelenium.c07_cross_browser, CenariosPlaywright.c07_cross_browser),
    (8,  "Interceptação de requisição XHR/Fetch",
         CenariosSelenium.c08_interceptacao_xhr, CenariosPlaywright.c08_interceptacao_xhr),
    (9,  f"Captura de screenshots em loop ({SCREENSHOT_N}x)",
         CenariosSelenium.c09_screenshots_loop, CenariosPlaywright.c09_screenshots_loop),
    (10, "Estabilidade em modo headless (CI/CD)",
         CenariosSelenium.c10_estabilidade_headless, CenariosPlaywright.c10_estabilidade_headless),
]

# Recursos nativos de cada ferramenta por cenário.  Selenium, Playwright
"""RECURSO_NATIVO = {
    1:  ("WebDriverWait + EC",   "auto-wait nativo"),
    2:  ("find_elements + loop", "query_selector_all nativo"),
    3:  ("Select + EC explícito","fill/click com auto-wait"),
    4:  ("readyState via JS",    "wait_for_load_state nativo"),
    5:  ("prefs de diretório",   "expect_download nativo"),
    6:  ("ThreadPoolExecutor",   "ThreadPoolExecutor + BrowserContext"),
    7:  ("Chrome + Firefox",     "Chromium + Firefox + WebKit"),
    8:  ("selenium-wire / CDP",  "page.route() nativo"),
    9:  ("save_screenshot loop", "page.screenshot loop"),
    10: ("headless=new flag",    "headless nativo + networkidle"),
}"""
# Recursos e estratégias técnicas aplicadas em cada cenário (Selenium, Playwright)
RECURSO_NATIVO = {
    1:  ("WebDriverWait + EC",           "Auto-wait nativo (Actionability)"),
    2:  ("find_elements + List Parsing", "query_selector_all + Locators"),
    3:  ("JS Injection + Stealth Ops",   "Strict Mode + Actionability Checks"),
    4:  ("readyState via JS (Polling)",  "wait_for_load_state (Events)"),
    5:  ("Profile Prefs + OS Path",      "expect_download + Event Listener"),
    6:  ("ThreadPoolExecutor (Sync)",    "Isolamento via BrowserContext"),
    7:  ("WebDriver Multi-instance",     "Cross-engine (Chromium/FF/WebKit)"),
    8:  ("CDP Network Domain Logs",      "API Mocking/Routing nativo"),
    9:  ("Buffer Write Loop",            "Async Screenshot Stream"),
    10: ("Headless New + Blink Bypass",  "Headless OOTB + Context Isolation"),
}

# ─────────────────────────────────────────────────────────
# EXECUÇÃO DE CENÁRIO
# ─────────────────────────────────────────────────────────
def executar_cenario(cid, nome, fn_sel, fn_pw,
                     n: int = REPETICOES) -> tuple[ResultadoCenario, ResultadoCenario]:
    """Executa um cenário N vezes para cada ferramenta e retorna ResultadoCenario."""

    def rodar_n(ferramenta, fn):
        log(f"  [{ferramenta}] Cenário {cid}: {nome} ({n}x)…", "info")
        metricas = []
        sucessos = 0
        for i in range(n):
            _, t, err = cronometrar(fn)
            ok = err is None
            if ok:
                sucessos += 1
            metricas.append(MetricaExecucao(
                cenario_id=cid, ferramenta=ferramenta,
                sucesso=ok, tempo_seg=t, erro=err
            ))
            simbolo = "✓" if ok else "✗"
            cor = "ok" if ok else "err"
            log(f"    [{i+1:02d}/{n}] {simbolo}  {t:.2f}s "
                + (f"  | {err[:60]}" if err else ""), cor)

        rn = RECURSO_NATIVO.get(cid, ("—", "—"))
        res = ResultadoCenario(
            cenario_id=cid, nome=nome, ferramenta=ferramenta,
            total_execucoes=n, sucessos=sucessos,
            recurso_nativo=rn[0] if ferramenta == "Selenium" else rn[1]
        ).calcular(metricas)
        return res

    r_sel = rodar_n("Selenium",   fn_sel)
    r_pw  = rodar_n("Playwright", fn_pw)
    return r_sel, r_pw



# ─────────────────────────────────────────────────────────
# PONTO DE ENTRADA
# ─────────────────────────────────────────────────────────
def main():
    log("═" * 70, "head")
    log("  TCC – Benchmark: Selenium vs. Playwright", "head")
    log(f"  Repetições por cenário : {REPETICOES}", "head")
    log(f"  Modo headless          : {HEADLESS}", "head")
    log(f"  Workers (cenário 6)    : {PARALLEL_N}", "head")
    log(f"  Screenshots (cenário 9): {SCREENSHOT_N}", "head")
    log(f"  Saída                  : {OUTPUT_DIR.resolve()}", "head")
    log("═" * 70, "head")

    # Cenários a executar (pode filtrar p/ testar subset)
    # Ex: EXECUTAR = [1, 2] para rodar só os cenários 1 e 2
    EXECUTAR = list(range(1, 11))

    todos_resultados: list[ResultadoCenario] = []

    for cid, nome, fn_sel, fn_pw in CENARIOS:
        if cid not in EXECUTAR:
            continue
        log(f"\n{'─'*60}", "head")
        log(f"  CENÁRIO {cid:02d}: {nome}", "head")
        log(f"{'─'*60}", "head")
        try:
            r_sel, r_pw = executar_cenario(cid, nome, fn_sel, fn_pw)
            todos_resultados.extend([r_sel, r_pw])
        except KeyboardInterrupt:
            log("  Interrompido pelo usuário.", "warn")
            break
        except Exception as e:
            log(f"  ERRO FATAL no cenário {cid}: {e}", "err")
            traceback.print_exc()

    if todos_resultados:
        gerar_relatorio(todos_resultados)
    else:
        log("Nenhum resultado coletado.", "err")


if __name__ == "__main__":
    main()
