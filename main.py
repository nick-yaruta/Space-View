from flask import Flask, render_template, request, jsonify
import wikipediaapi
import re
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NASA_KEY = os.getenv("NASA_API_KEY")

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MySpaceApp/1.0 (contact@example.com)',
    language='uk',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/planet')
def planet():
    return render_template('planet.html')


@app.route('/get_planet_data', methods=['POST'])
def get_planet_data():
    data = request.json
    planet_name = data.get('planet', 'Земля')

    PLANET_MAP = {
        "Меркурій": "Меркурій (планета)",
        "Венера": "Венера (планета)",
        "Земля": "Земля",
        "Марс": "Марс (планета)",
        "Юпітер": "Юпітер (планета)",
        "Сатурн": "Сатурн (планета)",
        "Уран": "Уран (планета)",
        "Нептун": "Нептун (планета)",
        "Сонце": "Сонце"
    }

    wiki_name = PLANET_MAP.get(planet_name, planet_name)
    page = wiki_wiki.page(wiki_name)

    if not page.exists():
        return jsonify({'success': False, 'error': 'Планету не знайдено'})

    # Опис
    paragraphs = page.text.split("\n")
    summary = "\n".join(paragraphs[:3])
    text = page.text

    # Характеристики
    def extract_strict(keys):
        for key in keys:
            pattern = rf"{key}\s*[:=]\s*([\d\s.,+\-]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "—"

    distance = extract_strict([
        "Середня відстань від Сонця",
        "Відстань від Сонця"
    ])

    radius = extract_strict([
        "Екваторіальний радіус",
        "Середній радіус",
        "Радіус"
    ])

    day_length = extract_strict([
        "Період обертання",
        "Тривалість доби",
        "Сидеричний період обертання"
    ])

    temperature = extract_strict([
        "Температура поверхні",
        "Температура",
        "Середня температура"
    ])

    p_type = "Планета Сонячної системи" if "(планета)" in wiki_name else "Небесне тіло"

    # NASA IMAGES
    images = get_nasa_images(planet_name)

    return jsonify({
        'success': True,
        'name': page.title,
        'type': p_type,
        'description': summary,
        'stats': {
            'distance': distance,
            'day': day_length,
            'radius': radius,
            'temp': temperature
        },
        'images': images
    })


def get_nasa_images(planet):
    NASA_MAP = {
        "Меркурій": "Mercury",
        "Венера": "Venus",
        "Земля": "Earth",
        "Марс": "Mars",
        "Юпітер": "Jupiter",
        "Сатурн": "Saturn",
        "Уран": "Uranus",
        "Нептун": "Neptune",
        "Сонце": "Sun"
    }

    query = NASA_MAP.get(planet, planet)

    url = (
        "https://images-api.nasa.gov/search"
        f"?q={query}&media_type=image"
        "&page=1"
    )

    try:
        res = httpx.get(url)
        data = res.json()

        items = data.get("collection", {}).get("items", [])
        photos = []

        for item in items:
            links = item.get("links")
            if not links:
                continue

            href = links[0].get("href", "")

            # фільтр сміття
            lower = href.lower()
            bad = ["movie", "logo", "poster", "drawing", "art", "cartoon"]
            if any(b in lower for b in bad):
                continue

            photos.append(href)

            if len(photos) >= 4:
                break

        return photos

    except Exception as e:
        print("NASA ERROR:", e)
        return []



if __name__ == '__main__':
    app.run(debug=True)