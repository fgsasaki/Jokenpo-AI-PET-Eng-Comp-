# modo_ia.py
import cv2
import mediapipe as mp
import random
import json
import os
from reconhecimento import identificar_gesto

def iniciar_jogo_ia():
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    # IA usa apenas 1 mão
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

    ARQUIVO_MEMORIA = "memoria_ia.json"
    padroes_padrao = {
        "Pedra,Pedra": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, "Pedra,Papel": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, "Pedra,Tesoura": {"Pedra": 0, "Papel": 0, "Tesoura": 0},
        "Papel,Pedra": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, "Papel,Papel": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, "Papel,Tesoura": {"Pedra": 0, "Papel": 0, "Tesoura": 0},
        "Tesoura,Pedra": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, "Tesoura,Papel": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, "Tesoura,Tesoura": {"Pedra": 0, "Papel": 0, "Tesoura": 0}
    }

    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, "r") as f:
            padroes = json.load(f)
    else:
        padroes = padroes_padrao

    historico_jogadas = []
    jogada_ia = "..."
    resultado_rodada = "Aperte ESPACO"

    cap = cv2.VideoCapture(0)

    while True:
        sucesso, frame = cap.read()
        if not sucesso: break

        frame = cv2.flip(frame, 1)
        resultado = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        gesto_detectado = "Nenhuma mao"

        if resultado.multi_hand_landmarks:
            for hand_landmarks in resultado.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesto_detectado = identificar_gesto(hand_landmarks)

        cv2.putText(frame, f"Sua mao: {gesto_detectado}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"IA jogou: {jogada_ia}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, resultado_rodada, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.imshow("Jokenpo - IA (Aperte Q para menu)", frame)
        tecla = cv2.waitKey(1) & 0xFF
        
        if tecla == ord('q'):
            with open(ARQUIVO_MEMORIA, "w") as f:
                json.dump(padroes, f, indent=4)
            break
            
        elif tecla == ord(' '):
            if gesto_detectado in ["Pedra", "Papel", "Tesoura"]:
                if len(historico_jogadas) < 2:
                    jogada_ia = random.choice(["Pedra", "Papel", "Tesoura"])
                else:
                    seq = f"{historico_jogadas[-2]},{historico_jogadas[-1]}"
                    opcoes = padroes[seq]
                    prev = max(opcoes, key=opcoes.get)
                    if opcoes[prev] == 0: jogada_ia = random.choice(["Pedra", "Papel", "Tesoura"])
                    elif prev == "Pedra": jogada_ia = "Papel"
                    elif prev == "Papel": jogada_ia = "Tesoura"
                    else: jogada_ia = "Pedra"
                
                if len(historico_jogadas) >= 2:
                    padroes[f"{historico_jogadas[-2]},{historico_jogadas[-1]}"][gesto_detectado] += 1
                    
                historico_jogadas.append(gesto_detectado)
                if len(historico_jogadas) > 2: historico_jogadas.pop(0)
                
                if gesto_detectado == jogada_ia: resultado_rodada = "EMPATE!"
                elif (gesto_detectado == "Pedra" and jogada_ia == "Tesoura") or (gesto_detectado == "Papel" and jogada_ia == "Pedra") or (gesto_detectado == "Tesoura" and jogada_ia == "Papel"):
                    resultado_rodada = "VOCE VENCEU!"
                else: resultado_rodada = "IA VENCEU!"

    cap.release()
    cv2.destroyAllWindows()