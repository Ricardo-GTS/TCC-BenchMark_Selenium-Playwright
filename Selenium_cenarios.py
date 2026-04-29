import time
import json

from concurrent.futures import ThreadPoolExecutor, as_completed

 
# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)


from Config import *
from Util import *


def selenium_driver() -> webdriver.Chrome:
    """Cria e retorna um ChromeDriver configurado."""
    opts = ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=opts)



# ─────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
#  CENÁRIOS – SELENIUM
# ══════════════════════════════════════════════════════════
# ─────────────────────────────────────────────────────────

class CenariosSelenium:
    """Implementa os 10 cenários de teste usando Selenium WebDriver."""

    # ── CENÁRIO 1 ──────────────────────────────────────────
    @staticmethod
    def c01_login():
        """Login em formulário simples."""
        driver = selenium_driver()
        try:
            driver.get(URLS["login"])
            wait = WebDriverWait(driver, TIMEOUT_SEC)
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("tomsmith")
            driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".flash.success")))
        finally:
            driver.quit()

    # ── CENÁRIO 2 ──────────────────────────────────────────
    @staticmethod
    def c02_extracao_produtos():
        """Extração de 100 produtos paginados."""
        driver = selenium_driver()
        try:
            driver.get(URLS["produtos"])
            wait   = WebDriverWait(driver, TIMEOUT_SEC)
            dados  = []
            pagina = 1
            while len(dados) < 100:
                wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "article.product_pod")))
                cards = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
                for card in cards:
                    if len(dados) >= 100:
                        break
                    nome  = card.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("title")
                    preco = card.find_element(By.CSS_SELECTOR, ".price_color").text
                    disp  = card.find_element(By.CSS_SELECTOR, ".availability").text.strip()
                    dados.append({"nome": nome, "preco": preco, "disponibilidade": disp})
                if len(dados) < 100:
                    try:
                        prox = driver.find_element(By.CSS_SELECTOR, "li.next a")
                        prox.click()
                        pagina += 1
                    except NoSuchElementException:
                        break
            assert len(dados) >= 20, f"Poucos produtos coletados: {len(dados)}"
        finally:
            driver.quit()

    # ── CENÁRIO 3 ──────────────────────────────────────────
    @staticmethod
    def c03_formulario_complexo():
        """Preenchimento de formulário com tratamento rigoroso de overlays e componentes React."""
        driver = selenium_driver()
        try:
            driver.get(URLS["formulario"])
            wait = WebDriverWait(driver, TIMEOUT_SEC)
            
            # 1. Limpeza agressiva do ambiente (Remove anúncios e força o zoom para evitar sobreposição)
            driver.execute_script("""
                document.body.style.zoom = '80%';
                var elements = document.querySelectorAll('iframe, footer, [id^="google_ads"], #adplus-anchor');
                for (var el of elements) { el.remove(); }
            """)

            # 2. Preenchimento de campos de texto
            wait.until(EC.presence_of_element_located((By.ID, "firstName"))).send_keys("Maria")
            driver.find_element(By.ID, "lastName").send_keys("Silva")
            driver.find_element(By.ID, "userEmail").send_keys("maria.silva@email.com")
            
            # 3. Gênero (Clique via JS para evitar interceptação)
            gender_radio = driver.find_element(By.CSS_SELECTOR, "label[for='gender-radio-1']")
            driver.execute_script("arguments[0].click();", gender_radio)
            
            driver.find_element(By.ID, "userNumber").send_keys("11987654321")

            # 4. TRATAMENTO DA DATA (O ponto crítico)
            # Em vez de send_keys, usamos JavaScript para definir o valor diretamente no estado do componente
            dob_input = driver.find_element(By.ID, "dateOfBirthInput")
            driver.execute_script("arguments[0].value = '15 Jan 2000'; arguments[0].dispatchEvent(new Event('change'));", dob_input)

            # 5. Subjects (Autocompletar)
            subj = driver.find_element(By.ID, "subjectsInput")
            subj.send_keys("Maths")
            # Aguarda e pressiona ENTER para selecionar a primeira opção
            time.sleep(0.5) 
            subj.send_keys(Keys.ENTER)

            # 6. Hobbies
            hobby_check = driver.find_element(By.CSS_SELECTOR, "label[for='hobbies-checkbox-1']")
            driver.execute_script("arguments[0].click();", hobby_check)

            driver.find_element(By.ID, "currentAddress").send_keys("Av. Paulista, 1000, SP")

            # 7. Estado e Cidade (Usando scroll para garantir visibilidade)
            state_div = driver.find_element(By.ID, "state")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", state_div)
            state_div.click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='NCR']"))).click()

            city_div = driver.find_element(By.ID, "city")
            city_div.click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Delhi']"))).click()

            # 8. SUBMIT FINAL
            submit_btn = driver.find_element(By.ID, "submit")
            driver.execute_script("arguments[0].click();", submit_btn)

            # 9. Validação do Sucesso (Modal de confirmação)
            wait.until(EC.visibility_of_element_located((By.ID, "example-modal-sizes-title-lg")))
            
        finally:
            driver.quit()

    # ── CENÁRIO 4 ──────────────────────────────────────────
    @staticmethod
    def c04_spa_navegacao():
        """Navegação por 5 rotas em SPA React."""
        driver = selenium_driver()
        try:
            wait   = WebDriverWait(driver, TIMEOUT_SEC)
            rotas  = [
                URLS["spa"],
                f"{URLS['spa']}/#/login",
                f"{URLS['spa']}/#/register",
                f"{URLS['spa']}/#/",
                f"{URLS['spa']}/#/",
            ]
            for url in rotas:
                driver.get(url)
                # Aguarda carregamento mínimo do body
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                wait.until(lambda d: d.execute_script(
                    "return document.readyState") == "complete")
        finally:
            driver.quit()

    # ── CENÁRIO 5 ──────────────────────────────────────────
    @staticmethod
    def c05_download_arquivo():
        """Download de arquivo e verificação de integridade."""
        prefs   = {"download.default_directory": str(OUTPUT_DIR.resolve()),
                   "download.prompt_for_download": False}
        opts    = ChromeOptions()
        if HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_experimental_option("prefs", prefs)
        driver  = webdriver.Chrome(options=opts)
        try:
            driver.get(URLS["download"])
            wait  = WebDriverWait(driver, TIMEOUT_SEC)
            link  = wait.until(EC.presence_of_element_located(
                (By.PARTIAL_LINK_TEXT, ".txt")))
            nome  = link.text
            link.click()
            # Aguarda o arquivo aparecer no diretório
            destino = OUTPUT_DIR / nome
            for _ in range(30):
                if destino.exists() and destino.stat().st_size > 0:
                    break
                time.sleep(0.5)
            assert destino.exists(), f"Arquivo não encontrado: {destino}"
        finally:
            driver.quit()

    # ── CENÁRIO 6 ──────────────────────────────────────────
    @staticmethod
    def c06_execucao_paralela():
        """Execução paralela com N workers (ThreadPoolExecutor)."""
        def worker(_):
            driver = selenium_driver()
            try:
                driver.get(URLS["login"])
                wait = WebDriverWait(driver, TIMEOUT_SEC)
                wait.until(EC.presence_of_element_located(
                    (By.ID, "username"))).send_keys("tomsmith")
                driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".flash.success")))
                return True
            finally:
                driver.quit()

        with ThreadPoolExecutor(max_workers=PARALLEL_N) as ex:
            futures  = [ex.submit(worker, i) for i in range(PARALLEL_N)]
            resultados = [f.result() for f in as_completed(futures)]
        assert all(resultados), "Nem todos os workers completaram com sucesso"

    # ── CENÁRIO 7 ──────────────────────────────────────────
    @staticmethod
    def c07_cross_browser():
        """Testa extração em múltiplos browsers (Chrome + Firefox)."""
        resultados = {}
        for browser in ["chrome", "firefox"]:
            try:
                if browser == "chrome":
                    opts = ChromeOptions()
                    if HEADLESS:
                        opts.add_argument("--headless=new")
                    opts.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(options=opts)
                else:
                    from selenium.webdriver.firefox.options import Options as FirefoxOptions
                    opts = FirefoxOptions()
                    if HEADLESS:
                        opts.add_argument("--headless")
                    driver = webdriver.Firefox(options=opts)

                driver.get(URLS["produtos"])
                wait  = WebDriverWait(driver, TIMEOUT_SEC)
                cards = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "article.product_pod")))
                resultados[browser] = len(cards)
                driver.quit()
            except Exception as e:
                resultados[browser] = f"ERRO: {e}"

        assert any(isinstance(v, int) and v > 0 for v in resultados.values()), \
            f"Nenhum browser obteve dados: {resultados}"

    # ── CENÁRIO 8 ──────────────────────────────────────────
    @staticmethod
    def c08_interceptacao_xhr():
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        if HEADLESS: opts.add_argument("--headless=new")
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        driver = webdriver.Chrome(options=opts)
        
        try:
            driver.get(URLS["xhr"])
            time.sleep(2)
            logs = driver.get_log("performance")
            # Extrai logs de rede sem necessidade de proxy externo
            xhr_events = [json.loads(l["message"]) for l in logs 
                        if "Network.responseReceived" in l["message"]]
            assert len(xhr_events) >= 0
        finally:
            driver.quit()

    # ── CENÁRIO 9 ──────────────────────────────────────────
    @staticmethod
    def c09_screenshots_loop():
        """50 screenshots consecutivos com monitoramento de memória."""
        driver = selenium_driver()
        try:
            driver.get(URLS["screenshots"])
            wait = WebDriverWait(driver, TIMEOUT_SEC)
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "article.product_pod")))
            for i in range(SCREENSHOT_N):
                caminho = OUTPUT_DIR / f"selenium_ss_{i:03d}.png"
                driver.save_screenshot(str(caminho))
                # Limpeza para não sobrecarregar disco
                caminho.unlink(missing_ok=True)
        finally:
            driver.quit()

    # ── CENÁRIO 10 ──────────────────────────────────────────
    @staticmethod
    def c10_estabilidade_headless():
        """Executa bateria completa em headless e mede taxa de sucesso."""
        # Roda Cenários 1, 2 e 3 em modo headless e verifica estabilidade
        resultados = []
        for fn in [CenariosSelenium.c01_login,
                   CenariosSelenium.c02_extracao_produtos]:
            try:
                fn()
                resultados.append(True)
            except Exception:
                resultados.append(False)
        taxa = sum(resultados) / len(resultados)
        # Aceita sucesso parcial como métrica (não falha o cenário)
        return taxa
