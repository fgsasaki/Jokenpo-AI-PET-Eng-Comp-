"""
JOKENPÔ VISION - Motor de Visão Computacional e IA
Desenvolvedores:João Pedro Queiroz de Abreu, Felipe Gabriel Sampaio Sasaki e Leonardo Alves Moreira
Programa de Educação Tutorial (PET) - Engenharia de Computação, UFC
"""

import cv2
import numpy as np
import sys
import tkinter as tk
from tkinter import simpledialog
from modo_ia import IAPreditiva
from leituradosdedos import DetectorMao, identificar_gesto, CONEXOES_MAO

# evita o lag que aparece com cv2.VideoCapture puro (principalmente em fontes
# de rede, como IP Webcam/DroidCam), pois a leitura roda numa thread
# separada e o loop principal sempre pega o frame mais recente.
from fontes_video import (
    CameraAsync,
    ler_frames,
    combinar_lado_a_lado,
    liberar_cameras,
)

# Tamanho do recorte (ROI) usado nos modos de 1 mão por câmera.
# Processar só essa região (em vez do frame inteiro) no MediaPipe
# reduz bastante o custo por frame -> mais fps, menos lag.
ROI_TAMANHO = 550
ROI_DESLOCAMENTO_Y = 50


# ==========================================
# 1. MOTOR DE MENUS GRÁFICOS (100% VISUAL)
# ==========================================
def menu_grafico(titulo, instrucao, botoes):
    """Renderiza um menu interativo clicável no OpenCV"""
    largura, altura = 800, 600
    nome_janela = "Jokenpo Vision - Setup"
    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nome_janela, largura, altura)

    areas_botoes = []
    y_inicial = 200
    altura_btn = 70
    espaco = 25

    for i, (texto, valor) in enumerate(botoes):
        y1 = y_inicial + i * (altura_btn + espaco)
        y2 = y1 + altura_btn
        areas_botoes.append((150, y1, 650, y2, texto, valor))

    selecao = None

    def clique_mouse(event, x, y, flags, param):
        nonlocal selecao
        if event == cv2.EVENT_LBUTTONDOWN:
            for x1, y1, x2, y2, texto, valor in areas_botoes:
                if x1 <= x <= x2 and y1 <= y <= y2:
                    selecao = valor

    cv2.setMouseCallback(nome_janela, clique_mouse)
    tela = np.zeros((altura, largura, 3), dtype=np.uint8)

    cv2.putText(tela, titulo, (70, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 200, 0), 3)
    cv2.putText(tela, instrucao, (150, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    for x1, y1, x2, y2, texto, valor in areas_botoes:
        cv2.rectangle(tela, (x1, y1), (x2, y2), (30, 30, 30), -1)
        cv2.rectangle(tela, (x1, y1), (x2, y2), (255, 200, 0), 2)
        tam_txt = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        px = x1 + ((x2 - x1) - tam_txt[0]) // 2
        py = y1 + ((y2 - y1) + tam_txt[1]) // 2
        cv2.putText(tela, texto, (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.putText(tela, "Desenvolvido para o PET - Eng. de Computacao (UFC)", (180, 560), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

    while selecao is None:
        cv2.imshow(nome_janela, tela)
        if cv2.waitKey(1) & 0xFF == ord('q'): sys.exit()
        if cv2.getWindowProperty(nome_janela, cv2.WND_PROP_VISIBLE) < 1: sys.exit()

    cv2.destroyWindow(nome_janela)
    return selecao

def pedir_ip_celular(titulo="Conectar Celular"):
    """Abre uma janela nativa do Windows para digitar o IP sem usar o terminal"""
    root = tk.Tk()
    root.withdraw()
    ip = simpledialog.askstring(titulo,
                                "Digite o IP e porta mostrados no aplicativo (IP Webcam/DroidCam)\nExemplo: 192.168.1.5:8080")
    root.destroy()
    return ip

# ==========================================
# 2. FUNÇÕES DO HUD DE COMBATE COM CORES SEMÂNTICAS
# ==========================================
def desenhar_hud(frame, texto_topo, texto_base, cor_destaque=(255, 200, 0), placar_texto=None):
    if frame is None:
        return
    altura, largura = frame.shape[:2]
    altura_topo = 90 if placar_texto else 60
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (largura, altura_topo), (10, 10, 10), -1)
    cv2.rectangle(overlay, (0, altura - 70), (largura, altura), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(frame, texto_topo, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    if placar_texto:
        cv2.putText(frame, placar_texto, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 220), 2)
    tamanho_texto = cv2.getTextSize(texto_base, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    pos_x = (largura - tamanho_texto[0]) // 2
    cv2.putText(frame, texto_base, (pos_x, altura - 25), cv2.FONT_HERSHEY_SIMPLEX, 1, cor_destaque, 2)

def desenhar_esqueleto_hud(frame, landmarks, offset_x, offset_y, roi_w, roi_h, gesto):
    """Muda a cor das linhas do esqueleto com base no gesto identificado.
    offset_x/offset_y e roi_w/roi_h permitem desenhar corretamente tanto
    quando os landmarks vêm do frame inteiro quanto de um recorte (ROI)."""
    gesto_lower = gesto.lower()

    if "pedra" in gesto_lower:
        cor_linha = (255, 128, 0)   # Azul Elétrico
    elif "papel" in gesto_lower:
        cor_linha = (0, 255, 255)   # Amarelo Vivo
    elif "tesoura" in gesto_lower:
        cor_linha = (0, 0, 255)     # Vermelho Fogo
    else:
        cor_linha = (255, 255, 0)   # Ciano Padrão

    pontos_px = [
        (int(p.x * roi_w) + offset_x, int(p.y * roi_h) + offset_y)
        for p in landmarks
    ]
    for a, b in CONEXOES_MAO:
        cv2.line(frame, pontos_px[a], pontos_px[b], cor_linha, 2)

    for x, y in pontos_px:
        cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
        cv2.circle(frame, (x, y), 3, cor_linha, -1)

def calcular_roi(frame):
    # Calcula as coordenadas da área de análise, garantindo um recorte quadrado
    altura, largura = frame.shape[:2]
    tamanho = min(ROI_TAMANHO, altura, largura)

    esquerda = max(largura // 2 - tamanho // 2, 0)

    topo_ideal = altura // 2 - tamanho // 2 + ROI_DESLOCAMENTO_Y
    if topo_ideal + tamanho > altura:
        topo = altura - tamanho
    elif topo_ideal < 0:
        topo = 0
    else:
        topo = topo_ideal

    return esquerda, topo, esquerda + tamanho, topo + tamanho

def processar_frame_roi_hud(frame, detector):
    """Usado nos modos de 1 mão por câmera (IA e PvP com 2 câmeras).
    Recorta uma ROI central do frame e roda o MediaPipe só nela, o que
    reduz muito o custo de processamento por frame."""
    if frame is None or detector is None:
        return frame, "Nenhum"

    altura, largura = frame.shape[:2]
    x1, y1, x2, y2 = calcular_roi(frame)
    largura_roi, altura_roi = x2 - x1, y2 - y1

    recorte = frame[y1:y2, x1:x2]
    if recorte.size == 0:
        return frame, "Nenhum"

    recorte_rgb = cv2.cvtColor(recorte, cv2.COLOR_BGR2RGB)
    resultado = detector.processar(recorte_rgb)

    gesto = "Nenhum"
    if resultado.hand_landmarks:
        landmarks = resultado.hand_landmarks[0]
        gesto = identificar_gesto(landmarks)
        desenhar_esqueleto_hud(frame, landmarks, x1, y1, largura_roi, altura_roi, gesto)

    cor_borda = (255, 128, 0) if "pedra" in gesto.lower() else \
                (0, 255, 255) if "papel" in gesto.lower() else \
                (0, 0, 255) if "tesoura" in gesto.lower() else (255, 255, 0)
    cv2.rectangle(frame, (x1, y1), (x2, y2), cor_borda, 2)
    cv2.putText(frame, "Area de Analise (ROI)", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_borda, 2)

    return frame, gesto

def processar_duas_maos_hud(frame, detector):
    """Usado no modo PvP com 1 câmera só (as 2 mãos dividem a mesma tela).
    Aqui o frame inteiro precisa ser processado, pois as duas mãos podem
    estar em qualquer ponto da imagem."""
    if frame is None or detector is None:
        return frame, []
    altura, largura = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = detector.processar(frame_rgb)
    maos_detectadas = []

    if resultado.hand_landmarks:
        for landmarks in resultado.hand_landmarks:
            gesto = identificar_gesto(landmarks)
            desenhar_esqueleto_hud(frame, landmarks, 0, 0, largura, altura, gesto)
            x_real = int(landmarks[0].x * largura)
            maos_detectadas.append((x_real, gesto))

        maos_detectadas.sort(key=lambda item: item[0])
    return frame, [g[1] for g in maos_detectadas]

def combinar_telas(frame_a, frame_b):
    if frame_a is None: return frame_b
    if frame_b is None: return frame_a
    return combinar_lado_a_lado(frame_a, frame_b)

# ==========================================
# 3. MOTOR PRINCIPAL
# ==========================================
def main():
    botoes_modo = [("[1] IA PREDITIVA", "1"), ("[2] JOGADOR VS JOGADOR", "2")]
    escolha = menu_grafico("JOKENPO VISION - COMBATE", "Selecione o modulo de operacao clicando abaixo:", botoes_modo)

    botoes_cam = [("CAMERA DO PC (WEBCAM)", "webcam"), ("CELULAR VIA WI-FI (REDE LOCAL)", "celular")]
    if escolha == '2':
        botoes_cam.append(("DUAS CAMERAS (PC + CELULAR)", "pc_celular"))
        botoes_cam.append(("DUAS CAMERAS (2 CELULARES)", "dois_celulares"))

    fonte = menu_grafico("FONTE DE VIDEO", "Selecione o hardware de captura:", botoes_cam)

    caps_conectadas = []

    if fonte in ["webcam", "pc_celular"]:
        caps_conectadas.append(CameraAsync(0))

    if fonte in ["celular", "pc_celular"]:
        ip = pedir_ip_celular("IP do Celular")
        if ip:
            if not ip.startswith("http"): ip = f"http://{ip}/video"
            caps_conectadas.append(CameraAsync(ip))

    elif fonte == "dois_celulares":
        ip1 = pedir_ip_celular("IP do Celular 1 (Esquerda)")
        if ip1:
            if not ip1.startswith("http"): ip1 = f"http://{ip1}/video"
            caps_conectadas.append(CameraAsync(ip1))

        ip2 = pedir_ip_celular("IP do Celular 2 (Direita)")
        if ip2:
            if not ip2.startswith("http"): ip2 = f"http://{ip2}/video"
            caps_conectadas.append(CameraAsync(ip2))

    if not caps_conectadas:
        caps_conectadas.append(CameraAsync(0))

    usando_duas_telas = len(caps_conectadas) > 1
    usando_duas_maos_numa_tela = (escolha == '2' and not usando_duas_telas)
    ia = IAPreditiva() if escolha == '1' else None

    if escolha == '1':
        detector_a, detector_b = DetectorMao(num_hands=1), None
    else:
        detector_a = DetectorMao(num_hands=2) if usando_duas_maos_numa_tela else DetectorMao(num_hands=1)
        detector_b = DetectorMao(num_hands=1) if usando_duas_telas else None

    nome_janela = "Jokenpo Vision - Modo de Combate"
    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nome_janela, 1280, 720)

    jogada_ia, resultado_texto, cor_alerta = "AGUARDANDO DADOS...", "SISTEMA PRONTO: APERTE ESPACO PARA JOGAR", (255, 255, 0)

    # Placar da sessao (zera ao reiniciar o programa)
    if escolha == '1':
        placar = {"jogador": 0, "ia": 0, "empate": 0}
    else:
        placar = {"j1": 0, "j2": 0, "empate": 0}

    try:
        while True:
            # Leitura assincrona: sempre pega o frame mais recente de cada
            # camera sem travar o loop esperando a rede/USB responder.
            frames_lidos = ler_frames(caps_conectadas)
            frame_a = frames_lidos[0] if len(frames_lidos) > 0 else None
            frame_b = frames_lidos[1] if len(frames_lidos) > 1 else None

            gestos_a, gestos_b = [], []
            gesto_a_unico, gesto_b_unico = "Nenhum", "Nenhum"

            if frame_a is not None:
                frame_a = cv2.flip(frame_a, 1)
                if usando_duas_maos_numa_tela:
                    frame_a, gestos_a = processar_duas_maos_hud(frame_a, detector_a)
                else:
                    frame_a, gesto_a_unico = processar_frame_roi_hud(frame_a, detector_a)

            if usando_duas_telas and frame_b is not None:
                frame_b = cv2.flip(frame_b, 1)
                frame_b, gesto_b_unico = processar_frame_roi_hud(frame_b, detector_b)

            if frame_a is None and frame_b is None:
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                continue

            gesto_j1, gesto_j2 = "NENHUM", "NENHUM"

            if escolha == '1':
                gesto_j1 = gesto_a_unico.upper()
                placar_texto = f"VOCE: {placar['jogador']}   IA: {placar['ia']}   EMPATES: {placar['empate']}"
                desenhar_hud(frame_a, f"SEU SENSOR: {gesto_j1}   |   IA ESTOCASTICA: {jogada_ia.upper()}", resultado_texto, cor_alerta, placar_texto)

            elif escolha == '2':
                placar_texto = f"JOGADOR 1: {placar['j1']}   JOGADOR 2: {placar['j2']}   EMPATES: {placar['empate']}"
                if usando_duas_telas:
                    gesto_j1 = gesto_a_unico.upper()
                    gesto_j2 = gesto_b_unico.upper()
                    desenhar_hud(frame_a, f"JOGADOR 1: {gesto_j1}", resultado_texto, cor_alerta, placar_texto)
                    if frame_b is not None: desenhar_hud(frame_b, f"JOGADOR 2: {gesto_j2}", resultado_texto, cor_alerta, placar_texto)
                else:
                    if len(gestos_a) >= 2: gesto_j1, gesto_j2 = gestos_a[0].upper(), gestos_a[1].upper()
                    elif len(gestos_a) == 1: gesto_j1 = gestos_a[0].upper()
                    desenhar_hud(frame_a, f"J1 (ESQ): {gesto_j1}   |   J2 (DIR): {gesto_j2}", resultado_texto, cor_alerta, placar_texto)

            tela_final = combinar_telas(frame_a, frame_b) if usando_duas_telas else frame_a
            cv2.imshow(nome_janela, tela_final)

            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q') or cv2.getWindowProperty(nome_janela, cv2.WND_PROP_VISIBLE) < 1: break

            elif tecla == ord(' '):
                if escolha == '1':
                    if gesto_j1.capitalize() in ["Pedra", "Papel", "Tesoura"]:
                        jogada_ia = ia.decidir_jogada()
                        if gesto_j1.capitalize() == jogada_ia:
                            resultado_texto, cor_alerta = f"EMPATE! IA TAMBEM JOGOU {jogada_ia.upper()}", (0, 255, 255)
                            placar["empate"] += 1
                        elif (gesto_j1.capitalize() == "Pedra" and jogada_ia == "Tesoura") or \
                             (gesto_j1.capitalize() == "Papel" and jogada_ia == "Pedra") or \
                             (gesto_j1.capitalize() == "Tesoura" and jogada_ia == "Papel"):
                            resultado_texto, cor_alerta = f"VITORIA HUMANA! IA FALHOU COM {jogada_ia.upper()}", (0, 255, 0)
                            placar["jogador"] += 1
                        else:
                            resultado_texto, cor_alerta = f"DERROTA! IA PREVIU SEUS MOVIMENTOS COM {jogada_ia.upper()}", (0, 0, 255)
                            placar["ia"] += 1
                        ia.aprender(gesto_j1.capitalize())
                    else: resultado_texto, cor_alerta = "FALHA DE LEITURA: COLOQUE A MAO NA AREA DO SENSOR", (0, 165, 255)

                elif escolha == '2':
                    if gesto_j1.capitalize() in ["Pedra", "Papel", "Tesoura"] and gesto_j2.capitalize() in ["Pedra", "Papel", "Tesoura"]:
                        if gesto_j1 == gesto_j2:
                            resultado_texto, cor_alerta = "EMPATE TECNICO ENTRE JOGADORES!", (0, 255, 255)
                            placar["empate"] += 1
                        elif (gesto_j1.capitalize() == "Pedra" and gesto_j2.capitalize() == "Tesoura") or \
                             (gesto_j1.capitalize() == "Papel" and gesto_j2.capitalize() == "Pedra") or \
                             (gesto_j1.capitalize() == "Tesoura" and gesto_j2.capitalize() == "Papel"):
                            resultado_texto, cor_alerta = "VITORIA DO JOGADOR 1", (255, 0, 0)
                            placar["j1"] += 1
                        else:
                            resultado_texto, cor_alerta = "VITORIA DO JOGADOR 2", (0, 0, 255)
                            placar["j2"] += 1
                    else: resultado_texto, cor_alerta = "FALHA: AMBOS OS JOGADORES DEVEM APRESENTAR UM SINAL", (0, 165, 255)

    finally:
        if ia: ia.salvar_memoria()
        if detector_a: detector_a.fechar()
        if detector_b: detector_b.fechar()
        liberar_cameras(caps_conectadas)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()