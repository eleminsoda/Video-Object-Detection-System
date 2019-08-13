import cv2
import numpy as np

NAMES_DIR = "../darknet/coco.names"
WEIGHTS_DIR = "../darknet/yolov3.weights"
CONFIG_DIR = "../darknet/yolov3.cfg"

VIDEO_DIR = "../darknet/data/"
RELEASE_DIR = "./static/"

# Load Yolo
def detect_object(filename):
    net = cv2.dnn.readNet(WEIGHTS_DIR, CONFIG_DIR)
    classes = []
    print('start loading video ... ')

    fps = 16     
    videowriter = None

    try:
        with open(NAMES_DIR, "r") as f:
            classes = [line.strip() for line in f.readlines()]
    except Exception as e:
        print(e)
    
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # Loading image
    print('loading image ...')
    file_dir = VIDEO_DIR + filename
    video = cv2.VideoCapture(file_dir)
    index = 1
    object_count = 0
    result = []
    flag_set_videowriter = 0

    ret, img = video.read()
    while (video.isOpened() and ret):
        # img = cv2.imread("room_ser.jpg")
        img = cv2.resize(img, None, fx=0.4, fy=0.4)
        height, width, channels = img.shape

        if flag_set_videowriter == 0:
            size = (width,height)
            try:
                videowriter = cv2.VideoWriter(RELEASE_DIR+"result.mp4",cv2.VideoWriter_fourcc('H','2','6','4'),fps,size)
            except Exception as e:
                print(e)
                print("failed to initiate videowriter")
            
            flag_set_videowriter = 1


        # Detecting objects
        blob = cv2.dnn.blobFromImage(img,
                                    0.00392, (416, 416), (0, 0, 0),
                                    True,
                                    crop=False)

        net.setInput(blob)
        outs = net.forward(output_layers)

        # Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    object_count += 1

                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

                    result.append([object_count, index, classes[class_id], x, y ,w, h])
                    

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        # print(indexes)
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[i]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y + 30), font, 1, color, 2)

        videowriter.write(img)

        index += 1
        ret, img = video.read()

    print('detect completed, returning ...')
    videowriter.release()
    return result
# cv2.imshow("Image", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# if __name__ == "__main__":
#     detect_object()