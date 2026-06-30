import streamlit as st
import datetime
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

# ================= 0. Session State 狀態管理 =================
now = datetime.datetime.now()

exclusion_keys = [
    "1宮主陷弱", "月亮與火土凶相", "月亮空亡", "火星或土星入1宮", 
    "6/8/12宮主入1宮", "火土與1宮主凶相", "6/8/12宮主與1宮主凶相", 
    "火星或土星合相上升", "6/8/12宮主合相上升", "土星入角宮", "土星合/沖四角"
]

if 'n_year' not in st.session_state:
    st.session_state.update({
        'n_year': 1990, 'n_month': 1, 'n_day': 1, 'n_hour': 12, 'n_minute': 0, 'n_loc': "Manchester", 'name_input': "Vincent",
        'p_year': now.year, 'p_month': now.month, 'p_day': now.day, 'p_hour': now.hour, 'p_minute': now.minute, 'p_loc': "Manchester",
        'target_age': now.year - 1990,
        'election_conditions': [],
        'calc_triggered': False,
        'election_results': [],
        'el_loc_input': "Manchester"
    })
    for k in exclusion_keys:
        st.session_state[k] = True

def toggle_all_exclusions():
    any_checked = any(st.session_state.get(k, True) for k in exclusion_keys)
    target_state = not any_checked
    for k in exclusion_keys:
        st.session_state[k] = target_state

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
    except:
        st.session_state.n_loc = "Hong Kong"
    st.session_state.calc_triggered = False

def update_year_from_age():
    st.session_state.p_year = max(1, st.session_state.n_year + st.session_state.target_age)

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
        '冥王星': swe.PLUTO, '北交點': swe.TRUE_NODE
    }
    positions = {}
    speeds = {}
    for name, planet_id in planets_map.items():
        pos, _ = swe.calc_ut(jd, planet_id)
        positions[name] = pos[0] 
        speeds[name] = pos[3] 
    cusps, ascmc = swe.houses(jd, lat, lon, house_system)
    positions['上升'] = ascmc[0]
    positions['中天'] = ascmc[1]
    return positions, ascmc[0], cusps, ascmc[1], speeds

def get_aspect_modifier_engine(p1, p2, target_angle, current_diff, jd, lat, lon, house_sys):
    positions_future, _, _, _, _ = calculate_chart_engine(jd + 0.005, lat, lon, house_sys)
    if p1 in positions_future and p2 in positions_future:
        f_diff = abs(positions_future[p1] - positions_future[p2])
        if f_diff > 180: f_diff = 360 - f_diff
        return "+" if abs(f_diff - target_angle) < abs(current_diff - target_angle) else "-"
    return ""

def calc_zodiacal_releasing(lot_lon, birth_jd, target_jd):
    start_sign = int(lot_lon // 30) % 12
    total_days = target_jd - birth_jd
    if total_days < 0: return None, None, False
    l1_sign = start_sign
    rem_days = total_days
    while True:
        period_days = ZR_PERIODS[l1_sign] * 360
        if rem_days >= period_days:
            rem_days -= period_days
            l1_sign = (l1_sign + 1) % 12
        else: break
    l2_sign = l1_sign
    months = 0
    is_lb = False
    while True:
        sub_period_days = ZR_PERIODS[l2_sign] * 30
        if rem_days >= sub_period_days:
            rem_days -= sub_period_days
            months += 1
            if months == 12: 
                l2_sign = (l2_sign + 6) % 12
                is_lb = True
            else:
                l2_sign = (l2_sign + 1) % 12
        else: break
    return l1_sign, l2_sign, is_lb

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
            if el1 == el2 == el3:
                patterns["大三角"].append(f"{el1}元素大三角：{p1} - {p2} - {p3}")
                
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
    
    try:
        local_dt = pytz.timezone(tz_str).localize(datetime.datetime(y, m, d, h, minute))
    except ValueError as e:
        raise ValueError(f"輸入的日期無效：{str(e)}")
        
    utc_dt = local_dt.astimezone(pytz.utc)
    hour_decimal = utc_dt.hour + (utc_dt.minute / 60.0)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
    info = f"城市: {location.address}\n時區: {tz_str}\n時間: {local_dt.strftime('%Y-%m-%d %H:%M')}\n"
    return jd, lat, lon, info, utc_dt

# ================= 3. 擇時引擎功能 =================
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
    pos, asc, cusps, mc, speed = calculate_chart_engine(jd, lat, lon, h_code)
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

# ================= 5. Streamlit UI 介面 =================
st.sidebar.header("本命盤基本資訊")
name = st.sidebar.text_input("姓名", key="name_input")
gender = st.sidebar.selectbox("性別", ["男", "女"])

col1, col2, col3 = st.sidebar.columns(3)
col1.number_input("年", key="n_year", min_value=1, max_value=9999, step=1)
col2.number_input("月", key="n_month", min_value=1, max_value=12)
col3.number_input("日", key="n_day", min_value=1, max_value=31)

col4, col5 = st.sidebar.columns(2)
col4.number_input("時", key="n_hour", min_value=0, max_value=23)
col5.number_input("分", key="n_minute", min_value=0, max_value=59)
st.sidebar.text_input("出生城市", key="n_loc")

btn_col1, btn_col2 = st.sidebar.columns(2)
btn_col1.button("🕒 當下時間", on_click=set_current_time, width="stretch")
btn_col2.button("📍 當下地點", on_click=set_current_loc, width="stretch")

st.sidebar.divider()

with st.sidebar.expander("推運 / 行運 / 日返設定", expanded=False):
    st.number_input("推運 年", key="p_year", min_value=1, max_value=9999, step=1, on_change=update_age_from_year)
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
    
    start_date = st.date_input("開始日期", datetime.date.today())
    end_date = st.date_input("結束日期", datetime.date.today() + datetime.timedelta(days=7))
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

    st.markdown("---")
    st.markdown("**剔選不包含之凶相狀況 (複選)**")
    
    st.button("🔄 全選 / 全不選", on_click=toggle_all_exclusions, use_container_width=True)
    exclusions_map = {k: st.checkbox(k, key=k) for k in exclusion_keys}

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
chk_greek = st.sidebar.checkbox("七大希臘點")
chk_midpoint = st.sidebar.checkbox("顯示中點")
chk_whole_rule = st.sidebar.checkbox("宮主星整宮制")
chk_solar_arc = st.sidebar.checkbox("真實日弧相位")
chk_sa_midpoint = st.sidebar.checkbox("日弧中點")    
chk_profection = st.sidebar.checkbox("顯示小限歲數")
chk_zr = st.sidebar.checkbox("黃道釋放")             
chk_solar_return = st.sidebar.checkbox("計算日返星盤")
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
            
            pos_n, asc_n, cusps_n, mc_n, speed_n = calculate_chart_engine(jd_n, lat_n, lon_n, h_code)
            img_n = draw_astrology_chart(pos_n, asc_n, cusps_n, aspect_specs_full, a_sys_name, speeds=speed_n)
            
            is_day = 7 <= get_house_number(pos_n['太陽'], cusps_n, h_code) <= 12
            elements_score = {'火': 0, '土': 0, '風': 0, '水': 0}
            modes_score = {'開創': 0, '固定': 0, '變動': 0}
            for p in WEIGHT_POINTS:
                if p in pos_n:
                    z_idx = int(pos_n[p] // 30) % 12
                    elements_score[ZODIAC_ELEMENTS[z_idx]] += p_weights.get(p, 1)
                    modes_score[ZODIAC_MODES[z_idx]] += p_weights.get(p, 1)
            
            detected_patterns = find_astrology_patterns(pos_n)
            report = f"== 命盤基本觀測 ==\n持有人：{st.session_state.name_input} ({gender})\n{meta_n}\n"
            
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
            report += "【星體位置】\n"
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
                report += "\n【黃道釋放 Zodiacal Releasing】\n"
                f_l1, f_l2, f_lb = calc_zodiacal_releasing(fortune % 360, jd_n, jd_p)
                if f_l1 is not None: report += f"幸運點釋放：L1 {ZODIAC_NAMES[f_l1]} -> L2 {ZODIAC_NAMES[f_l2]}{' (解縛 LB)' if f_lb else ''}\n"
                s_l1, s_l2, s_lb = calc_zodiacal_releasing(spirit % 360, jd_n, jd_p)
                if s_l1 is not None: report += f"精神點釋放：L1 {ZODIAC_NAMES[s_l1]} -> L2 {ZODIAC_NAMES[s_l2]}{' (解縛 LB)' if s_lb else ''}\n"

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

            if chk_midpoint:
                report += "\n\n【行星中點】\n"
                mid_lines = []
                for i in range(len(ALL_POINTS)):
                    for j in range(i+1, len(ALL_POINTS)):
                        bp1, bp2 = ALL_POINTS[i], ALL_POINTS[j]; m_lon = calc_midpoint(pos_n[bp1], pos_n[bp2])
                        for p in ALL_POINTS:
                            diff = (pos_n[p] - m_lon) % 360
                            for angle in [0, 90, 180, 270]:
                                dev = diff - angle; dev = dev - 360 if dev > 180 else (dev + 360 if dev < -180 else dev)
                                if abs(dev) <= 1.0: mid_lines.append(f"{p} ＝ {bp1}/{bp2} {'+' if dev>=0 else '-'}{abs(dev):.1f}°"); break
                report += "\n".join(mid_lines) if mid_lines else "無符合容許度的中點相位"

            if chk_profection:
                report += "\n\n【小限宮位管轄歲數 (0-75)】\n"
                for h in range(12):
                    sign_name = ZODIAC_NAMES[(int(asc_n // 30) % 12 + h) % 12] if chk_whole_rule else ZODIAC_NAMES[int(c_list_n[h] // 30) % 12]
                    report += f"{h+1}宮-{TRADITIONAL_RULERS[sign_name]}：{ '、'.join([str(age) for age in range(76) if age % 12 == h]) }\n"

            solar_arc = (swe.calc_ut(jd_n + ((dt_p_utc - dt_n_utc).days / 365.242199), swe.SUN)[0][0] - pos_n['太陽']) % 360
            if chk_solar_arc:
                report += "\n\n【日弧相位】\n"
                sa_lines = []
                for p1 in ALL_POINTS:
                    sa_lon = (pos_n[p1] + solar_arc) % 360
                    for p2 in ALL_POINTS:
                        diff = abs(sa_lon - pos_n[p2]); diff = 360 - diff if diff > 180 else diff
                        for angle, a_name in [(0, "合相"), (45, "半四分"), (90, "四分"), (135, "補八分"), (180, "對相")]:
                            if abs(diff - angle) <= 1.0: sa_lines.append(f"［弧］{p1} - ［命］{p2} {a_name} {'+' if abs((sa_lon + 0.005) % 360 - pos_n[p2]) < diff else '-'}{abs(diff - angle):.1f}°"); break
                report += "\n".join(sa_lines) if sa_lines else "無符合規格之日弧相位"

            if chk_transit:
                pos_t, _, _, _, _ = calculate_chart_engine(jd_p, lat_p, lon_p, h_code)
                report += f"\n\n【行運觀測資訊】\n目標城市：{st.session_state.p_loc}\n"
                for k in TRANSIT_POINTS: report += f"[運]{k} ：{format_degree(pos_t[k])} [命] {get_house_number(pos_t[k], cusps_n, h_code)}宮\n"
                report += "\n【行運星與本命星相位】\n"
                t_lines = []
                for p1 in TRANSIT_POINTS:
                    for p2 in ALL_POINTS:
                        diff = abs(pos_t[p1] - pos_n[p2]); diff = 360 - diff if diff > 180 else diff
                        for angle, a_name, _, orb in aspect_specs_full:
                            if orb == 0: continue
                            if abs(diff - angle) <= (LILLY_MOITIES.get(p1, 2.5) + LILLY_MOITIES.get(p2, 2.5) if a_sys_name == "古典 (威廉・里利)" else 3.0):
                                t_lines.append(f"[運]{p1} {a_name} [命]{p2} {'+' if abs(calculate_chart_engine(jd_p + 0.005, lat_p, lon_p, h_code)[0][p1] - pos_n[p2]) < diff else '-'}{abs(diff - angle):.1f}°")
                report += "\n".join(t_lines) if t_lines else "無符合交叉行運相位"

            img_sr = None
            if chk_solar_return:
                try:
                    jd_approx = swe.julday(st.session_state.p_year, dt_n_utc.month, dt_n_utc.day, 12.0)
                    j1, j2 = jd_approx - 2, jd_approx + 2
                    f1, f2 = ((swe.calc_ut(j1, swe.SUN)[0][0] - pos_n['太陽'] + 180) % 360 - 180), ((swe.calc_ut(j2, swe.SUN)[0][0] - pos_n['太陽'] + 180) % 360 - 180)
                    for _ in range(20):
                        if abs(f2 - f1) < 1e-11: break
                        j_next = j2 - f2 * (j2 - j1) / (f2 - f1)
                        
                        # 💡 [防護修正] 強制防發散邊界，不允許演算法將日子跳躍超過 jd_approx 的正負 10 天
                        if abs(j_next - jd_approx) > 10:
                            j_next = jd_approx + 0.1 # 重設並打破無效迴圈
                            
                        j1, j2, f1 = j2, j_next, f2
                        f2 = ((swe.calc_ut(j2, swe.SUN)[0][0] - pos_n['太陽'] + 180) % 360 - 180)
                        
                    pos_sr, asc_sr, cusps_sr, mc_sr, speed_sr = calculate_chart_engine(j2, lat_p, lon_p, h_code)
                    img_sr = draw_astrology_chart(pos_sr, asc_sr, cusps_sr, aspect_specs_full, a_sys_name, speeds=speed_sr)
                    
                    days_offset = j2 - 2451545.0
                    sr_local_dt = (datetime.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.utc) + datetime.timedelta(days=days_offset)).astimezone(pytz.timezone(TimezoneFinder().timezone_at(lng=lon_p, lat=lat_p) or "UTC"))
                    report += f"\n\n【日返報告】\n返照精確時間：{sr_local_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    for k in ALL_POINTS: report += f"日返{k}：{format_degree(pos_sr[k])} {get_house_number(pos_sr[k], cusps_sr, h_code)}宮\n"
                except Exception as e:
                    report += f"\n\n【日返報告】\n無法計算此年份之日返星盤 ({str(e)})\n"

            # ================= UI 佈局顯示 =================
            has_el_results = chk_election and 'election_results' in st.session_state and len(st.session_state['election_results']) > 0
            
            if has_el_results: col_main1, col_main2, col_main3 = st.columns([1.2, 1, 0.8])
            else: col_main1, col_main2 = st.columns([1, 1])

            with col_main1:
                st.subheader("圖表視覺化")
                tab1, tab2 = st.tabs(["本命星盤", "日返星盤"])
                with tab1: st.image(img_n, use_container_width=True)
                with tab2:
                    if img_sr: st.image(img_sr, use_container_width=True)
                    else: st.info("請於左側勾選「計算日返星盤」以生成。")
            
            with col_main2:
                st.subheader("綜合觀測報告")
                st.code(report, language="text") 
                
            if has_el_results:
                with col_main3:
                    st.subheader("📅 擇時最優結果")
                    st.caption("已將連續符合的時間段合併，並僅保留最接近精確成相的時間點：")
                    for idx, target_dt in enumerate(st.session_state['election_results']):
                        time_str = target_dt.strftime("%Y-%m-%d %H:%M")
                        st.button(f"⏱️ {time_str}", key=f"btn_el_sync_{idx}", use_container_width=True)

    except Exception as e:
        st.error(f"系統執行時發生問題：\n{str(e)}")