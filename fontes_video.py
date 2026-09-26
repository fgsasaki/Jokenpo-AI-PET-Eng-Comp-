import time
import cv2
import numpy as np
import threading
import os
import ssl

# =================================================================
# BYPASS DE SEGURANÇA SSL/HTTPS
# Força o Python e o motor do OpenCV a aceitarem certificados autoassinados
# =================================================================
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Tenta avisar o FFmpeg (motor interno do OpenCV) para não validar o TLS
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "tls_verify;0|verify;0"

#Zera o delay, rodando em 2 plano
class CameraAsync:
    """Lê os frames continuamente em uma thread separada para evitar acúmulo no buffer."""
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        #Tenta forçar o OpenCV a guardar apenas 1 frame na memória
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.ret, self.frame = self.cap.read()
        self.rodando = True
        self.lock = threading.Lock()
        
        if self.cap.isOpened():
            #Não deixa o vídeo travar
            threading.Thread(target=self._atualizar, daemon=True).start()

    def _atualizar(self):
        while self.rodando:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is not None:
                #Retorna uma cópia para não corromper a imagem na memória
                return self.ret, self.frame.copy()
            return self.ret, None

    def release(self):
        self.rodando = False
        self.cap.release()
        
    def isOpened(self):
        return self.cap.isOpened()

#Dados dos celulares
SISTEMAS_CELULAR = {
    "1": {"chave": "android", "nome_app": "IP Webcam", "porta_padrao": "8080"},
    "2": {"chave": "iphone", "nome_app": "DroidCam", "porta_padrao": "4747"},
}

def escolher_sistema_celular(nome_celular="Celular"):
    print(f"\n--- Configurando {nome_celular} ---")
    print(f"Qual o sistema do {nome_celular}?")
    print("  1) Android (app IP Webcam)")
    print("  2) iPhone (app DroidCam)")

    while True:
        escolha = input("> ").strip()
        if escolha in SISTEMAS_CELULAR:
            return SISTEMAS_CELULAR[escolha]
        print("Opção inválida. Digite 1 ou 2.")

def exibir_instrucoes_celular(sistema):
    if sistema["chave"] == "android":
        print("  [Instrução] Abra o IP Webcam, role até o fim, toque em 'Start server' e anote o IP.")
    else:
        print("  [Instrução] Abra o DroidCam, ative a conexão via Wi-Fi e anote o IP.")

def solicitar_ip_porta_celular(sistema):
    ip = input("  Digite o IP mostrado no app (ex: 192.168.1.5): ").strip()
    ip = ip.replace("http://", "").replace("https://", "").rstrip("/")
    
    porta_padrao = sistema["porta_padrao"]
    porta = input(f"  Porta (Enter para usar o padrão {porta_padrao}): ").strip()
    porta = porta or porta_padrao
    
    return f"https://{ip}:{porta}/video"

def conectar_celular(nome="Celular", tentativas=3):
    sistema = escolher_sistema_celular(nome)
    exibir_instrucoes_celular(sistema)
    url = solicitar_ip_porta_celular(sistema)

    for tentativa in range(1, tentativas + 1):
        print(f"[*] Conectando a {url} (Tentativa {tentativa}/{tentativas})...")
        
        # USA A NOSSA NOVA CLASSE RÁPIDA EM VEZ DO cv2.VideoCapture PADRÃO!
        cap = CameraAsync(url)
        time.sleep(1.5)  # Dá tempo do stream Wi-Fi estabilizar
        
        if cap.isOpened():
            ok, _ = cap.read()
            if ok:
                print(f"[+] {nome} conectado com sucesso e sem delay!")
                return cap
        
        cap.release()
        time.sleep(1.0)

    print(f"[-] Erro ao conectar no {nome}. Verifique a rede ou o IP digitado.")
    return None

def inicializar_cameras_interativo():
    print("=======================================")
    print("        MENU DE FONTES DE VÍDEO        ")
    print("=======================================")
    print("Escolha o layout de câmeras:")
    print("  1) 1 Câmera (Webcam do PC)")
    print("  2) 1 Câmera (Celular via Wi-Fi)")
    print("  3) 2 Câmeras (Webcam + Celular)")
    print("  4) 2 Câmeras (Celular 1 + Celular 2)")

    while True:
        op = input("> ").strip()
        if op in ["1", "2", "3", "4"]:
            break
        print("Opção inválida.")

    caps = []
    
    # A webcam também ganha a classe veloz!
    if op == "1":
        caps.append(CameraAsync(0))
    elif op == "2":
        caps.append(conectar_celular("Celular (Único)"))
    elif op == "3":
        caps.append(CameraAsync(0))
        caps.append(conectar_celular("Celular (Auxiliar)"))
    elif op == "4":
        caps.append(conectar_celular("Celular 1 (Esquerda)"))
        caps.append(conectar_celular("Celular 2 (Direita)"))

    if not caps or all(c is None for c in caps):
        raise RuntimeError("Nenhuma câmera conectou com sucesso. Encerrando o motor.")

    return caps

def ler_frames(caps):
    frames = []
    for cap in caps:
        if cap is not None:
            ok, frame = cap.read()
            frames.append(frame if ok else None)
        else:
            frames.append(None)
    return frames

def redimensionar_para_altura(frame, altura):
    h, w = frame.shape[:2]
    nova_largura = int(w * (altura / h))
    return cv2.resize(frame, (nova_largura, altura))

def combinar_lado_a_lado(frame_a, frame_b, altura=480):
    def preparar(frame):
        if frame is None:
            return np.zeros((altura, int(altura * 4 / 3), 3), dtype="uint8")
        return redimensionar_para_altura(frame, altura)

    return cv2.hconcat([preparar(frame_a), preparar(frame_b)])

def liberar_cameras(caps):
    for cap in caps:
        if cap is not None:
            cap.release()