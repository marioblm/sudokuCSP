from SudokuField import SudokuField, FIELD_SIZE
import numpy as np
import cv2

filenames = ["./templates/{}.jpg".format(x) for x in range(1, FIELD_SIZE + 1)]
colors = [x * 255 // (FIELD_SIZE + 1) for x in range(1, FIELD_SIZE + 1)]


def generate_templates(filename):
    """
    Create templates for numbers to be labeled manually
    """
    img = cv2.imread(filename)
    field_px_x = img.shape[0] // FIELD_SIZE
    field_px_y = img.shape[1] // FIELD_SIZE
    for x, y in np.ndindex((FIELD_SIZE, FIELD_SIZE)):
        # Crop image to field
        field = img[x * field_px_x:(x + 1) * field_px_x, y * field_px_y:(y + 1) * field_px_y]
        # Crop out background
        field = field[field_px_x // 4:-field_px_x // 4, field_px_y // 4:-field_px_y // 4]
        cv2.imwrite('./templates/{}-{}.jpg'.format(x, y), field)


def get_field_from_file(filename):
    """
    Get Sudoku board as array from image
    :return: field as 2d array
    """
    sudoku_field = np.array([[SudokuField() for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)])
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    field_px_x = img.shape[0] // FIELD_SIZE
    field_px_y = img.shape[1] // FIELD_SIZE
    blank_image = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

    # template matching for each number
    for color, filename in zip(colors, filenames):
        # color fields based on matching number
        template = cv2.imread(filename, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            # draw rect on blank image
            cv2.rectangle(blank_image, pt, (pt[0] + w, pt[1] + h), color, -1)

    # determine number based on highest color value in field
    for x, y in np.ndindex((FIELD_SIZE, FIELD_SIZE)):
        # get number in field from color
        field = blank_image[x * field_px_x:(x + 1) * field_px_x, y * field_px_y:(y + 1) * field_px_y]
        value = np.max(field)
        if value in colors:
            sudoku_field[x][y] = SudokuField(colors.index(value) + 1)
    return sudoku_field
