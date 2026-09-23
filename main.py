import cv2
import mediapipe as mp

# ============================================================
# INICIALIZAÇÃO DO MEDIAPIPE (DETECÇÃO DE MÃOS)
# ============================================================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ============================================================
# FUNÇÃO PARA RECONHECER O GESTO
# ============================================================
def identificar_gesto(hand_landmarks):
    tip_ids = [8, 12, 16, 20]
    dedos_abertos = []

    for tip_id in tip_ids:
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            dedos_abertos.append(1)
        else:
            dedos_abertos.append(0)

    if sum(dedos_abertos) == 0:
        return "Pedra"
    elif sum(dedos_abertos) == 4:
        return "Papel"
    elif dedos_abertos[0] == 1 and dedos_abertos[1] == 1 and sum(dedos_abertos[2:]) == 0:
        return "Tesoura"
    
    return "Gesto Desconhecido"

# ============================================================
# LOOP PRINCIPAL DO JOGO
# ============================================================
# INICIALIZA A CÂMERA (0 é a webcam padrão)
cap = cv2.VideoCapture(0)

print("Pressione 'Q' para sair do jogo.")

while True:
    sucesso, frame = cap.read()
    if not sucesso:
        print("[!] Falha ao ler frame da webcam.")
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(frame_rgb)

    gesto_detectado = "Nenhuma mao detectada"

    if resultado.multi_hand_landmarks:
        for hand_landmarks in resultado.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesto_detectado = identificar_gesto(hand_landmarks)

    # Escreve o gesto detectado na tela do vídeo
    cv2.putText(frame, f"Jogada: {gesto_detectado}", (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # MOSTRA A JANELA DE VÍDEO
    cv2.imshow("Jokenpo - Equipe Rosa", frame)

    # Fecha o jogo se apertar a tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a câmera e fecha as janelas ao sair
cap.release()
cv2.destroyAllWindows()