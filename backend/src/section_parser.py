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
                rule = text[i - 4:i]

                if text[read_index:open_paren_index] != "":
                    names.append(
                        {
                            "name": complete_pref_name(
                                union_rule.sub("", text[read_index:open_paren_index]),
                                names,
                            ),
                            "exclude": parse_section_text(text[open_paren_index + 1:i - 4])
                            if rule == "を除く。"
                            else [],
                            "include": parse_section_text(text[open_paren_index + 1:i - 4])
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
            elif text[i:i + 2] == "及び":
                if "丁目" in text[read_index:i]:
                    start_block_number_index = text.find("丁目", read_index)
                    names.append(
                        {
                            "name": complete_pref_name(
                                text[read_index:start_block_number_index + 2], names
                            ),
                        }
                    )

                    end_block_number_index = text.find(
                        "丁目", start_block_number_index + 2
                    )
                    if end_block_number_index == -1:
                        read_index = i + 2
                        continue

                    end_block_number = text[i + 2:end_block_number_index]

                    if re.match(r"^[一二三四五六七八九十]+$", end_block_number) is None:
                        names.append(
                            {
                                "name": complete_pref_name(
                                    text[
                                        start_block_number_index
                                        + 4:end_block_number_index
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
                        text[end_block_number_index + 2:end_block_number_index + 4]
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
            elif text[i:i + 3] == "並びに":
                if len(text[read_index:i]) > 0:
                    names.append(
                        {"name": complete_pref_name(text[read_index:i], names)}
                    )
                read_index = i + 3
            elif text[i:i + 2] == "から":
                start_block_number_index = text.find("丁目", read_index)

                start_block_number = text[
                    start_block_number_index - 1:start_block_number_index
                ]
                end_block_number_index = text.find("丁目", start_block_number_index + 2)
                end_block_number = text[
                    start_block_number_index + 4:start_block_number_index + 5
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
