import os
import math
import mediapipe as mp
import itertools
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core.base_options import BaseOptions

# Conexões para desenhar o esqueleto na tela
CONEXOES_MAO = [(c.start, c.end) for c in vision.HandLandmarksConnections.HAND_CONNECTIONS]

class DetectorMao:
    def __init__(self, num_hands=1):
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_modelo = os.path.join(pasta_atual, 'hand_landmarker.task')

        if not os.path.exists(caminho_modelo):
            raise FileNotFoundError("Baixe o arquivo hand_landmarker.task para a pasta do projeto!")

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=caminho_modelo),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self._landmarker = vision.HandLandmarker.create_from_options(options)
        self._relogio = itertools.count(start=0, step=33)

    def processar(self, frame_rgb):
        imagem_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        return self._landmarker.detect_for_video(imagem_mp, next(self._relogio))

    def fechar(self):
        self._landmarker.close()

def calcular_distancia(p1, p2):
    """Calcula a distância entre dois pontos usando Pitágoras (ignora rotação da mão)"""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def identificar_gesto(hand_landmarks):
    pulso = hand_landmarks[0] # Ponto 0 é a base da mão (pulso)
    
    tip_ids = [8, 12, 16, 20] # Pontas dos dedos
    pip_ids = [6, 10, 14, 18] # Articulações do meio
    
    dedos_abertos = []
    
    for tip, pip in zip(tip_ids, pip_ids):
        dist_ponta = calcular_distancia(hand_landmarks[tip], pulso)
        dist_meio = calcular_distancia(hand_landmarks[pip], pulso)
        
        # Se a ponta está mais longe do pulso que o meio do dedo, está esticado
        if dist_ponta > dist_meio:
            dedos_abertos.append(1)
        else:
            dedos_abertos.append(0)
            
    total_abertos = sum(dedos_abertos)
    
    if total_abertos == 0: return "Pedra"
    elif total_abertos == 4: return "Papel"
    elif dedos_abertos[0] == 1 and dedos_abertos[1] == 1 and sum(dedos_abertos[2:]) == 0: return "Tesoura"
    
    return "Desconhecido"