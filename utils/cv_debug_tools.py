import cv2, functools

# —— 全局状态 —— 
mouse_pos = [0, 0]
current_frame = None  # 存储最新一帧，用于回调读取

def on_mouse(ev, x, y, flags, param):
    global mouse_pos, current_frame
    if ev == cv2.EVENT_MOUSEMOVE:
        mouse_pos[0], mouse_pos[1] = x, y
    elif ev == cv2.EVENT_LBUTTONDOWN and current_frame is not None:
        hsv_img = cv2.cvtColor(current_frame, cv2.COLOR_BGR2HSV)
        h, s, v = hsv_img[y, x]
        print(f"[CLICK] Pos=({x},{y}), HSV=({h},{s},{v})")

def init_debug_panel(params, win="Debug Panel"):
    cv2.namedWindow(win)
    for key, cfg in params.items():
        mn, mx = cfg["range"]
        init = int(cfg["init"])
        cv2.createTrackbar(key, win, init, mx, lambda x: None)

def get_debug_params(params, win="Debug Panel"):
    vals = {}
    for key, cfg in params.items():
        raw = cv2.getTrackbarPos(key, win)
        if cfg.get("float", False):
            mn, mx = cfg["range"]
            vals[key] = mn + raw * ((mx - mn) / mx)
        else:
            v = raw
            if key.lower() == "blur" and v % 2 == 0:
                v += 1
            vals[key] = v
    return vals

def cv_debug(params, debug=False):
    def deco(func):
        @functools.wraps(func)
        def wrapper(img):
            if not debug:
                defaults = {k: v["init"] for k, v in params.items()}
                return func(img, **defaults)
            vals = get_debug_params(params)
            return func(img, **vals)
        return wrapper
    return deco

def show_hsv_overlay(img, window="Result"):
    x, y = mouse_pos
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[y, x]
    overlay = img.copy()
    cv2.circle(overlay, (x, y), 3, (0, 255, 255), -1)
    cv2.putText(overlay, f"HSV:{h},{s},{v}",
                (x+10, y+10), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 255), 1, cv2.LINE_AA)
    cv2.imshow(window, overlay)

if __name__ == "__main__":
    params = {
        "blur":   {"range": (1, 25),  "init": 5,   "float": False},
        "thresh": {"range": (0, 255), "init": 127, "float": False},
    }

    @cv_debug(params, debug=True)
    def process(img, blur, thresh):
        k = int(blur) | 1
        _, out = cv2.threshold(
            cv2.GaussianBlur(img, (k, k), 0),
            int(thresh), 255, cv2.THRESH_BINARY
        )
        return out

    # 初始化窗口与回调
    init_debug_panel(params)
    cv2.namedWindow("Result")
    cv2.setMouseCallback("Result", on_mouse)

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        current_frame = frame  # 更新全局帧

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = process(gray)

        cv2.imshow("Debug Panel", result)
        show_hsv_overlay(frame)

        if (cv2.waitKey(30) & 0xFF) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
