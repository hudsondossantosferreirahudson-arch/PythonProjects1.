"""
Testes para o jogo Batalha Naval.
"""

import pytest
from batalha_naval import (
    Navio,
    Tabuleiro,
    IA,
    TAMANHO_TABULEIRO,
    AGUA,
    NAVIO,
    ACERTO,
    ERRO,
    NAVIOS,
    COLUNAS,
)

NUM_ITERACOES_TESTE = 50  # iterações para testes de repetição da IA


# ---------------------------------------------------------------------------
# Navio
# ---------------------------------------------------------------------------

class TestNavio:
    def test_navio_nao_afundado_inicialmente(self):
        n = Navio("Destruidor", 2)
        assert not n.afundado()

    def test_navio_afundado_apos_todos_acertos(self):
        n = Navio("Destruidor", 2)
        n.posicoes = [(0, 0), (0, 1)]
        n.receber_tiro(0, 0)
        assert not n.afundado()
        n.receber_tiro(0, 1)
        assert n.afundado()

    def test_receber_tiro_acerto(self):
        n = Navio("Submarino", 3)
        n.posicoes = [(2, 3), (2, 4), (2, 5)]
        assert n.receber_tiro(2, 3) is True
        assert (2, 3) in n.acertos

    def test_receber_tiro_erro(self):
        n = Navio("Submarino", 3)
        n.posicoes = [(2, 3), (2, 4), (2, 5)]
        assert n.receber_tiro(0, 0) is False
        assert len(n.acertos) == 0


# ---------------------------------------------------------------------------
# Tabuleiro
# ---------------------------------------------------------------------------

class TestTabuleiro:
    def test_grade_inicial_agua(self):
        t = Tabuleiro()
        for linha in t.grade:
            for cel in linha:
                assert cel == AGUA

    def test_posicionar_navio_horizontal(self):
        t = Tabuleiro()
        n = Navio("Destruidor", 2)
        assert t.posicionar_navio(n, 0, 0, horizontal=True)
        assert t.grade[0][0] == NAVIO
        assert t.grade[0][1] == NAVIO
        assert n.posicoes == [(0, 0), (0, 1)]

    def test_posicionar_navio_vertical(self):
        t = Tabuleiro()
        n = Navio("Destruidor", 2)
        assert t.posicionar_navio(n, 3, 5, horizontal=False)
        assert t.grade[3][5] == NAVIO
        assert t.grade[4][5] == NAVIO

    def test_posicionar_navio_fora_do_tabuleiro(self):
        t = Tabuleiro()
        n = Navio("Porta-Aviões", 5)
        # Horizontal começando na coluna 8 (índice), 8+5=13 > 10
        assert not t.posicionar_navio(n, 0, 8, horizontal=True)

    def test_posicionar_navio_sobreposto(self):
        t = Tabuleiro()
        n1 = Navio("Destruidor", 2)
        n2 = Navio("Submarino", 3)
        t.posicionar_navio(n1, 0, 0, horizontal=True)
        # Tenta sobrepor na mesma posição
        assert not t.posicionar_navio(n2, 0, 0, horizontal=True)

    def test_receber_ataque_acerto(self):
        t = Tabuleiro()
        n = Navio("Destruidor", 2)
        t.posicionar_navio(n, 1, 1, horizontal=True)
        acerto, afundado = t.receber_ataque(1, 1)
        assert acerto is True
        assert t.grade[1][1] == ACERTO

    def test_receber_ataque_erro(self):
        t = Tabuleiro()
        acerto, afundado = t.receber_ataque(0, 0)
        assert acerto is False
        assert t.grade[0][0] == ERRO

    def test_receber_ataque_afunda_navio(self):
        t = Tabuleiro()
        n = Navio("Destruidor", 2)
        t.posicionar_navio(n, 0, 0, horizontal=True)
        t.receber_ataque(0, 0)
        _, afundado = t.receber_ataque(0, 1)
        assert afundado is n

    def test_todos_afundados(self):
        t = Tabuleiro()
        n = Navio("Destruidor", 2)
        t.posicionar_navio(n, 0, 0, horizontal=True)
        t.receber_ataque(0, 0)
        assert not t.todos_afundados()
        t.receber_ataque(0, 1)
        assert t.todos_afundados()

    def test_posicionar_aleatorio_coloca_todos_navios(self):
        t = Tabuleiro()
        t.posicionar_aleatorio()
        assert len(t.navios) == len(NAVIOS)

    def test_posicionar_aleatorio_tamanhos_corretos(self):
        t = Tabuleiro()
        t.posicionar_aleatorio()
        nomes_esperados = sorted(nome for nome, _ in NAVIOS)
        nomes_obtidos = sorted(n.nome for n in t.navios)
        assert nomes_obtidos == nomes_esperados

    def test_posicionar_aleatorio_sem_sobreposicao(self):
        t = Tabuleiro()
        t.posicionar_aleatorio()
        todas_posicoes = []
        for n in t.navios:
            todas_posicoes.extend(n.posicoes)
        # Sem duplicatas
        assert len(todas_posicoes) == len(set(todas_posicoes))

    def test_posicionar_aleatorio_dentro_do_tabuleiro(self):
        t = Tabuleiro()
        t.posicionar_aleatorio()
        for n in t.navios:
            for l, c in n.posicoes:
                assert 0 <= l < TAMANHO_TABULEIRO
                assert 0 <= c < TAMANHO_TABULEIRO


# ---------------------------------------------------------------------------
# IA
# ---------------------------------------------------------------------------

class TestIA:
    def test_escolher_ataque_posicao_valida(self):
        ia = IA()
        l, c = ia.escolher_ataque()
        assert 0 <= l < TAMANHO_TABULEIRO
        assert 0 <= c < TAMANHO_TABULEIRO

    def test_escolher_ataque_sem_repeticao(self):
        ia = IA()
        disparos = set()
        for _ in range(NUM_ITERACOES_TESTE):
            l, c = ia.escolher_ataque()
            assert (l, c) not in disparos
            disparos.add((l, c))
            ia.registrar_resultado(l, c, acerto=False, afundou=False)

    def test_ia_investiga_apos_acerto(self):
        ia = IA()
        # Simula um acerto em (5, 5) sem afundar
        ia._disparos.add((5, 5))
        ia.registrar_resultado(5, 5, acerto=True, afundou=False)
        # A IA deve ter adicionado vizinhos como alvos
        assert len(ia._alvo) > 0
        vizinhos_esperados = {(4, 5), (6, 5), (5, 4), (5, 6)}
        alvos_obtidos = set(ia._alvo)
        assert alvos_obtidos.issubset(vizinhos_esperados)

    def test_ia_limpa_alvos_apos_afundar(self):
        ia = IA()
        ia._alvo = [(1, 0), (1, 2)]
        ia._disparos.add((1, 1))
        ia.registrar_resultado(1, 1, acerto=True, afundou=True)
        assert len(ia._alvo) == 0


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

class TestConstantes:
    def test_tamanho_tabuleiro(self):
        assert TAMANHO_TABULEIRO == 10

    def test_numero_navios(self):
        assert len(NAVIOS) == 5

    def test_colunas(self):
        assert len(COLUNAS) == TAMANHO_TABULEIRO
        assert COLUNAS[0] == "A"
        assert COLUNAS[-1] == "J"
