from dataclasses import dataclass, field, asdict
from typing import Optional


# ─────────────────────────────────────────────────────────
# ESTRUTURAS DE DADOS
# ─────────────────────────────────────────────────────────
@dataclass
class MetricaExecucao:
    """Resultado de uma única execução de um cenário."""
    cenario_id  : int
    ferramenta  : str          # "Selenium" ou "Playwright"
    sucesso     : bool
    tempo_seg   : float
    erro        : Optional[str] = None


@dataclass
class ResultadoCenario:
    """Resultado consolidado de N execuções de um cenário."""
    cenario_id      : int
    nome            : str
    ferramenta      : str
    total_execucoes : int
    sucessos        : int
    tempo_medio     : float = 0.0
    tempo_min       : float = 0.0
    tempo_max       : float = 0.0
    taxa_sucesso    : float = 0.0
    recurso_nativo  : str   = "—"
    erros           : list  = field(default_factory=list)

    def calcular(self, metricas: list[MetricaExecucao]):
        tempos  = sorted([m.tempo_seg for m in metricas if m.sucesso])
        # Aparamento: descarta maior e menor se houver ≥ 4 valores
        if len(tempos) >= 4:
            tempos = tempos[1:-1]
        self.tempo_medio   = round(sum(tempos) / len(tempos), 2) if tempos else 0.0
        self.tempo_min     = round(min(tempos), 2) if tempos else 0.0
        self.tempo_max     = round(max(tempos), 2) if tempos else 0.0
        self.taxa_sucesso  = round(self.sucessos / self.total_execucoes * 100, 1)
        self.erros         = [m.erro for m in metricas if m.erro]
        return self

