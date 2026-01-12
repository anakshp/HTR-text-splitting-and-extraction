import pandas as pd
import json
import re
from openai import OpenAI

# --- CONFIGURATION ---
OPENAI_API_KEY = "YOUR_API_KEY_HERE"
INPUT_CSV = "verdict_output.csv"
OUTPUT_CSV = "Extracted_output.csv"

client = OpenAI(api_key=OPENAI_API_KEY)

# --- LOAD DATA ---
df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
df = df[df["Line"].notna() & (df["Line"].str.strip() != "")]

df_grouped = df.groupby("Verdict").agg({
    "Line": lambda x: "\n".join(x.astype(str)),
    "Page Name": "first"
}).reset_index()


def extract_information(verdict_text, scannummer="N/B", vonnisnummer="N/B"):
    prompt = """
Haal de volgende informatie uit onderstaand vonnis en geef deze terug als een JSON-object.
Als een gegeven niet voorkomt, gebruik 'N/B'.

{JSON_SCHEMA}

Vonnistekst:
""".replace("{JSON_SCHEMA}", """
{
  "Scannummer": "N/B",
  "Rechtbank": "N/B",
  "Vonnisnummer": "N/B",
  "Rolnummer": "N/B",
  "Vonnisdatum in het format JJJJ-MM-DD": "N/B",
  "Vonnis in vijf trefwoorden": "N/B",
  "Samenvatting in maximaal 150 woorden": "N/B",
  "Locatie delict": "N/B",
  "Datum delict_start in het format JJJJ-MM-DD": "N/B",
  "Datum delict_end in het format JJJJ-MM-DD": "N/B",
  "Delict soort": "N/B",
  "Gedaagde_volledige naam": "N/B",
  "Gedaagde_leeftijd": "N/B",
  "Gedaagde_beroep": "N/B",
  "Gedaagde_woonplaats": "N/B",
  "Gedaagde_Strafmaat": "N/B",
  "Benadeelde_volledige naam": "N/B",
  "Benadeelde_leeftijd": "N/B",
  "Benadeelde_beroep": "N/B",
  "Benadeelde_woonplaats": "N/B",
  "Getuige_volledige naam": "N/B",
  "Getuige_leeftijd": "N/B",
  "Getuige_beroep": "N/B",
  "Getuige_woonplaats": "N/B"
}
""")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Je extraheert gestructureerde gegevens uit Nederlandse vonnissen en retourneert alleen JSON."},
                {"role": "user", "content": prompt + verdict_text}
            ]
        )

        content = response.choices[0].message.content
        match = re.search(r"\{[\s\S]*\}", content)

        if match:
            parsed = json.loads(match.group())
            parsed["Scannummer"] = scannummer
            parsed["Vonnisnummer"] = vonnisnummer
            return parsed

    except Exception as e:
        print(f"Error processing verdict {vonnisnummer}: {e}")

    return {"Scannummer": scannummer, "Vonnisnummer": vonnisnummer}


results = []

for _, row in df_grouped.iterrows():
    info = extract_information(
        row["Line"],
        scannummer=row["Page Name"],
        vonnisnummer=row["Verdict"]
    )
    results.append(info)

df_result = pd.DataFrame(results)
df_result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"Extraction saved to {OUTPUT_CSV}")
