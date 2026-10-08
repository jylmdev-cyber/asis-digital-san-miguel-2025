"""Read original PDF into a private local audit directory, never into public/."""
import json, os
from pathlib import Path
from pypdf import PdfReader

root = Path(os.environ.get('ASIS_SOURCE_DIR', str(Path(__file__).resolve().parents[2]))).resolve()
audit = root / 'audit'
audit.mkdir(exist_ok=True)
(audit / 'renders').mkdir(exist_ok=True)
reader = PdfReader(root / 'ASIS_RIS_SAN_MIGUEL_2025.pdf')
pages = [{'page': i + 1, 'text': page.extract_text() or ''} for i, page in enumerate(reader.pages)]
(audit / 'pdf-pages.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf8')
print(f'Extracted {len(pages)} pages to private local audit.')
