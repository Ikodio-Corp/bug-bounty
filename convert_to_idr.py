#!/usr/bin/env python3
import re

# Read file
with open('PRICING_STRATEGY_COMPLETE.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Rate: Rp 15,500/USD
rate = 15500

# Remove USD equivalents that are in parentheses (setara $XX)
content = re.sub(r'\s*\(setara \$[\d,]+/?(month|year|bulan|tahun)?\)', '', content)

# Remove standalone USD mentions like "/ $XX"
content = re.sub(r'\s*/\s*\$[\d,]+', '', content)

# Remove USD in parentheses like "($XXX)"
content = re.sub(r'\s*\(\$[\d,\.]+[KMB]?\)', '', content)

# Convert simple patterns like "$X.XM" to Rupiah
def convert_millions(match):
    value = float(match.group(1).replace(',', ''))
    unit = match.group(2)
    if unit == 'K':
        idr_value = value * 1000 * rate / 1_000_000_000  # Convert to Miliar
        return f"Rp {idr_value:.1f} Miliar"
    elif unit == 'M':
        idr_value = value * 1_000_000 * rate / 1_000_000_000  # Convert to Miliar
        return f"Rp {idr_value:.1f} Miliar"
    elif unit == 'B':
        idr_value = value * 1_000_000_000 * rate / 1_000_000_000  # Convert to Trilun
        return f"Rp {idr_value:.1f} Triliun"
    return match.group(0)

content = re.sub(r'\$([0-9,.]+)([KMB])', convert_millions, content)

# Convert remaining simple USD amounts like $500, $1,000, etc
def convert_simple(match):
    value = int(match.group(1).replace(',', ''))
    if value >= 1_000_000:  # Millions
        idr_value = value * rate / 1_000_000
        return f"Rp {idr_value:.0f} Juta"
    elif value >= 1_000:  # Thousands
        idr_value = value * rate / 1_000
        if idr_value >= 1000:
            return f"Rp {idr_value/1000:.1f} Juta"
        return f"Rp {idr_value:.0f} Ribu"
    else:
        idr_value = value * rate
        if idr_value >= 1_000_000:
            return f"Rp {idr_value/1_000_000:.1f} Juta"
        return f"Rp {idr_value:,.0f}"

content = re.sub(r'\$([0-9,]+)', convert_simple, content)

# Write back
with open('PRICING_STRATEGY_COMPLETE.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Conversion complete!")
print("All USD amounts converted to Rupiah at rate Rp 15,500/USD")
