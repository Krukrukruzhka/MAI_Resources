WORD_CLASSES = {
    "существительное": {
        "женский": {
            "одушевленный": {
                " ".join(["а", "ой", "ы", ""]): "044",
                " ".join(["a", "ей", "ы", ""]): "045",
                " ".join(["я", "ей", "и", "й"]): "046",
                " ".join(["я", "ей", "и", "й"]): "047",
                " ".join(["я", "ей", "и", "ь"]): "050",
                " ".join(["а", "ой", "и", ""]): "051",
                " ".join(["ь", "ю", "и", "ей"]): "052",
                " ".join(["", "", "", ""]): "146"  # here must be empty strings
            },
            "неодушевленный": {
                " ".join(["а", "ой", "ы", "ых"]): "053",
                " ".join(["ь", "ю", "и", "ей"]): "054",
                " ".join(["ь", "ю", "и", "ей"]): "055",
                " ".join(["а", "ой", "ы", ""]): "056",
                " ".join(["а", "ей", "и", ""]): "057",
                " ".join(["а", "ой", "и", ""]): "060",
                " ".join(["я", "ей", "и", "й"]): "061",
                " ".join(["я", "ей", "и", "й"]): "062",
                " ".join(["я", "ей", "и", "ь"]): "063",
                " ".join(["я", "ей", "и", "ий"]): "064",
                " ".join(["я", "ей", "и", "ей"]): "065",
                " ".join(["я", "ей", "и", ""]): "066",
                " ".join(["я", "ей", "и", ""]): "067",
                " ".join(["", "", "", ""]): "146"
            }
        },
        "мужской": {
            "одушевленный": {
                " ".join(["", "ом", "ы", "ов"]): "021",
                " ".join(["", "ом", "ы", ""]): "022",
                " ".join(["", "ом", "и", "ей"]): "023",
                " ".join(["", "ом", "и", "ей"]): "024",
                " ".join(["й", "ем", "и", "ев"]): "025",
                " ".join(["ей", "ем", "и", "ев"]): "026",
                " ".join(["ь", "ем", "и", "ей"]): "027",
                " ".join(["ь", "ем", "я", "ей"]): "030",
                " ".join(["", "ом", "и", "ов"]): "031",
                " ".join(["", "ем", "ы", "ев"]): "032",
                " ".join(["а", "ей", "и", "ей"]): "033",
                " ".join(["а", "ой", "ы", ""]): "034",
                " ".join(["я", "ей", "и", "ей"]): "035",
                " ".join(["", "ем", "и", "ей"]): "036",
                " ".join(["", "ом", "е", ""]): "037",
                " ".join(["", "ом", "а", "ов"]): "040",
                " ".join(["", "ем", "я", "ей"]): "041",
                " ".join(["", "ым", "ы", "ых"]): "042",
                " ".join(["", "ом", "я", "ей"]): "043",
                " ".join(["", "", "", ""]): "145"  # here must be empty strings
            },
            "неодушевленный": {
                " ".join(["", "ом", "ы", "ов"]): "001",
                " ".join(["", "ом", "и", "ей"]): "002",
                " ".join(["ь", "ем", "и", "ей"]): "003",
                " ".join(["й", "ем", "и", "ев"]): "004",
                " ".join(["", "ом", "и", "ов"]): "006",
                " ".join(["", "ом", "и", ""]): "007",
                " ".join(["", "ом", "а", "ов"]): "010",
                " ".join(["", "ем", "ы", "ев"]): "011",
                " ".join(["й", "ем", "я", "ев"]): "013",
                " ".join(["", "ом", "я", "ев"]): "014",
                " ".join(["", "ом", "а", ""]): "015",
                " ".join(["", "ем", "и", "ей"]): "016",
                " ".join(["", "ом", "ы", ""]): "017",
                " ".join(["ь", "ем", "я", "ей"]): "020",
                " ".join(["", "", "", ""]): "145"
            }
        },
        "средний": {
            "одушевленный": {
                " ".join(["о", "ом", "а", ""]): "070",
                " ".join(["о", "ом", "а", "ов"]): "071",
                " ".join(["е", "ем", "я", "ей"]): "072",
                " ".join(["е", "ем", "я", "й"]): "073",
                " ".join(["е", "ем", "а", ""]): "074",
                " ".join(["о", "ом", "я", "ев"]): "075",
                " ".join(["я", "ем", "а", ""]): "076",
                " ".join(["е", "ем", "я", "ий"]): "077",
                " ".join(["о", "ом", "и", "ей"]): "100",
                " ".join(["о", "ом", "и", "ов"]): "101",
                " ".join(["е", "ем", "я", "ей"]): "102",
                " ".join(["", "", "", ""]): "147"
            },
            "неодушевленный": {
                " ".join(["о", "ом", "а", ""]): "070",
                " ".join(["о", "ом", "а", "ов"]): "071",
                " ".join(["е", "ем", "я", "ей"]): "072",
                " ".join(["е", "ем", "я", "й"]): "073",
                " ".join(["е", "ем", "а", ""]): "074",
                " ".join(["о", "ом", "я", "ев"]): "075",
                " ".join(["я", "ем", "а", ""]): "076",
                " ".join(["е", "ем", "я", "ий"]): "077",
                " ".join(["о", "ом", "и", "ей"]): "100",
                " ".join(["о", "ом", "и", "ов"]): "101",
                " ".join(["е", "ем", "я", "ей"]): "102",
                " ".join(["", "", "", ""]): "147"
            }
        }
    },
    "глагол": {

    },
    "прилагательное": {

    },
    "числительное": {
        "два": "131",
        "две": "131",
        "три": "132",
        "четыре": "133",
        "двое": "134",
        "трое": "134",
        "еро": "135",
        "оба": "140",
        "обе": "140",
        "столько": "137",
        "сколько": "137",
        "ь": "136"
    },
    "деепричастие": "152",
    "причастие": "152",
    "наречие": "152",
    "предикатив": "143"
}
