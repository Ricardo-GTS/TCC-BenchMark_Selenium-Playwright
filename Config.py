from pathlib import Path


# ─────────────────────────────────────────────────────────
# CONFIGURAÇÕES GERAIS
# ─────────────────────────────────────────────────────────
HEADLESS       = True          # False para ver o navegador
TIMEOUT_MS     = 15_000        # Timeout padrão Playwright (ms)
TIMEOUT_SEC    = 15            # Timeout padrão Selenium (s)
REPETICOES     = 10            # Execuções por cenário para calcular média
PARALLEL_N     = 10            # Workers no cenário 6
SCREENSHOT_N   = 50            # Capturas no cenário 9
OUTPUT_DIR     = Path("resultados_benchmark")
OUTPUT_DIR.mkdir(exist_ok=True)

# URLs dos sites de teste
URLS = {
    "login"       : "https://the-internet.herokuapp.com/login",
    "produtos"    : "https://books.toscrape.com",
    "formulario"  : "https://demoqa.com/automation-practice-form",
    "spa"         : "https://angular.realworld.io/",
    "download"    : "https://the-internet.herokuapp.com/download",
    "xhr"         : "https://reqres.in",
    "screenshots" : "https://books.toscrape.com",
}
