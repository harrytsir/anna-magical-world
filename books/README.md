# Πηγές των βιβλίων (Word)

Δεν δημοσιεύονται στο site (το Netlify δημοσιεύει μόνο το `public/`).

- `petres/petres.md`: Οι Πέτρες του Φάρονγουεστ. Word: `node petres/build.js petres/petres.md petres/toc.json Οι_Πέτρες_του_Φάρονγουεστ.docx` (χρειάζεται `npm i docx`). Το toc.json έχει τις σελίδες των κεφαλαίων.
- `vol1/*.md`: Ιστορίες της Άννας Ι. Word: `python3 ist_build.py templates/vol-template.docx vol1 Οι_Ιστορίες_της_Άννας.docx`
- `vol2/*.md`: Ιστορίες της Άννας ΙΙ. Word: `python3 ist_build2.py templates/vol-template.docx vol2 Οι_Ιστορίες_της_Άννας_ΙΙ.docx "Οι Ιστορίες της Άννας ΙΙ"`, μετά αλλαγή `<w:t>I</w:t>` σε `<w:t>II</w:t>` στο word/header1.xml.
- `zornak/`: Η ιστορία του Ζόρνακ. Word: `python3 zornak/zornak_build.py zornak/template.docx Η_ιστορία_του_Ζόρνακ.docx` (το κείμενο είναι μέσα στο script).

Κύρια πηγή της ιστορίας είναι το artifact «Ο Μαγικός Κόσμος της Άννας» στο Claude (https://claude.ai/artifact/T4tkisSmnYj85yHYk52SRk). Το `public/` ξαναχτίζεται από εκεί με το `tools/build.py`.
