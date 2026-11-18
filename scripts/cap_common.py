"""Utilidades comunes para generar capítulos sobre la plantilla UNER (portada con logo)."""
import os
import re
import zipfile

from docx_xml import P, T, IMG_RUN
from PIL import Image


def H1(text):
    return P(text, size=28, bold=True, before=240, after=120, keep_next=True, align='left')


def PB():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def CAP(text):
    return P(text, size=18, italic=True, align='center', after=200)


def _runs_of(p_xml):
    return p_xml[p_xml.index('<w:r>'):-len('</w:p>')]


def EQ(text, num):
    """Ecuación centrada con su número alineado a la derecha."""
    return ('<w:p><w:pPr><w:keepNext/><w:tabs><w:tab w:val="center" w:pos="4419"/>'
            '<w:tab w:val="right" w:pos="8838"/></w:tabs><w:spacing w:before="80" w:after="120"/></w:pPr>'
            '<w:r><w:tab/></w:r>' + _runs_of(P(text, size=22, italic=True)) +
            '<w:r><w:tab/></w:r>' + _runs_of(P(f'({num})', size=22)) + '</w:p>')


def KT(*a, **k):
    k.setdefault('keep', True)
    return T(*a, **k)


class Figuras:
    def __init__(self, fig_dir, prefix):
        self.dir, self.prefix, self.images = fig_dir, prefix, []

    def __call__(self, archivo, ancho_cm, leyenda):
        rid = f'rId{self.prefix}F{len(self.images) + 1}'
        self.images.append((rid, archivo))
        w, h = Image.open(os.path.join(self.dir, archivo)).size
        cx = int(ancho_cm * 360000)
        cy = int(cx * h / w)
        return [f'<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr>'
                f'{IMG_RUN(rid, cx, cy, 400 + len(self.images), archivo)}</w:p>', CAP(leyenda)]


def ensamblar(tpl, body, figs, out):
    z = zipfile.ZipFile(tpl)
    files = {n: z.read(n) for n in z.namelist()}
    doc = files['word/document.xml'].decode('utf-8')
    b0 = doc.index('<w:body>') + len('<w:body>')
    paras = list(re.finditer(r'<w:p[ >].*?</w:p>', doc[b0:], re.S))
    header = ''.join(m.group(0) for m in paras[:3])  # logo + Universidad, Facultad, Especialización
    sect = re.search(r'<w:sectPr>.*?</w:sectPr>', doc, re.S).group(0)
    doc = doc[:b0] + header + ''.join(body) + sect + '</w:body></w:document>'
    files['word/document.xml'] = doc.encode('utf-8')
    rels = files['word/_rels/document.xml.rels'].decode()
    extra = ''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                    f'relationships/image" Target="media/{fn}"/>' for rid, fn in figs.images)
    files['word/_rels/document.xml.rels'] = rels.replace('</Relationships>', extra + '</Relationships>').encode()
    for _, fn in figs.images:
        files[f'word/media/{fn}'] = open(os.path.join(figs.dir, fn), 'rb').read()
    ct = files['[Content_Types].xml'].decode()
    if 'Extension="png"' not in ct:
        ct = ct.replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
    files['[Content_Types].xml'] = ct.encode()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n, data in files.items():
            zo.writestr(n, data)


def CODE(lines, size=16):
    """Bloque de código monoespaciado con fondo gris (una línea por párrafo)."""
    from xml.sax.saxutils import escape
    out = []
    for i, ln in enumerate(lines):
        last = i == len(lines) - 1
        ppr = ('<w:pPr>' + ('' if last else '<w:keepNext/>') +
               '<w:shd w:val="clear" w:color="auto" w:fill="F3F3F3"/>'
               f'<w:spacing w:before="0" w:after="{120 if last else 0}" w:line="240" w:lineRule="auto"/>'
               '<w:ind w:left="284"/></w:pPr>')
        rpr = ('<w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
               f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>')
        out.append(f'<w:p>{ppr}<w:r>{rpr}<w:t xml:space="preserve">{escape(ln)}</w:t></w:r></w:p>')
    return ''.join(out)
