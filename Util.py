import time
from colorama import init, Fore, Style
# ─────────────────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────────────────


def cronometrar(func, *args, **kwargs):
    """Executa func e retorna (resultado, tempo_seg, memoria_mb, erro)."""
    t0 = time.perf_counter()
    erro = None
    resultado = None
    try:
        resultado = func(*args, **kwargs)
    except Exception as e:
        erro = f"{type(e).__name__}: {str(e)[:120]}"
    t1 = time.perf_counter()
    return resultado, round(t1 - t0, 3), erro


def log(msg: str, level: str = "info"):
    cores = {"info": Fore.CYAN, "ok": Fore.GREEN, "err": Fore.RED,
             "warn": Fore.YELLOW, "head": Fore.MAGENTA}
    print(f"{cores.get(level, '')}{msg}{Style.RESET_ALL}")


