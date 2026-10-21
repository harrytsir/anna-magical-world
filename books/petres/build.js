const fs = require('fs');
const d = require('docx');
const {Document, Packer, Paragraph, TextRun, AlignmentType, Header, Footer, PageNumber, SectionType, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader, PageBreak} = d;
const md = fs.readFileSync(process.argv[2], 'utf8');
const toc = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3],'utf8')) : null;
const out = process.argv[4] || 'book.docx';
const TITLE = 'Οι Πέτρες του Φάρονγουεστ';
const F = 'Times New Roman';
const BODY = 23; // 11.5pt

function inline(text, base={}) {
  // split on *...*
  const runs = []; const parts = text.split(/(\*[^*]+\*)/);
  for (const p of parts) { if (!p) continue;
    if (p.startsWith('*') && p.endsWith('*') && p.length>2) runs.push(new TextRun({text:p.slice(1,-1), italics:!base.italics, font:F, size:base.size||BODY}));
    else runs.push(new TextRun({text:p, italics:!!base.italics, font:F, size:base.size||BODY}));
  }
  return runs;
}

// parse into chapters
const lines = md.split('\n');
const chapters = []; let cur = null; let buf = [];
const flush = () => { if (buf.length && cur) cur.blocks.push(buf.join('\n')); buf = []; };
for (const l of lines) {
  if (l.startsWith('# ')) continue;
  if (l.startsWith('## ')) { flush(); cur = {title: l.slice(3).trim(), blocks: []}; chapters.push(cur); continue; }
  if (l.startsWith('### ')) { flush(); cur.blocks.push({sub: l.slice(4).trim()}); continue; }
  if (l.trim()==='') { flush(); continue; }
  buf.push(l);
}
flush();

function chapterHead(title) {
  let [label, name] = title.split(' — ');
  if (!name) { name = label; label = ''; }
  const ps = [new Paragraph({spacing:{before:2200, after:0}, children:[]})];
  if (label) ps.push(new Paragraph({alignment:AlignmentType.CENTER, spacing:{after:240}, children:[new TextRun({text:label.normalize('NFD').replace(/\u0301/g,'').toUpperCase(), font:F, size:20, characterSpacing:60})]}));
  ps.push(new Paragraph({alignment:AlignmentType.CENTER, spacing:{after:200}, keepNext:true, children:[new TextRun({text:name, font:F, size:36, italics:true})]}));
  ps.push(new Paragraph({alignment:AlignmentType.CENTER, spacing:{after:720}, children:[new TextRun({text:'~ ✦ ~', font:F, size:20})]}));
  return {ps, short: name};
}

const page = {size:{width:8640, height:12960}, margin:{top:1200, bottom:1150, left:1080, right:1080, header:620, footer:620}};
const sections = [];
// Title page
sections.push({properties:{page}, children:[
  new Paragraph({spacing:{before:3400}, children:[]}),
  new Paragraph({alignment:AlignmentType.CENTER, spacing:{after:300}, children:[new TextRun({text:'ΟΙ ΠΕΤΡΕΣ', font:F, size:52, characterSpacing:80})]}),
  new Paragraph({alignment:AlignmentType.CENTER, spacing:{after:300}, children:[new TextRun({text:'του', font:F, size:30, italics:true})]}),
  new Paragraph({alignment:AlignmentType.CENTER, spacing:{after:900}, children:[new TextRun({text:'ΦΑΡΟΝΓΟΥΕΣΤ', font:F, size:52, characterSpacing:80})]}),
  new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({text:'~ ✦ ~', font:F, size:24})]}),
  new Paragraph({alignment:AlignmentType.CENTER, spacing:{before:900}, children:[new TextRun({text:'Μια ιστορία πριν από τις Ιστορίες της Άννας', font:F, size:24, italics:true})]}),
  new Paragraph({children:[new PageBreak()]}),
  ...Array.from({length:12},()=>new Paragraph({children:[]})),
  new Paragraph({ alignment:AlignmentType.CENTER, children:[new TextRun({text:'Για την Άννα', font:F, size:26, italics:true})]}),
]});
// Contents
const tocKids = [new Paragraph({spacing:{before:1400, after:600}, alignment:AlignmentType.CENTER, children:[new TextRun({text:'ΠΕΡΙΕΧΟΜΕΝΑ', font:F, size:26, characterSpacing:60})]})];
chapters.forEach((c,i) => {
  const kids = [new TextRun({text:c.title.replace(' — ', ' · '), font:F, size:21})];
  if (toc) kids.push(new TextRun({text:'\t'+String(toc[i]), font:F, size:21}));
  tocKids.push(new Paragraph({spacing:{after:110}, tabStops:[{type:d.TabStopType.RIGHT, position:6480, leader:'dot'}], children:kids}));
});
sections.push({properties:{page, type:SectionType.NEXT_PAGE}, children:tocKids});

const footer = new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({children:[PageNumber.CURRENT], font:F, size:19})]})]});
const hdr = t => new Header({children:[new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({text:t, font:F, size:17, italics:true, color:'555555'})]})]});
const empty = new Header({children:[new Paragraph({children:[]})]});

const inAppendix = c => c.title.startsWith('Παράρτημα');
chapters.forEach((c, ci) => {
  const {ps, short} = chapterHead(c.title);
  const kids = [...ps]; let first = true;
  for (const b of c.blocks) {
    if (typeof b === 'object') { kids.push(new Paragraph({alignment:AlignmentType.CENTER, spacing:{before:480, after:300}, keepNext:true, children:[new TextRun({text:b.sub, font:F, size:28, italics:true})]})); first = true; continue; }
    if (b.trim()==='---') { kids.push(new Paragraph({alignment:AlignmentType.CENTER, spacing:{before:200, after:200}, children:[new TextRun({text:'*   *   *', font:F, size:BODY})]})); first = true; continue; }
    const ls = b.split('\n');
    const verse = ls.length>1 && ls.every(x=>/\*\\?$/.test(x.trim()));
    const allItal = /^\*[^*]+\*$/.test(b.trim());
    if (verse) {
      const runs = [];
      ls.forEach((x,i)=>{ const t = x.replace(/\\$/,'').trim().replace(/^\*|\*$/g,''); runs.push(new TextRun({text:t, italics:true, font:F, size:BODY, break: i?1:0})); });
      kids.push(new Paragraph({alignment:AlignmentType.CENTER, spacing:{after:240, line:300}, keepLines:true, children:runs})); continue;
    }
    if (allItal && (inAppendix(c) || b.trim()==='*Τέλος.*')) {
      kids.push(new Paragraph({alignment:AlignmentType.CENTER, spacing:{before: b.trim()==='*Τέλος.*'?480:0, after:300}, children:inline(b.trim(), {size: inAppendix(c)?21:BODY})})); first = true; continue;
    }
    kids.push(new Paragraph({alignment:AlignmentType.BOTH, spacing:{after:0, line:290}, indent: first?undefined:{firstLine:340}, widowControl:true, children:inline(ls.join(' '))}));
    first = false;
  }
  sections.push({properties:{page, type:SectionType.NEXT_PAGE, titlePage:true}, headers:{default:hdr(short), even:hdr(TITLE), first:empty}, footers:{default:footer, even:footer, first:footer}, children:kids});
});

const doc = new Document({creator:'', title:TITLE, evenAndOddHeaderAndFooters:true, features:{}, styles:{default:{document:{run:{font:F, size:BODY}}}}, sections});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync(out,b); console.log('ok', chapters.length);});
