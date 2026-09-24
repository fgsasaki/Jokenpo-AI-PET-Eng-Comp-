# reconhecimento.py

def identificar_gesto(hand_landmarks):
    tip_ids = [8, 12, 16, 20]
    dedos_abertos = []

    # O zero no eixo Y é no topo da tela. Se a ponta for menor, o dedo está esticado.
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