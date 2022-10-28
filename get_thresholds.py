import cv2


def dummy(x):
    pass


img_path = "red image.tif"

original_rgb = cv2.imread(img_path)
original_rgb = cv2.resize(original_rgb, (512, 512))
for x in range(original_rgb.shape[1]):
    for y in range(original_rgb.shape[0]):
        original_rgb[y, x] = [0, original_rgb[y, x][2], 0]  # todo: this assumes reading in a read image and makes green

cv2.namedWindow('SC Section')
cv2.createTrackbar('Threshold', 'SC Section', 50, 255, dummy)  # 50 is the initialization value for the bar

end = False
pressed_left = False
pressed_right = False

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
    if k == 119:  # Right SC, key 'w'
        print(f'Right {slider_val}')
        pressed_right = True
    if pressed_left and pressed_right:
        end = True

cv2.destroyAllWindows()

# Find what key codes are for your machine
# import cv2
# img = cv2.imread(r'C:\Users\joema\PycharmProjects\ctb_excel sheet\16b.tif') # load a dummy image
# while(1):
#     cv2.imshow('img', img)
#     k = cv2.waitKey(33)
#     if k==27:    # Esc key to stop
#         break
#     elif k==-1:  # normally -1 returned,so don't print it
#         continue
#     else:
#         print(k) # else print its value
