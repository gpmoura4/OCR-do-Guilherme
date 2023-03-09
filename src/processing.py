import cv2
import matplotlib.pyplot as plt
import pytesseract
import re
import config
pytesseract.pytesseract.tesseract_cmd = r'c:\Program Files\Tesseract-OCR\Tesseract.exe'

######################################################################################
# Configurações de imagem


def mostrar(image, min=10, max=10):
    plt.imshow(image, cmap='gray')
    plt.show()


def lerImagem(path=config.PATH, file=config.FILE, format=config.FORMAT):
    return cv2.imread(path + file + format)

######################################################################################
# Pré-processamento


def escalaCinza(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def gaussiano(image, gaussian_a=config.GAUSSIAN_A, gaussian_b=config.GAUSSIAN_B):
    if (gaussian_a % 2 == 0) or (gaussian_b % 2 == 0):
        raise Exception("Config arguments must be odd.")
    return cv2.GaussianBlur(image, (gaussian_a, gaussian_b), 0)


def thresholdingGaussiano(image):
    return cv2.adaptiveThreshold(image, 250, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, config.NOISE_REDUCTION_STRENGTH)


def removerRuido(image, blur_strength=config.NOISE_REDUCTION_STRENGTH):
    return cv2.medianBlur(image, blur_strength)


def thresholding(image):
    return cv2.threshold(image, 0, 50, config.THRESHOLDING + cv2.THRESH_OTSU)[1]


def detectarAresta(image, thr1=100, thr2=200):
    return cv2.Canny(image, thr1, thr2)


def pegarDados(image):
    return pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='por')


def pegaBlocoImg(image):
    h = image.shape[0]
    boxes = pytesseract.image_to_boxes(image)
    for b in boxes.splitlines():
        b = b.split(' ')
        image = cv2.rectangle(
            image, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (255, 255, 255), 4)
    return image


def palavraBlocoImg(image, rgb=(0, 0, 0), img=None):
    try:
        if img == None:
            img = image
    except:
        pass
    d = pegarDados(image)
    for i, text in enumerate(d['text']):
        if int(d['conf'][i]) > 60:
            (x, y, w, h) = (d['left'][i], d['top']
                            [i], d['width'][i], d['height'][i])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), rgb, 4)
    return img


def corroerImg(image, iterations=1):
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (config.ERODE_X, config.ERODE_Y))
    return cv2.erode(image, kernel, iterations=iterations)


def dilatarImg(image, iterations=1):
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (config.DILATE_X, config.DILATE_Y))
    return cv2.dilate(image, kernel, iterations=iterations)


def pegarString(image):
    return pytesseract.image_to_string(image=image, lang=config.LANG)


def pegarContorno(image):
    contours, hierarchy = cv2.findContours(
        image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    return contours, hierarchy


def desenharContorno(image, contours):
    return cv2.drawContours(image, contours, -1, (255, 0, 0), 3)

# ----------------------------------------OCR


def ocr(image):
    try:
        return pytesseract.image_to_string(image, lang=config.LANG, config=config.CUSTOM_CONFIG)
    except:
        return pytesseract.image_to_string(image, lang=config.LANG)

# ----------------------------------------POSTPROCESSING


def removerLetraSolo(string: str, keep_e=False, keep_a=False, keep_o=False):
    if keep_e and keep_a and keep_o:
        return re.sub(r"\b(?![eEéÉaAàÀoO]\b)\w\b", "", string)
    elif keep_e and keep_o:
        return re.sub(r"\b(?![eEéÉoO]\b)\w\b", "", string)
    elif keep_a and keep_o:
        return re.sub(r"\b(?![aAàÀoO]\b)\w\b", "", string)
    elif keep_e and keep_a:
        return re.sub(r"\b(?![eEéÉaAàÀ]\b)\w\b", "", string)
    elif keep_e:
        return re.sub(r"\b(?![eEéÉ]\b)\w\b", "", string)
    elif keep_a:
        return re.sub(r"\b(?![aAàÀ]\b)\w\b", "", string)
    elif keep_o:
        return re.sub(r"\b(?![oO]\b)\w\b", "", string)
    else:
        return re.sub(r"\b\w{1}\b\s*", "", string)


def removerQuebra(string: str, add_space=False):
    if add_space:
        return re.sub(r'[\n\x0c]', ' ', string)
    else:
        return re.sub(r'[\n\x0c]', '', string)


def removerCaracEspecial(string: str, keep_dot_comma=False):
    string_aux = string.split('\n')
    final = list()
    for single_string in string_aux:
        if keep_dot_comma:
            final.append(
                re.sub(r"[^a-zA-ZáàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ0-9+,. ]+", "", single_string))
        else:
            final.append(
                re.sub(r"[^a-zA-ZáàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ0-9+ ]+", "", single_string))
    return final


def removerEspaçoDuplo(string: str):
    return re.sub(r"\s+", " ", ''.join(string))
