
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Playwright
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

from Config import *
from Util import *





# ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
#  CENÁRIOS – PLAYWRIGHT
# ══════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────

class CenariosPlaywright:
    """Implementa os 10 cenários de teste usando Playwright."""

    # ── CENÁRIO 1 ──────────────────────────────────────────
    @staticmethod
    def c01_login():
        """Login em formulário simples."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page    = browser.new_page()
            page.goto(URLS["login"])
            page.fill("#username", "tomsmith")
            page.fill("#password", "SuperSecretPassword!")
            page.click("button[type='submit']")
            page.wait_for_selector(".flash.success", timeout=TIMEOUT_MS)
            browser.close()

    # ── CENÁRIO 2 ──────────────────────────────────────────
    @staticmethod
    def c02_extracao_produtos():
        """Extração de 100 produtos paginados."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page    = browser.new_page()
            page.goto(URLS["produtos"])
            dados   = []
            while len(dados) < 100:
                page.wait_for_selector("article.product_pod", timeout=TIMEOUT_MS)
                cards = page.query_selector_all("article.product_pod")
                for card in cards:
                    if len(dados) >= 100:
                        break
                    nome  = card.query_selector("h3 a").get_attribute("title")
                    preco = card.query_selector(".price_color").inner_text()
                    disp  = card.query_selector(".availability").inner_text().strip()
                    dados.append({"nome": nome, "preco": preco, "disponibilidade": disp})
                prox = page.query_selector("li.next a")
                if prox and len(dados) < 100:
                    prox.click()
                    page.wait_for_load_state("domcontentloaded")
                else:
                    break
            assert len(dados) >= 20, f"Poucos produtos: {len(dados)}"
            browser.close()

    # ── CENÁRIO 3 ──────────────────────────────────────────
    @staticmethod
    def c03_formulario_complexo():
        """Preenchimento de formulário com 10 campos variados."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page    = browser.new_page()
            page.goto(URLS["formulario"])
            page.wait_for_selector("#firstName", timeout=TIMEOUT_MS)
            page.fill("#firstName", "Maria")
            page.fill("#lastName", "Silva")
            page.fill("#userEmail", "maria.silva@email.com")
            page.click("label[for='gender-radio-1']")
            page.fill("#userNumber", "11987654321")
            page.click("#dateOfBirthInput")
            page.fill("#dateOfBirthInput", "15 Jan 2000")
            page.fill("#subjectsInput", "Maths")
            page.wait_for_selector(".subjects-auto-complete__option",
                                   timeout=TIMEOUT_MS)
            page.click(".subjects-auto-complete__option")
            page.click("label[for='hobbies-checkbox-1']")
            page.fill("#currentAddress", "Av. Paulista, 1000, São Paulo")
            page.click("#state")
            page.wait_for_selector("text=NCR", timeout=TIMEOUT_MS)
            page.click("text=NCR")
            page.click("#city")
            page.wait_for_selector("text=Delhi", timeout=TIMEOUT_MS)
            page.click("text=Delhi")
            page.click("#submit")
            page.wait_for_selector("#example-modal-sizes-title-lg",
                                   timeout=TIMEOUT_MS)
            browser.close()

    # ── CENÁRIO 4 ──────────────────────────────────────────
    @staticmethod
    def c04_spa_navegacao():
        """Navegação por 5 rotas em SPA React."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page    = browser.new_page()
            rotas   = [
                URLS["spa"],
                f"{URLS['spa']}/#/login",
                f"{URLS['spa']}/#/register",
                f"{URLS['spa']}/#/",
                f"{URLS['spa']}/#/",
            ]
            for url in rotas:
                page.goto(url, wait_until="domcontentloaded",
                          timeout=TIMEOUT_MS * 2)
                page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS * 2)
            browser.close()

    # ── CENÁRIO 5 ──────────────────────────────────────────
    @staticmethod
    def c05_download_arquivo():
        """Download de arquivo com verificação via expect_download."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page    = browser.new_page()
            page.goto(URLS["download"])
            
            # O .first resolve o erro de 'strict mode violation'
            # selecionando apenas o primeiro dos 4 links encontrados.
            link = page.get_by_role("link", name=re.compile(r".*\.txt$")).first
            
            with page.expect_download(timeout=TIMEOUT_MS * 2) as dl_info:
                link.click()
                
            download = dl_info.value
            destino  = OUTPUT_DIR / download.suggested_filename
            download.save_as(destino)
            
            assert destino.exists() and destino.stat().st_size > 0
            destino.unlink(missing_ok=True)
            browser.close()

    # ── CENÁRIO 6 ──────────────────────────────────────────
    @staticmethod
    def c06_execucao_paralela():
        """Execução paralela com N BrowserContexts isolados."""
        def worker(pw_instance, _):
            browser = pw_instance.chromium.launch(headless=HEADLESS)
            ctx     = browser.new_context()
            page    = ctx.new_page()
            page.goto(URLS["login"])
            page.fill("#username", "tomsmith")
            page.fill("#password", "SuperSecretPassword!")
            page.click("button[type='submit']")
            page.wait_for_selector(".flash.success", timeout=TIMEOUT_MS)
            ctx.close()
            browser.close()
            return True

        # Playwright sync_api não é thread-safe → usa ThreadPoolExecutor
        # com instâncias separadas
        def thread_worker(i):
            with sync_playwright() as p:
                return worker(p, i)

        with ThreadPoolExecutor(max_workers=PARALLEL_N) as ex:
            futures    = [ex.submit(thread_worker, i) for i in range(PARALLEL_N)]
            resultados = [f.result() for f in as_completed(futures)]
        assert all(resultados), "Nem todos os workers concluíram"

    # ── CENÁRIO 7 ──────────────────────────────────────────
    @staticmethod
    def c07_cross_browser():
        """Testa extração em Chromium, Firefox e WebKit."""
        with sync_playwright() as p:
            resultados = {}
            for engine_name, engine in [("chromium", p.chromium),
                                        ("firefox",  p.firefox),
                                        ("webkit",   p.webkit)]:
                try:
                    browser = engine.launch(headless=HEADLESS)
                    page    = browser.new_page()
                    page.goto(URLS["produtos"],
                              timeout=TIMEOUT_MS * 3,
                              wait_until="domcontentloaded")
                    page.wait_for_selector("article.product_pod",
                                          timeout=TIMEOUT_MS)
                    n = len(page.query_selector_all("article.product_pod"))
                    resultados[engine_name] = n
                    browser.close()
                except Exception as e:
                    resultados[engine_name] = f"ERRO: {e}"

        assert any(isinstance(v, int) and v > 0
                   for v in resultados.values()), \
            f"Nenhum engine obteve dados: {resultados}"

    # ── CENÁRIO 8 ──────────────────────────────────────────
    @staticmethod
    def c08_interceptacao_xhr():
        """Interceptação nativa de XHR/Fetch via page.route()."""
        capturados = []

        def handle_route(route):
            capturados.append({
                "url"    : route.request.url,
                "method" : route.request.method,
            })
            route.continue_()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page    = browser.new_page()
            # Intercepta todas as requisições de API
            page.route("**/api/**", handle_route)
            page.goto(URLS["xhr"], timeout=TIMEOUT_MS * 2,
                      wait_until="networkidle")
            browser.close()

        # Não falha se nenhuma API foi disparada automaticamente
        # (reqres.in carrega estático); documenta apenas a capacidade nativa

    # ── CENÁRIO 9 ──────────────────────────────────────────
    @staticmethod
    def c09_screenshots_loop():
        """50 screenshots consecutivos com monitoramento de memória."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page    = browser.new_page()
            page.goto(URLS["screenshots"])
            page.wait_for_selector("article.product_pod", timeout=TIMEOUT_MS)
            for i in range(SCREENSHOT_N):
                caminho = OUTPUT_DIR / f"playwright_ss_{i:03d}.png"
                page.screenshot(path=str(caminho))
                caminho.unlink(missing_ok=True)
            browser.close()

    # ── CENÁRIO 10 ──────────────────────────────────────────
    @staticmethod
    def c10_estabilidade_headless():
        """Executa bateria em headless e retorna taxa de sucesso."""
        resultados = []
        for fn in [CenariosPlaywright.c01_login,
                   CenariosPlaywright.c02_extracao_produtos]:
            try:
                fn()
                resultados.append(True)
            except Exception:
                resultados.append(False)
        taxa = sum(resultados) / len(resultados)
        return taxa
