# -*- coding: utf-8 -*-
"""Trade vernacular -> HomeRun catalog English.

This is the domain asset. Hindi/Kannada/Hinglish terms that building-trade
customers actually say, mapped to the words the Shopify catalog uses.
Used by the rule-based fallback, and injected into the LLM prompt as hints.
"""

VERNACULAR = {
    # --- Hindi / Hinglish: materials ---
    "sunmica": "laminate", "sunmika": "laminate", "suntop": "laminate",
    "plywood": "plywood", "ply": "plywood", "board": "board",
    # romanisation varies wildly - customers type/say all of these
    "lakdi": "wood", "lakadi": "wood", "lakri": "wood", "lakari": "wood",
    "lakdee": "wood", "लकड़ी": "wood", "ಮರದ": "wood",
    "seement": "cement", "siment": "cement", "cement": "cement",
    "sariya": "TMT steel bar", "saria": "TMT steel bar", "sarya": "TMT steel bar",
    "gitti": "aggregate", "ret": "sand", "baalu": "sand",
    "safedi": "wall putty", "putty": "wall putty",
    "rang": "paint", "ranga": "paint", "paint": "paint", "distemper": "emulsion",
    "chuna": "white cement",

    # --- Hindi: hardware / fittings ---
    "kabza": "hinge", "kabja": "hinge", "kabaza": "hinge",
    "chaukhat": "door frame", "chowkhat": "door frame",
    "darwaza": "door", "khidki": "window",
    "taala": "lock", "tala": "lock", "chitkani": "latch",
    "handle": "handle",
    "putty patti": "putty blade", "putty wali patti": "putty blade",
    "patti": "beading strip",
    "pech": "screw", "screw": "screw", "keel": "nail", "kili": "nail",
    "khila": "nail",
    "channel": "drawer channel", "chaneel": "drawer channel",

    # --- Hindi: plumbing ---
    "nal": "tap", "nalka": "tap", "tuti": "tap", "tonti": "tap",
    "tanki": "water tank", "paani ki tanki": "water tank",
    "paip": "pipe", "pipe": "pipe", "nali": "drain pipe",
    "geyser": "water heater", "gyser": "water heater",
    "paikhana": "WC toilet", "latrine": "WC toilet", "commode": "WC",
    "fuhara": "shower", "jhirna": "shower",
    "basin": "wash basin", "washbasin": "wash basin",

    # --- Networking / data (customers never say "CAT6") ---
    "internet": "LAN cable", "इंटरनेट": "LAN cable", "ಇಂಟರ್ನೆಟ್": "LAN cable",
    "lan": "LAN cable", "ethernet": "LAN cable", "broadband": "LAN cable",
    "netwrk": "LAN cable", "network cable": "LAN cable",
    "wifi": "wifi router", "wi-fi": "wifi router", "router": "wifi router",
    "camera ka wire": "CCTV coaxial cable", "cctv wire": "CCTV coaxial cable",

    # --- Hindi: electrical ---
    "taar": "wire", "tar": "wire", "bijli": "electrical",
    "batti": "light", "bulb": "LED bulb", "tube": "tube light",
    "pankha": "fan", "switchboard": "modular switch plate",
    "holder": "lamp holder", "meter": "meter",

    # --- Hindi: tools ---
    "hathoda": "hammer", "hathauda": "hammer",
    "pana": "spanner", "panaa": "spanner", "plas": "pliers", "plaas": "pliers",
    "pechkas": "screwdriver", "pechkash": "screwdriver",
    "drill machine": "drill", "kattar": "cutter", "aari": "saw",
    "randa": "planer", "basula": "chisel",
    # Trade name for a plasterer's float. The catalogue spells it "Gurmala"
    # (Haks Plaster Trowel Gurmala); ASR also hears "gurumala", "gurmalla".
    "gurmala": "plaster trowel", "gurumala": "plaster trowel",
    "gurmalla": "plaster trowel", "ಗುರ್ಮಾಲಾ": "plaster trowel",
    "kaincha": "masonry trowel", "kaicha": "masonry trowel",

    # --- Hindi: adhesives / chemicals ---
    "gond": "adhesive", "chipkane wala": "adhesive", "fevicol": "Fevicol adhesive",
    "mseal": "M-Seal", "m seal": "M-Seal", "silicone": "silicone sealant",
    "waterproofing": "waterproofing", "seelan": "damp waterproofing",

    # --- Hindi: surfaces ---
    "deewar": "wall", "diwar": "wall", "chhat": "ceiling", "farsh": "floor",
    "tile": "tiles", "marble": "marble", "granite": "granite",

    # --- Kannada ---
    "ಬಣ್ಣ": "paint", "banna": "paint",
    "ಕೊಳಾಯಿ": "tap", "kolayi": "tap", "nalli": "tap",
    "ನೀರಿನ ಟ್ಯಾಂಕ್": "water tank", "neerina tank": "water tank",
    "ಮರ": "wood", "mara": "wood",
    "ಕಬ್ಬಿಣ": "steel", "kabbina": "steel",
    "ಬಾಗಿಲು": "door", "bagilu": "door",
    "ಕಿಟಕಿ": "window", "kitaki": "window",
    "ತಂತಿ": "wire", "tanti": "wire",
    "ಸಿಮೆಂಟ್": "cement", "ಗೋಡೆ": "wall", "gode": "wall",
    "ನೆಲ": "floor", "nela": "floor", "ಬಲ್ಬ್": "LED bulb",
    "ಸ್ವಿಚ್": "switch", "ಬೀಗ": "lock", "beega": "lock",
    "ಕೊಳವೆ": "pipe", "kolave": "pipe", "ಸುತ್ತಿಗೆ": "hammer",

    # --- Kannada / Hindi qualifiers (colour, placement) ---
    "ಬಿಳಿ": "white", "bili": "white", "safed": "white", "सफेद": "white",
    "ಕಪ್ಪು": "black", "kappu": "black",
    "kala": "black", "kale": "black", "kali": "black", "काला": "black", "काले": "black",
    "lal": "red", "laal": "red", "लाल": "red", "ಕೆಂಪು": "red",
    "neela": "blue", "neele": "blue", "नीला": "blue", "ನೀಲಿ": "blue",
    "hara": "green", "hare": "green", "हरा": "green", "ಹಸಿರು": "green",
    "bhura": "brown", "भूरा": "brown", "slety": "grey", "स्लेटी": "grey",
    "ಹೊರಗೋಡೆ": "exterior wall", "ಹೊರ": "exterior", "hora": "exterior",
    "bahar": "exterior", "बाहर": "exterior",
    "ಒಳಗೋಡೆ": "interior wall", "ಒಳ": "interior", "andar": "interior", "अंदर": "interior",
    "ಅಡುಗೆಮನೆ": "kitchen", "adugemane": "kitchen", "rasoi": "kitchen", "रसोई": "kitchen",
    "ಸ್ನಾನದ ಕೋಣೆ": "bathroom", "ಸ್ನಾನ": "bath", "bathroom": "bathroom",
    "ಚಾವಣಿ": "ceiling", "ಮಹಡಿ": "floor",
    "ಸಿಂಕ್": "sink", "ಟೈಲ್ಸ್": "tiles", "ಪೈಪ್": "pipe", "ಬಾಗಿಲಿನ": "door",
    "ನೆಲಹಾಸು": "flooring", "nelahasu": "flooring", "ನೆಲಗಟ್ಟು": "flooring",
    "ಕಟ್ಟಡ": "building", "kattada": "building", "ಪದಾರ್ಥ": "material",
    "ಸಾಮಾನು": "material", "samaan": "material", "saman": "material",
}

NUMBERS = {
    "ek": 1, "एक": 1, "ondu": 1, "ಒಂದು": 1, "one": 1,
    "do": 2, "दो": 2, "eradu": 2, "ಎರಡು": 2, "two": 2,
    "teen": 3, "तीन": 3, "mooru": 3, "ಮೂರು": 3, "three": 3,
    "char": 4, "चार": 4, "naalku": 4, "ನಾಲ್ಕು": 4, "four": 4,
    "paanch": 5, "panch": 5, "पांच": 5, "aidu": 5, "ಐದು": 5, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "das": 10, "दस": 10, "hattu": 10, "ಹತ್ತು": 10, "ten": 10,
    "bees": 20, "इक्कीस": 21, "ipphattu": 20,
}

UNITS = {
    "kilo": "kg", "kg": "kg", "किलो": "kg", "ಕೆಜಿ": "kg",
    "litre": "L", "liter": "L", "ltr": "L", "लीटर": "L", "ಲೀಟರ್": "L",
    "bag": "bag", "बोरी": "bag", "bori": "bag", "ಚೀಲ": "bag",
    "dabba": "box", "box": "box", "डिब्बा": "box", "ಡಬ್ಬ": "box",
    "piece": "piece", "nag": "piece", "नग": "piece", "pcs": "piece",
    "bundle": "bundle", "coil": "coil", "roll": "roll",
    "meter": "m", "metre": "m", "मीटर": "m", "ಮೀಟರ್": "m",
    "foot": "ft", "feet": "ft", "फुट": "ft", "inch": "in", "इंच": "in",
    "sheet": "sheet", "शीट": "sheet", "ಶೀಟ್": "sheet",
    "mm": "mm", "cm": "cm",
}


# Surfaces, rooms and colours: these qualify a product but are never the product
# itself. Used to decide what an ambiguous word like "rang" refers to.
QUALIFIERS = {
    "white", "black", "red", "blue", "green", "brown", "grey", "gray", "ivory",
    "exterior", "interior", "exterior wall", "interior wall",
    "wall", "ceiling", "floor", "kitchen", "bathroom", "bath",
    # Generic nouns that name no product. A query made only of these is not an
    # answer: "material building" matched an Unloading Service.
    "material", "building", "stuff", "item", "goods", "thing", "work",
    "house", "home", "room", "site", "flooring", "wood", "steel", "metal",
}

# "rang"/"banna" mean BOTH the product (paint) and the attribute (colour).
# "kale rang ka sink"  -> colour  (a sink is being bought)
# "bili banna gode-ge" -> product (nothing else is being bought)
AMBIGUOUS = {
    "rang": "paint", "ranga": "paint", "रंग": "paint",
    "ಬಣ್ಣ": "paint", "banna": "paint",
}


# Domain synonyms for suppressing a generic word when a specific one is present:
# "internet bichhane wala wire" -> "LAN cable", not "LAN cable wire".
GENERIC_EQUIV = {"wire": "cable", "cable": "cable", "taar": "cable",
                 "pipe": "pipe", "paip": "pipe"}


# "X banane ke liye Y" = "Y, for making X". X is being BUILT, not bought -
# searching for it returns the wrong thing entirely ("wood table" -> a table-top
# basin). Strip the word these markers govern.
BUILD_MARKERS = [
    "banane ke liye", "banane keliye", "banane ke liya",
    "banani hai", "banana hai", "banwana hai", "banwani hai",
    "banane hai", "ಮಾಡಲು", "ಮಾಡಬೇಕು",
]
