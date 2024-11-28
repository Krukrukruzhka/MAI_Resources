import aiohttp
import asyncio
import logging
import re
import glob

from bs4 import BeautifulSoup
from docx import Document
from word_classes import WORD_CLASSES


logger = logging.getLogger()
logger.setLevel("DEBUG")


def _prepare_word(word: str) -> str:
    letters = []
    for symbol in word:
        if symbol == "ё":
            symbol = "е"
        if "а" <= symbol <= "я":
            letters.append(symbol)
    return "".join(letters)


def _prepare_noun_endings(endings: list[str]) -> None:
    if len(endings[0]) > 1 and endings[0][-2:] == "ей":
        endings[0] = "ей"
    elif endings[0][-1] == "ь":
        endings[0] = "ь"
    elif endings[0][-1] == "й":
        endings[0] = "й"
    elif endings[0][-1] == "а":
        endings[0] = "а"
    elif endings[0][-1] == "о":
        endings[0] = "о"
    elif endings[0][-1] == "я":
        endings[0] = "я"
    elif endings[0][-1] == "е":
        endings[0] = "е"
    else:
        endings[0] = ""

    if len(endings[1]) > 1 and endings[1][-2:] == "ом":
        endings[1] = "ом"
    elif len(endings[1]) > 1 and endings[1][-2:] == "ем":
        endings[1] = "ем"
    elif len(endings[1]) > 1 and endings[1][-2:] == "ей":
        endings[1] = "ей"
    elif len(endings[1]) > 1 and endings[1][-2:] == "ой":
        endings[1] = "ой"
    elif len(endings[1]) > 1 and endings[1][-2:] == "ым":
        endings[1] = "ым"
    elif endings[1][-1] == "ю":
        endings[1] = "ю"

    if endings[2][-1] == "ы":
        endings[2] = "ы"
    elif endings[2][-1] == "и":
        endings[2] = "и"
    elif endings[2][-1] == "а":
        endings[2] = "а"
    elif endings[2][-1] == "я":
        endings[2] = "я"
    elif endings[2][-1] == "е":
        endings[2] = "е"

    if len(endings[3]) > 1 and endings[3][-2:] == "ов":
        endings[3] = "ов"
    elif len(endings[3]) > 1 and endings[3][-2:] == "ей":
        endings[3] = "ей"
    elif len(endings[3]) > 1 and endings[3][-2:] == "ев":
        endings[3] = "ев"
    elif len(endings[3]) > 1 and endings[3][-2:] == "ов":
        endings[3] = "ов"
    elif len(endings[3]) > 1 and endings[3][-2:] == "ых":
        endings[3] = "ых"
    elif len(endings[3]) > 1 and endings[3][-2:] == "ий":
        endings[3] = "ий"
    elif endings[3][-1] == "ь":
        endings[3] = "ь"
    elif endings[3][-1] == "й":
        endings[3] = "й"
    else:
        endings[3] = ""


async def get_word_html(word: str) -> str:
    async with aiohttp.ClientSession() as session:
        url = f"http://ru.wiktionary.org/wiki/{word}"
        logger.warning(f"GET HTML from {url} ")
        async with session.get(url, ssl=False) as resp:
            if resp.status != 200:
                logger.exception(f"Something went wrong with word {word}. Status code {resp.status}.")
                return f"HTTP error. Status code {resp.status}"
            return await resp.text()


async def get_word_metadata(word: str) -> list[str | None]:
    word = word.lower().replace("ё", "е")

    word_html = await get_word_html(word)
    if len(word_html) > 4 and word_html[:4] == "HTTP":
        return [word_html]

    soup = BeautifulSoup(word_html, 'html.parser')
    try:
        div = soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
        p_elements = div.find_all("p")

        word_params = p_elements[1].text.lower().replace("; ", ", ").split(", ")
        for i in range(len(word_params)):
            word_params[i] = word_params[i].replace("ё", "е")

        word_type = word_params[0].replace("\n", "")
        logger.warning(word_type)
        word_params = set(word_params)

        metadata = [word_type]

        if word_type == "существительное":
            if "мужской род" in word_params or "мужской" in word_params:
                metadata.append("мужской")
            elif "женский род" in word_params or "женский" in word_params:
                metadata.append("женский")
            elif "средний род" in word_params or "средний" in word_params:
                metadata.append("средний")
            else:
                raise RuntimeError("Слово без рода")

            if "одушевленное" in word_params:
                metadata.append("одушевленный")
            elif "неодушевленное" in word_params:
                metadata.append("неодушевленный")
            else:
                raise RuntimeError(r"Без души ¯\_(ツ)_/¯")

            raws = div.find("table", {"class": "morfotable ru"}).find_all("tr")
            endings = [
                _prepare_word(raws[1].find_all("td")[1].text),
                _prepare_word(raws[5].find_all("td")[1].text),
                _prepare_word(raws[1].find_all("td")[2].text),
                _prepare_word(raws[2].find_all("td")[2].text)
            ]

            _prepare_noun_endings(endings)
            metadata.append(" ".join(endings))

        elif word_type == "глагол":
            metadata = ["глагол"]
        elif word_type == "числительное":
            if len(word) > 2 and word[-3:] == "еро":
                metadata = ["еро"]
            elif word[-1] == "ь":
                metadata = ["ь"]
            else:
                metadata.append(word)
        elif word_type in ("деепричастие", "причастие", "наречие", "предикатив"):
            metadata = [word_type]
        else:
            metadata = ["Unknown type"]
        return metadata

    except Exception as exept:
        return [f"Ошибка {exept}"]


async def identity_word_class(word: str) -> str:
    tmp = WORD_CLASSES
    metadata = await get_word_metadata(word)
    logger.warning(metadata)

    if metadata and len(metadata[0]) > 6 and (metadata[0][:6] == "Ошибка" or metadata[0][:4] == "HTTP"):
        logger.warning(metadata[0])
        logger.warning("\n\n")
        return metadata[0]

    for param in metadata:
        tmp = tmp.get(param, None)
        if tmp is None:
            logger.warning(f"word: {word}\t\tparams: {metadata}")
            logger.warning("Ошибка Invalid WORD_CLASSES structure\n\n")
            return "Ошибка Invalid WORD_CLASSES structure"

    logger.warning(tmp)
    logger.warning("\n\n")
    return tmp


async def generate_answer_file():
    path = f"res/input/*.docx"
    docx_files = glob.glob(path)

    for file_path in docx_files:
        doc = Document(file_path)
        filename = file_path.split("/")[-1]

        output_file_path = f"res/output/{filename[:-5]}.txt"
        with open(output_file_path, 'w+', encoding='utf-8') as output_file:
            for paragraph in doc.paragraphs:
                text = re.sub(r'\.', '', re.sub(r'\s+', ' ', paragraph.text))
                text_elements = text.split()
                if len(text_elements) == 3:
                    word = text_elements[0] + (text_elements[1] if text_elements[1] != "+" else "")
                    text_elements.append(await identity_word_class(word))
                    output_file.write(" ".join(text_elements) + '\n')


if __name__ == "__main__":
    asyncio.run(generate_answer_file())
