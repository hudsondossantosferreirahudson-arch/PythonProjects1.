# PythonProjects1.

## Batalha Naval ⚓

Um jogo de batalha naval para jogar no terminal, escrito em Python.

### Como jogar

```bash
python batalha_naval.py
```

### Regras

- Tabuleiro 10×10 (colunas A–J, linhas 1–10)
- Cinco navios por jogador:

| Navio              | Tamanho |
|--------------------|---------|
| Porta-Aviões       | 5       |
| Cruzador           | 4       |
| Contratorpedeiro   | 3       |
| Submarino          | 3       |
| Destruidor         | 2       |

- Jogador vs Computador (IA)
- Posicionamento manual ou aleatório dos navios
- Coordenadas no formato `LetraLinha` (ex.: `B3`, `J10`)
- Quem afundar todos os navios inimigos primeiro vence

### Legenda do tabuleiro

| Símbolo | Significado      |
|---------|-----------------|
| `~`     | Água (vazio)    |
| `N`     | Navio           |
| `X`     | Acerto          |
| `O`     | Erro (água)     |

### Executar os testes

```bash
python -m pytest test_batalha_naval.py -v
```

### Requisitos

- Python 3.12+