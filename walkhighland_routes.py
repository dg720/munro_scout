import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

INPUT_FILE = "munro_list.json"
OUTPUT_FILE = "munro_descriptions.json"


def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment for silent run
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_route_page_url(driver):
    try:
        h2s = driver.find_elements(By.TAG_NAME, "h2")
        for h2 in h2s:
            if "Detailed route description and map" in h2.text:
                sibling = h2.find_element(By.XPATH, "following-sibling::p[1]/b/a")
                return sibling.get_attribute("href")
    except Exception:
        pass
    return None


def extract_description_from_route_page(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "walk_desc"))
        )
        # Extract main route description from stage paragraphs
        desc_paragraphs = driver.find_elements(By.CSS_SELECTOR, "#walk_desc .desc p")
        description = "\n\n".join(
            p.text.strip() for p in desc_paragraphs if p.text.strip()
        )

        # Extract summary section from the h2 + p block
        summary = ""
        try:
            summary_heading = driver.find_element(
                By.XPATH, "//h2[normalize-space(text())='Summary']"
            )
            summary_paragraph = summary_heading.find_element(
                By.XPATH, "following-sibling::p[1]"
            )
            summary = summary_paragraph.text.strip()
        except Exception:
            pass

        return summary, description
    except Exception as e:
        print(f"⚠️ Failed to extract from {url}: {e}")
        return "", ""


def main():
    print("📥 Loading Munro list...")
    munros = load_json(INPUT_FILE)
    existing_data = load_json(OUTPUT_FILE)

    enriched_by_url = {m["url"]: m for m in existing_data if m.get("description")}
    remaining = [m for m in munros if m["url"] not in enriched_by_url]

    print(f"🔗 Total Munros: {len(munros)}")
    print(f"✅ Already processed: {len(enriched_by_url)}")
    print(f"🧭 Remaining: {len(remaining)}\n")

    driver = setup_driver()
    enriched = list(enriched_by_url.values())

    for i, munro in enumerate(remaining, start=len(enriched) + 1):
        name = munro["name"]
        url = munro["url"]
        print(f"📄 [{i}/{len(munros)}] {name}")

        try:
            driver.get(url)
            time.sleep(1)
            route_page_url = get_route_page_url(driver)

            if route_page_url:
                summary, desc = extract_description_from_route_page(
                    driver, route_page_url
                )
            else:
                print(f"⚠️ No route link found on {url}")
                summary, desc = "", ""
        except Exception as e:
            print(f"⚠️ Error processing {url}: {e}")
            summary, desc = "", ""

        enriched.append({**munro, "summary": summary, "description": desc})
        save_json(enriched, OUTPUT_FILE)
        time.sleep(6)

    driver.quit()
    print(f"\n💾 Done. Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
