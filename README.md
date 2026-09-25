# ✌️ Jokenpô Vision - IA Preditiva (PET Eng Comp)

Este projeto é um jogo de Pedra, Papel e Tesoura (Jokenpô) desenvolvido em Python utilizando Visão Computacional. O sistema rastreia as mãos do usuário pela webcam e utiliza um modelo preditivo (Cadeia de Markov de 2ª Ordem) para prever as jogadas humanas e contra-atacar em tempo real.

Projeto desenvolvido como parte das atividades do **PET Engenharia de Computação**.

---

## 🚀 Funcionalidades

- **Reconhecimento de Gestos:** Utiliza a biblioteca Google MediaPipe para mapear 21 pontos da mão e identificar as poses de Pedra, Papel ou Tesoura instantaneamente.
- **Modo Jogador vs IA (Preditiva):** A máquina aprende o padrão de comportamento do jogador registrando as últimas jogadas e utiliza probabilidades para prever o próximo movimento.
- **Memória Permanente:** O "cérebro" da IA é salvo automaticamente em um arquivo `memoria_ia.json` ao fechar o jogo, permitindo que a máquina fique mais inteligente ao longo do tempo.
- **Modo Jogador vs Jogador (PvP):** Identificação de duas mãos simultâneas na mesma webcam (Em desenvolvimento pela equipe).

---

## ⚙️ Pré-requisitos e Instalação

É altamente recomendado utilizar o **Python 3.11** para evitar conflitos de compatibilidade com os binários do MediaPipe.

**1. Clone o repositório:**
```bash
git clone [https://github.com/SEU-USUARIO/Jokenpo-AI-PET-Eng-Comp-.git](https://github.com/SEU-USUARIO/Jokenpo-AI-PET-Eng-Comp-.git)
cd Jokenpo-AI-PET-Eng-Comp-
