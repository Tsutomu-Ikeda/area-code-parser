import json
from tempfile import NamedTemporaryFile

import camelot
import pandas
import fastapi

from section_parser import parse_section_text


app = fastapi.FastAPI()


@app.post("/parse")
async def pptx_to_mp4(
    pdf_file: bytes = fastapi.File(),
):
    with NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(pdf_file)
        tmp.seek(0)
        tables = camelot.read_pdf(tmp.name, pages='all', split_text=True, strip_text="\n", line_scale=40)
        all_tables = pandas.concat([table.df for table in tables], ignore_index=True)

        all_tables = all_tables.drop(0)

        json_value = [
            {
                "番号区画コード": row[0],
                "番号区画": parse_section_text(str(row[1])),
                "市外局番": row[2],
                "市内局番": row[3],
            }
            for key, row in all_tables.iterrows()
        ]

        return json_value
