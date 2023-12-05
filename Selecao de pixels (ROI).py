import cv2

video_path = 'C:\\Users\\igork\\Desktop\\ppg\\2.mp4'  

cap = cv2.VideoCapture(video_path)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    x, y, w, h = 120, 2, 120, 90  #COORDENADAS ROI

    # Desenhar um retângulo na ROI
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow('Video com ROI', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()