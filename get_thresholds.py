import cv2
import pandas as pd
import os


def get_threshold(image_path):
    def dummy(x):
        pass

    img_path = image_path

    original_rgb = cv2.imread(img_path)
    original_rgb = cv2.resize(original_rgb, (512, 512))
    for x in range(original_rgb.shape[1]):
        for y in range(original_rgb.shape[0]):
            original_rgb[y, x] = [0, original_rgb[y, x][2],
                                  0]  # todo: this assumes reading in a read image and makes green

    cv2.namedWindow('SC Section')
    cv2.createTrackbar('Threshold', 'SC Section', 50, 255, dummy)  # 50 is the initialization value for the bar

    end = False
    pressed_left = False
    pressed_right = False
    left = None
    right = None

    while not end:
        rgb = original_rgb.copy()
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

        slider_val = cv2.getTrackbarPos("Threshold", "SC Section")
        ret, thresh = cv2.threshold(rgb, slider_val, 255, cv2.THRESH_BINARY)

        for x in range(rgb.shape[0]):
            for y in range(rgb.shape[1]):
                if thresh[y, x][1] == 255:
                    rgb[y, x] = [0, 0, 255]  # todo: this assumes reading in a read image and makes green

        cv2.imshow('SC Section', rgb)

        # Create Key Bindings to Switch from Left and Right SC
        if k == 113:  # Left SC, key 'q'
            print(f'Left: {slider_val}')
            pressed_left = True
            left = slider_val
        if k == 119:  # Right SC, key 'w'
            print(f'Right {slider_val}')
            pressed_right = True
            right = slider_val
        if pressed_left and pressed_right:
            end = True

    cv2.destroyAllWindows()
    return left, right


thresholds = {}
directory_with_images = 'this_dir'
for root, dirs, files in os.walk(directory_with_images):
    for file in files:
        thresholds[file] = get_threshold(os.path.join(root, file))

filenames = thresholds.keys()
left_thresholds = [i[1][0] for i in thresholds.items()]
right_thresholds = [i[1][1] for i in thresholds.items()]
df = pd.DataFrame(zip(filenames, left_thresholds, right_thresholds), columns=['filename', 'left', 'right'])
df.to_excel('threshold_values.xlsx')
