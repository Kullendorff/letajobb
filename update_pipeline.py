"""Move new scan jobs into correct pipeline sections and update counters."""
import re
from pathlib import Path

HTML = Path("/sessions/bold-clever-einstein/mnt/hittajobb/pipeline.html")
content = HTML.read_text(encoding="utf-8")

# --- 1. Remove the entire scan section at the bottom ---
scan_section_pattern = r'<div class="section-label">🔍 Platsbanken-scan.*?</ul>'
scan_match = re.search(scan_section_pattern, content, re.DOTALL)
if scan_match:
    content = content[:scan_match.start()] + content[scan_match.end():]

# --- 2. Build the Gbg job card for Ovärderade ---
gbg_card = '''  <a href="https://arbetsformedlingen.se/platsbanken/annonser/31066372" target="_blank" class="job" data-tags="tech gbg">
    <div class="job-info">
      <div class="job-title">Supporttekniker till utbildningsförvaltningen <span style="color:#f87171;font-size:0.75rem;margin-left:0.5rem">Deadline 2026-06-04</span></div>
      <div class="job-company">Göteborgs kommun - Göteborg</div>
    </div>
    <div class="tags">
      <span class="tag tag-tech">IT Support</span>
      <span class="tag tag-gbg">Göteborg</span>
    </div>
    <span class="arrow">→</span>
  </a>'''

# --- 3. Build the Landskrona job card for EJ AKTUELLA ---
ej_card = '''  <a href="https://arbetsformedlingen.se/platsbanken/annonser/31071371" target="_blank" class="job ej" data-tags="tech ej">
    <div class="job-info">
      <div class="job-title">Project Engineer Electrical & Automation</div>
      <div class="job-company">Hitachi Energy Sweden AB - EJ AKTUELL: Landskrona + el/automation-ingenjör, fel geografi och profil</div>
    </div>
    <div class="tags">
      <span class="tag tag-ej">EJ AKTUELL</span>
      <span class="tag tag-tech">Engineering</span>
    </div>
    <span class="arrow">→</span>
  </a>'''

# --- 4. Insert Gbg job into Ovärderade section (after section label) ---
ovärderade_marker = '🔍 Ovärderade'
ov_match = re.search(r'(🔍 Ovärderade \(\d+\)</div>\s*<ul class="job-list">)', content)
if ov_match:
    insert_pos = ov_match.end()
    content = content[:insert_pos] + "\n" + gbg_card + "\n" + content[insert_pos:]

# --- 5. Insert Landskrona job into EJ AKTUELLA section (after section label) ---
ej_match = re.search(r'(❌ Ej aktuella \(\d+\)</div>\s*<ul class="job-list">)', content)
if ej_match:
    insert_pos = ej_match.end()
    content = content[:insert_pos] + "\n" + ej_card + "\n" + content[insert_pos:]

# --- 6. Update counters ---
# Ovärderade: was in parentheses, now +1 (Gbg job added, Landskrona moved to ej)
# Actually scan added 2 to ovärderade section, now we move 1 to ej. Net: ovärderade +1, ej +1
# But we removed the scan section entirely - so we need to count from scratch

# Count actual jobs
total = len(re.findall(r'target="_blank" class="job', content))
applied = len(re.findall(r'class="job applied"', content))
ej = len(re.findall(r'class="job ej"', content))
done_not_applied = len(re.findall(r'class="job done"', content))
ovärderade = total - applied - ej - done_not_applied

print(f"Total: {total}, Applied: {applied}, Done(utvärderade): {done_not_applied}, Ovärderade: {ovärderade}, Ej: {ej}")
print(f"Sum check: {applied} + {done_not_applied} + {ovärderade} + {ej} = {applied + done_not_applied + ovärderade + ej}")

# Update section labels
content = re.sub(r'✅ Ansökta \(\d+\)', f'✅ Ansökta ({applied})', content)
content = re.sub(r'🔍 Ovärderade \(\d+\)', f'🔍 Ovärderade ({ovärderade})', content)
content = re.sub(r'❌ Ej aktuella \(\d+\)', f'❌ Ej aktuella ({ej})', content)

# Update stats header
content = re.sub(r'(<span class="num">)\d+(</span> jobb totalt)', rf'\g<1>{total}\2', content)
content = re.sub(r'(<span class="num">)\d+(</span> ansökta)', rf'\g<1>{applied}\2', content)
content = re.sub(r'(<span class="num">)\d+(</span> ej aktuella)', rf'\g<1>{ej}\2', content)

# Update footer
content = re.sub(
    r'\d+ ansökningar, \d+ utvärderade, \d+ ovärderade, \d+ ej aktuella',
    f'{applied} ansökningar, {done_not_applied} utvärderade, {ovärderade} ovärderade, {ej} ej aktuella',
    content
)

HTML.write_text(content, encoding="utf-8")
print("✅ pipeline.html uppdaterad")
