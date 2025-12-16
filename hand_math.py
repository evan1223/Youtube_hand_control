import math

def vector_2d_angle(v1, v2):
    v1_x, v1_y = v1
    v2_x, v2_y = v2
    try:
        dot_product = v1_x*v2_x + v1_y*v2_y
        magnitudes = math.sqrt(v1_x**2 + v1_y**2) * math.sqrt(v2_x**2 + v2_y**2)
        angle = math.degrees(math.acos(dot_product / magnitudes))
    except:
        angle = 0
    return angle

def get_angle(a, b, c):
    ang = math.degrees(math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x))
    return abs(ang) if abs(ang) < 180 else 360 - abs(ang)

def get_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# def is_finger_straight(lm, tips, pips, mcps, idx, threshold=100):
#     if idx == 0: # 拇指
#         angle = get_angle(lm[2], lm[3], lm[4])
#         return angle > threshold
#     tip = lm[tips[idx]]
#     pip = lm[pips[idx]]
#     mcp = lm[mcps[idx]]
#     angle = get_angle(mcp, pip, tip)
#     # print(idx, " ", angle)
#     return angle > threshold

def is_finger_straight(lm, tips, pips, mcps, idx, threshold=150):
    if idx == 0: # 拇指
        angle = get_angle(lm[2], lm[3], lm[4])
        return angle > threshold
    tip = lm[tips[idx]]
    pip = lm[pips[idx]]
    mcp = lm[mcps[idx]]
    # print(mcp.y - pip.y, pip.y - tip.y)
    return mcp.y > pip.y and pip.y > tip.y

# --- 新增/修改的核心判斷 ---

def is_palm_facing_up(lm, handedness_label):
    """
    判斷手心是否向上 (Soup bowl / 端盤子)
    特徵：大拇指在小拇指的「外側」
    Right Hand: Thumb(4).x > Pinky(20).x
    Left Hand:  Thumb(4).x < Pinky(20).x
    """
    thumb_x = lm[4].x
    pinky_x = lm[20].x
    
    if handedness_label == "Right":
        return thumb_x > pinky_x
    elif handedness_label == "Left":
        return thumb_x < pinky_x
    return False

def is_palm_facing_down_or_camera(lm, handedness_label):
    """
    判斷手心是否向下 (摸頭) 或 面向鏡頭 (Stop)
    特徵：大拇指在小拇指的「內側」
    Right Hand: Thumb(4).x < Pinky(20).x
    Left Hand:  Thumb(4).x > Pinky(20).x
    """
    thumb_x = lm[4].x
    pinky_x = lm[20].x
    
    if handedness_label == "Right":
        return thumb_x < pinky_x
    elif handedness_label == "Left":
        return thumb_x > pinky_x
    return False

def is_palm_facing_inward(lm, handedness_label):
    """
    判斷手心是否面向內側 (手刀/切換影片)
    特徵：這通常發生在手掌側立時。
    邏輯：大拇指與小拇指的 X 軸非常接近，或符合 Facing Up 的特徵但手指指向側面
    為了簡化，我們主要用「手指水平指向」+「手心側向」來判斷
    這裡沿用 Thumb > Pinky (Right) 的邏輯，但在 Logic 層會加上手指方向判斷
    """
    # 其實 Inward 的特徵跟 Facing Up 很像 (大拇指都在外側)
    # 我們在 gesture_logic 裡用「移動方向」來區分比較準
    return is_palm_facing_up(lm, handedness_label)

def is_fist(lm):
    tips = [4, 8, 12, 16, 20]
    pips = [3, 7, 11, 15, 19]
    mcps = [2, 6, 10, 14, 18]
    bent_count = 0
    for i in range(1, 5): 
        if not is_finger_straight(lm, tips, pips, mcps, i, threshold=100):
            bent_count += 1
    return bent_count == 4