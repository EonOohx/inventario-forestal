from ultralytics import YOLO
class YoloControl:
    def __init__(self):
        self.ncnn_model = YOLO("arboles_secos_ncnn_model")        
        
    def detectar_objetos(self, frame):
        return (self.ncnn_model(frame, conf=0.75))[0].plot()
        