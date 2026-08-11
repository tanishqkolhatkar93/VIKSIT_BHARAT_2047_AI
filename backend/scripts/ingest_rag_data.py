import csv
import io
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = PROJECT_ROOT / "RAG_Data"
OUTPUT_PATH = PROJECT_ROOT / "backend" / "app" / "data" / "knowledge_documents.json"
CURRENT_YEAR = "2026"

CHUNK_SIZE = 1800
CHUNK_OVERLAP = 120
MAX_CHUNKS_PER_PDF = 25

VALID_CATEGORIES = {
    "Agriculture",
    "Education",
    "Healthcare",
    "Employment",
    "Technology",
    "Infrastructure",
    "Environment",
    "Climate",
    "Smart Cities",
    "Rural Development",
    "Women Empowerment",
    "Entrepreneurship",
    "Digital India",
    "Manufacturing",
    "Transportation",
    "Energy",
    "Space & Science",
}

CATEGORY_HINTS = [
    (("school", "education", "skilling", "credential", "enrolment", "enrollment", "nep", "literacy", "learning"), "Education"),
    (("health", "hospital", "medical", "ndhm", "ayurveda", "life-expectancy", "doctor", "physician", "nutrition", "vaccine"), "Healthcare"),
    (("semiconductor", "manufacturing", "make in india"), "Manufacturing"),
    (("energy", "electricity", "solar", "wind", "power", "coal", "renewable", "emission", "co2", "carbon"), "Energy"),
    (("climate", "cooling", "greenhouse", "net zero", "global warming"), "Climate"),
    (("city", "urban", "municipal", "smart city"), "Smart Cities"),
    (("farm", "agriculture", "crop", "agri", "kisan", "irrigation", "food security"), "Agriculture"),
    (("employment", "labour", "labor", "plfs", "job", "workforce", "unemploy"), "Employment"),
    (("digital", "internet", "dpi", "connectivity", "broadband", "e-governance", "technology", "semicon", "research", "science", "bioeconomy"), "Technology"),
    (("fiscal", "investment", "economy", "gdp", "trade", "export", "import", "finance", "budget", "infrastructure", "rail", "road", "transport"), "Infrastructure"),
]

FALLBACK_CATEGORY = "Technology"

OWID_DIRECTORY = {
    "children-born-per-woman": ("Fertility", "Healthcare", "children born per woman", "fertility"),
    "co2-emissions-per-capita": ("CO2 emissions per capita", "Climate", "CO2 emissions", "carbon dioxide"),
    "education-spending": ("Government spending on education", "Education", "education spending", "public expenditure on education"),
    "life-expectancy": ("Life expectancy", "Healthcare", "life expectancy", "longevity"),
    "population": ("Population", "Infrastructure", "population", "demographics"),
    "population-growth-rates": ("Population growth rate", "Infrastructure", "population growth", "demographics"),
    "primary-enrollment-selected-countries": ("Primary school enrollment", "Education", "primary enrollment", "school enrollment"),
}

WORLD_BANK_HEADLINES = (
    "gdp (current us$)",
    "gdp growth (annual %)",
    "gdp per capita (current us$)",
    "gdp per capita, ppp",
    "gni per capita, atlas method",
    "inflation, consumer prices",
    "poverty headcount ratio at $",
    "unemployment, total",
    "population, total",
    "population growth (annual %)",
    "urban population (% of total population)",
    "life expectancy at birth",
    "fertility rate, total",
    "birth rate, crude",
    "death rate, crude",
    "mortality rate, under-5",
    "co2 emissions",
    "electric power consumption",
    "access to electricity",
    "access to clean fuels",
    "renewable electricity output",
    "energy use",
    "mobile cellular subscriptions",
    "individuals using the internet",
    "literacy rate, adult",
    "school enrollment, primary",
    "school enrollment, secondary",
    "school enrollment, tertiary",
    "agriculture, forestry, and fishing, value added",
    "industry (including construction), value added",
    "services, value added",
    "foreign direct investment, net inflows",
    "exports of goods and services",
    "imports of goods and services",
    "personal remittances, received",
    "physicians",
    "hospital beds",
    "research and development expenditure",
    "patent applications, residents",
    "high-technology exports",
    "rail lines",
    "air transport, passengers carried",
    "container port traffic",
    "forest area (% of land area)",
    "agricultural land (% of land area)",
    "improved water source",
    "improved sanitation facilities",
    "maternal mortality ratio",
)


def summarize_world_bank(csv_path: Path, indicator_meta: dict[str, dict]) -> list[dict]:
    lines = csv_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if "Indicator Name" in line and "1960" in line:
            header_index = index
            break
    if header_index is None:
        return []

    reader = csv.reader(io.StringIO("\n".join(lines[header_index:])))
    header = next(reader)
    year_columns = [h for h in header[4:] if h.isdigit()]
    by_indicator: dict[str, dict] = {}
    for row in reader:
        if len(row) < 5:
            continue
        indicator_name = row[2].strip()
        indicator_code = row[3].strip()
        low = indicator_name.lower()
        if not any(pattern in low for pattern in WORLD_BANK_HEADLINES):
            continue
        values = row[4:4 + len(year_columns)]
        latest_year, latest_value = "", ""
        for index in range(len(year_columns) - 1, -1, -1):
            value = values[index].strip() if index < len(values) else ""
            if value and value not in {"0", ".", ""}:
                try:
                    float(value)
                except ValueError:
                    continue
                latest_year = year_columns[index]
                latest_value = value
                break
        if not latest_value or int(latest_year) < 2010:
            continue
        existing = by_indicator.get(indicator_code)
        if existing and int(existing["latest_year"]) >= int(latest_year):
            continue
        by_indicator[indicator_code] = {
            "name": indicator_name,
            "code": indicator_code,
            "latest_year": latest_year,
            "latest_value": latest_value,
        }

    documents = []
    for record in sorted(by_indicator.values(), key=lambda r: r["name"].lower()):
        content = (
            f"World Bank World Development Indicators: {record['name']}. For India, the latest recorded value was "
            f"{record['latest_value']} in {record['latest_year']}."
        )
        documents.append(
            {
                "title": f"{record['name']} (India)",
                "source": "World Bank, World Development Indicators",
                "url": "https://data.worldbank.org/country/india",
                "category": "Infrastructure",
                "state": "All India",
                "date": record["latest_year"],
                "content": content,
            }
        )
    return documents

YEAR_RE = re.compile(r"(19|20)\d{2}")


def human_title(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"\.(pdf|csv)$", "", stem, flags=re.IGNORECASE)
    parts = [p for p in re.split(r"[-_.\s]+", stem) if p]
    words = []
    for part in parts:
        if re.fullmatch(r"(Q[1-4])?(FY)?\d{2,4}", part, flags=re.IGNORECASE):
            continue
        words.append(part.lower())
    title = " ".join(words) if words else Path(filename).stem
    return title[:120].capitalize()


def infer_category(name: str, content: str = "") -> str:
    haystack = f"{name} {content}".lower()
    for keywords, category in CATEGORY_HINTS:
        if any(keyword in haystack for keyword in keywords):
            return category
    return FALLBACK_CATEGORY


def detect_year(text: str) -> str:
    match = YEAR_RE.search(text)
    if match:
        year = int(match.group(0))
        if 1947 <= year <= 2100:
            return str(year)
    return CURRENT_YEAR


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    return text.strip()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            split_at = text.rfind(" ", start + int(size * 0.7), end)
            if split_at > start:
                end = split_at
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
        if len(chunks) >= MAX_CHUNKS_PER_PDF:
            break
    return chunks


PDF_SOURCE_HINTS = [
    ("ndhm", "National Digital Health Mission, Ministry of Health"),
    ("plfs", "Ministry of Statistics and Programme Implementation (MoSPI)"),
    ("dpi", "NITI Aayog - Digital Public Infrastructure"),
    ("semiconductor", "NITI Aayog - Future of India Semiconductor Industry"),
]

GENERIC_PDF_TOOLS = ("ilovepdf", "adobe", "pdfium", "scanner", "pdfsam", "in design", "indesign", "powerpoint", "microsoft")


def pdf_source(pdf_path: Path, meta: dict) -> str:
    name = pdf_path.name.lower()
    for marker, source in PDF_SOURCE_HINTS:
        if marker in name:
            return source
    author = (meta.get("/Author") or "").strip()
    if author and not any(tool in author.lower() for tool in GENERIC_PDF_TOOLS):
        return author
    return "Government of India policy report (RAG_Data)"


def ingest_pdf(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    meta = reader.metadata or {}
    source = pdf_source(pdf_path, meta)
    base_title = human_title(pdf_path.name)
    category = infer_category(pdf_path.name)
    year = detect_year(f"{pdf_path.name} {source}")

    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    text = clean_text("\n".join(pages))

    if len(text) < 200:
        return []

    chunks = chunk_text(text)
    docs = []
    for index, chunk in enumerate(chunks):
        title = base_title if len(chunks) == 1 else f"{base_title} (Part {index + 1})"
        docs.append(
            {
                "title": title,
                "source": str(source),
                "url": "",
                "category": category,
                "state": "All India",
                "date": year,
                "content": chunk,
            }
        )
    return docs


def read_metadata(meta_path: Path) -> dict:
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest_value(rows: list[list[str]], value_index: int) -> tuple[str, str]:
    for row in reversed(rows):
        value = row[value_index].strip() if len(row) > value_index else ""
        if value and value not in {"", "0", "."}:
            return value, row[2].strip()
    return "", ""


def summarize_owid_folder(folder: Path) -> list[dict]:
    info = OWID_DIRECTORY.get(folder.name)
    if not info:
        return []
    display_name, category, keyword, keyword_plural = info
    csv_path = next(folder.glob("*.csv"), None)
    if csv_path is None:
        return []

    meta = read_metadata(next(folder.glob("*.metadata.json"), Path("__missing__")))
    citation = ""
    description = ""
    unit = ""
    for column in (meta.get("columns") or {}).values():
        citation = column.get("citationShort") or ""
        description = column.get("descriptionShort") or ""
        unit = column.get("unit") or ""
        break

    rows = []
    with csv_path.open(encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            rows.append(row)

    india_rows = [row for row in rows if (row.get("Entity") or "").strip().lower() == "india"]
    if not india_rows:
        india_rows = rows

    value_keys = [k for k in india_rows[0].keys() if k not in {"Entity", "Code", "Year"}]
    meta_columns = list((meta.get("columns") or {}).values())
    fallback_label = (meta_columns[0].get("titleShort") or meta_columns[0].get("descriptionShort") or "") if len(meta_columns) == 1 else ""
    column_labels = {}
    for key, column in (meta.get("columns") or {}).items():
        column_labels[key] = column.get("titleShort") or column.get("descriptionShort") or key
    text_parts = []
    if description:
        text_parts.append(f"Indicator: {description}")
    if citation:
        text_parts.append(f"Source: {citation}.")

    for key in value_keys:
        points = []
        for row in india_rows:
            raw = (row.get(key) or "").strip()
            if not raw:
                continue
            year = row["Year"]
            try:
                value = float(raw)
            except ValueError:
                continue
            points.append((int(year), value))
        if not points:
            continue
        points.sort()
        latest_year, latest_value = points[-1]
        earliest_year, earliest_value = points[0]
        values = [v for _, v in points]
        lowest, highest = min(values), max(values)
        label = column_labels.get(key, key)
        if label == "all years" and fallback_label:
            label = fallback_label
        text_parts.append(
            f"For India, {label}: {latest_value:g} in {latest_year}, ranging from {lowest:g} ({min(points)[0]}) "
            f"to {highest:g} ({max(points, key=lambda p: p[1])[0]}) across {earliest_year}-{latest_year} "
            f"({len(points)} data points)."
        )

    if not text_parts:
        return []
    content = " ".join(text_parts)
    title = f"{display_name} - India"
    return [
        {
            "title": title,
            "source": citation or "Our World in Data",
            "url": "",
            "category": category,
            "state": "All India",
            "date": detect_year(f"{csv_path.name} {meta.get('dateDownloaded', '')}"),
            "content": content,
        }
    ]


def summarize_owid_energy(csv_path: Path) -> list[dict]:
    india_rows = []
    with csv_path.open(encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            if (row.get("country") or "").strip().lower() == "india":
                india_rows.append(row)
    if not india_rows:
        return []

    india_rows.sort(key=lambda r: int(r["year"] or 0))
    latest = india_rows[-1]
    year = latest["year"]

    def fmt(value: str) -> str:
        value = (value or "").strip()
        try:
            return f"{float(value):,.2f}"
        except ValueError:
            return value or "not available"

    snapshot = (
        f"For India in {year}: population {fmt(latest.get('population'))}; primary energy consumption "
        f"{fmt(latest.get('primary_energy_consumption'))} terawatt-hours; energy per capita "
        f"{fmt(latest.get('energy_per_capita'))} kWh; electricity generation {fmt(latest.get('electricity_generation'))} TWh; "
        f"per capita electricity {fmt(latest.get('per_capita_electricity'))} kWh. Electricity mix shares: renewables "
        f"{fmt(latest.get('renewables_share_elec'))}%, solar {fmt(latest.get('solar_share_elec'))}%, wind "
        f"{fmt(latest.get('wind_share_elec'))}%, hydro {fmt(latest.get('hydro_share_elec'))}%, nuclear "
        f"{fmt(latest.get('nuclear_share_elec'))}%, coal {fmt(latest.get('coal_share_elec'))}%, gas "
        f"{fmt(latest.get('gas_share_elec'))}%. Renewables share of primary energy "
        f"{fmt(latest.get('renewables_share_energy'))}%. Greenhouse gas emissions {fmt(latest.get('greenhouse_gas_emissions'))} "
        f"million tonnes CO2-equivalent. Source: Our World in Data / Ember (Energy dataset)."
    )

    trend_parts = [f"India energy trends by year (Our World in Data / Ember):"]
    for row in india_rows:
        ryear = row["year"]
        if int(ryear) % 5 == 0 or ryear == year:
            trend_parts.append(
                f"{ryear}: renewables share of electricity {fmt(row.get('renewables_share_elec'))}%, "
                f"coal share {fmt(row.get('coal_share_elec'))}%, primary energy {fmt(row.get('primary_energy_consumption'))} TWh, "
                f"greenhouse gas emissions {fmt(row.get('greenhouse_gas_emissions'))} Mt CO2e."
            )
    content = f"{snapshot}\n\n{' '.join(trend_parts)}"
    return [
        {
            "title": "India Energy Data",
            "source": "Our World in Data / Ember",
            "url": "https://ourworldindata.org/energy",
            "category": "Energy",
            "state": "All India",
            "date": year,
            "content": content,
        }
    ]


def load_indicator_metadata(meta_path: Path) -> dict[str, dict]:
    result = {}
    if not meta_path.exists():
        return result
    with meta_path.open(encoding="utf-8-sig", errors="replace") as handle:
        for row in csv.DictReader(handle):
            code = row.get("INDICATOR_CODE") or ""
            if code:
                result[code] = row
    return result


def main() -> None:
    documents: list[dict] = []
    if OUTPUT_PATH.exists():
        documents = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    existing_titles = {doc["title"] for doc in documents}
    added = 0
    skipped = []

    for pdf_path in sorted(RAG_DIR.glob("*.pdf")):
        docs = ingest_pdf(pdf_path)
        fresh = [doc for doc in docs if doc["title"] not in existing_titles]
        documents.extend(fresh)
        existing_titles.update(doc["title"] for doc in fresh)
        added += len(fresh)
        skipped.append((pdf_path.name, len(docs), len(fresh)))

    for folder in sorted(RAG_DIR.iterdir()):
        if not folder.is_dir() or folder.name == "archive":
            continue
        docs = summarize_owid_folder(folder)
        fresh = [doc for doc in docs if doc["title"] not in existing_titles]
        documents.extend(fresh)
        existing_titles.update(doc["title"] for doc in fresh)
        added += len(fresh)

    energy_csv = RAG_DIR / "owid-energy-data.csv"
    if energy_csv.exists():
        docs = summarize_owid_energy(energy_csv)
        fresh = [doc for doc in docs if doc["title"] not in existing_titles]
        documents.extend(fresh)
        existing_titles.update(doc["title"] for doc in fresh)
        added += len(fresh)

    wb_csv = RAG_DIR / "World_Bank_Data" / "API_IND_DS2_en_csv_v2_1896.csv"
    wb_indicator_meta = RAG_DIR / "World_Bank_Data" / "Metadata_Indicator_API_IND_DS2_en_csv_v2_1896.csv"
    if wb_csv.exists():
        indicator_meta = load_indicator_metadata(wb_indicator_meta)
        docs = summarize_world_bank(wb_csv, indicator_meta)
        fresh = [doc for doc in docs if doc["title"] not in existing_titles]
        documents.extend(fresh)
        existing_titles.update(doc["title"] for doc in fresh)
        added += len(fresh)

    documents.sort(key=lambda doc: (doc["category"], doc["title"].lower()))
    OUTPUT_PATH.write_text(json.dumps(documents, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(documents)} documents to {OUTPUT_PATH}")
    print(f"Added {added} new documents from RAG_Data.")
    for name, total, fresh in skipped:
        print(f"  PDF: {name} -> {total} chunks ({fresh} new)")


if __name__ == "__main__":
    main()
