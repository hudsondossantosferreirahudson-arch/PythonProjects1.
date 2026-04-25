"""
Batalha Naval - Um jogo de batalha naval em Python.

Regras:
  - Tabuleiro 10x10
  - Navios: Porta-Aviões (5), Cruzador (4), Contratorpedeiro (3),
            Submarino (3), Destruidor (2)
  - Turno a turno: escolha uma coordenada para atacar
  - Quem afundar todos os navios inimigos primeiro vence
"""

import random
import os

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

TAMANHO_TABULEIRO = 10
AGUA = "~"
NAVIO = "N"
ACERTO = "X"
ERRO = "O"

NAVIOS = [
    ("Porta-Aviões", 5),
    ("Cruzador", 4),
    ("Contratorpedeiro", 3),
    ("Submarino", 3),
    ("Destruidor", 2),
]

COLUNAS = "ABCDEFGHIJ"


# ---------------------------------------------------------------------------
# Classe Navio
# ---------------------------------------------------------------------------

class Navio:
    def __init__(self, nome: str, tamanho: int):
        self.nome = nome
        self.tamanho = tamanho
        self.posicoes: list[tuple[int, int]] = []
        self.acertos: set[tuple[int, int]] = set()

    def afundado(self) -> bool:
        return len(self.acertos) == self.tamanho

    def receber_tiro(self, linha: int, coluna: int) -> bool:
        if (linha, coluna) in self.posicoes:
            self.acertos.add((linha, coluna))
            return True
        return False


# ---------------------------------------------------------------------------
# Classe Tabuleiro
# ---------------------------------------------------------------------------

class Tabuleiro:
    def __init__(self):
        self.grade = [[AGUA] * TAMANHO_TABULEIRO for _ in range(TAMANHO_TABULEIRO)]
        self.navios: list[Navio] = []

    # ------------------------------------------------------------------
    # Posicionamento de navios
    # ------------------------------------------------------------------

    def posicionar_navio(self, navio: Navio, linha: int, coluna: int,
                         horizontal: bool) -> bool:
        """Tenta posicionar um navio no tabuleiro. Retorna True se bem-sucedido."""
        posicoes = self._calcular_posicoes(navio.tamanho, linha, coluna, horizontal)
        if posicoes is None:
            return False
        navio.posicoes = posicoes
        for l, c in posicoes:
            self.grade[l][c] = NAVIO
        self.navios.append(navio)
        return True

    def _calcular_posicoes(self, tamanho: int, linha: int, coluna: int,
                           horizontal: bool) -> list[tuple[int, int]] | None:
        posicoes = []
        for i in range(tamanho):
            l = linha + (0 if horizontal else i)
            c = coluna + (i if horizontal else 0)
            if l >= TAMANHO_TABULEIRO or c >= TAMANHO_TABULEIRO:
                return None
            if self.grade[l][c] != AGUA:
                return None
            posicoes.append((l, c))
        return posicoes

    def posicionar_aleatorio(self):
        """Posiciona todos os navios aleatoriamente."""
        for nome, tamanho in NAVIOS:
            navio = Navio(nome, tamanho)
            colocado = False
            while not colocado:
                horizontal = random.choice([True, False])
                if horizontal:
                    linha = random.randint(0, TAMANHO_TABULEIRO - 1)
                    coluna = random.randint(0, TAMANHO_TABULEIRO - tamanho)
                else:
                    linha = random.randint(0, TAMANHO_TABULEIRO - tamanho)
                    coluna = random.randint(0, TAMANHO_TABULEIRO - 1)
                colocado = self.posicionar_navio(navio, linha, coluna, horizontal)

    # ------------------------------------------------------------------
    # Ataque
    # ------------------------------------------------------------------

    def receber_ataque(self, linha: int, coluna: int) -> tuple[bool, Navio | None]:
        """
        Processa um ataque na posição (linha, coluna).
        Retorna (acerto, navio_afundado_ou_None).
        """
        for navio in self.navios:
            if (linha, coluna) in navio.posicoes:
                navio.receber_tiro(linha, coluna)
                self.grade[linha][coluna] = ACERTO
                if navio.afundado():
                    return True, navio
                return True, None
        self.grade[linha][coluna] = ERRO
        return False, None

    def todos_afundados(self) -> bool:
        return all(n.afundado() for n in self.navios)

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------

    def exibir(self, ocultar_navios: bool = False):
        """Imprime o tabuleiro."""
        print("   " + "  ".join(COLUNAS))
        for i, linha in enumerate(self.grade):
            celulas = []
            for celula in linha:
                if ocultar_navios and celula == NAVIO:
                    celulas.append(AGUA)
                else:
                    celulas.append(celula)
            print(f"{i + 1:2} " + "  ".join(celulas))


# ---------------------------------------------------------------------------
# Classe IA
# ---------------------------------------------------------------------------

class IA:
    def __init__(self):
        self._disparos: set[tuple[int, int]] = set()
        self._alvo: list[tuple[int, int]] = []  # posições para investigar após acerto

    def escolher_ataque(self) -> tuple[int, int]:
        if self._alvo:
            pos = self._alvo.pop(0)
            if pos in self._disparos:
                return self.escolher_ataque()
            return pos
        while True:
            l = random.randint(0, TAMANHO_TABULEIRO - 1)
            c = random.randint(0, TAMANHO_TABULEIRO - 1)
            if (l, c) not in self._disparos:
                return l, c

    def registrar_resultado(self, linha: int, coluna: int, acerto: bool,
                            afundou: bool):
        self._disparos.add((linha, coluna))
        if acerto and not afundou:
            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nl, nc = linha + dl, coluna + dc
                if (0 <= nl < TAMANHO_TABULEIRO and 0 <= nc < TAMANHO_TABULEIRO
                        and (nl, nc) not in self._disparos):
                    self._alvo.append((nl, nc))
        elif afundou:
            self._alvo.clear()


# ---------------------------------------------------------------------------
# Funções auxiliares de entrada
# ---------------------------------------------------------------------------

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def ler_coordenada(prompt: str = "Coordenada (ex: A5): ") -> tuple[int, int]:
    """Lê e valida uma coordenada do usuário (ex: A5 → coluna 0, linha 4)."""
    while True:
        entrada = input(prompt).strip().upper()
        if len(entrada) < 2:
            print("  Entrada inválida. Use formato como A5 ou B10.")
            continue
        letra = entrada[0]
        if letra not in COLUNAS:
            print(f"  Coluna inválida. Use uma letra de A a {COLUNAS[-1]}.")
            continue
        try:
            numero = int(entrada[1:])
        except ValueError:
            print("  Número inválido. Use um número de 1 a 10.")
            continue
        if not (1 <= numero <= TAMANHO_TABULEIRO):
            print(f"  Linha inválida. Use um número de 1 a {TAMANHO_TABULEIRO}.")
            continue
        coluna = COLUNAS.index(letra)
        linha = numero - 1
        return linha, coluna


def ler_orientacao() -> bool:
    """Lê a orientação do navio. Retorna True para horizontal."""
    while True:
        resp = input("  Orientação ([H]orizontal / [V]ertical): ").strip().upper()
        if resp in ("H", "HORIZONTAL"):
            return True
        if resp in ("V", "VERTICAL"):
            return False
        print("  Digite H para horizontal ou V para vertical.")


def posicionar_navios_manualmente(tabuleiro: Tabuleiro):
    """Permite ao jogador posicionar seus navios manualmente."""
    for nome, tamanho in NAVIOS:
        while True:
            limpar_tela()
            print("=== Posicionamento de Navios ===")
            print("Seu tabuleiro atual:")
            tabuleiro.exibir()
            print(f"\nPosicione o {nome} (tamanho {tamanho})")
            print("  Informe a posição da proa (início do navio).")
            linha, coluna = ler_coordenada("  Posição inicial: ")
            horizontal = ler_orientacao()
            navio = Navio(nome, tamanho)
            if tabuleiro.posicionar_navio(navio, linha, coluna, horizontal):
                print(f"  {nome} posicionado com sucesso!")
                break
            else:
                print("  Posição inválida (fora do tabuleiro ou sobrepõe outro navio). Tente novamente.")


# ---------------------------------------------------------------------------
# Classe Jogo
# ---------------------------------------------------------------------------

class Jogo:
    def __init__(self, nome_jogador: str = "Jogador"):
        self.nome_jogador = nome_jogador
        self.tabuleiro_jogador = Tabuleiro()
        self.tabuleiro_ia = Tabuleiro()
        self.ia = IA()
        self.rastreamento_jogador = Tabuleiro()  # usado só para exibir acertos/erros do jogador
        self._disparos_jogador: set[tuple[int, int]] = set()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def configurar(self, posicionar_manual: bool):
        if posicionar_manual:
            posicionar_navios_manualmente(self.tabuleiro_jogador)
        else:
            self.tabuleiro_jogador.posicionar_aleatorio()
            print(f"  Navios de {self.nome_jogador} posicionados aleatoriamente.")

        self.tabuleiro_ia.posicionar_aleatorio()

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def jogar(self):
        turno = 0
        while True:
            turno += 1
            limpar_tela()
            self._exibir_estado()

            # --- Turno do jogador ---
            print(f"\n=== Turno {turno} — {self.nome_jogador} ===")
            linha, coluna = self._turno_jogador()
            acerto, afundado = self.tabuleiro_ia.receber_ataque(linha, coluna)
            self._atualizar_rastreamento(linha, coluna, acerto)

            if acerto:
                if afundado:
                    print(f"  💥 Você afundou o {afundado.nome} inimigo!")
                else:
                    print("  🎯 Acerto!")
            else:
                print("  💧 Água!")

            if self.tabuleiro_ia.todos_afundados():
                limpar_tela()
                self._exibir_estado()
                print(f"\n🏆 Parabéns, {self.nome_jogador}! Você venceu!")
                break

            input("\n  Pressione Enter para o turno da IA...")

            # --- Turno da IA ---
            limpar_tela()
            self._exibir_estado()
            print("\n=== Turno da IA ===")
            self._turno_ia()

            if self.tabuleiro_jogador.todos_afundados():
                limpar_tela()
                self._exibir_estado()
                print("\n💀 A IA venceu! Todos os seus navios foram afundados.")
                break

            input("\n  Pressione Enter para continuar...")

    # ------------------------------------------------------------------
    # Turno do jogador
    # ------------------------------------------------------------------

    def _turno_jogador(self) -> tuple[int, int]:
        while True:
            linha, coluna = ler_coordenada("  Escolha onde atacar (ex: B3): ")
            if (linha, coluna) in self._disparos_jogador:
                print("  Você já atirou nessa posição. Escolha outra.")
            else:
                self._disparos_jogador.add((linha, coluna))
                return linha, coluna

    def _atualizar_rastreamento(self, linha: int, coluna: int, acerto: bool):
        self.rastreamento_jogador.grade[linha][coluna] = ACERTO if acerto else ERRO

    # ------------------------------------------------------------------
    # Turno da IA
    # ------------------------------------------------------------------

    def _turno_ia(self):
        linha, coluna = self.ia.escolher_ataque()
        acerto, afundado = self.tabuleiro_jogador.receber_ataque(linha, coluna)
        coord = f"{COLUNAS[coluna]}{linha + 1}"
        self.ia.registrar_resultado(linha, coluna, acerto, afundado is not None)

        if acerto:
            if afundado:
                print(f"  💥 A IA afundou seu {afundado.nome} em {coord}!")
            else:
                print(f"  🎯 A IA acertou em {coord}!")
        else:
            print(f"  💧 A IA errou em {coord}.")

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------

    def _exibir_estado(self):
        print("=" * 50)
        print(f"  SEU TABULEIRO ({self.nome_jogador})")
        print("=" * 50)
        self.tabuleiro_jogador.exibir(ocultar_navios=False)
        print()
        print("=" * 50)
        print("  SEU MAPA DE ATAQUES")
        print("=" * 50)
        self.rastreamento_jogador.exibir(ocultar_navios=False)


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------

def menu_principal():
    limpar_tela()
    print("╔══════════════════════════════════════╗")
    print("║       BATALHA NAVAL  ⚓               ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("  1. Novo Jogo (Jogador vs Computador)")
    print("  2. Sair")
    print()
    while True:
        opcao = input("  Escolha uma opção: ").strip()
        if opcao == "1":
            return True
        if opcao == "2":
            return False
        print("  Opção inválida. Digite 1 ou 2.")


def perguntar_nome() -> str:
    nome = input("  Qual é o seu nome? ").strip()
    return nome if nome else "Jogador"


def perguntar_posicionamento() -> bool:
    while True:
        resp = input("  Deseja posicionar seus navios manualmente? (S/N): ").strip().upper()
        if resp in ("S", "SIM"):
            return True
        if resp in ("N", "NÃO"):
            return False
        print("  Digite S para sim ou N para não.")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main():
    while True:
        jogar = menu_principal()
        if not jogar:
            print("\n  Até a próxima! ⚓\n")
            break

        nome = perguntar_nome()
        manual = perguntar_posicionamento()

        jogo = Jogo(nome_jogador=nome)
        jogo.configurar(posicionar_manual=manual)

        jogo.jogar()

        print()
        jogar_novamente = input("  Jogar novamente? (S/N): ").strip().upper()
        if jogar_novamente not in ("S", "SIM"):
            print("\n  Até a próxima! ⚓\n")
            break


if __name__ == "__main__":
    main()
