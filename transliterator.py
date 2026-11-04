"""Arabic to Algerian French-letters (Arabizi) transliterator."""
import re

AR_TO_FR_WORDS = {
    "واش": "wach",
    "شنو": "chenhou",
    "علاش": "3lah",
    "كيفاش": "kifech",
    "وقتاش": "waqtech",
    "شكون": "chkoune",
    "وين": "wine",
    "دروك": "derwek",
    "دوكا": "douka",
    "ضرك": "derk",
    "لازم": "lazem",
    "ندير": "ndir",
    "نديرلها": "ndirlha",
    "نديرلو": "ndirlou",
    "مع": "m3a",
    "بيبي": "bebe",
    "الجديد": "jdid",
    "جديد": "jdid",
    "وليدي": "wlidi",
    "بنتي": "benti",
    "ولدي": "weldi",
    "طفل": "tefel",
    "طفلة": "tofla",
    "طبيب": "tbib",
    "طبيبة": "tbiba",
    "دكتور": "docteur",
    "دكتورة": "docteur",
    "سخانة": "skhana",
    "حمى": "homa",
    "دواء": "dwa",
    "دوا": "dwa",
    "لقاح": "vaccin",
    "تلقيح": "talqih",
    "تلقيحات": "talqihat",
    "كرش": "kerch",
    "كرشو": "kerchou",
    "وجع": "wja3",
    "سعلة": "so3la",
    "صدر": "sder",
    "حليب": "hlib",
    "رضاعة": "reda3a",
    "طبيعية": "tabi3iya",
    "صناعية": "sna3iya",
    "حماية": "protection",
    "مدنية": "civile",
    "سبيطار": "sbitar",
    "مستشفى": "hopital",
    "استعجالات": "urgences",
    "خطر": "danger",
    "ماكاش": "makach",
    "كاين": "kayen",
    "كاينين": "kaynin",
    "بزاف": "bezzef",
    "شوية": "chwiya",
    "مليح": "mlih",
    "مليحة": "mliha",
    "ماشي": "machi",
    "ولا": "wella",
    "باش": "bach",
    "على": "3la",
    "في": "fi",
    "من": "men",
    "عندو": "3andou",
    "عندها": "3andha",
    "عندي": "3andi",
    "هيا": "hiya",
    "هو": "houwa",
    "أنا": "ana",
    "نزيف": "nazif",
    "دوخة": "dawkha",
    "تقيؤ": "radan",
    "إسهال": "is-hal",
    "رعشة": "ra3cha",
}

CHAR_MAP = {
    'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'a', 'ء': "'", 'ى': 'a',
    'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'ch',
    'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'dh', 'ع': '3', 'غ': 'gh',
    'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h', 'و': 'ou', 'ي': 'i', 'ئ': 'y', 'ؤ': 'ou', 'ة': 'a',
    '؟': '?', '،': ',', '؛': ';'
}

def arabic_to_darja_latin(text: str) -> str:
    """Convert an Arabic script Darja question into clean French-letters Darja."""
    if not text:
        return ""
    words = text.split()
    converted_words = []
    for w in words:
        clean_w = re.sub(r'[^\w\s]', '', w)
        punct = "".join(c for c in w if c in "?!.,:;؟،")
        if clean_w in AR_TO_FR_WORDS:
            lat = AR_TO_FR_WORDS[clean_w]
            if punct:
                lat += '?' if '؟' in punct else punct
            converted_words.append(lat)
        else:
            # Character-by-character mapping
            chars = []
            for c in w:
                chars.append(CHAR_MAP.get(c, c))
            res = "".join(chars)
            # Polish phonetic transitions
            res = re.sub(r'ou([aeiou])', r'w\1', res)
            res = re.sub(r'i([aeou])', r'y\1', res)
            converted_words.append(res)
    
    result = " ".join(converted_words)
    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]
    return result

if __name__ == "__main__":
    test1 = "هشام، واش لازم ندير مع بيبي الجديد؟"
    test2 = "شنو الدواء اللي لازم يتعطاه بنتي؟"
    test3 = "وليدي كمل شهرين، واش من لقاح يدير دروك؟"
    print(test1, "->", arabic_to_darja_latin(test1))
    print(test2, "->", arabic_to_darja_latin(test2))
    print(test3, "->", arabic_to_darja_latin(test3))

