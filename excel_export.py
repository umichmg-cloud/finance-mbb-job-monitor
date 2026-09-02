from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


INVALID_XML_CHARS = {
    chr(i)
    for i in range(32)
    if i not in (9, 10, 13)
}


def clean_text(value):
    if value is None:
        return ""

    text = str(value)

    for char in INVALID_XML_CHARS:
        text = text.replace(char, "")

    return text


def column_letter(number):
    result = ""

    while number:
        number, remainder = divmod(
            number - 1,
            26,
        )

        result = (
            chr(65 + remainder)
            + result
        )

    return result


def xml_text(value):
    return escape(
        clean_text(value),
        {
            '"': "&quot;",
        },
    )


def make_cell(
    row,
    column,
    value,
    style=0,
):
    ref = (
        f"{column_letter(column)}"
        f"{row}"
    )

    value = xml_text(value)

    return (
        f'<c r="{ref}" '
        f't="inlineStr" '
        f's="{style}">'
        f"<is><t xml:space=\"preserve\">"
        f"{value}"
        f"</t></is>"
        f"</c>"
    )


def make_sheet(
    headers,
    rows,
    widths,
):
    parts = []

    parts.append(
        '<?xml version="1.0" '
        'encoding="UTF-8" '
        'standalone="yes"?>'
    )

    parts.append(
        '<worksheet '
        'xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main">'
    )

    # Freeze the header row.
    parts.append(
        "<sheetViews>"
        '<sheetView workbookViewId="0">'
        '<pane ySplit="1" '
        'topLeftCell="A2" '
        'activePane="bottomLeft" '
        'state="frozen"/>'
        "</sheetView>"
        "</sheetViews>"
    )

    # Column widths.
    parts.append("<cols>")

    for index, width in enumerate(
        widths,
        start=1,
    ):
        parts.append(
            f'<col min="{index}" '
            f'max="{index}" '
            f'width="{width}" '
            'customWidth="1"/>'
        )

    parts.append("</cols>")

    parts.append("<sheetData>")

    # Header.
    parts.append('<row r="1" ht="22">')

    for column, header in enumerate(
        headers,
        start=1,
    ):
        parts.append(
            make_cell(
                1,
                column,
                header,
                style=1,
            )
        )

    parts.append("</row>")

    # Body.
    for row_index, row in enumerate(
        rows,
        start=2,
    ):
        parts.append(
            f'<row r="{row_index}">'
        )

        for column, value in enumerate(
            row,
            start=1,
        ):
            parts.append(
                make_cell(
                    row_index,
                    column,
                    value,
                    style=0,
                )
            )

        parts.append("</row>")

    parts.append("</sheetData>")

    # Excel filter.
    if headers:
        last_column = column_letter(
            len(headers)
        )

        last_row = max(
            len(rows) + 1,
            1,
        )

        parts.append(
            f'<autoFilter ref="A1:'
            f'{last_column}{last_row}"/>'
        )

    parts.append("</worksheet>")

    return "".join(parts)


def workbook_xml():
    return (
        '<?xml version="1.0" '
        'encoding="UTF-8" '
        'standalone="yes"?>'
        '<workbook '
        'xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships">'
        "<sheets>"
        '<sheet name="All Jobs" '
        'sheetId="1" '
        'r:id="rId1"/>'
        '<sheet name="Relevant HK-CDMX" '
        'sheetId="2" '
        'r:id="rId2"/>'
        '<sheet name="Sources Summary" '
        'sheetId="3" '
        'r:id="rId3"/>'
        "</sheets>"
        "</workbook>"
    )


def workbook_rels_xml():
    return (
        '<?xml version="1.0" '
        'encoding="UTF-8" '
        'standalone="yes"?>'
        '<Relationships '
        'xmlns="http://schemas.openxmlformats.org/'
        'package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet2.xml"/>'
        '<Relationship Id="rId3" '
        'Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet3.xml"/>'
        '<Relationship Id="rId4" '
        'Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
        "</Relationships>"
    )


def root_rels_xml():
    return (
        '<?xml version="1.0" '
        'encoding="UTF-8" '
        'standalone="yes"?>'
        '<Relationships '
        'xmlns="http://schemas.openxmlformats.org/'
        'package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def content_types_xml():
    return (
        '<?xml version="1.0" '
        'encoding="UTF-8" '
        'standalone="yes"?>'
        '<Types '
        'xmlns="http://schemas.openxmlformats.org/'
        'package/2006/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-'
        'package.relationships+xml"/>'
        '<Default Extension="xml" '
        'ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" '
        'ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet3.xml" '
        'ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.styles+xml"/>'
        "</Types>"
    )


def styles_xml():
    return (
        '<?xml version="1.0" '
        'encoding="UTF-8" '
        'standalone="yes"?>'
        '<styleSheet '
        'xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main">'

        '<fonts count="2">'

        '<font>'
        '<sz val="10"/>'
        '<name val="Aptos"/>'
        '</font>'

        '<font>'
        '<b/>'
        '<color rgb="FFFFFFFF"/>'
        '<sz val="10"/>'
        '<name val="Aptos"/>'
        '</font>'

        '</fonts>'

        '<fills count="3">'

        '<fill>'
        '<patternFill patternType="none"/>'
        '</fill>'

        '<fill>'
        '<patternFill patternType="gray125"/>'
        '</fill>'

        '<fill>'
        '<patternFill patternType="solid">'
        '<fgColor rgb="FF17365D"/>'
        '<bgColor indexed="64"/>'
        '</patternFill>'
        '</fill>'

        '</fills>'

        '<borders count="1">'
        '<border>'
        '<left/><right/><top/><bottom/><diagonal/>'
        '</border>'
        '</borders>'

        '<cellStyleXfs count="1">'
        '<xf numFmtId="0" '
        'fontId="0" '
        'fillId="0" '
        'borderId="0"/>'
        '</cellStyleXfs>'

        '<cellXfs count="2">'

        '<xf numFmtId="0" '
        'fontId="0" '
        'fillId="0" '
        'borderId="0" '
        'xfId="0"/>'

        '<xf numFmtId="0" '
        'fontId="1" '
        'fillId="2" '
        'borderId="0" '
        'xfId="0" '
        'applyFont="1" '
        'applyFill="1" '
        'applyAlignment="1">'
        '<alignment horizontal="center" '
        'vertical="center"/>'
        '</xf>'

        '</cellXfs>'

        '<cellStyles count="1">'
        '<cellStyle name="Normal" '
        'xfId="0" '
        'builtinId="0"/>'
        '</cellStyles>'

        '</styleSheet>'
    )


def jobs_to_rows(jobs):
    rows = []

    for job in jobs:
        rows.append(
            [
                job.get("company", ""),
                job.get("category", ""),
                job.get("title", ""),
                job.get("location", ""),
                job.get(
                    "location_group",
                    "",
                ),
                job.get("posted_at", ""),
                job.get("department", ""),
                job.get("team", ""),
                job.get("id", ""),
                job.get("url", ""),
            ]
        )

    return rows


def summary_to_rows(summary):
    rows = []

    for item in summary:
        rows.append(
            [
                item.get("company", ""),
                item.get("category", ""),
                item.get("status", ""),
                item.get("retrieved", 0),
                item.get("relevant", 0),
                item.get("error", ""),
            ]
        )

    return rows


def export_jobs_excel(
    all_jobs,
    relevant_jobs,
    source_summary,
    output_path,
):
    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    job_headers = [
        "Company",
        "Category",
        "Title",
        "Location",
        "Target Market",
        "Posted At",
        "Department",
        "Team",
        "Job ID",
        "URL",
    ]


    job_widths = [
        24,
        12,
        55,
        42,
        16,
        20,
        28,
        26,
        32,
        80,
    ]


    summary_headers = [
        "Company",
        "Category",
        "Status",
        "Jobs Retrieved",
        "Relevant Jobs",
        "Error",
    ]


    summary_widths = [
        28,
        14,
        14,
        18,
        16,
        70,
    ]


    sheet1 = make_sheet(
        job_headers,
        jobs_to_rows(
            all_jobs
        ),
        job_widths,
    )


    sheet2 = make_sheet(
        job_headers,
        jobs_to_rows(
            relevant_jobs
        ),
        job_widths,
    )


    sheet3 = make_sheet(
        summary_headers,
        summary_to_rows(
            source_summary
        ),
        summary_widths,
    )


    with ZipFile(
        output_path,
        "w",
        ZIP_DEFLATED,
    ) as workbook:

        workbook.writestr(
            "[Content_Types].xml",
            content_types_xml(),
        )

        workbook.writestr(
            "_rels/.rels",
            root_rels_xml(),
        )

        workbook.writestr(
            "xl/workbook.xml",
            workbook_xml(),
        )

        workbook.writestr(
            "xl/_rels/workbook.xml.rels",
            workbook_rels_xml(),
        )

        workbook.writestr(
            "xl/styles.xml",
            styles_xml(),
        )

        workbook.writestr(
            "xl/worksheets/sheet1.xml",
            sheet1,
        )

        workbook.writestr(
            "xl/worksheets/sheet2.xml",
            sheet2,
        )

        workbook.writestr(
            "xl/worksheets/sheet3.xml",
            sheet3,
        )


    print(
        f"Excel created: "
        f"{output_path}"
    )
