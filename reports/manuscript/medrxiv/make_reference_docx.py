"""Build the Word style template (reference.docx) that pandoc uses for the manuscript.

Usage (from this folder):
    python3 make_reference_docx.py
    /opt/anaconda3/bin/pandoc MANUSCRIPT_medRxiv_v1.md -f markdown -t docx --reference-doc=reference.docx \
        --resource-path=. -o MANUSCRIPT_medRxiv_v1.docx

Starts from pandoc's default reference.docx and restyles it: serif body text, sans-serif headings, small captions,
three-rule tables, A4 page with 2.2 cm margins and a centred page number in the footer.
"""
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

PANDOC = "/opt/anaconda3/bin/pandoc"
OUT = Path(__file__).with_name("reference.docx")
BODY, HEAD = "Cambria", "Helvetica Neue"
INK, ACCENT, MUTED = "1D2733", "2B5B8F", "5B6675"


def fonts(name):
    return f'<w:rFonts w:ascii="{name}" w:hAnsi="{name}" w:eastAsia="{name}" w:cs="{name}"/>'


def para(sid, name, ppr="", rpr="", based="Normal", nxt="BodyText", custom=False):
    c = ' w:customStyle="1"' if custom else ""
    return (f'<w:style w:type="paragraph"{c} w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="{based}"/>'
            f'<w:next w:val="{nxt}"/><w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


def heading(level, size, before, after, color, caps=False):
    rpr = f'{fonts(HEAD)}<w:b/><w:color w:val="{color}"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    if caps:
        rpr += '<w:spacing w:val="10"/>'
    ppr = (f'<w:keepNext/><w:keepLines/><w:spacing w:before="{before}" w:after="{after}"/>'
           f'<w:outlineLvl w:val="{level - 1}"/>')
    return para(f"Heading{level}", f"heading {level}", ppr, rpr)


STYLES = {
    "Normal": ('<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
               f'<w:pPr><w:spacing w:after="0" w:line="276" w:lineRule="auto"/></w:pPr>'
               f'<w:rPr>{fonts(BODY)}<w:color w:val="{INK}"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:style>'),
    "BodyText": para("BodyText", "Body Text", '<w:spacing w:before="0" w:after="140"/><w:jc w:val="both"/>'),
    "FirstParagraph": para("FirstParagraph", "First Paragraph", based="BodyText", custom=True),
    "Compact": para("Compact", "Compact", '<w:spacing w:before="20" w:after="40"/>', based="BodyText", custom=True),
    "Title": para("Title", "Title", '<w:spacing w:before="0" w:after="320" w:line="300" w:lineRule="auto"/>',
                  f'{fonts(HEAD)}<w:b/><w:color w:val="{INK}"/><w:sz w:val="34"/><w:szCs w:val="34"/>'),
    "Heading1": heading(1, 26, 400, 140, ACCENT),
    "Heading2": heading(2, 22, 280, 100, INK),
    "Heading3": heading(3, 20, 220, 80, MUTED),
    "Caption": para("Caption", "caption", '<w:spacing w:before="80" w:after="280" w:line="252" w:lineRule="auto"/>'
                    '<w:jc w:val="both"/>', f'{fonts(HEAD)}<w:color w:val="{MUTED}"/><w:sz w:val="16"/><w:szCs w:val="16"/>',
                    based="Normal"),
    "ImageCaption": para("ImageCaption", "Image Caption", based="Caption", custom=True),
    "TableCaption": para("TableCaption", "Table Caption", '<w:keepNext/><w:spacing w:before="200" w:after="80"/>',
                         based="Caption", custom=True),
    "CaptionedFigure": para("CaptionedFigure", "Captioned Figure", '<w:keepNext/><w:spacing w:before="200" w:after="0"/>'
                            '<w:jc w:val="center"/>', custom=True),
    "Figure": para("Figure", "Figure", '<w:keepNext/><w:jc w:val="center"/>', custom=True),
    "Hyperlink": (f'<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/>'
                  f'<w:basedOn w:val="BodyTextChar"/><w:rPr><w:color w:val="{ACCENT}"/></w:rPr></w:style>'),
    "Table": ('<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/>'
              '<w:basedOn w:val="TableNormal"/><w:qFormat/>'
              f'<w:pPr><w:spacing w:before="40" w:after="40" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>'
              f'<w:rPr>{fonts(HEAD)}<w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr>'
              '<w:tblPr><w:jc w:val="center"/><w:tblInd w:w="0" w:type="dxa"/>'
              f'<w:tblBorders><w:top w:val="single" w:sz="10" w:space="0" w:color="{INK}"/>'
              f'<w:bottom w:val="single" w:sz="10" w:space="0" w:color="{INK}"/></w:tblBorders>'
              '<w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="100" w:type="dxa"/>'
              '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr>'
              '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/></w:rPr><w:tcPr>'
              f'<w:tcBorders><w:bottom w:val="single" w:sz="6" w:space="0" w:color="{INK}"/></w:tcBorders>'
              '<w:shd w:val="clear" w:color="auto" w:fill="EEF2F6"/><w:vAlign w:val="bottom"/></w:tcPr></w:tblStylePr>'
              '</w:style>'),
}

FOOTER = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
          '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
          f'<w:r><w:rPr>{fonts(HEAD)}<w:color w:val="{MUTED}"/><w:sz w:val="16"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
          f'<w:r><w:rPr>{fonts(HEAD)}<w:color w:val="{MUTED}"/><w:sz w:val="16"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
          f'<w:r><w:rPr>{fonts(HEAD)}<w:color w:val="{MUTED}"/><w:sz w:val="16"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
          f'<w:r><w:rPr>{fonts(HEAD)}<w:color w:val="{MUTED}"/><w:sz w:val="16"/></w:rPr><w:t>1</w:t></w:r>'
          f'<w:r><w:rPr>{fonts(HEAD)}<w:color w:val="{MUTED}"/><w:sz w:val="16"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>'
          '</w:p></w:ftr>')
SECT = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooterPage"/>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1247" w:right="1247" w:bottom="1247" w:left="1247" w:header="567" w:footer="567" w:gutter="0"/>'
        '</w:sectPr>')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "default.docx"
        base.write_bytes(subprocess.run([PANDOC, "--print-default-data-file", "reference.docx"],
                                        check=True, capture_output=True).stdout)
        src = zipfile.ZipFile(base)
        parts = {n: src.read(n) for n in src.namelist()}

        styles = parts["word/styles.xml"].decode()
        for sid, xml in STYLES.items():
            pat = re.compile(r'<w:style [^>]*w:styleId="' + sid + r'"[^>]*>.*?</w:style>', re.S)
            styles, n = pat.subn(lambda _: xml, styles, count=1)
            if n == 0:
                styles = styles.replace("</w:styles>", xml + "</w:styles>")
        parts["word/styles.xml"] = styles.encode()

        doc = parts["word/document.xml"].decode()
        doc = re.sub(r"<w:sectPr\b.*?</w:sectPr>", SECT, doc, flags=re.S)
        parts["word/document.xml"] = doc.encode()
        parts["word/footer1.xml"] = FOOTER.encode()

        rels = parts["word/_rels/document.xml.rels"].decode()
        rels = rels.replace("</Relationships>", '<Relationship Id="rIdFooterPage" Type="http://schemas.openxmlformats.org/'
                            'officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>')
        parts["word/_rels/document.xml.rels"] = rels.encode()
        ct = parts["[Content_Types].xml"].decode()
        ct = ct.replace("</Types>", '<Override PartName="/word/footer1.xml" ContentType="application/'
                        'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
        parts["[Content_Types].xml"] = ct.encode()

        tmp_out = Path(tmp) / "reference.docx"
        with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as z:
            for n, b in parts.items():
                z.writestr(n, b)
        shutil.copyfile(tmp_out, OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
