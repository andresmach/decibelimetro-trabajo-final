"""Helpers para generar WordprocessingML (párrafos, viñetas, tablas, imágenes)."""
import re
from xml.sax.saxutils import escape

# ───────────────────────── helpers de XML ─────────────────────────
FONT = '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial" w:eastAsia="Arial"/>'


def runs(text, size=22, bold=False, italic=False, color=None):
    """Texto con **negrita** inline → runs."""
    out = []
    for i, chunk in enumerate(re.split(r'\*\*', text)):
        if not chunk:
            continue
        b = bold or (i % 2 == 1)
        rpr = FONT + ('<w:b/>' if b else '') + ('<w:i/>' if italic else '')
        if color:
            rpr += f'<w:color w:val="{color}"/>'
        rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(chunk)}</w:t></w:r>')
    return ''.join(out)


def P(text='', size=22, bold=False, italic=False, align='both', before=0, after=120,
      ind_left=0, hanging=0, keep_next=False, color=None):
    if size < 22 and align == 'both':
        align = 'left'  # texto chico (tablas): sin justificar
    ppr = '<w:pStyle w:val="Normal"/>'
    if keep_next:
        ppr += '<w:keepNext/>'
    ppr += f'<w:spacing w:before="{before}" w:after="{after}" w:line="276" w:lineRule="auto"/>'
    if ind_left or hanging:
        ppr += f'<w:ind w:left="{ind_left}" w:hanging="{hanging}"/>'
    ppr += f'<w:jc w:val="{align}"/>'
    return f'<w:p><w:pPr>{ppr}</w:pPr>{runs(text, size, bold, italic, color)}</w:p>'


def B(text, size=22, level=0):
    """Viñeta con sangría francesa (la plantilla no trae numbering.xml)."""
    sym = '•' if level == 0 else '–'
    left = 425 + 360 * level
    return P(f'{sym}\t{text}', size=size, ind_left=left, hanging=283, after=60)


def H2(text):
    return P(text, size=24, bold=True, before=160, after=80, keep_next=True, align='left')


BORDER = ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="808080"/>'
                 for s in ('top', 'left', 'bottom', 'right'))


def cell(content_xml, w, fill=None, valign='center'):
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ''
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders>{BORDER}</w:tcBorders>{shd}'
            f'<w:tcMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tcMar>'
            f'<w:vAlign w:val="{valign}"/></w:tcPr>{content_xml}</w:tc>')


def T(headers, rows, widths, size=18, header_fill='D9E2F3', center_cols=(), keep=False):
    """keep=True: la tabla no se parte entre páginas (keepNext en todas las filas menos la última)."""
    total = sum(widths)
    grid = ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    x = (f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:jc w:val="center"/>'
         f'<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>')
    if headers:
        x += '<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' + ''.join(
            cell(P(h, size=size, bold=True, align='center', after=0, keep_next=keep), w, header_fill)
            for h, w in zip(headers, widths)) + '</w:tr>'
    for ri, r in enumerate(rows):
        kn = keep and ri < len(rows) - 1
        x += '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
        for j, (c, w) in enumerate(zip(r, widths)):
            if isinstance(c, tuple):  # (texto, relleno)
                txt, fill = c
            else:
                txt, fill = c, None
            bold = txt.startswith('##')
            txt = txt.lstrip('#')
            al = 'center' if j in center_cols else 'left'
            lines = txt.split('\n')
            x += cell(''.join(P(ln, size=size, bold=bold, align=al, after=0 if k == len(lines) - 1 else 40, keep_next=kn)
                              for k, ln in enumerate(lines)), w, fill)
        x += '</w:tr>'
    return x + '</w:tbl>' + P('', after=60)


def IMG_RUN(rid, cx, cy, pid, name):
    return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{pid}" name="{name}"/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{pid}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            f'</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')


