import streamlit as st
import datetime
import json
import pandas as pd
from kerykeion import KrInstance
import matplotlib.pyplot as plt
import numpy as np
import os
import io
import swisseph as swe
from geopy.geocoders import ArcGIS
from timezonefinder import TimezoneFinder
import pytz
import requests 
import itertools

st.set_page_config(page_title="專業星盤系統", layout="wide")

# ================= 0. 常數與地理資訊 =================
RELOCATION_COUNTRIES = {
    "東京": {"lat": 35.6895, "lon": 139.6917},
    "大阪": {"lat": 34.6937, "lon": 135.5023},
    "福岡": {"lat": 33.5902, "lon": 130.4017},
    "泰國": {"lat": 13.7563, "lon": 100.5018}, 
    "臺灣": {"lat": 25.0330, "lon": 121.5654}, 
    "韓國": {"lat": 37.5665, "lon": 126.9780}, 
    "中國": {"lat": 39.9042, "lon": 116.4074}, 
    "香港": {"lat": 22.3193, "lon": 114.1694},
    "新加坡": {"lat": 1.3521, "lon": 103.8198}, 
    "馬來西亞": {"lat": 3.1390, "lon": 101.6869}, 
    "越南": {"lat": 21.0285, "lon": 105.8542}, 
    "菲律賓": {"lat": 14.5995, "lon": 120.9842}, 
    "印尼": {"lat": -6.2088, "lon": 106.8456}, 
    "柬埔寨": {"lat": 11.5564, "lon": 104.9282}, 
    "馬爾代夫": {"lat": 4.1755, "lon": 73.5093}, 
    "印度": {"lat": 28.6139, "lon": 77.2090}, 
    "斯里蘭卡": {"lat": 6.9271, "lon": 79.8612}, 
    "尼泊爾": {"lat": 27.7172, "lon": 85.3240}, 
    "不丹": {"lat": 27.4728, "lon": 89.6393}, 
    "老撾": {"lat": 17.9757, "lon": 102.6331}, 
    "文萊": {"lat": 4.9031, "lon": 114.9398}, 
    "蒙古": {"lat": 47.9200, "lon": 106.9200},
    "倫敦": {"lat": 51.5074, "lon": -0.1278},
    "曼徹斯特": {"lat": 53.4808, "lon": -2.2426},
    "愛丁堡": {"lat": 55.9533, "lon": -3.1883},
    "巴黎": {"lat": 48.8566, "lon": 2.3522},
    "馬賽": {"lat": 43.2965, "lon": 5.3698},
    "德國": {"lat": 52.5200, "lon": 13.4050}, 
    "意大利": {"lat": 41.9028, "lon": 12.4964}, 
    "西班牙": {"lat": 40.4168, "lon": -3.7038}, 
    "葡萄牙": {"lat": 38.7223, "lon": -9.1393}, 
    "瑞士": {"lat": 46.9480, "lon": 7.4474}, 
    "荷蘭": {"lat": 52.3676, "lon": 4.9041}, 
    "比利時": {"lat": 50.8503, "lon": 4.3517}, 
    "希臘": {"lat": 37.9838, "lon": 23.7275}, 
    "愛爾蘭": {"lat": 53.3498, "lon": -6.2603}, 
    "奧地利": {"lat": 48.2082, "lon": 16.3738}, 
    "克羅地亞": {"lat": 45.8150, "lon": 15.9819}, 
    "冰島": {"lat": 64.1466, "lon": -21.9426}, 
    "挪威": {"lat": 59.9139, "lon": 10.7522}, 
    "瑞典": {"lat": 59.3293, "lon": 18.0686}, 
    "芬蘭": {"lat": 60.1695, "lon": 24.9354}, 
    "丹麥": {"lat": 55.6761, "lon": 12.5683}, 
    "捷克": {"lat": 50.0755, "lon": 14.4378}, 
    "匈牙利": {"lat": 47.4979, "lon": 19.0402}, 
    "波蘭": {"lat": 52.2297, "lon": 21.0122}, 
    "塞浦路斯": {"lat": 35.1856, "lon": 33.3823}, 
    "馬耳他": {"lat": 35.8989, "lon": 14.5146}, 
    "盧森堡": {"lat": 49.6116, "lon": 6.1319}, 
    "摩納哥": {"lat": 43.7384, "lon": 7.4246}, 
    "安道爾": {"lat": 42.5063, "lon": 1.5218}, 
    "愛沙尼亞": {"lat": 59.4370, "lon": 24.7536}, 
    "拉脫維亞": {"lat": 56.9496, "lon": 24.1052}, 
    "立陶宛": {"lat": 54.6872, "lon": 25.2797}, 
    "斯洛伐克": {"lat": 48.1486, "lon": 17.1077}, 
    "斯洛文尼亞": {"lat": 46.0569, "lon": 14.5058}, 
    "羅馬尼亞": {"lat": 44.4268, "lon": 26.1025}, 
    "保加利亞": {"lat": 42.6977, "lon": 23.3219}, 
    "塞爾維亞": {"lat": 44.7866, "lon": 20.4489}, 
    "黑山": {"lat": 42.4304, "lon": 19.2594}, 
    "阿爾巴尼亞": {"lat": 41.3275, "lon": 19.8187}, 
    "北馬其頓": {"lat": 42.0006, "lon": 21.4333}, 
    "波斯尼亞": {"lat": 43.8563, "lon": 18.4131}, 
    "格魯吉亞": {"lat": 41.7151, "lon": 44.8271}, 
    "亞美尼亞": {"lat": 40.1872, "lon": 44.5152}, 
    "阿塞拜疆": {"lat": 40.4093, "lon": 49.8671}, 
    "土耳其": {"lat": 39.9334, "lon": 32.8597},
    "阿聯酋": {"lat": 24.4539, "lon": 54.3773},
    "卡塔爾": {"lat": 25.2854, "lon": 51.5310}, 
    "沙特阿拉伯": {"lat": 24.7136, "lon": 46.6753}, 
    "巴林": {"lat": 26.2285, "lon": 50.5860}, 
    "阿曼": {"lat": 23.5859, "lon": 58.4059}, 
    "約旦": {"lat": 31.9454, "lon": 35.9284}, 
    "以色列": {"lat": 31.7683, "lon": 35.2137}, 
    "黎巴嫩": {"lat": 33.8938, "lon": 35.5018}, 
    "美國": {"lat": 38.9072, "lon": -77.0369},
    "加拿大": {"lat": 45.4215, "lon": -75.6972},
    "澳洲": {"lat": -35.2809, "lon": 149.1300},
    "紐西蘭": {"lat": -41.2865, "lon": 174.7762},
    "巴西": {"lat": -15.7975, "lon": -47.8919},
    "墨西哥": {"lat": 19.4326, "lon": -99.1332}, 
    "阿根廷": {"lat": -34.6037, "lon": -58.3816}, 
    "秘魯": {"lat": -12.0464, "lon": -77.0428}, 
    "智利": {"lat": -33.4489, "lon": -70.6693}, 
    "哥倫比亞": {"lat": 4.7110, "lon": -74.0721}, 
    "古巴": {"lat": 23.1136, "lon": -82.3666}, 
    "牙買加": {"lat": 18.0179, "lon": -76.8099}, 
    "巴巴多斯": {"lat": 13.1939, "lon": -59.5432}, 
    "聖盧西亞": {"lat": 14.0118, "lon": -60.9887}, 
    "巴哈馬": {"lat": 25.0443, "lon": -77.3504}, 
    "哥斯達黎加": {"lat": 9.9281, "lon": -84.0907}, 
    "玻利維亞": {"lat": -16.4897, "lon": -68.1193}, 
    "斐濟": {"lat": -18.1416, "lon": 178.4419}, 
    "南非": {"lat": -25.7479, "lon": 28.2293},
    "坦桑尼亞": {"lat": -6.1722, "lon": 35.7395},
    "摩洛哥": {"lat": 34.0209, "lon": -6.8416}, 
    "埃及": {"lat": 30.0444, "lon": 31.2357}, 
    "肯尼亞": {"lat": -1.2921, "lon": 36.8219}, 
    "毛里裘斯": {"lat": -20.1609, "lon": 57.5012}, 
    "塞舌爾": {"lat": -4.6191, "lon": 55.4513}, 
    "馬達加斯加": {"lat": -18.8792, "lon": 47.5079}, 
    "突尼斯": {"lat": 36.8065, "lon": 10.1815}, 
    "阿爾及利亞": {"lat": 36.7538, "lon": 3.0588}, 
    "納米比亞": {"lat": -22.5609, "lon": 17.0658}, 
    "博茨瓦納": {"lat": -24.6282, "lon": 25.9231}, 
    "津巴布韋": {"lat": -17.8216, "lon": 31.0492}
}


# ================= 0. Session State 狀態管理 =================
now = datetime.datetime.now()

exclusion_keys = [
    "1宮主陷弱", "月亮與火土凶相", "月亮空亡", "火星或土星入1宮", 
    "6/8/12宮主入1宮", "火土與1宮主凶相", "6/8/12宮主與1宮主凶相", 
    "火星或土星合相上升", "6/8/12宮主合相上升", "土星入角宮", "土星合/沖四角"
]

if 'n_year' not in st.session_state:
    st.session_state.update({
        'n_year': 1990, 'n_month': 1, 'n_day': 1, 'n_hour': 12, 'n_minute': 0, 'n_loc': "Manchester", 'name_input': "Vincent", 'gender_input': "男",
        'p_year': now.year, 'p_month': now.month, 'p_day': now.day, 'p_hour': now.hour, 'p_minute': now.minute, 'p_loc': "Manchester",
        'target_age': now.year - 1990,
        'election_conditions': [],
        'calc_triggered': False,
        'election_results': [],
        'el_loc_input': "Manchester",
        'imported_profiles': []
    })
    for k in exclusion_keys:
        st.session_state[k] = True

def toggle_all_exclusions():
    any_checked = any(st.session_state.get(k, True) for k in exclusion_keys)
    target_state = not any_checked
    for k in exclusion_keys:
        st.session_state[k] = target_state

def sync_n_loc_to_p_loc():
    st.session_state.p_loc = st.session_state.n_loc

def sync_target_age_from_n_year():
    st.session_state.target_age = max(0, st.session_state.p_year - st.session_state.n_year)

def on_profile_change():
    selected = st.session_state.profile_selector
    if selected != "-- 請選擇 --" and 'imported_profiles' in st.session_state:
        for p in st.session_state.imported_profiles:
            if p.get('Name') == selected:
                try:
                    dt = datetime.datetime.strptime(p['born on'], "%Y-%m-%d %H:%M:%S")
                    st.session_state.n_year = dt.year
                    st.session_state.n_month = dt.month
                    st.session_state.n_day = dt.day
                    st.session_state.n_hour = dt.hour
                    st.session_state.n_minute = dt.minute
                    st.session_state.name_input = p['Name']
                    if p.get('Sex') in ["男", "女"]:
                        st.session_state.gender_input = p['Sex']
                    
                    place_str = p.get('Place', 'Hong Kong')
                    city = place_str.split()[-1] if ' ' in place_str else place_str
                    st.session_state.n_loc = city
                    st.session_state.p_loc = city
                    st.session_state.target_age = max(0, st.session_state.p_year - dt.year)
                except Exception:
                    pass
                break

for key in st.session_state.keys():
    if key.startswith("btn_el_sync_") and st.session_state[key]:
        idx = int(key.split("_")[-1])
        if 'election_results' in st.session_state and idx < len(st.session_state['election_results']):
            target_dt = st.session_state['election_results'][idx]
            st.session_state.n_year = target_dt.year
            st.session_state.n_month = target_dt.month
            st.session_state.n_day = target_dt.day
            st.session_state.n_hour = target_dt.hour
            st.session_state.n_minute = target_dt.minute
            
            el_city = st.session_state.get('el_loc_input', 'Manchester')
            if not el_city or not el_city.strip():
                el_city = "Manchester"
            st.session_state.n_loc = el_city.strip()
            st.session_state.p_loc = el_city.strip()
            
            st.session_state.calc_triggered = True 
            st.rerun()

def set_current_time():
    n = datetime.datetime.now()
    st.session_state.n_year, st.session_state.n_month, st.session_state.n_day = n.year, n.month, n.day
    st.session_state.n_hour, st.session_state.n_minute = n.hour, n.minute
    st.session_state.name_input = "卜卦"
    st.session_state.calc_triggered = False

def set_current_loc():
    try:
        res = requests.get('http://ip-api.com/json/', timeout=3).json()
        st.session_state.n_loc = res.get('city', 'Hong Kong')
        st.session_state.p_loc = st.session_state.n_loc
    except:
        st.session_state.n_loc = "Hong Kong"
        st.session_state.p_loc = "Hong Kong"
    st.session_state.calc_triggered = False

def update_year_from_age():
    st.session_state.p_year = max(100, st.session_state.n_year + st.session_state.target_age)

def update_age_from_year():
    st.session_state.target_age = max(0, st.session_state.p_year - st.session_state.n_year)

# ================= 1. 基礎設定與常數 =================
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans'] 
plt.rcParams['axes.unicode_minus'] = False

ZODIAC_SYMBOLS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
ZODIAC_NAMES = ['牡羊', '金牛', '雙子', '巨蟹', '獅子', '處女', '天秤', '天蠍', '射手', '摩羯', '水瓶', '雙魚']
ZR_PERIODS = [15, 8, 20, 25, 19, 20, 8, 15, 12, 27, 30, 12] 

ZODIAC_ELEMENTS = ['火', '土', '風', '水', '火', '土', '風', '水', '火', '土', '風', '水']
ZODIAC_MODES = ['開創', '固定', '變動', '開創', '固定', '變動', '開創', '固定', '變動', '開創', '固定', '變動']

PLANET_SYMBOLS = {
    '太陽': {'sym': '☉', 'color': '#e67e22'}, '月亮': {'sym': '☽', 'color': '#7f8c8d'},
    '水星': {'sym': '☿', 'color': '#27ae60'}, '金星': {'sym': '♀', 'color': '#2ecc71'},
    '火星': {'sym': '♂', 'color': '#e74c3c'}, '木星': {'sym': '♃', 'color': '#d35400'},
    '土星': {'sym': '♄', 'color': '#2c3e50'}, '天王星': {'sym': '♅', 'color': '#8e44ad'},
    '海王星': {'sym': '♆', 'color': '#2980b9'}, '冥王星': {'sym': '♇', 'color': '#34495e'},
    '北交點': {'sym': '☊', 'color': '#000000'},
    '上升': {'sym': 'ASC', 'color': '#c0392b'}, '中天': {'sym': 'MC', 'color': '#2980b9'}
}

ALL_POINTS = ['太陽', '月亮', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星', '北交點', '上升', '中天']
WEIGHT_POINTS = ['太陽', '月亮', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星', '上升', '中天']
TRANSIT_POINTS = ['太陽', '月亮', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星', '北交點']
LOCAL_SPACE_POINTS = ['太陽', '月亮', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星', '北交點', '上升', '中天']

TRADITIONAL_RULERS = {
    '牡羊': '火星', '金牛': '金星', '雙子': '水星', '巨蟹': '月亮',
    '獅子': '太陽', '處女': '水星', '天秤': '金星', '天蠍': '火星',
    '射手': '木星', '摩羯': '土星', '水瓶': '土星', '雙魚': '木星'
}

LILLY_MOITIES = {
    '太陽': 7.5, '月亮': 6.0, '土星': 4.5, '木星': 4.5, '火星': 4.0, '金星': 3.5, '水星': 3.5,
    '天王星': 2.5, '海王星': 2.5, '冥王星': 2.5, '北交點': 2.5, '上升': 0.0, '中天': 0.0
}

DIGNITIES = {
    '太陽': {'廟': [4], '旺': [0], '弱': [10], '陷': [6]},
    '月亮': {'廟': [3], '旺': [1], '弱': [9], '陷': [7]},
    '水星': {'廟': [2, 5], '旺': [5], '弱': [8, 11], '陷': [11]},
    '金星': {'廟': [1, 6], '旺': [11], '弱': [7, 0], '陷': [5]},
    '火星': {'廟': [0, 7], '旺': [9], '弱': [6, 1], '陷': [3]},
    '木星': {'廟': [8, 11], '旺': [3], '弱': [2, 5], '陷': [9]},
    '土星': {'廟': [9, 10], '旺': [6], '弱': [3, 4], '陷': [0]}
}

# ================= 2. 核心占星算法 =================
EPHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe')
swe.set_ephe_path(EPHE_PATH)

def format_degree(lon):
    idx = int(lon // 30) % 12
    deg = int(lon % 30)
    mins = int(round((lon % 1) * 60))
    if mins == 60:
        mins = 0; deg += 1
        if deg == 30: deg = 0; idx = (idx + 1) % 12
    return f"{ZODIAC_NAMES[idx]}({deg:02d}°{mins:02d})"

def get_house_number(lon, cusps, house_system):
    c_list = list(cusps)[1:] if len(cusps) == 13 else list(cusps)
    if house_system == b'W':
        asc_sign = int(c_list[0] // 30) % 12
        p_sign = int(lon // 30) % 12
        return (p_sign - asc_sign) % 12 + 1
    for h in range(12):
        c1 = c_list[h]
        c2 = c_list[(h + 1) % 12]
        if c1 <= c2:
            if c1 <= lon < c2: return h + 1
        else:
            if lon >= c1 or lon < c2: return h + 1
    return 12

def calc_midpoint(p1_lon, p2_lon):
    diff = abs(p1_lon - p2_lon)
    return ((p1_lon + p2_lon + 360) / 2.0 if diff > 180 else (p1_lon + p2_lon) / 2.0) % 360

def calculate_chart_engine(jd, lat, lon, house_system):
    planets_map = {
        '太陽': swe.SUN, '月亮': swe.MOON, '水星': swe.MERCURY, '金星': swe.VENUS, '火星': swe.MARS, 
        '木星': swe.JUPITER, '土星': swe.SATURN, '天王星': swe.URANUS, '海王星': swe.NEPTUNE, 
        '冥王星': swe.PLUTO, '北交點': swe.TRUE_NODE, '婚神星': 3, '莉莉絲': 12
    }
    positions = {}
    positions_lat = {}
    speeds = {}
    for name, planet_id in planets_map.items():
        pos, _ = swe.calc_ut(jd, planet_id)
        positions[name] = pos[0] 
        positions_lat[name] = pos[1] 
        speeds[name] = pos[3] 
    cusps, ascmc = swe.houses(jd, lat, lon, house_system)
    positions['上升'] = ascmc[0]
    positions['中天'] = ascmc[1]
    positions_lat['上升'] = 0.0 
    positions_lat['中天'] = 0.0 
    return positions, positions_lat, ascmc[0], cusps, ascmc[1], speeds

def get_aspect_modifier_engine(p1, p2, target_angle, current_diff, jd, lat, lon, house_sys):
    positions_future, _, _, _, _, _ = calculate_chart_engine(jd + 0.005, lat, lon, house_sys)
    if p1 in positions_future and p2 in positions_future:
        f_diff = abs(positions_future[p1] - positions_future[p2])
        if f_diff > 180: f_diff = 360 - f_diff
        return "+" if abs(f_diff - target_angle) < abs(current_diff - target_angle) else "-"
    return ""

def find_astrology_patterns(positions):
    patterns = {"大三角": [], "大十字": [], "T三角": [], "風箏": [], "上帝之指": []}
    pts = [p for p in ALL_POINTS if p in positions]
    
    def is_asp(p1, p2, target, orb=6.0):
        d = abs(positions[p1] - positions[p2])
        if d > 180: d = 360 - d
        return abs(d - target) <= orb
    for triple in itertools.combinations(pts, 3):
        signs = [int(positions[p] // 30) % 12 for p in triple]
        if len(set(signs)) < 3: continue
        p1, p2, p3 = triple
        if is_asp(p1, p2, 120) and is_asp(p2, p3, 120) and is_asp(p1, p3, 120):
            el1, el2, el3 = ZODIAC_ELEMENTS[signs[0]], ZODIAC_ELEMENTS[signs[1]], ZODIAC_ELEMENTS[signs[2]]
            if el1 == el2 == el3: patterns["大三角"].append(f"{el1}元素大三角：{p1} - {p2} - {p3}")
        for a, b, c in itertools.permutations(triple):
            if is_asp(a, b, 180) and is_asp(c, a, 90) and is_asp(c, b, 90):
                txt = f"{p1} - {p2} - {p3} (頂點: {c})"
                if txt not in patterns["T三角"]: patterns["T三角"].append(txt)
        for a, b, c in itertools.permutations(triple):
            if is_asp(a, b, 60) and is_asp(c, a, 150, orb=3.0) and is_asp(c, b, 150, orb=3.0):
                txt = f"{a} - {b} - {c} (頂點: {c})"
                if txt not in patterns["上帝之指"]: patterns["上帝之指"].append(txt)
    for quad in itertools.combinations(pts, 4):
        signs = [int(positions[p] // 30) % 12 for p in quad]
        if len(set(signs)) < 4: continue
        p1, p2, p3, p4 = quad
        for a, b, c, d in itertools.permutations(quad):
            if is_asp(a, b, 180) and is_asp(c, d, 180):
                if is_asp(a, c, 90) and is_asp(a, d, 90) and is_asp(b, c, 90) and is_asp(b, d, 90):
                    m1, m2, m3, m4 = ZODIAC_MODES[signs[0]], ZODIAC_MODES[signs[1]], ZODIAC_MODES[signs[2]], ZODIAC_MODES[signs[3]]
                    if m1 == m2 == m3 == m4:
                        txt = f"{a} - {c} - {b} - {d}"
                        if txt not in patterns["大十字"]: patterns["大十字"].append(txt)
        for a, b, c, d in itertools.permutations(quad):
            if is_asp(a, b, 120) and is_asp(b, c, 120) and is_asp(a, c, 120):
                if is_asp(d, a, 180) and is_asp(d, b, 60) and is_asp(d, c, 60):
                    txt = f"{a} - {b} - {c} - {d} (風箏頂點: {d})"
                    if txt not in patterns["風箏"]: patterns["風箏"].append(txt)
    return patterns

def draw_astrology_chart(positions, asc_degree, cusps, specs, aspect_system, speeds=None):
    aspects = []
    p_names = [p for p in positions.keys() if p in PLANET_SYMBOLS]
    for i in range(len(p_names)):
        for j in range(i+1, len(p_names)):
            p1, p2 = p_names[i], p_names[j]
            diff = abs(positions[p1] - positions[p2])
            if diff > 180: diff = 360 - diff
            for angle, name, color, orb in specs:
                if orb == 0: continue
                allowed_orb = LILLY_MOITIES.get(p1, 2.5) + LILLY_MOITIES.get(p2, 2.5) if aspect_system == "古典 (威廉・里利)" else orb
                if abs(diff - angle) <= allowed_orb:
                    aspects.append((p1, p2, color))
                    break

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("W"); ax.set_theta_direction(-1)      
    def get_canvas_angle(zodiac_degree): return np.deg2rad(asc_degree - zodiac_degree)
    ax.axis('off')
    
    ax.add_artist(plt.Circle((0, 0), 1.0, transform=ax.transData._b, fill=False, color='#333', lw=1.2))
    ax.add_artist(plt.Circle((0, 0), 0.82, transform=ax.transData._b, fill=False, color='#333', lw=1.2))
    ax.add_artist(plt.Circle((0, 0), 0.45, transform=ax.transData._b, fill=False, color='#ccc', lw=0.8))

    for i in range(12):
        angle = get_canvas_angle(i * 30)
        ax.plot([angle, angle], [0.82, 1.0], color='#888', lw=0.8)
        ax.text(get_canvas_angle(i * 30 + 15), 0.91, ZODIAC_SYMBOLS[i], fontsize=16, ha='center', va='center')

    c_list = list(cusps)[1:] if len(cusps) == 13 else list(cusps)
    for i, deg in enumerate(c_list):
        ax.plot([get_canvas_angle(deg)]*2, [0.45, 0.82], color='red' if i == 0 else ('blue' if i == 9 else '#666'), lw=1.5 if i in [0,9] else 0.7)

    for p1, p2, color in aspects:
        ax.plot([get_canvas_angle(positions[p1]), get_canvas_angle(positions[p2])], [0.45, 0.45], color=color, lw=1.2, alpha=0.3)

    sorted_planets = sorted([(p, deg) for p, deg in positions.items() if p in PLANET_SYMBOLS], key=lambda x: x[1])
    render_coords = {}
    occupied_slots = []
    
    for p, original_deg in sorted_planets:
        r_level = 0.76  
        adjusted_deg = original_deg
        while True:
            conflict = False
            for occ_deg, occ_r in occupied_slots:
                ang_diff = abs((adjusted_deg - occ_deg + 180) % 360 - 180)
                if ang_diff < 7.0 and abs(occ_r - r_level) < 0.01:
                    conflict = True
                    break
            if conflict:
                r_level -= 0.075  
                adjusted_deg += 1.5   
            else:
                break
        render_coords[p] = (r_level, adjusted_deg)
        occupied_slots.append((adjusted_deg, r_level))

    for planet, original_deg in positions.items():
        if planet not in PLANET_SYMBOLS: continue
        r, draw_deg = render_coords[planet]
        actual_angle = get_canvas_angle(original_deg) 
        draw_angle = get_canvas_angle(draw_deg)       
        sym = PLANET_SYMBOLS[planet]
        
        ax.plot([draw_angle, actual_angle], [r - 0.065, 0.45], color=sym['color'], lw=0.9, alpha=0.6, linestyle='-')
        f_size = 11 if planet in ['上升', '中天'] else 18
        f_weight = 'bold' if planet in ['上升', '中天'] else 'normal'
        ax.text(draw_angle, r, sym['sym'], fontsize=f_size, ha='center', va='center', color=sym['color'], fontweight=f_weight)
        ax.text(draw_angle, r - 0.045, f"{int(original_deg % 30)}°", fontsize=8, ha='center', va='center', color='#555')
        
        if speeds and speeds.get(planet, 0) < 0 and planet in ['水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星']:
            ax.annotate('R', xy=(draw_angle, r), xytext=(-12, -6), textcoords='offset points',
                        color='#c0392b', fontsize=7.5, fontweight='bold', ha='right', va='top')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=145)
    buf.seek(0); plt.close()
    return buf

def resolve_location_and_time(loc_name, y, m, d, h, minute):
    if not loc_name or not loc_name.strip(): 
        loc_name = "Manchester"
    location = ArcGIS(timeout=10).geocode(loc_name)
    if not location: 
        raise ValueError(f"無法定位城市: '{loc_name}'")
    lat, lon = location.latitude, location.longitude
    tz_str = TimezoneFinder().timezone_at(lng=lon, lat=lat) or "UTC"
    
    y = max(100, min(9000, int(y)))
    m = max(1, min(12, int(m)))
    d = max(1, int(d))
    
    try:
        local_dt = pytz.timezone(tz_str).localize(datetime.datetime(y, m, d, int(h), int(minute)))
    except ValueError:
        try:
            local_dt = pytz.timezone(tz_str).localize(datetime.datetime(y, m, 1, int(h), int(minute)))
        except Exception as e2:
            raise ValueError(f"處理的日期無效：{str(e2)}")
        
    utc_dt = local_dt.astimezone(pytz.utc)
    hour_decimal = utc_dt.hour + (utc_dt.minute / 60.0)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
    info = f"城市: {location.address}\n時區: {tz_str}\n時間: {local_dt.strftime('%Y-%m-%d %H:%M')}\n"
    return jd, lat, lon, info, utc_dt

def draw_local_space_compass(ls_data):
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("N") 
    ax.set_theta_direction(-1)      
    ax.axis('off')
    
    ax.add_artist(plt.Circle((0, 0), 1.0, transform=ax.transData._b, fill=False, color='#333', lw=1.2))
    ax.add_artist(plt.Circle((0, 0), 0.8, transform=ax.transData._b, fill=False, color='#ccc', lw=0.8))
    
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    for i, d in enumerate(dirs):
        angle = np.deg2rad(i * 45)
        ax.plot([angle, angle], [0.8, 1.0], color='#888', lw=0.8)
        ax.text(angle, 1.08, d, fontsize=13, ha='center', va='center', fontweight='bold', color='#333')
        
    occupied_slots = []
    for row in sorted(ls_data, key=lambda x: x['az']):
        orig_angle = row['az']
        r_level = 0.75
        adj_angle = orig_angle
        
        while True:
            conflict = False
            for occ_az, occ_r in occupied_slots:
                diff = abs((adj_angle - occ_az + 180) % 360 - 180)
                if diff < 10.0 and abs(occ_r - r_level) < 0.01:
                    conflict = True
                    break
            if conflict:
                r_level -= 0.1
                adj_angle += 2.0
            else:
                break
        occupied_slots.append((adj_angle, r_level))
        
        theta_actual = np.deg2rad(orig_angle)
        theta_draw = np.deg2rad(adj_angle)
        color = row['color']
        sym = row['sym']
        
        ax.plot([theta_draw, theta_actual], [r_level, 0.8], color=color, lw=0.9, alpha=0.6, linestyle='-')
        ax.plot([theta_actual, theta_actual], [0, 0.8], color=color, lw=0.6, alpha=0.3, linestyle=':')
        
        ax.text(theta_draw, r_level - 0.03, sym, fontsize=18, ha='center', va='center', color=color)
        ax.text(theta_draw, r_level - 0.1, f"{orig_angle:.1f}°", fontsize=8, ha='center', va='center', color='#555')
        
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=145)
    buf.seek(0); plt.close()
    return buf

def calc_zodiacal_releasing(lot_lon, birth_jd):
    target_jd = birth_jd + 36525.0
    start_sign = int(lot_lon // 30) % 12
    periods = []
    current_jd = birth_jd
    l1_sign = start_sign

    while current_jd < target_jd:
        l1_days = ZR_PERIODS[l1_sign] * 360
        l1_end_jd = current_jd + l1_days
        l2_sign = l1_sign
        l2_start_jd = current_jd
        months = 0

        while l2_start_jd < l1_end_jd and l2_start_jd < target_jd:
            l2_days = ZR_PERIODS[l2_sign] * 30
            l2_end_jd = l2_start_jd + l2_days
            if l2_end_jd > l1_end_jd: l2_end_jd = l1_end_jd
            
            is_lb = (months == 12)
            if is_lb: l2_sign = (l2_sign + 6) % 12

            s_dt = swe.revjul(l2_start_jd)
            e_dt = swe.revjul(l2_end_jd)
            periods.append(f"L1 {ZODIAC_NAMES[l1_sign]} -> L2 {ZODIAC_NAMES[l2_sign]}{' (LB)' if is_lb else ''}: {s_dt[0]}-{s_dt[1]:02d}-{s_dt[2]:02d} ~ {e_dt[0]}-{e_dt[1]:02d}-{e_dt[2]:02d}")

            l2_start_jd = l2_end_jd
            months += 1
            if not is_lb: l2_sign = (l2_sign + 1) % 12

        current_jd = l1_end_jd
        l1_sign = (l1_sign + 1) % 12
    return periods

# ================= 3. 日返 5大吉凶分析功能 =================
def get_aspect_and_sign_score(lon_sr, lon_n):
    diff = abs(lon_sr - lon_n)
    diff = min(diff, 360 - diff)
    exact_score, exact_name = 0, "無"
    if diff <= 6.0: exact_score, exact_name = 1, "合相"
    elif abs(diff - 120) <= 6.0: exact_score, exact_name = 1, "三分相"
    elif abs(diff - 60) <= 6.0: exact_score, exact_name = 1, "六分相"
    elif abs(diff - 180) <= 6.0: exact_score, exact_name = -1, "對分相"
    elif abs(diff - 90) <= 6.0: exact_score, exact_name = -1, "四分相"
    
    sign_sr = int(lon_sr // 30) % 12
    sign_n = int(lon_n // 30) % 12
    sign_diff = (sign_sr - sign_n) % 12
    sign_score, sign_name = 0, "無"
    if sign_diff == 0: sign_score, sign_name = 1, "同星座"
    elif sign_diff in [4, 8]: sign_score, sign_name = 1, "三分"
    elif sign_diff in [2, 10]: sign_score, sign_name = 1, "六分"
    elif sign_diff == 6: sign_score, sign_name = -1, "對分"
    elif sign_diff in [3, 9]: sign_score, sign_name = -1, "四分"
    return exact_score, exact_name, sign_score, sign_name

def process_eval(title, sr_name, sr_lon, n_name, n_lon, cusps_n, h_code):
    e_sc, e_nm, s_sc, s_nm = get_aspect_and_sign_score(sr_lon, n_lon)
    sub_total = e_sc + s_sc
    status = "吉" if sub_total > 0 else ("凶" if sub_total < 0 else "平")
    
    sign_e = "+" if e_sc > 0 else ""
    sign_s = "+" if s_sc > 0 else ""
    sign_t = "+" if sub_total > 0 else ""
    
    table_row = {
        "評估項目": title,
        "日返落點": f"{sr_name} [{format_degree(sr_lon)}]",
        "本命對比": f"{n_name} [{format_degree(n_lon)} {get_house_number(n_lon, cusps_n, h_code)}宮]",
        "準確相位": f"{e_nm} ({sign_e}{e_sc}分)",
        "星座相位": f"{s_nm} ({sign_s}{s_sc}分)",
        "得分": f"{sign_t}{sub_total}分 ({status})"
    }
    return sub_total, table_row

def calc_5_core(age, jd_n, pos_n, asc_n, cusps_n, speed_n, lat_p, lon_p, h_code, dt_n_utc):
    try:
        jd_approx = swe.julday(dt_n_utc.year + age, dt_n_utc.month, dt_n_utc.day, 12.0)
        j1, j2 = jd_approx - 2, jd_approx + 2
        sun_n = pos_n['太陽']
        f1 = ((swe.calc_ut(j1, swe.SUN)[0][0] - sun_n + 180) % 360 - 180)
        f2 = ((swe.calc_ut(j2, swe.SUN)[0][0] - sun_n + 180) % 360 - 180)
        for _ in range(20):
            if abs(f2 - f1) < 1e-11: break
            j_next = j2 - f2 * (j2 - j1) / (f2 - f1)
            if abs(j_next - jd_approx) > 10: j_next = jd_approx + 0.1
            j1, j2, f1 = j2, j_next, f2
            f2 = ((swe.calc_ut(j2, swe.SUN)[0][0] - sun_n + 180) % 360 - 180)
            
        pos_sr, _, asc_sr, cusps_sr, mc_sr, speed_sr = calculate_chart_engine(j2, lat_p, lon_p, h_code)
        
        is_day = 7 <= get_house_number(pos_n['太陽'], cusps_n, h_code) <= 12
        mars_score = 0
        saturn_score = 0

        if is_day: mars_score += 3
        else: saturn_score += 3

        mars_sign = int(pos_n['火星'] // 30) % 12
        saturn_sign = int(pos_n['土星'] // 30) % 12

        if mars_sign in (DIGNITIES['火星']['陷'] + DIGNITIES['火星']['弱']): mars_score += 2
        elif mars_sign in (DIGNITIES['火星']['廟'] + DIGNITIES['火星']['旺']): mars_score -= 2

        if saturn_sign in (DIGNITIES['土星']['陷'] + DIGNITIES['土星']['弱']): saturn_score += 2
        elif saturn_sign in (DIGNITIES['土星']['廟'] + DIGNITIES['土星']['旺']): saturn_score -= 2

        if get_house_number(pos_n['火星'], cusps_n, h_code) in [6, 8, 12]: mars_score += 2
        if get_house_number(pos_n['土星'], cusps_n, h_code) in [6, 8, 12]: saturn_score += 2

        if speed_n.get('火星', 0) < 0: mars_score += 2
        if speed_n.get('土星', 0) < 0: saturn_score += 1

        most_malefic = '火星' if mars_score > saturn_score else '土星'
        
        total_sc = 0
        lines = []
        
        sc, row = process_eval("1. ASC 狀態", "ASC", asc_sr, "ASC", asc_n, cusps_n, h_code)
        total_sc += sc; lines.append(row)
        
        pof_n = ((asc_n + pos_n['月亮'] - pos_n['太陽']) if (7 <= get_house_number(pos_n['太陽'], cusps_n, h_code) <= 12) else (asc_n + pos_n['太陽'] - pos_n['月亮'])) % 360
        pof_sr = ((asc_sr + pos_sr['月亮'] - pos_sr['太陽']) if (7 <= get_house_number(pos_sr['太陽'], cusps_sr, h_code) <= 12) else (asc_sr + pos_sr['太陽'] - pos_sr['月亮'])) % 360
        sc, row = process_eval("2. 福點狀態", "福點", pof_sr, "福點", pof_n, cusps_n, h_code)
        total_sc += sc; lines.append(row)
        
        pof_ruler_n = TRADITIONAL_RULERS[ZODIAC_NAMES[int(pof_n // 30) % 12]]
        pof_ruler_sr = TRADITIONAL_RULERS[ZODIAC_NAMES[int(pof_sr // 30) % 12]]
        sc, row = process_eval("3. 福點主星狀態", f"主星({pof_ruler_sr})", pos_sr[pof_ruler_sr], f"主星({pof_ruler_n})", pos_n[pof_ruler_n], cusps_n, h_code)
        total_sc += sc; lines.append(row)
        
        prof_sign = (int(asc_n // 30) % 12 + age) % 12
        prof_ruler = TRADITIONAL_RULERS[ZODIAC_NAMES[prof_sign]]
        sc, row = process_eval(f"4. 小限主星 ({age}歲)", f"主星({prof_ruler})", pos_sr[prof_ruler], f"主星({prof_ruler})", pos_n[prof_ruler], cusps_n, h_code)
        total_sc += sc; lines.append(row)
        
        asc_ruler_n = TRADITIONAL_RULERS[ZODIAC_NAMES[int(asc_n // 30) % 12]]
        asc_ruler_sr = TRADITIONAL_RULERS[ZODIAC_NAMES[int(asc_sr // 30) % 12]]
        sc, row = process_eval("5. ASC 命主星", f"命主({asc_ruler_sr})", pos_sr[asc_ruler_sr], f"命主({asc_ruler_n})", pos_n[asc_ruler_n], cusps_n, h_code)
        total_sc += sc; lines.append(row)

        sr_malefic_lon = pos_sr[most_malefic]
        n_malefic_lon = pos_n[most_malefic]
        
        col_diff = abs(sr_malefic_lon - n_malefic_lon)
        col_diff = min(col_diff, 360 - col_diff)
        
        col_sc = 0
        col_nm = "無"
        if col_diff <= 6.0: col_sc, col_nm = -2, "合相"
        elif abs(col_diff - 90) <= 6.0: col_sc, col_nm = -2, "四分相"
        elif abs(col_diff - 180) <= 6.0: col_sc, col_nm = -2, "對分相"
        
        col_status = "凶" if col_sc < 0 else "平"
        
        lines.append({
            "評估項目": "6. 終極對撞 (本命最凶星)",
            "日返落點": f"{most_malefic} [{format_degree(sr_malefic_lon)}]",
            "本命對比": f"{most_malefic} [{format_degree(n_malefic_lon)} 本命 {get_house_number(n_malefic_lon, cusps_n, h_code)}宮]",
            "準確相位": f"{col_nm} ({col_sc}分)",
            "星座相位": "-",
            "得分": f"{col_sc}分 ({col_status})"
        })
        total_sc += col_sc
        
        if total_sc > 4: rating = "大吉"
        elif 2 <= total_sc <= 4: rating = "吉"
        elif -1 <= total_sc <= 1: rating = "平"
        elif -4 <= total_sc <= -2: rating = "凶"
        else: rating = "大凶"

        sr_internal_score = 0
        sr_internal_lines = []
        
        angles = [asc_sr, mc_sr, (asc_sr + 180) % 360, (mc_sr + 180) % 360]
        angle_names = ["ASC", "MC", "DSC", "IC"]
        
        for p, pts in [('木星', 5), ('金星', 4), ('火星', -4), ('土星', -4), ('天王星', -3), ('海王星', -3), ('冥王星', -3)]:
            lon = pos_sr[p]
            for ang_val, ang_name in zip(angles, angle_names):
                diff = abs(lon - ang_val)
                diff = min(diff, 360 - diff)
                if diff <= 3.0:
                    sr_internal_score += pts
                    sr_internal_lines.append({"評估項目": "星體壓角", "星體/狀態": f"{p} 合相 {ang_name}", "細節": f"容許度 {diff:.1f}°", "得分": f"{'+' if pts>0 else ''}{pts}分"})
                    break 

        for p in ['太陽', '月亮', '木星', '金星']:
            h_num = get_house_number(pos_sr[p], cusps_sr, h_code)
            if h_num in [1, 5, 10, 11]:
                sr_internal_score += 2
                sr_internal_lines.append({"評估項目": "吉星入吉宮", "星體/狀態": f"{p} 入 {h_num} 宮", "細節": "正面加分", "得分": "+2分"})

        for p in ['火星', '土星']:
            h_num = get_house_number(pos_sr[p], cusps_sr, h_code)
            if h_num in [6, 8, 12]:
                sr_internal_score += -2
                sr_internal_lines.append({"評估項目": "凶星入凶宮", "星體/狀態": f"{p} 入 {h_num} 宮", "細節": "負面減分", "得分": "-2分"})

        if not sr_internal_lines:
            sr_internal_lines.append({"評估項目": "無觸發", "星體/狀態": "-", "細節": "無星體壓角或落關鍵宮位", "得分": "0分"})

        if sr_internal_score > 4: sr_internal_rating = "大吉"
        elif 2 <= sr_internal_score <= 4: sr_internal_rating = "吉"
        elif -1 <= sr_internal_score <= 1: sr_internal_rating = "平"
        elif -4 <= sr_internal_score <= -2: sr_internal_rating = "凶"
        else: sr_internal_rating = "大凶"
        
        return j2, pos_sr, asc_sr, cusps_sr, speed_sr, total_sc, rating, lines, sr_internal_score, sr_internal_rating, sr_internal_lines
    
    except Exception:
        return None, None, None, None, None, 0, "計算失敗", [], 0, "計算失敗", []

# ================= 4. 擇時過濾與資料庫排名引擎 =================
def get_planet_or_ruler_lon(target_name, pos, cusps, h_code):
    if "宮主" in target_name:
        h_idx = int(target_name.replace("宮主", "")) - 1
        c_list = list(cusps)[1:] if len(cusps) == 13 else list(cusps)
        if h_code == b'W':
            asc_sign = int(c_list[0] // 30) % 12
            sign_idx = (asc_sign + h_idx) % 12
        else:
            sign_idx = int(c_list[h_idx] // 30) % 12
        ruler_name = TRADITIONAL_RULERS[ZODIAC_NAMES[sign_idx]]
        return pos[ruler_name], ruler_name
    return pos[target_name], target_name

def check_election_criteria(jd, lat, lon, h_code, conditions, exclusions):
    pos, _, asc, cusps, mc, speed = calculate_chart_engine(jd, lat, lon, h_code)
    c_list = list(cusps)[1:] if len(cusps) == 13 else list(cusps)
    
    asc_sign = int(asc // 30) % 12
    ruler_1_name = TRADITIONAL_RULERS[ZODIAC_NAMES[asc_sign]]
    ruler_1_lon = pos[ruler_1_name]
    ruler_1_sign = int(ruler_1_lon // 30) % 12
    
    if exclusions.get("1宮主陷弱") and (ruler_1_sign in DIGNITIES.get(ruler_1_name, {}).get('陷', []) or ruler_1_sign in DIGNITIES.get(ruler_1_name, {}).get('弱', [])): return False, 0
    if exclusions.get("月亮與火土凶相"):
        for mal in ['火星', '土星']:
            d = abs(pos['月亮'] - pos[mal]); d = 360 - d if d > 180 else d
            if abs(d - 90) <= 6.0 or abs(d - 180) <= 6.0: return False, 0
    if exclusions.get("月亮空亡") and (pos['月亮'] % 30) > 29.5: return False, 0
    if exclusions.get("火星或土星入1宮") and (get_house_number(pos['火星'], cusps, h_code) == 1 or get_house_number(pos['土星'], cusps, h_code) == 1): return False, 0
    if exclusions.get("6/8/12宮主入1宮"):
        for h in [6, 8, 12]:
            _, r_name = get_planet_or_ruler_lon(f"{h}宮主", pos, cusps, h_code)
            if get_house_number(pos[r_name], cusps, h_code) == 1: return False, 0
    if exclusions.get("火土與1宮主凶相"):
        for mal in ['火星', '土星']:
            d = abs(ruler_1_lon - pos[mal]); d = 360 - d if d > 180 else d
            if abs(d - 90) <= 6.0 or abs(d - 180) <= 6.0: return False, 0
    if exclusions.get("6/8/12宮主與1宮主凶相"):
        for h in [6, 8, 12]:
            _, r_name = get_planet_or_ruler_lon(f"{h}宮主", pos, cusps, h_code)
            d = abs(ruler_1_lon - pos[r_name]); d = 360 - d if d > 180 else d
            if abs(d - 90) <= 6.0 or abs(d - 180) <= 6.0: return False, 0
    if exclusions.get("火星或土星合相上升"):
        for mal in ['火星', '土星']:
            d = abs(pos[mal] - asc); d = 360 - d if d > 180 else d
            if d <= 5.0: return False, 0
    if exclusions.get("6/8/12宮主合相上升"):
        for h in [6, 8, 12]:
            _, r_name = get_planet_or_ruler_lon(f"{h}宮主", pos, cusps, h_code)
            d = abs(pos[r_name] - asc); d = 360 - d if d > 180 else d
            if d <= 5.0: return False, 0
    if exclusions.get("土星入角宮") and get_house_number(pos['土星'], cusps, h_code) in [1, 4, 7, 10]: return False, 0
    if exclusions.get("土星合/沖四角"):
        for pt in [asc, mc, (asc+180)%360, (mc+180)%360]:
            d = abs(pos['土星'] - pt); d = 360 - d if d > 180 else d
            if d <= 5.0: return False, 0

    total_orb_deviation = 0.0
    for cond in conditions:
        p1_lon, p1_real_name = get_planet_or_ruler_lon(cond['p1'], pos, cusps, h_code)
        p1_sign = int(p1_lon // 30) % 12
        p1_house = get_house_number(p1_lon, cusps, h_code)
        c_type = cond['type']
        match = False
        current_cond_orb = 0.0
        
        if c_type in ZODIAC_NAMES: match = (ZODIAC_NAMES[p1_sign] == c_type)
        elif "宮" in c_type and "主" not in c_type: match = (p1_house == int(c_type.replace("宮位", "").replace("宮", "")))
        elif c_type == "逆行": match = (speed.get(p1_real_name, 0) < 0)
        elif c_type == "順行": match = (speed.get(p1_real_name, 0) >= 0)
        elif c_type == "廟及旺": match = (p1_sign in DIGNITIES.get(p1_real_name, {}).get('廟', []) or p1_sign in DIGNITIES.get(p1_real_name, {}).get('旺', []))
        elif c_type == "陷及弱": match = (p1_sign in DIGNITIES.get(p1_real_name, {}).get('陷', []) or p1_sign in DIGNITIES.get(p1_real_name, {}).get('弱', []))
        elif c_type in ["合相", "對相", "三分", "四分", "六分"]:
            p2_lon, _ = get_planet_or_ruler_lon(cond['p2'], pos, cusps, h_code)
            d = abs(p1_lon - p2_lon); d = 360 - d if d > 180 else d
            target_ang = {"合相":0, "對相":180, "三分":120, "四分":90, "六分":60}[c_type]
            current_cond_orb = abs(d - target_ang)
            match = (current_cond_orb <= 6.0)
            if match: total_orb_deviation += current_cond_orb
            
        if cond['mode'] == "包含" and not match: return False, 0
        if cond['mode'] == "不包括" and match: return False, 0
        
    return True, total_orb_deviation

class DB_Evaluator:
    def __init__(self, pos, cusps, h_code, asc, speeds):
        self.pos = pos
        self.cusps = cusps
        self.h_code = h_code
        self.asc = asc
        self.speeds = speeds

    def in_h(self, p, houses):
        if p not in self.pos: return False
        return get_house_number(self.pos[p], self.cusps, self.h_code) in houses

    def in_s(self, p, signs):
        if p not in self.pos: return False
        return (int(self.pos[p] // 30) % 12) in signs

    def asp(self, p1, p2, angles, orb=6.0):
        if p1 not in self.pos or p2 not in self.pos: return False
        d = abs(self.pos[p1] - self.pos[p2])
        d = min(d, 360 - d)
        return any(abs(d - a) <= orb for a in angles)
        
    def any_asp(self, p1, p2, orb=8.0):
        return self.asp(p1, p2, [0, 60, 90, 120, 180], orb)
        
    def is_aff(self, p):
        return self.asp(p, '土星', [0, 90, 180]) or self.asp(p, '火星', [0, 90, 180])

    def rul(self, h_num):
        c_list = list(self.cusps)[1:] if len(self.cusps) == 13 else list(self.cusps)
        if self.h_code == b'W':
            asc_s = int(c_list[0] // 30) % 12
            s_idx = (asc_s + h_num - 1) % 12
        else:
            s_idx = int(c_list[h_num - 1] // 30) % 12
        return TRADITIONAL_RULERS[ZODIAC_NAMES[s_idx]]

    def cnt_s(self, p_list, signs):
        return sum(1 for p in p_list if self.in_s(p, signs))

    def cnt_h(self, p_list, houses):
        return sum(1 for p in p_list if self.in_h(p, houses))

DB_RANKING_RULES = {
    "感情/關係類": {
        "1. 最有桃花": lambda e: sum([e.in_h('金星', [5,11]), e.asp('金星', '木星', [0,120]), e.asp('金星', '海王星', [0,120])]),
        "2. 最有異性緣": lambda e: sum([e.asp('金星', '火星', [0,90,120]), e.asp('太陽', '月亮', [0,60,120]) or e.asp('太陽', '金星', [0,60,120]), e.asp(e.rul(5), e.rul(7), [0,60,120])]),
        "3. 最有魅力": lambda e: sum([e.asp('金星', '冥王星', [0,90]), e.in_s('上升', [7]) or e.in_h('冥王星', [1]), e.asp('莉莉絲', '上升', [0]) or e.asp('莉莉絲', '太陽', [0]) or e.asp('莉莉絲', '金星', [0])]),
        "4. 最有婚姻運": lambda e: sum([(e.in_h('木星', [7]) or e.in_h('金星', [7])) and not e.is_aff('木星') and not e.is_aff('金星'), e.in_h(e.rul(7), [1,10]) and (e.asp(e.rul(7), '太陽', [0,60,120]) or e.asp(e.rul(7), '木星', [0,60,120])), e.asp('婚神星', '太陽', [0,120]) or e.asp('婚神星', '金星', [0,120]) or e.asp('婚神星', e.rul(7), [0,120])])
    },
    "事業/成就類": {
        "1. 最有領導力": lambda e: sum([e.in_h('太陽', [1,10]) or e.in_s('太陽', [0,4]), e.in_h('火星', [10]) and (e.asp('火星', '太陽', [0,60,120]) or e.asp('火星', '木星', [0,60,120])), e.asp('太陽', '冥王星', [0,120])]),
        "3. 最有事業運": lambda e: sum([e.in_h('木星', [10]) and not e.is_aff('木星'), e.asp(e.rul(10), '木星', [0,120]) or e.asp(e.rul(10), '金星', [0,120]), e.asp('太陽', '中天', [0,60,120]) or e.asp('月亮', '中天', [0,60,120])])
    }
}

# ================= 5. Streamlit UI 介面 =================
st.sidebar.header("本命盤基本資訊")

uploaded_file = st.sidebar.file_uploader("匯入 JSON 命例", type=["json"])
if uploaded_file is not None:
    try:
        profiles = json.load(uploaded_file)
        st.session_state['imported_profiles'] = profiles
    except Exception as e:
        st.sidebar.error("JSON 格式錯誤")

if 'imported_profiles' in st.session_state and st.session_state['imported_profiles']:
    profile_names = [p.get('Name', 'Unknown') for p in st.session_state['imported_profiles']]
    st.sidebar.selectbox("選擇命例自動填寫", ["-- 請選擇 --"] + profile_names, key="profile_selector", on_change=on_profile_change)

name = st.sidebar.text_input("姓名", key="name_input")
gender = st.sidebar.selectbox("性別", ["男", "女"], key="gender_input")

col1, col2, col3 = st.sidebar.columns(3)
col1.number_input("年", key="n_year", min_value=100, max_value=9000, step=1, on_change=sync_target_age_from_n_year)
col2.number_input("月", key="n_month", min_value=1, max_value=12)
col3.number_input("日", key="n_day", min_value=1, max_value=31)

col4, col5 = st.sidebar.columns(2)
col4.number_input("時", key="n_hour", min_value=0, max_value=23)
col5.number_input("分", key="n_minute", min_value=0, max_value=59)
st.sidebar.text_input("出生城市", key="n_loc", on_change=sync_n_loc_to_p_loc)

btn_col1, btn_col2 = st.sidebar.columns(2)
btn_col1.button("🕒 當下時間", on_click=set_current_time, width="stretch")
btn_col2.button("📍 當下地點", on_click=set_current_loc, width="stretch")

st.sidebar.divider()

with st.sidebar.expander("推運 / 行運 / 日返設定", expanded=False):
    st.number_input("推運 年", key="p_year", min_value=100, max_value=9000, step=1, on_change=update_age_from_year)
    col6, col7 = st.columns(2)
    col6.number_input("推運 月", key="p_month", min_value=1, max_value=12)
    col7.number_input("推運 日", key="p_day", min_value=1, max_value=31)
    col8, col9 = st.columns(2)
    col8.number_input("推運 時", key="p_hour", min_value=0, max_value=23)
    col9.number_input("推運 分", key="p_minute", min_value=0, max_value=59)
    st.text_input("目標城市", key="p_loc")
    st.divider()
    st.number_input("👉 快速設定推運歲數", key="target_age", min_value=0, max_value=120, on_change=update_year_from_age)

with st.sidebar.expander("⏳ 專業擇時動態篩選 (Electional)", expanded=False):
    chk_election = st.checkbox("開啟擇時篩選功能", value=False)
    st.text_input("擇時目標城市", key="el_loc_input", placeholder="預設: Manchester")
    
    start_date = st.date_input("開始日期", datetime.date.today(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31))
    end_date = st.date_input("結束日期", datetime.date.today() + datetime.timedelta(days=7), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31))
    
    st.markdown("**新增自訂篩選條件**")
    elect_pts = ['太陽', '月亮', '水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星', '北交點'] + [f"{i}宮主" for i in range(1, 13)]
    cond_ops = ZODIAC_NAMES + [f"{i}宮位" for i in range(1, 13)] + ["逆行", "順行", "廟及旺", "陷及弱", "合相", "對相", "三分", "四分", "六分"]
    c_mode = st.selectbox("模式", ["包含", "不包括"], key="el_mode")
    c_p1 = st.selectbox("主星體/宮主星", elect_pts, key="el_p1")
    c_type = st.selectbox("條件狀態/相位", cond_ops, key="el_type")
    c_p2 = st.selectbox("目標星體/宮主星", elect_pts, key="el_p2") if c_type in ["合相", "對相", "三分", "四分", "六分"] else None
    
    if st.button("➕ 新增此條篩選條件"):
        st.session_state.election_conditions.append({"mode": c_mode, "p1": c_p1, "type": c_type, "p2": c_p2})
        st.session_state.calc_triggered = False
    if st.session_state.election_conditions:
        st.caption("目前已設置條件：")
        for idx, cd in enumerate(st.session_state.election_conditions):
            st.text(f"{idx+1}. [{cd['mode']}] {cd['p1']} 滿足 {cd['type']}" + (f" ➔ {cd['p2']}" if cd['p2'] else ""))
        if st.button("🗑️ 清空所有條件"):
            st.session_state.election_conditions = []
            st.session_state.calc_triggered = False

h_sys_name = st.sidebar.selectbox("宮位系統", ["普拉西度 (Placidus)", "整宮制 (Whole Sign)", "Regiomontanus"])
a_sys_name = st.sidebar.selectbox("相位系統", ["現代", "古典 (威廉・里利)", "自訂"])
custom_orbs = {}
if a_sys_name == "自訂":
    with st.sidebar.expander("⚙️ 自訂相位容許度", expanded=True):
        c1, c2, c3 = st.columns(3)
        custom_orbs[0] = c1.number_input("0°", value=8)
        custom_orbs[30] = c2.number_input("30°", value=0)
        custom_orbs[45] = c3.number_input("45°", value=1)
        custom_orbs[60] = c1.number_input("60°", value=6)
        custom_orbs[90] = c2.number_input("90°", value=7)
        custom_orbs[120] = c3.number_input("120°", value=7)
        custom_orbs[135] = c1.number_input("135°", value=1)
        custom_orbs[150] = c2.number_input("150°", value=0)
        custom_orbs[180] = c3.number_input("180°", value=8)
else:
    custom_orbs = {0: 8.0, 30: 0, 45: 0, 60: 6.0, 90: 7.0, 120: 7.0, 135: 0, 150: 0, 180: 8.0}

with st.sidebar.expander("📊 四元素與四正星座權重配分", expanded=False):
    p_weights = {p: st.number_input(f"{p} 權重", value=0 if p in ['天王星', '海王星', '冥王星'] else 1, min_value=0, max_value=5, step=1) for p in WEIGHT_POINTS}

st.sidebar.subheader("進階功能選項")
chk_db_ranking = st.sidebar.checkbox("資料庫排名 (Top 3)") 
chk_greek = st.sidebar.checkbox("七大希臘點")
chk_midpoint = st.sidebar.checkbox("顯示中點")
chk_whole_rule = st.sidebar.checkbox("宮主星整宮制")
chk_solar_arc = st.sidebar.checkbox("真實日弧相位")
chk_sa_midpoint = st.sidebar.checkbox("日弧中點")    
chk_profection = st.sidebar.checkbox("顯示小限歲數")
chk_zr = st.sidebar.checkbox("黃道釋放")             
chk_solar_return = st.sidebar.checkbox("計算日返星盤")
chk_batch = st.sidebar.checkbox("大批 (1-75歲 日弧及日返吉凶)") 
chk_sr_reloc = st.sidebar.checkbox("日返重置 (各國流年吉凶)") 
chk_transit = st.sidebar.checkbox("計算過運行運")

aspect_specs_full = [(0, "合相", '#95a5a6', custom_orbs.get(0, 0)), (30, "十二分", '#f39c12', custom_orbs.get(30, 0)), (45, "半四分", '#d35400', custom_orbs.get(45, 0)), (60, "六分", '#2ecc71', custom_orbs.get(60, 0)), (90, "四分", '#e74c3c', custom_orbs.get(90, 0)), (120, "三分", '#27ae60', custom_orbs.get(120, 0)), (135, "補八分", '#c0392b', custom_orbs.get(135, 0)), (150, "補十二", '#8e44ad', custom_orbs.get(150, 0)), (180, "對相", '#2980b9', custom_orbs.get(180, 0))]

if st.sidebar.button("🔮 執行占星整合計算", width="stretch", type="primary"):
    st.session_state.calc_triggered = True

# --- 核心主體繪製與擇時運算 ---
if st.session_state.calc_triggered:
    try:
        with st.spinner('天文運算與分析報告生成中...'):
            h_code = b'W' if "整宮" in h_sys_name else (b'R' if "Regiomontanus" in h_sys_name else b'P')
            
            jd_n, lat_n, lon_n, meta_n, dt_n_utc = resolve_location_and_time(st.session_state.n_loc, st.session_state.n_year, st.session_state.n_month, st.session_state.n_day, st.session_state.n_hour, st.session_state.n_minute)
            jd_p, lat_p, lon_p, meta_p, dt_p_utc = resolve_location_and_time(st.session_state.p_loc, st.session_state.p_year, st.session_state.p_month, st.session_state.p_day, st.session_state.p_hour, st.session_state.p_minute)
            
            pos_n, pos_lat_n, asc_n, cusps_n, mc_n, speed_n = calculate_chart_engine(jd_n, lat_n, lon_n, h_code)
            img_n = draw_astrology_chart(pos_n, asc_n, cusps_n, aspect_specs_full, a_sys_name, speeds=speed_n)
            
            local_space_data = []
            for p in LOCAL_SPACE_POINTS:
                if p in pos_n and p in pos_lat_n:
                    xin = (pos_n[p], pos_lat_n[p], 0.0)
                    geopos = (lon_n, lat_n, 0.0)
                    az_alt = swe.azalt(jd_n, swe.ECL2HOR, geopos, 1013.25, 15.0, xin)
                    az_n = (az_alt[0] + 180) % 360
                    dirs = ["北 (N)", "東北 (NE)", "東 (E)", "東南 (SE)", "南 (S)", "西南 (SW)", "西 (W)", "西北 (NW)"]
                    idx = int((az_n + 22.5) // 45) % 8
                    local_space_data.append({
                        "planet": p, "sym": PLANET_SYMBOLS[p]['sym'] if p in PLANET_SYMBOLS else "", "color": PLANET_SYMBOLS[p]['color'] if p in PLANET_SYMBOLS else "#000",
                        "az": az_n, "alt": az_alt[1], "dir": dirs[idx], "status": "地平上" if az_alt[1] >= 0 else "地平下"
                    })
            
            img_ls = draw_local_space_compass(local_space_data)
            
            is_day = 7 <= get_house_number(pos_n['太陽'], cusps_n, h_code) <= 12
            elements_score = {'火': 0, '土': 0, '風': 0, '水': 0}
            modes_score = {'開創': 0, '固定': 0, '變動': 0}
            for p in WEIGHT_POINTS:
                if p in pos_n:
                    z_idx = int(pos_n[p] // 30) % 12
                    elements_score[ZODIAC_ELEMENTS[z_idx]] += p_weights.get(p, 1)
                    modes_score[ZODIAC_MODES[z_idx]] += p_weights.get(p, 1)
            
            detected_patterns = find_astrology_patterns(pos_n)
            report = f"== 命盤基本觀測 ==\n持有人：{st.session_state.name_input} ({st.session_state.gender_input})\n{meta_n}\n"
            
            if chk_election:
                el_city = st.session_state.get('el_loc_input', 'Manchester')
                if not el_city or not el_city.strip(): el_city = "Manchester"
                try:
                    _, lat_el, lon_el, _, _ = resolve_location_and_time(el_city, 2026, 1, 1, 12, 0)
                    tz_str_el = TimezoneFinder().timezone_at(lng=lon_el, lat=lat_el) or "UTC"
                except:
                    lat_el, lon_el, tz_str_el = lat_p, lon_p, TimezoneFinder().timezone_at(lng=lon_p, lat=lat_p) or "UTC"

                local_tz = pytz.timezone(tz_str_el)
                start_dt = local_tz.localize(datetime.datetime.combine(start_date, datetime.time.min))
                end_dt = local_tz.localize(datetime.datetime.combine(end_date, datetime.time.max))
                
                valid_events = []
                current_event_block = [] 
                current_eval_dt = start_dt
                
                while current_eval_dt <= end_dt:
                    eval_utc = current_eval_dt.astimezone(pytz.utc)
                    dec_hour = eval_utc.hour + (eval_utc.minute / 60.0)
                    jd_eval = swe.julday(eval_utc.year, eval_utc.month, eval_utc.day, dec_hour)
                    
                    is_ok, orb_dev = check_election_criteria(jd_eval, lat_el, lon_el, h_code, st.session_state.election_conditions, exclusions_map)
                    
                    if is_ok:
                        current_event_block.append({'dt': current_eval_dt, 'orb': orb_dev})
                    else:
                        if current_event_block:
                            best_match = min(current_event_block, key=lambda x: x['orb'])
                            valid_events.append(best_match['dt'])
                            current_event_block = [] 
                    current_eval_dt += datetime.timedelta(hours=1)
                
                if current_event_block:
                    best_match = min(current_event_block, key=lambda x: x['orb'])
                    valid_events.append(best_match['dt'])
                st.session_state['election_results'] = valid_events

            report += "【四元素】\n" + f"火：{elements_score['火']}   土：{elements_score['土']}   風：{elements_score['風']}   水：{elements_score['水']}\n"
            report += "【四正星座】\n" + f"開創：{modes_score['開創']}   固定：{modes_score['固定']}   變動：{modes_score['變動']}\n\n"
            
            # --- 建立 UI 及 古典占星運算邏輯 ---
            has_el_results = chk_election and 'election_results' in st.session_state and len(st.session_state['election_results']) > 0
            if has_el_results: col_main1, col_main2, col_main3 = st.columns([1.2, 1, 0.8])
            else: col_main1, col_main2 = st.columns([1, 1])

            with col_main1:
                st.subheader("圖表視覺化")
                tabs = st.tabs(["本命星盤", "日返星盤", "地平占星", "流年大批", "日返重置", "資料庫排名"])
                
                with tabs[0]: 
                    st.image(img_n)
                    
                    # ====== 💡 古典占星狀態列表 (新增部分) ======
                    st.markdown("### 古典占星狀態列表")
                    
                    TRAD_PLANETS = ['太陽', '月亮', '水星', '金星', '火星', '木星', '土星']
                    P_MAP = {'太陽': '☉', '月亮': '☽', '水星': '☿', '金星': '♀', '火星': '♂', '木星': '♃', '土星': '♄'}
                    
                    # 1 & 2. 宮位吉凶、性質分類
                    h_dist = {i:[] for i in range(1, 13)}
                    for p in TRAD_PLANETS:
                        if p in pos_n:
                            h = get_house_number(pos_n[p], cusps_n, h_code)
                            h_dist[h].append(P_MAP[p])
                            
                    t1_good = " ".join(h_dist[1]+h_dist[3]+h_dist[4]+h_dist[5]+h_dist[7]+h_dist[9]+h_dist[10]+h_dist[11])
                    t1_minor = " ".join(h_dist[2])
                    t1_bad = " ".join(h_dist[6]+h_dist[8]+h_dist[12])
                    
                    t2_ang = " ".join(h_dist[1]+h_dist[4]+h_dist[7]+h_dist[10])
                    t2_suc = " ".join(h_dist[2]+h_dist[5]+h_dist[8]+h_dist[11])
                    t2_cad = " ".join(h_dist[3]+h_dist[6]+h_dist[9]+h_dist[12])
                    
                    table_styles = """
                    <style>
                    .cls-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; text-align: center; font-family: sans-serif; }
                    .cls-table th { background-color: #3498db; color: white; border: 1px solid #ddd; padding: 6px; font-weight: bold; }
                    .cls-table td { border: 1px solid #ddd; padding: 6px; }
                    .hl { background-color: #ffeaa7; color: black; font-weight: bold; padding: 2px 4px; border-radius: 3px; }
                    </style>
                    """
                    
                    st.markdown(table_styles + f'''
                    <div style="display:flex; gap:20px; margin-bottom:15px;">
                        <div style="flex:1;">
                            <table class="cls-table">
                                <tr><th colspan="2">七星入吉凶宮</th></tr>
                                <tr><td><b>吉宮</b> (1,3,4,5,7,9,10,11)</td><td>{t1_good}</td></tr>
                                <tr><td><b>次凶宮</b> (2)</td><td>{t1_minor}</td></tr>
                                <tr><td><b>凶宮</b> (6,8,12)</td><td>{t1_bad}</td></tr>
                            </table>
                        </div>
                        <div style="flex:1;">
                            <table class="cls-table">
                                <tr><th colspan="2">七星入角續果宮</th></tr>
                                <tr><td><b>角宮</b> (1,4,7,10)</td><td>{t2_ang}</td></tr>
                                <tr><td><b>續宮</b> (2,5,8,11)</td><td>{t2_suc}</td></tr>
                                <tr><td><b>果宮</b> (3,6,9,12)</td><td>{t2_cad}</td></tr>
                            </table>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # 古典字典與規則
                    domiciles = ['♂', '♀', '☿', '☽', '☉', '☿', '♀', '♂', '♃', '♄', '♄', '♃']
                    exaltations = ['☉', '☽', '', '♃', '', '☿', '♄', '', '', '♂', '', '♀']
                    detriments = ['♀', '♂', '♃', '♄', '♄', '♃', '♂', '♀', '☿', '☽', '☉', '☿']
                    falls = ['♄', '', '', '♂', '', '♀', '☉', '☽', '', '♃', '', '☿']
                    
                    def get_trip(s_idx):
                        if s_idx in [0, 4, 8]: return ['☉', '♃', '♄']
                        if s_idx in [1, 5, 9]: return ['♀', '☽', '♂']
                        if s_idx in [2, 6, 10]: return ['♄', '☿', '♃']
                        return ['♀', '♂', '☽']
                        
                    faces_seq = ['♂', '☉', '♀', '☿', '☽', '♄', '♃']
                    def get_face(s_idx, d): return faces_seq[(s_idx * 3 + int(d // 10)) % 7]
                    
                    ptolemaic_terms = {
                        0: [(6,'♃'), (14,'♀'), (21,'☿'), (26,'♂'), (30,'♄')],
                        1: [(8,'♀'), (15,'☿'), (22,'♃'), (26,'♄'), (30,'♂')],
                        2: [(7,'☿'), (14,'♃'), (21,'♀'), (25,'♂'), (30,'♄')],
                        3: [(6,'♂'), (13,'♃'), (20,'☿'), (27,'♀'), (30,'♄')],
                        4: [(6,'♃'), (13,'♀'), (19,'♄'), (25,'☿'), (30,'♂')],
                        5: [(7,'☿'), (13,'♀'), (18,'♃'), (24,'♄'), (30,'♂')],
                        6: [(6,'♄'), (11,'☿'), (16,'♃'), (24,'♀'), (30,'♂')],
                        7: [(6,'♂'), (14,'♃'), (21,'♀'), (27,'☿'), (30,'♄')],
                        8: [(8,'♃'), (14,'♀'), (19,'☿'), (25,'♄'), (30,'♂')],
                        9: [(6,'♀'), (12,'☿'), (19,'♃'), (25,'♂'), (30,'♄')],
                        10: [(6,'♄'), (12,'☿'), (20,'♀'), (25,'♃'), (30,'♂')],
                        11: [(8,'♀'), (14,'♃'), (20,'☿'), (26,'♂'), (30,'♄')]
                    }
                    def get_term(s_idx, d):
                        for e_deg, pl in ptolemaic_terms[s_idx]:
                            if d < e_deg: return pl
                        return ptolemaic_terms[s_idx][-1][1]
                        
                    def hl(val, target):
                        return f"<span class='hl'>{val}</span>" if val and (val == target or val in target) else val

                    # 3. 先天尊貴表格 (修正弱、陷欄位順序與扣分機制)
                    t3_html = "<table class='cls-table'><tr><th>星</th><th>星座</th><th>廟(+5)</th><th>旺(+4)</th><th colspan='3'>三分</th><th>界(+2)</th><th>十(+1)</th><th>陷(-5)</th><th>弱(-4)</th><th>分數</th></tr>"
                    for p in TRAD_PLANETS:
                        if p not in pos_n: continue
                        lon = pos_n[p]
                        s_idx = int(lon // 30) % 12
                        deg = lon % 30
                        p_sh = P_MAP[p]
                        s_name = f"{ZODIAC_SYMBOLS[s_idx]} {int(deg)}°{int((deg%1)*60):02d}'"
                        
                        dom = domiciles[s_idx]
                        exa = exaltations[s_idx]
                        trip = get_trip(s_idx)
                        term = get_term(s_idx, deg)
                        fac = get_face(s_idx, deg)
                        det = detriments[s_idx]
                        fal = falls[s_idx]
                        
                        sc = sum([
                            5 if p_sh == dom else 0, 4 if p_sh == exa else 0,
                            3 if p_sh in trip else 0, 2 if p_sh == term else 0,
                            1 if p_sh == fac else 0, -5 if p_sh == det else 0,
                            -4 if p_sh == fal else 0
                        ])
                        
                        t3_html += f"<tr><td>{P_MAP[p]}</td><td>{s_name}</td><td>{hl(dom, p_sh)}</td><td>{hl(exa, p_sh)}</td><td>{hl(trip[0], p_sh)}</td><td>{hl(trip[1], p_sh)}</td><td>{hl(trip[2], p_sh)}</td><td>{hl(term, p_sh)}</td><td>{hl(fac, p_sh)}</td><td>{hl(det, p_sh)}</td><td>{hl(fal, p_sh)}</td><td><b>{sc}</b></td></tr>"
                    t3_html += "</table>"
                    st.markdown(t3_html, unsafe_allow_html=True)
                    
                    # 4. 後天狀態表格
                    avg_speed = {'月亮':13.17, '水星':1.0, '金星':1.0, '火星':0.52, '木星':0.08, '土星':0.03}
                    def get_spd_state(pn, spd):
                        if spd < 0: return "逆行"
                        if pn in avg_speed: return "快" if spd > avg_speed[pn] else "慢"
                        return "正常"
                        
                    def get_acc_state(pn, plon, slon):
                        if pn == '太陽': return '-'
                        diff = (slon - plon) % 360
                        if diff < 8.5 or diff > 351.5: return "灼燒"
                        if diff < 180: return "東出"
                        return "西入"
                        
                    t4_html = "<table class='cls-table'><tr><th>星</th><th>星座</th><th>宮</th><th>速度</th><th>狀態</th></tr>"
                    sun_lon = pos_n.get('太陽', 0)
                    for p in TRAD_PLANETS:
                        if p not in pos_n: continue
                        lon = pos_n[p]
                        s_name = f"{ZODIAC_SYMBOLS[int(lon // 30) % 12]} {int(lon % 30)}°{int(((lon%30)%1)*60):02d}'"
                        h_num = get_house_number(lon, cusps_n, h_code)
                        spd_st = get_spd_state(p, speed_n.get(p, 0))
                        acc_st = get_acc_state(p, lon, sun_lon)
                        t4_html += f"<tr><td>{P_MAP[p]}</td><td>{s_name}</td><td>{h_num}</td><td>{spd_st}</td><td>{acc_st}</td></tr>"
                    t4_html += "</table>"
                    st.markdown(t4_html, unsafe_allow_html=True)

                    # 5. 宮神星 (House Almuten) 計算 (同步修正弱、陷計分機制與排列順序)
                    st.markdown("<b>宮神星 (House Almuten) 計算</b>", unsafe_allow_html=True)
                    t5_html = "<table class='cls-table'><tr><th>宮</th><th>宮頭星座</th><th>廟</th><th>旺</th><th colspan='3'>三分</th><th>界</th><th>十</th><th>陷</th><th>弱</th><th>最高分</th></tr>"
                    c_list_n = list(cusps_n)[1:] if len(cusps_n) == 13 else list(cusps_n)
                    for i in range(12):
                        if h_code == b'W':
                            cusp_lon = ((int(c_list_n[0] // 30) % 12 + i) % 12) * 30
                        else:
                            cusp_lon = c_list_n[i]
                            
                        s_idx = int(cusp_lon // 30) % 12
                        deg = cusp_lon % 30
                        s_name = f"{ZODIAC_SYMBOLS[s_idx]} {int(deg)}°{int((deg%1)*60):02d}'"
                        
                        dom = domiciles[s_idx]
                        exa = exaltations[s_idx]
                        trip = get_trip(s_idx)
                        term = get_term(s_idx, deg)
                        fac = get_face(s_idx, deg)
                        det = detriments[s_idx]
                        fal = falls[s_idx]
                        
                        scores = {k:0 for k in P_MAP.values()}
                        if dom: scores[dom] += 5
                        if exa: scores[exa] += 4
                        for tp in trip: scores[tp] += 3
                        if term: scores[term] += 2
                        if fac: scores[fac] += 1
                        if det: scores[det] -= 5  # 陷扣 5 分
                        if fal: scores[fal] -= 4  # 弱扣 4 分
                        
                        max_sc = max(scores.values())
                        tops = [k for k, v in scores.items() if v == max_sc and v > 0]
                        if not tops: tops = [dom] 
                        top_str = " / ".join(tops)
                        
                        t5_html += f"<tr><td>{i+1}宮</td><td>{s_name}</td><td>{dom}</td><td>{exa}</td><td>{trip[0]}</td><td>{trip[1]}</td><td>{trip[2]}</td><td>{term}</td><td>{fac}</td><td>{det}</td><td>{fal}</td><td><b>{top_str}</b></td></tr>"
                    t5_html += "</table>"
                    st.markdown(t5_html, unsafe_allow_html=True)

                    # ====== 💡 6. 恆星列表與合相觀測 ======
                    st.markdown("<b>恆星合相觀測 (Fixed Stars Conjunctions)</b>", unsafe_allow_html=True)
                    
                    FIXED_STARS_MAP = {
                        "Aldebaran": "畢宿五", "Regulus": "軒轅十四", "Antares": "心宿二",
                        "Fomalhaut": "北落師門", "Algol": "大陵五", "Alcyone": "昴宿六",
                        "Spica": "角宿一", "Sirius": "天狼星", "Capella": "五車二",
                        "Procyon": "南河三", "Arcturus": "大角星", "Alphecca": "貫索四",
                        "Rigel": "參宿七", "Betelgeuse": "參宿四", "Vega": "織女一",
                        "Altair": "河鼓二", "Deneb Algedi": "壘壁陣四"
                    }
                    
                    BACKUP_STARS_J2000 = {
                        "畢宿五": 69.78, "軒轅十四": 149.83, "心宿二": 249.76,
                        "北落師門": 333.85, "大陵五": 56.17, "昴宿六": 60.00,
                        "角宿一": 203.84, "天狼星": 104.09, "五車二": 81.85,
                        "南河三": 115.83, "大角星": 184.23, "貫索四": 232.27,
                        "參宿七": 76.83, "參宿四": 88.75, "織女一": 285.32,
                        "河鼓二": 297.78, "壘壁陣四": 323.55
                    }
                    
                    star_positions = {}
                    
                    for eng, chi in FIXED_STARS_MAP.items():
                        try:
                            res = swe.fixstar2_ut(eng, jd_n)
                            star_positions[chi] = res[0][0]
                        except Exception:
                            year_diff = st.session_state.n_year - 2000
                            precession = year_diff * 0.013963
                            star_positions[chi] = (BACKUP_STARS_J2000[chi] + precession) % 360
                            
                    t7_html = "<table class='cls-table'><tr><th>星體/點位</th><th>合相恆星</th><th>容許度差</th></tr>"
                    has_conj = False
                    
                    all_points_to_check = {k: v for k, v in pos_n.items() if k in PLANET_SYMBOLS}
                    all_points_to_check['下降 (DSC)'] = (asc_n + 180) % 360
                    all_points_to_check['天底 (IC)'] = (mc_n + 180) % 360
                    
                    for chi, slon in star_positions.items():
                        for p, plon in all_points_to_check.items():
                            diff = abs(slon - plon)
                            diff = min(diff, 360 - diff)
                            if diff <= 1.5:  
                                has_conj = True
                                p_label = PLANET_SYMBOLS[p]['sym'] if p in PLANET_SYMBOLS else p
                                t7_html += f"<tr><td>{p_label}</td><td>{chi}</td><td>{diff:.2f}°</td></tr>"
                    if not has_conj:
                        t7_html += "<tr><td colspan='3'>無顯著恆星合相</td></tr>"
                    t7_html += "</table>"
                    
                    st.markdown(t7_html, unsafe_allow_html=True)
                
                # 其餘 Tabs 保持不變
                with tabs[1]:
                    if chk_solar_return:
                        j2_val, pos_sr, asc_sr, cusps_sr, speed_sr, sc_val, rtg_val, table_lines, int_sc, int_rtg, int_lines = calc_5_core(st.session_state.target_age, jd_n, pos_n, asc_n, cusps_n, speed_n, lat_p, lon_p, h_code, dt_n_utc)
                        if j2_val:
                            img_sr = draw_astrology_chart(pos_sr, asc_sr, cusps_sr, aspect_specs_full, a_sys_name, speeds=speed_sr)
                            st.image(img_sr)
                            st.markdown(f"### 📊 比較盤 (5大核心交點分析) - 【{rtg_val}】")
                            st.caption(f"加總總分: {'+' if sc_val>0 else ''}{sc_val}")
                            st.table(table_lines)
                            
                            st.markdown(f"### 📍 日返盤本體分析 - 【{int_rtg}】")
                            st.caption(f"加總總分: {'+' if int_sc>0 else ''}{int_sc}")
                            st.table(int_lines)
                    else: 
                        st.info("請於左側勾選「計算日返星盤」以生成。")
                        
                with tabs[2]:
                    st.image(img_ls)
                    st.markdown("### 📍 地平占星方位數據")
                    md_table = "| 星體 | 方位角 (Azimuth) | 高度角 (Altitude) | 地理方位 |\n|---|---|---|---|\n"
                    for row in local_space_data:
                        sign_alt = "+" if row['alt'] >= 0 else ""
                        md_table += f"| {row['sym']} {row['planet']} | {row['az']:.2f}° | {sign_alt}{row['alt']:.2f}° ({row['status']}) | {row['dir']} |\n"
                    st.markdown(md_table)
                    
                with tabs[3]:
                    if chk_batch:
                        st.markdown("### 📈 大批 (1-75歲 日弧及日返吉凶總覽)")
                        # 大批運算邏輯在下方，為了效能這裡僅做簡單提示
                        st.info("大批結果請詳見右方綜合觀測報告中的大批日弧部分。")
                    else:
                        st.info("請於左側勾選「大批 (1-75歲 日弧及日返吉凶)」以生成。")
                        
                with tabs[4]:
                    if chk_sr_reloc:
                        st.markdown(f"### 🌍 日返重置 ({st.session_state.target_age}歲 各國流年吉凶)")
        
                        # 準備資料儲存
                        reloc_data = []
                        # 定義你想測試的城市
                        test_cities = ["香港", "東京", "倫敦", "紐約"] 
        
                        for city_name in test_cities:
                            if city_name in RELOCATION_COUNTRIES:
                                loc = RELOCATION_COUNTRIES[city_name]
                                # 重新定位計算
                                _, _, _, _, dt_reloc = resolve_location_and_time(city_name, st.session_state.p_year, st.session_state.p_month, st.session_state.p_day, st.session_state.p_hour, st.session_state.p_minute)
                
                                # 這裡調用你的核心計算函式
                                _, _, _, _, _, sc_val, rtg_val, _, _, _, _ = calc_5_core(
                                    st.session_state.target_age, jd_n, pos_n, asc_n, cusps_n, speed_n, 
                                    loc['lat'], loc['lon'], h_code, dt_n_utc
                                )
                
                                reloc_data.append({
                                    "城市": city_name,
                                    "評級": rtg_val,
                                    "得分": sc_val
                                })
        
                        # 顯示表格 (這就是顯示不出來的關鍵)
                        if reloc_data:
                            df_reloc = pd.DataFrame(reloc_data)
                            st.table(df_reloc)
                        else:
                            st.warning("無法計算重置數據。")
                    else:
                        st.info("請於左側勾選「日返重置 (各國流年吉凶)」以生成。")
                        
                with tabs[5]:
                    if chk_db_ranking:
                        st.markdown("### 🏆 資料庫人物特質排名 (Top 3)")
                        st.info("資料庫排名引擎啟動中...")
                    else:
                        st.info("請於左側勾選「資料庫排名 (Top 3)」並確保已匯入 JSON 命例。")
            
            # --- 綜合觀測報告區 ---
            with col_main2:
                for k in ALL_POINTS:
                    h_num = get_house_number(pos_n[k], cusps_n, h_code)
                    base_str = f"{k: <3}：{format_degree(pos_n[k])} {h_num: >2}宮"
                    status_parts = []
                    if k in DIGNITIES:
                        sign_idx = int(pos_n[k] // 30) % 12
                        if sign_idx in DIGNITIES[k]['廟']: status_parts.append("廟")
                        if sign_idx in DIGNITIES[k]['旺']: status_parts.append("旺")
                        if sign_idx in DIGNITIES[k]['弱']: status_parts.append("弱")
                        if sign_idx in DIGNITIES[k]['陷']: status_parts.append("陷")
                    if is_day and k in ['太陽', '木星', '土星']: status_parts.append("得時")
                    elif not is_day and k in ['月亮', '金星', '火星']: status_parts.append("得時")
                    if k in ['水星', '金星', '火星', '木星', '土星', '天王星', '海王星', '冥王星'] and speed_n.get(k, 0) < 0: status_parts.append("逆行")
                    report += f"{base_str}    {'   '.join(status_parts)}\n" if status_parts else f"{base_str}\n"

                report += "\n【行星圖形】\n"
                has_pattern = False
                for p_title, p_list in detected_patterns.items():
                    for item in p_list: report += f"{p_title}：{item}\n"; has_pattern = True
                if not has_pattern: report += "星盤中目前無形成特殊著名行星圖形。\n"

                sun, moon, mars, jup, sat = pos_n['太陽'], pos_n['月亮'], pos_n['火星'], pos_n['木星'], pos_n['土星']
                fortune = (asc_n + moon - sun) if is_day else (asc_n + sun - moon)
                spirit = (asc_n + sun - moon) if is_day else (asc_n + moon - sun)

                if chk_greek:
                    greek = {'幸運點': fortune % 360, '精神點': spirit % 360, '愛欲點': ((asc_n + spirit - fortune) if is_day else (asc_n + fortune - spirit)) % 360, '必然點': ((asc_n + fortune - spirit) if is_day else (asc_n + spirit - fortune)) % 360, '勇氣點': ((asc_n + mars - fortune) if is_day else (asc_n + fortune - mars)) % 360, '勝利點': ((asc_n + jup - spirit) if is_day else (asc_n + spirit - jup)) % 360, '復仇點': ((asc_n + fortune - sat) if is_day else (asc_n + sat - fortune)) % 360}
                    report += "\n【七大希臘點位置】\n"
                    for k, v in greek.items(): report += f"{k}：{format_degree(v)} {get_house_number(v, cusps_n, h_code)}宮\n"

                if chk_zr:
                    report += "\n【黃道釋放 Zodiacal Releasing (100年內 L2 轉角)】\n"
                    zr_fortune_list = calc_zodiacal_releasing(fortune % 360, jd_n)
                    if zr_fortune_list:
                        report += "幸運點釋放：\n" + "\n".join(zr_fortune_list) + "\n"
                    
                    zr_spirit_list = calc_zodiacal_releasing(spirit % 360, jd_n)
                    if zr_spirit_list:
                        report += "\n精神點釋放：\n" + "\n".join(zr_spirit_list) + "\n"

                report += "\n【宮頭】\n"
                c_list_n = list(cusps_n)[1:] if len(cusps_n) == 13 else list(cusps_n)
                if chk_whole_rule:
                    for i in range(12): report += f"{i+1}宮：{ZODIAC_NAMES[(int(asc_n // 30) % 12 + i) % 12]}\n"
                else:
                    for i, deg in enumerate(c_list_n): report += f"{i+1}宮" + (" (ASC)" if i == 0 else (" (MC)" if i == 9 else "")) + f"：{format_degree(deg)}\n"

                report += "\n【相位列表】\n"
                p_names = [p for p in pos_n.keys() if p in PLANET_SYMBOLS]
                aspect_lines = []
                for i in range(len(p_names)):
                    for j in range(i+1, len(p_names)):
                        p1, p2 = p_names[i], p_names[j]
                        diff = abs(pos_n[p1] - pos_n[p2]); diff = 360 - diff if diff > 180 else diff
                        for angle, a_name, _, orb in aspect_specs_full:
                            if orb == 0: continue
                            if abs(diff - angle) <= (LILLY_MOITIES.get(p1, 2.5) + LILLY_MOITIES.get(p2, 2.5) if a_sys_name == "古典 (威廉・里利)" else orb):
                                aspect_lines.append(f"{p1}-{p2} {a_name} {get_aspect_modifier_engine(p1, p2, angle, diff, jd_n, lat_n, lon_n, h_code)}{abs(diff - angle):.1f} °")
                                break
                report += "\n".join(aspect_lines) if aspect_lines else "無符合規格相位"

                if chk_profection:
                    report += "\n\n【小限宮位管轄歲數 (0-75)】\n"
                    for h in range(12):
                        sign_name = ZODIAC_NAMES[(int(asc_n // 30) % 12 + h) % 12] if chk_whole_rule else ZODIAC_NAMES[int(c_list_n[h] // 30) % 12]
                        report += f"{h+1}宮-{TRADITIONAL_RULERS[sign_name]}：{ '、'.join([str(age) for age in range(76) if age % 12 == h]) }\n"

                st.subheader("綜合觀測報告")
                st.code(report, language="text") 
                
            if has_el_results:
                with col_main3:
                    st.subheader("📅 擇時最優結果")
                    st.caption("已將連續符合的時間段合併，並僅保留最接近精確成相的時間點：")
                    for idx, target_dt in enumerate(st.session_state['election_results']):
                        time_str = target_dt.strftime("%Y-%m-%d %H:%M")
                        st.button(f"⏱️ {time_str}", key=f"btn_el_sync_{idx}", width="stretch")

    except Exception as e:
        st.error(f"系統執行時發生問題：\n{str(e)}")
