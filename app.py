import cv2
import numpy as np
import face_recognition
import sqlite3
import pickle

from database import ENGINE

# Conectar ao banco de dados
conn = ENGINE
c = conn.cursor()

# Iniciar a captura de vídeo
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao acessar a câmera")
    exit()

print("Pressione 'q' para sair")

# Defina um limite de distância para a comparação
threshold = 0.6

while True:
    ret, frame = cap.read()
    if not ret:
        print("Não foi possível ler o frame")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(frame_rgb)
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

    for (face_encoding, face_location) in zip(face_encodings, face_locations):
        # Obter todos os rostos do banco de dados
        c.execute("SELECT nome, encoding FROM usuarios")
        usuarios = c.fetchall()

        name = "Desconhecido"
        color = (0, 0, 255)  # Vermelho por padrão

        for usuario in usuarios:
            stored_name = usuario[0]
            stored_encoding = pickle.loads(usuario[1])  # Carregar o encoding do banco de dados
            face_distance = face_recognition.face_distance([stored_encoding], face_encoding)

            if face_distance < threshold:  # Verifique se o rosto corresponde
                name = stored_name
                color = (0, 255, 0)  # Verde se reconhecido
                break

        (top, right, bottom, left) = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

    cv2.imshow("Detecção de Faces em Tempo Real", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()
