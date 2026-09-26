import cv2
from modo_ia import IAPreditiva
from leituradosdedos import DetectorMao, identificar_gesto, CONEXOES_MAO

# Importa o sistema de câmeras Wi-Fi do seu colega
from fontes_video import (
    inicializar_cameras_interativo,
    ler_frames,
    combinar_lado_a_lado,
    liberar_cameras
)

def desenhar_esqueleto(frame, landmarks, largura, altura):
    """Desenha os pontos e conexões na mão"""
    pontos_px = [(int(p.x * largura), int(p.y * altura)) for p in landmarks]
    for a, b in CONEXOES_MAO:
        cv2.line(frame, pontos_px[a], pontos_px[b], (0, 255, 0), 2)
    for x, y in pontos_px:
        cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)

def processar_frame(frame, detector):
    """Processa a imagem e retorna os gestos lidos da esquerda para a direita"""
    if frame is None or detector is None:
        return frame, []

    altura, largura = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = detector.processar(frame_rgb)

    maos_detectadas = []
    if resultado.hand_landmarks:
        for landmarks in resultado.hand_landmarks:
            desenhar_esqueleto(frame, landmarks, largura, altura)
            gesto = identificar_gesto(landmarks)
            x_real = int(landmarks[0].x * largura)
            maos_detectadas.append((x_real, gesto))
        
        # Ordena as mãos da esquerda para a direita (Menor X = Esquerda)
        maos_detectadas.sort(key=lambda item: item[0])

    # Retorna apenas os nomes dos gestos
    return frame, [g[1] for g in maos_detectadas]


def main():
    print("\n" + "="*40)
    print("   JOKENPO VISION - PET ENG (MULTI-CAM)   ")
    print("="*40)
    print("1. Jogador vs IA Preditiva")
    print("2. Jogador vs Jogador (PvP)")
    escolha = input("Escolha o modo de jogo (1 ou 2): ").strip()

    # 1. Menu de Câmeras do Colega
    # Permite escolher 1 ou 2 câmeras (Webcam ou Celular Wi-Fi)
    caps_conectadas = inicializar_cameras_interativo()
    usando_duas_telas = len(caps_conectadas) > 1

    # 2. Configura a IA
    ia = IAPreditiva() if escolha == '1' else None
    
    # 3. Configura a quantidade de mãos que cada câmera deve ler
    if escolha == '1':
        detector_a = DetectorMao(num_hands=1)
        detector_b = None
    else: # Modo PvP
        if usando_duas_telas:
            detector_a = DetectorMao(num_hands=1) # Cam 1 lê uma mão
            detector_b = DetectorMao(num_hands=1) # Cam 2 lê a outra mão
        else:
            detector_a = DetectorMao(num_hands=2) # 1 Cam lê as duas mãos
            detector_b = None

    print("\n[*] Motores ligados! Pressione ESPAÇO para confirmar a jogada ou 'q' para sair.")
    
    nome_janela = "Jokenpo Vision"
    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nome_janela, 1280, 720)

    jogada_ia = "Aguardando..."
    resultado_texto = "Aperte ESPACO para jogar"

    try:
        while True:
            # Lê os frames usando a função multithread do seu colega
            frames_lidos = ler_frames(caps_conectadas)

            # --- PROCESSA CÂMERA 1 ---
            frame_a = frames_lidos[0]
            gestos_a = []
            if frame_a is not None:
                frame_a = cv2.flip(frame_a, 1)
                frame_a, gestos_a = processar_frame(frame_a, detector_a)

            # --- PROCESSA CÂMERA 2 (Se existir) ---
            frame_b = None
            gestos_b = []
            if usando_duas_telas and frames_lidos[1] is not None:
                frame_b = frames_lidos[1]
                frame_b = cv2.flip(frame_b, 1)
                frame_b, gestos_b = processar_frame(frame_b, detector_b)

            # Verifica se pelo menos uma câmera está funcionando
            if frame_a is None and frame_b is None:
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                continue

            gesto_j1 = "Nenhum"
            gesto_j2 = "Nenhum"

            # --- RENDERIZA INTERFACE IA ---
            if escolha == '1':
                if gestos_a: gesto_j1 = gestos_a[0]
                cv2.putText(frame_a, f"Sua mao: {gesto_j1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame_a, f"IA jogou: {jogada_ia}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame_a, resultado_texto, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # --- RENDERIZA INTERFACE PVP ---
            elif escolha == '2':
                if usando_duas_telas:
                    # Cada pessoa em uma câmera
                    if gestos_a: gesto_j1 = gestos_a[0]
                    if gestos_b: gesto_j2 = gestos_b[0]
                    
                    cv2.putText(frame_a, f"J1: {gesto_j1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    if frame_b is not None:
                        cv2.putText(frame_b, f"J2: {gesto_j2}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(frame_b, resultado_texto, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    # Duas pessoas na mesma câmera
                    if len(gestos_a) >= 2:
                        gesto_j1, gesto_j2 = gestos_a[0], gestos_a[1]
                    elif len(gestos_a) == 1:
                        gesto_j1 = gestos_a[0]

                    cv2.putText(frame_a, f"J1 (Esq): {gesto_j1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    cv2.putText(frame_a, f"J2 (Dir): {gesto_j2}", (350, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(frame_a, resultado_texto, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # Junta as duas imagens caso haja duas câmeras
            tela_final = combinar_lado_a_lado(frame_a, frame_b) if usando_duas_telas else frame_a
            cv2.imshow(nome_janela, tela_final)

            # --- LÓGICA DE VITÓRIA (GATILHO ESPAÇO) ---
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q') or cv2.getWindowProperty(nome_janela, cv2.WND_PROP_VISIBLE) < 1:
                break
                
            elif tecla == ord(' '):
                if escolha == '1': # IA
                    if gesto_j1 in ["Pedra", "Papel", "Tesoura"]:
                        jogada_ia = ia.decidir_jogada()
                        if gesto_j1 == jogada_ia: resultado_texto = "EMPATE!"
                        elif (gesto_j1 == "Pedra" and jogada_ia == "Tesoura") or \
                             (gesto_j1 == "Papel" and jogada_ia == "Pedra") or \
                             (gesto_j1 == "Tesoura" and jogada_ia == "Papel"):
                            resultado_texto = "VOCE VENCEU!"
                        else: resultado_texto = "IA VENCEU!"
                        ia.aprender(gesto_j1)
                    else:
                        resultado_texto = "Faca uma jogada valida!"
                
                elif escolha == '2': # PvP
                    if gesto_j1 in ["Pedra", "Papel", "Tesoura"] and gesto_j2 in ["Pedra", "Papel", "Tesoura"]:
                        if gesto_j1 == gesto_j2: resultado_texto = "EMPATE!"
                        elif (gesto_j1 == "Pedra" and gesto_j2 == "Tesoura") or \
                             (gesto_j1 == "Papel" and gesto_j2 == "Pedra") or \
                             (gesto_j1 == "Tesoura" and gesto_j2 == "Papel"):
                            resultado_texto = "JOGADOR 1 VENCEU!"
                        else: resultado_texto = "JOGADOR 2 VENCEU!"
                    else:
                        resultado_texto = "Ambos precisam colocar a mao!"

    finally:
        # Fecha tudo em segurança
        if ia: ia.salvar_memoria()
        if detector_a: detector_a.fechar()
        if detector_b: detector_b.fechar()
        liberar_cameras(caps_conectadas)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()