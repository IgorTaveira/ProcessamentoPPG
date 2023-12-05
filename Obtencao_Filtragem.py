import cv2
import numpy as np
from scipy.signal import butter, lfilter, find_peaks
import matplotlib.pyplot as plt

def extract_ppg(video_path):
    # Abre o vídeo
    cap = cv2.VideoCapture(video_path)
    
    # Taxa de amostragem (quadros por segundo)
    taxa_amostragem = round(cap.get(cv2.CAP_PROP_FPS))

    sinal_ppg = []

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        x, y, w, h = 120, 2, 120, 90  # ROI região de interesse (Onde a "pulsação" é clara)
        roi = frame[y:y+h, x:x+w]
        
        # Extrai o canal vermelho
        canal_vermelho = roi[:, :, 2]

        # Calcula a média do canal vermelho
        media_canalV = np.mean(canal_vermelho)
        sinal_ppg.append(media_canalV)
        cv2.imwrite('C:\\Users\\igork\\Desktop\\ppg\\red-channel.png', canal_vermelho)

    cap.release()

    return sinal_ppg, taxa_amostragem

def butter_bandpass_filter(data, lowcut, highcut, taxa_amostragem, order=2):
    nyquist_freq = 0.5 * taxa_amostragem
    low = lowcut / nyquist_freq
    high = highcut / nyquist_freq
    b, a = butter(order, [low, high], btype='band', analog=False)
    y = lfilter(b, a, data)
    return y

def filter_with_stabilization(signal, taxa_amostragem, stabilization_time=1.0, initial_cutoff_period=0):
    # Aplica Butterworth bandpass filter com taxa de estabilização de 1s
    lowcut = 40.0  # Range do filtro em bpm
    highcut = 220.0  #   Range do filtro em bpm
    lowcut_hz = lowcut / 60.0  # Converte para Hz
    highcut_hz = highcut / 60.0  # Converte para Hz

    sinal_filtrado = butter_bandpass_filter(signal, lowcut_hz, highcut_hz, taxa_amostragem)

    # Apply filter stabilization
    stabilization_frames = int(stabilization_time * taxa_amostragem)
    frames_cutoff = int(initial_cutoff_period * taxa_amostragem)

    sinal_filtrado[:frames_cutoff] = signal[:frames_cutoff]

    for i in range(frames_cutoff, len(signal)):
        sinal_filtrado[i] = (sinal_filtrado[i - 1] * stabilization_frames + sinal_filtrado[i]) / (stabilization_frames + 1)

    return sinal_filtrado

# Encontra os picos no sinal PPG
def find_peaks_indices(signal):
    peaks, _ = find_peaks(signal, distance=85)
    return peaks

video = 'C:\\Users\\igork\\Desktop\\ppg\\2.mp4'

sinal_ppg, taxa_amostragem = extract_ppg(video)

plt.figure(figsize=(12, 6))
plt.plot(sinal_ppg, label='PPG Original', color='r')
plt.title('Sinal PPG Original')
plt.xlabel('Frames')
plt.ylabel('Magnitude do Canal Vermelho')
plt.legend()
plt.grid(True)
plt.show()

# Aplicar filtro e estabilização
PPG_Filtrado = filter_with_stabilization(sinal_ppg, taxa_amostragem, stabilization_time=1.0, initial_cutoff_period=0)

plt.figure(figsize=(12, 6))
plt.plot(PPG_Filtrado, label='PPG Filtrado', color='r')
plt.title('Sinal PPG Filtrado')
plt.xlabel('Frames')
plt.ylabel('Magnitude do Canal Vermelho')
plt.legend()
plt.grid(True)
plt.show()

# Encontra os picos no sinal PPG
picos = find_peaks_indices(PPG_Filtrado)

plt.figure(figsize=(12, 6))
plt.plot(PPG_Filtrado, label='Sinal PPG Filtrado')
plt.plot(picos, PPG_Filtrado[picos], "rx", markersize=10, label='Picos')
plt.title('Sinal PPG Filtrado com Picos')
plt.xlabel('Quadros')
plt.ylabel('Intensidade do Canal Vermelho')
plt.legend()
plt.grid(True)
plt.show()

# Encontra a frequência cardíaca (batimentos por minuto) a partir do sinal PPG.
# Calcula os intervalos entre picos (intervalo R-R)
intervalo_rr = np.diff(picos) / taxa_amostragem
# Calcula a frequência cardíaca média
frequencia_cardiaca = 60 / np.mean(intervalo_rr)
print("Frequência Cardíaca: {:.2f} BPM".format(frequencia_cardiaca))
print("Intervalos R-R (em segundos):", intervalo_rr)

plt.figure(figsize=(12, 6))
plt.plot(PPG_Filtrado, label=f'BPM {frequencia_cardiaca:.2f}', color='r')
plt.plot(picos, PPG_Filtrado[picos], "b.", markersize=10, label='Picos')
plt.title('Sinal PPG Medido')
plt.xlabel('Frames')
plt.ylabel('Magnitude do Canal Vermelho')
plt.legend()
plt.grid(True)
plt.show()