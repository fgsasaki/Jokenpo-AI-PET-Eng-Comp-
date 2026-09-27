"""
JOKENPÔ VISION - Motor de Visão Computacional e IA
Desenvolvedor: Leonardo Alves Moreira (Matrícula: 580988)
Programa de Educação Tutorial (PET) - Engenharia de Computação, UFC
"""

import cv2
import numpy as np
import sys
import tkinter as tk
from tkinter import simpledialog
from modo_ia import IAPreditiva
from leituradosdedos import DetectorMao, identificar_gesto, CONEXOES_MAO

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
def desenhar_hud(frame, texto_topo, texto_base, cor_destaque=(255, 200, 0)):
    altura, largura = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (largura, 60), (10, 10, 10), -1)
    cv2.rectangle(overlay, (0, altura - 70), (largura, altura), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.putText(frame, texto_topo, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    tamanho_texto = cv2.getTextSize(texto_base, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    pos_x = (largura - tamanho_texto[0]) // 2
    cv2.putText(frame, texto_base, (pos_x, altura - 25), cv2.FONT_HERSHEY_SIMPLEX, 1, cor_destaque, 2)

def desenhar_esqueleto_hud(frame, landmarks, largura, altura, gesto):
    """Muda a cor das linhas do esqueleto com base no gesto identificado"""
    gesto_lower = gesto.lower()
    
    if "pedra" in gesto_lower:
        cor_linha = (255, 128, 0)   # Azul Elétrico
    elif "papel" in gesto_lower:
        cor_linha = (0, 255, 255)   # Amarelo Vivo
    elif "tesoura" in gesto_lower:
        cor_linha = (0, 0, 255)     # Vermelho Fogo
    else:
        cor_linha = (255, 255, 0)   # Ciano Padrão

    pontos_px = [(int(p.x * largura), int(p.y * altura)) for p in landmarks]
    for a, b in CONEXOES_MAO: 
        cv2.line(frame, pontos_px[a], pontos_px[b], cor_linha, 2)
        
    for x, y in pontos_px:
        cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
        cv2.circle(frame, (x, y), 3, cor_linha, -1)

def processar_frame_hud(frame, detector):
    if frame is None or detector is None: return frame, []
    altura, largura = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = detector.processar(frame_rgb)
    maos_detectadas = []
    
    if resultado.hand_landmarks:
        for landmarks in resultado.hand_landmarks:
            gesto = identificar_gesto(landmarks)
            # Desenha o esqueleto dinamicamente reajustado à cor do gesto
            desenhar_esqueleto_hud(frame, landmarks, largura, altura, gesto)
            
            x_real = int(landmarks[0].x * largura)
            maos_detectadas.append((x_real, gesto))
            
        maos_detectadas.sort(key=lambda item: item[0])
    return frame, [g[1] for g in maos_detectadas]

def combinar_telas(frame_a, frame_b):
    if frame_a is None: return frame_b
    if frame_b is None: return frame_a
    h, w = frame_a.shape[:2]
    frame_b_redimensionado = cv2.resize(frame_b, (w, h))
    return np.hstack((frame_a, frame_b_redimensionado))

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
        caps_conectadas.append(cv2.VideoCapture(0))
        
    if fonte in ["celular", "pc_celular"]:
        ip = pedir_ip_celular("IP do Celular")
        if ip:
            if not ip.startswith("http"): ip = f"http://{ip}/video"
            caps_conectadas.append(cv2.VideoCapture(ip))
            
    elif fonte == "dois_celulares":
        ip1 = pedir_ip_celular("IP do Celular 1 (Esquerda)")
        if ip1:
            if not ip1.startswith("http"): ip1 = f"http://{ip1}/video"
            caps_conectadas.append(cv2.VideoCapture(ip1))
            
        ip2 = pedir_ip_celular("IP do Celular 2 (Direita)")
        if ip2:
            if not ip2.startswith("http"): ip2 = f"http://{ip2}/video"
            caps_conectadas.append(cv2.VideoCapture(ip2))
            
    if not caps_conectadas: 
        caps_conectadas.append(cv2.VideoCapture(0))

    usando_duas_telas = len(caps_conectadas) > 1
    ia = IAPreditiva() if escolha == '1' else None
    
    if escolha == '1':
        detector_a, detector_b = DetectorMao(num_hands=1), None
    else:
        detector_a = DetectorMao(num_hands=1) if usando_duas_telas else DetectorMao(num_hands=2)
        detector_b = DetectorMao(num_hands=1) if usando_duas_telas else None

    nome_janela = "Jokenpo Vision - Modo de Combate"
    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nome_janela, 1280, 720)

    jogada_ia, resultado_texto, cor_alerta = "AGUARDANDO DADOS...", "SISTEMA PRONTO: APERTE ESPACO PARA JOGAR", (255, 255, 0)

    try:
        while True:
            sucesso_a, frame_a = caps_conectadas[0].read() if len(caps_conectadas) > 0 else (False, None)
            sucesso_b, frame_b = caps_conectadas[1].read() if len(caps_conectadas) > 1 else (False, None)

            gestos_a, gestos_b = [], []
            
            if frame_a is not None:
                frame_a = cv2.flip(frame_a, 1)
                frame_a, gestos_a = processar_frame_hud(frame_a, detector_a)

            if usando_duas_telas and frame_b is not None:
                frame_b = cv2.flip(frame_b, 1)
                frame_b, gestos_b = processar_frame_hud(frame_b, detector_b)

            if frame_a is None and frame_b is None:
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                continue

            gesto_j1, gesto_j2 = "NENHUM", "NENHUM"

            if escolha == '1':
                if gestos_a: gesto_j1 = gestos_a[0].upper()
                desenhar_hud(frame_a, f"SEU SENSOR: {gesto_j1}   |   IA ESTOCASTICA: {jogada_ia.upper()}", resultado_texto, cor_alerta)

            elif escolha == '2':
                if usando_duas_telas:
                    if gestos_a: gesto_j1 = gestos_a[0].upper()
                    if gestos_b: gesto_j2 = gestos_b[0].upper()
                    desenhar_hud(frame_a, f"JOGADOR 1: {gesto_j1}", resultado_texto, cor_alerta)
                    if frame_b is not None: desenhar_hud(frame_b, f"JOGADOR 2: {gesto_j2}", resultado_texto, cor_alerta)
                else:
                    if len(gestos_a) >= 2: gesto_j1, gesto_j2 = gestos_a[0].upper(), gestos_a[1].upper()
                    elif len(gestos_a) == 1: gesto_j1 = gestos_a[0].upper()
                    desenhar_hud(frame_a, f"J1 (ESQ): {gesto_j1}   |   J2 (DIR): {gesto_j2}", resultado_texto, cor_alerta)

            tela_final = combinar_telas(frame_a, frame_b) if usando_duas_telas else frame_a
            cv2.imshow(nome_janela, tela_final)

            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q') or cv2.getWindowProperty(nome_janela, cv2.WND_PROP_VISIBLE) < 1: break
                
            elif tecla == ord(' '):
                if escolha == '1':
                    if gesto_j1.capitalize() in ["Pedra", "Papel", "Tesoura"]:
                        jogada_ia = ia.decidir_jogada()
                        if gesto_j1.capitalize() == jogada_ia: 
                            resultado_texto, cor_alerta = f"EMPATE MUTUO! IA TAMBEM JOGOU {jogada_ia.upper()}", (0, 255, 255)
                        elif (gesto_j1.capitalize() == "Pedra" and jogada_ia == "Tesoura") or \
                             (gesto_j1.capitalize() == "Papel" and jogada_ia == "Pedra") or \
                             (gesto_j1.capitalize() == "Tesoura" and jogada_ia == "Papel"):
                            resultado_texto, cor_alerta = f"VITORIA HUMANA! IA FALHOU COM {jogada_ia.upper()}", (0, 255, 0)
                        else: 
                            resultado_texto, cor_alerta = f"DERROTA! IA PREVIU SEUS MOVIMENTOS COM {jogada_ia.upper()}", (0, 0, 255)
                        ia.aprender(gesto_j1.capitalize())
                    else: resultado_texto, cor_alerta = "FALHA DE LEITURA: COLOQUE A MAO NA AREA DO SENSOR", (0, 165, 255)
                
                elif escolha == '2':
                    if gesto_j1.capitalize() in ["Pedra", "Papel", "Tesoura"] and gesto_j2.capitalize() in ["Pedra", "Papel", "Tesoura"]:
                        if gesto_j1 == gesto_j2: resultado_texto, cor_alerta = "EMPATE TACTICO ENTRE JOGADORES!", (0, 255, 255)
                        elif (gesto_j1.capitalize() == "Pedra" and gesto_j2.capitalize() == "Tesoura") or \
                             (gesto_j1.capitalize() == "Papel" and gesto_j2.capitalize() == "Pedra") or \
                             (gesto_j1.capitalize() == "Tesoura" and gesto_j2.capitalize() == "Papel"):
                            resultado_texto, cor_alerta = "VITORIA DO JOGADOR 1", (255, 0, 0)
                        else: resultado_texto, cor_alerta = "VITORIA DO JOGADOR 2", (0, 0, 255)
                    else: resultado_texto, cor_alerta = "FALHA: AMBOS OS JOGADORES DEVEM APRESENTAR UM SINAL", (0, 165, 255)

    finally:
        if ia: ia.salvar_memoria()
        if detector_a: detector_a.fechar()
        if detector_b: detector_b.fechar()
        for cap in caps_conectadas: cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()