# ✊✋✌️ Jokenpô Vision - Motor de Visão Computacional e IA

Projeto desenvolvido para o processo seletivo/apresentação do **Programa de Educação Tutorial (PET) - Engenharia de Computação** da **Universidade Federal do Ceará (UFC)**.

O **Jokenpô Vision** é um sistema interativo de Pedra, Papel e Tesoura que utiliza Visão Computacional em tempo real para detectar os gestos das mãos humanas. O projeto conta com um módulo de Inteligência Artificial preditiva baseada em **Cadeia de Markov Estocástica** e suporte para processamento paralelo (Multithreading) de múltiplas câmeras.

---

## 👨‍💻 Desenvolvedor
* **Nome:** Leonardo Alves Moreira


---

## 🚀 Funcionalidades e Modos de Jogo

* **[1] Modo IA Preditiva (Homem vs Máquina):** A Inteligência Artificial aprende o padrão de jogadas do usuário e utiliza um modelo probabilístico para prever o próximo movimento e lançar o contra-ataque.
* **[2] Modo Jogador vs Jogador (PvP):** Suporte nativo para duas câmeras simultâneas (Webcams USB ou Celulares via Wi-Fi/IP), permitindo que dois jogadores disputem em tempo real.
* **HUD Semântico Dinâmico:** O esqueleto mapeado na mão do jogador muda de cor em tempo real de acordo com o gesto detectado (Pedra = Azul, Papel = Amarelo, Tesoura = Vermelho).
* **Interface 100% OpenCV:** Menus interativos e responsivos desenhados diretamente na matriz de pixels através de primitivas geométricas, eliminando a necessidade de bibliotecas gráficas pesadas (como Tkinter ou PyQt) durante o gameplay.

---

## 🧠 Destaques de Arquitetura e Engenharia

### 1. Separação de Threads (I/O Bound vs CPU Bound)
Para evitar o estrangulamento da CPU devido à latência natural de redes sem fio (celulares via Wi-Fi), o projeto utiliza um módulo dedicado (`fontes_video.py`) baseado em **Multithreading**.
* **Thread Produtora (Rede):** Dedicada exclusivamente a capturar os frames da câmera de forma assíncrona.
* **Thread Consumidora (IA):** O motor de inferência (MediaPipe) consome o frame mais recente alocado na memória RAM.
* **Resultado:** O sistema roda de forma fluida a 30+ FPS, sem o gargalo de I/O de rede.

### 2. Memória e Decisão Estocástica
A IA não toma decisões absolutas, mas sim estocásticas. Ela analisa uma janela deslizante das últimas duas jogadas do humano (ex: `"Pedra,Papel"`) e consulta um dicionário de frequências salvo persistentemente no arquivo `memoria_ia.json`. A decisão de previsão é feita girando uma "roleta ponderada" (`random.choices`), garantindo um comportamento estatisticamente inteligente, porém orgânico e imprevisível.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.x:** Linguagem principal do projeto.
* **OpenCV (`cv2`):** Captura de vídeo, processamento de matrizes e renderização da interface gráfica HUD.
* **MediaPipe (`mediapipe`):** Framework do Google para inferência de Machine Learning e rastreamento de pontos de articulação (Hand Tracking) em tempo real.
* **Numpy:** Manipulação matemática de arrays de imagem.
* **Threading:** Paralelismo para otimização de entrada e saída (I/O) de vídeo.

---

## ⚙️ Pré-requisitos e Instalação

1. Clone o repositório ou baixe os arquivos fonte.
2. Certifique-se de ter o Python 3 instalado no seu sistema.
3. Instale as dependências via terminal:

```bash
pip install opencv-python mediapipe numpy
