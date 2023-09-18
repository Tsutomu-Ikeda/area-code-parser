import json
import re


kanji_to_number = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}
number_to_kanji = {v: k for k, v in kanji_to_number.items()}
prefectures = {
    1: "北海道",
    2: "青森県",
    3: "岩手県",
    4: "宮城県",
    5: "秋田県",
    6: "山形県",
    7: "福島県",
    8: "茨城県",
    9: "栃木県",
    10: "群馬県",
    11: "埼玉県",
    12: "千葉県",
    13: "東京都",
    14: "神奈川県",
    15: "新潟県",
    16: "富山県",
    17: "石川県",
    18: "福井県",
    19: "山梨県",
    20: "長野県",
    21: "岐阜県",
    22: "静岡県",
    23: "愛知県",
    24: "三重県",
    25: "滋賀県",
    26: "京都府",
    27: "大阪府",
    28: "兵庫県",
    29: "奈良県",
    30: "和歌山県",
    31: "鳥取県",
    32: "島根県",
    33: "岡山県",
    34: "広島県",
    35: "山口県",
    36: "徳島県",
    37: "香川県",
    38: "愛媛県",
    39: "高知県",
    40: "福岡県",
    41: "佐賀県",
    42: "長崎県",
    43: "熊本県",
    44: "大分県",
    45: "宮崎県",
    46: "鹿児島県",
    47: "沖縄県",
}
prefecture_names = prefectures.values()


def complete_pref_name(new_name: str, names: list[dict]) -> str:
    if len(names) == 0:
        return new_name

    if any(new_name.startswith(pref_name) for pref_name in prefecture_names):
        return new_name

    for pref_name in prefecture_names:
        if names[-1]["name"].startswith(pref_name):
            return f"{pref_name}{new_name}"

    return new_name


def parse_section_text(text: str):
    global kanji_to_number
    global number_to_kanji

    union_rule = re.compile(r"^(、|及び)")

    open_paren_index = 0
    paren_count = 0
    names: list[dict] = []
    read_index = 0

    for i in range(len(text)):
        if i < read_index:
            continue

        if text[i] == "（":
            if paren_count == 0:
                open_paren_index = i
            paren_count += 1
        elif text[i] == "）":
            paren_count -= 1

            if paren_count == 0:
                rule = text[i - 4 : i]

                if text[read_index:open_paren_index] != "":
                    names.append(
                        {
                            "name": complete_pref_name(
                                union_rule.sub("", text[read_index:open_paren_index]),
                                names,
                            ),
                            "exclude": parse_section_text(text[open_paren_index + 1 : i - 4])
                            if rule == "を除く。"
                            else [],
                            "include": parse_section_text(text[open_paren_index + 1 : i - 4])
                            if rule == "に限る。"
                            else [],
                        }
                    )

                read_index = i + 1
        elif paren_count == 0:
            if text[i] == "、":
                if len(text[read_index:i]) > 0:
                    names.append(
                        {"name": complete_pref_name(text[read_index:i], names)}
                    )
                read_index = i + 1
            elif text[i : i + 2] == "及び":
                if "丁目" in text[read_index:i]:
                    start_block_number_index = text.find("丁目", read_index)
                    names.append(
                        {
                            "name": complete_pref_name(
                                text[read_index : start_block_number_index + 2], names
                            ),
                        }
                    )

                    end_block_number_index = text.find(
                        "丁目", start_block_number_index + 2
                    )
                    if end_block_number_index == -1:
                        read_index = i + 2
                        continue

                    end_block_number = text[i + 2 : end_block_number_index]

                    if re.match(r"^[一二三四五六七八九十]+$", end_block_number) is None:
                        names.append(
                            {
                                "name": complete_pref_name(
                                    text[
                                        start_block_number_index
                                        + 4 : end_block_number_index
                                        + 2
                                    ],
                                    names,
                                ),
                            }
                        )
                        read_index = end_block_number_index + 2
                        continue

                    names.append(
                        {
                            "name": complete_pref_name(
                                f"{text[read_index:start_block_number_index - 1]}{end_block_number}丁目",
                                names,
                            ),
                        }
                    )

                    if (
                        text[end_block_number_index + 2 : end_block_number_index + 4]
                        == "から"
                    ):
                        final_end_block_number = text[end_block_number_index + 4]

                        for j in range(
                            kanji_to_number[end_block_number] + 1,
                            kanji_to_number[final_end_block_number] + 1,
                        ):
                            names.append(
                                {
                                    "name": complete_pref_name(
                                        f"{text[read_index:start_block_number_index - 1]}{number_to_kanji[j]}丁目",
                                        names,
                                    ),
                                }
                            )

                        end_block_number_index += 7

                    read_index = end_block_number_index + 2
                elif len(text[read_index:i]) > 0:
                    names.append(
                        {"name": complete_pref_name(text[read_index:i], names)}
                    )
                    read_index = i + 2
            elif text[i : i + 3] == "並びに":
                if len(text[read_index:i]) > 0:
                    names.append(
                        {"name": complete_pref_name(text[read_index:i], names)}
                    )
                read_index = i + 3
            elif text[i : i + 2] == "から":
                start_block_number_index = text.find("丁目", read_index)

                start_block_number = text[
                    start_block_number_index - 1 : start_block_number_index
                ]
                end_block_number_index = text.find("丁目", start_block_number_index + 2)
                end_block_number = text[
                    start_block_number_index + 4 : start_block_number_index + 5
                ]

                for j in range(
                    kanji_to_number[start_block_number],
                    kanji_to_number[end_block_number] + 1,
                ):
                    number_to_kanji = {v: k for k, v in kanji_to_number.items()}
                    names.append(
                        {
                            "name": complete_pref_name(
                                f"{text[read_index:start_block_number_index - 1]}{number_to_kanji[j]}丁目",
                                names,
                            ),
                        }
                    )

                read_index = end_block_number_index + 4

    if read_index < len(text):
        names.append(
            {"name": complete_pref_name(union_rule.sub("", text[read_index:]), names)}
        )

    return names


if __name__ == "__main__":
    inputs = [
        # "北海道沙流郡（平取町及び日高町（栄町西、栄町東、新町、千栄、富岡、日高、本町西、本町東、松風町、三岩、宮下町、山手町及び若葉町に限る。）に限る。）",
        # "北海道標津郡標津町、野付郡別海町（尾岱沼、尾岱沼港町、尾岱沼岬町、尾岱沼潮見町及び床丹に限る。）、目梨郡",
        # "北海道網走郡（大空町（東藻琴、東藻琴清浦、東藻琴栄、東藻琴新富、東藻琴末広、東藻琴大進、東藻琴千草、東藻琴西倉、東藻琴福富、東藻琴明生及び東藻琴山園に限る。）を除く。）",
        "東京都町田市（三輪町及び三輪緑山を除く。）、神奈川県相模原市（緑区（小原、小渕、佐野川、澤井、寸沢嵐、千木良、名倉、日連、牧野、吉野、与瀬、与瀬本町及び若柳に限る。）及び南区（磯部、新磯野一丁目及び三丁目から五丁目まで、新戸、相武台並びに相武台団地に限る。）を除く。）、座間市（相模が丘一丁目及び五丁目に限る。）",
        # "東京都稲城市、小金井市（梶野町一丁目から四丁目まで並びに東町二丁目及び三丁目を除く。）、国分寺市（高木町、内藤、西町、光町、日吉町二丁目及び三丁目、富士本並びに戸倉三丁目を除く。）、小平市（鈴木町二丁目、花小金井及び花小金井南町を除く。）、多摩市、東村山市、府中市（押立町四丁目及び五丁目、北山町、西原町二丁目から四丁目まで並びに西府町四丁目を除く。）",
        # "広島県庄原市（東城町を除く。）",
        # "広島県福山市（今津町、金江町金見、金江町藁江、神村町、高西町川尻、高西町真田、高西町南、東村町、藤江町、本郷町、松永町、南松永町、宮前町及び柳津町に限る。）（ただし、市外局番を除く電気通信番号による発信については、番号区画コード499の番号区画（福山市（内海町、神辺町及び沼隈町に限る。）を除く。）を含む。）",
        # "新潟県燕市（秋葉町、井土巻、大関、大船渡、大曲、上児木、勘新、蔵関、小池、小池新町、穀町、小関、小高、寿町、小中川、小古津新、小牧、幸町、桜町、佐渡、三王渕、下児木、新栄町、新生町、新町、水道町、杉名、杉柳、関崎、杣木、舘野、中央通、長所、長所乙、長所甲、次新、燕、道金、殿島、中川、仲町、長渡、二階堂、灰方、白山町、八王寺、花園町、花見、東太田、日之出町、物流センタ－、本町、又新、松橋、南、宮町、柳山、横田及び四ツ屋を除く。）、新潟市西蒲区（打越、姥島、潟浦新、上小吉、高野宮、河間、五之上、小吉、道上、中之口、長場、羽黒、針ヶ曽根、東小吉、東中、東船越、福島、真木、巻大原、牧ケ島、三ツ門、門田及び六部を除く。）、長岡市（赤沼、大沼新田、小沼新田、下沼新田、寺泊小豆曽根、寺泊有信、寺泊入軽井、寺泊岩方、寺泊木島、寺泊北曽根、寺泊五分一、寺泊下桐、寺泊下中条、寺泊新長、寺泊高内、寺泊竹森、寺泊田尻、寺泊敦ケ曽根、寺泊当新田、寺泊中曽根、寺泊硲田、寺泊万善寺、寺泊平野新村新田、寺泊蛇塚、寺泊町軽井、寺泊求草、寺泊矢田、寺泊鰐口、中条新田、中之島西野及び真野代新田に限る。）、西蒲原郡",
    ]

    for input_str in inputs:
        output = parse_section_text(input_str)
        print(json.dumps(output, ensure_ascii=False, indent=4))
