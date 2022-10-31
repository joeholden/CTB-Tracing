import cv2
import pandas as pd
import os


def get_threshold(image_path):
    """
    Takes in an 8-bit LUT tif (RGB) and allows user input to determine lower threshold
    Outputs the thresholds for all images in a directory to an Excel sheet
    Read in any LUT you want
    """
    def dummy(x):
        pass

    img_path = image_path

    original_rgb = cv2.imread(img_path)
    original_rgb = cv2.resize(original_rgb, (512, 512))
    # Determine the LUT used
    first_pixel = original_rgb[0, 0]
    filled_channels = [i for i, e in enumerate(first_pixel) if e != 0]  # 0, 1, 2 for b, g, r

    for x in range(original_rgb.shape[1]):
        for y in range(original_rgb.shape[0]):
            original_rgb[y, x] = [0, original_rgb[y, x][filled_channels[0]], 0]

    cv2.namedWindow('SC Section')
    cv2.createTrackbar('Threshold', 'SC Section', 50, 255, dummy)  # 50 is the initialization value for the bar

    end = False
    pressed_left = False
    pressed_right = False
    left_thresh = None
    right_thresh = None

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
                    rgb[y, x] = [0, 0, 255]

        cv2.imshow('SC Section', rgb)

        # Create Key Bindings to Switch from Left and Right SC
        if k == 113:  # Left SC, key 'q'
            print(f'Left: {slider_val}')
            pressed_left = True
            left_thresh = slider_val
        if k == 119:  # Right SC, key 'w'
            print(f'Right {slider_val}')
            pressed_right = True
            right_thresh = slider_val
        if pressed_left and pressed_right:
            end = True

    cv2.destroyAllWindows()
    return left_thresh, right_thresh


thresholds = {}
directory_with_images = '/Users/joemattholden/PycharmProjects/ctb_tracing/this_dir/'
for root, dirs, files in os.walk(directory_with_images):
    for file in files:
        if not file.endswith('.DS_Store'):
            thresholds[file] = get_threshold(os.path.join(root, file))

filenames = thresholds.keys()
left_thresholds = [i[1][0] for i in thresholds.items()]
right_thresholds = [i[1][1] for i in thresholds.items()]
df = pd.DataFrame(zip(filenames, left_thresholds, right_thresholds), columns=['Filename', 'Left BG', 'Right BG'])
df.to_excel('threshold_values.xlsx')
