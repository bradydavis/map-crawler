

Map crawler readme · MD
map-crawler
Analyze satellite imagery at scale using AI vision. Give map-crawler a list of coordinates and a natural-language prompt, and it pulls the Mapbox satellite tile for each location, runs it through OpenAI's vision model, and tells you which locations match what you're looking for.

Point it at a thousand coordinates and ask "which of these have a visible construction staging area?" or "flag any site with standing water" — and let the model do the looking.

Why
Reviewing aerial or satellite imagery by hand doesn't scale. Analysts burn hours eyeballing tiles one at a time to answer a simple yes/no question about each site. map-crawler turns that into a batch job: describe what you're hunting for in plain English, hand it the coordinates, and get back a structured answer per location.

Built out of [real GIS / field-operations problems — replace with your own one-line motivation, e.g. "vegetation encroachment along utility rights-of-way"].

How it works
Input — a list of coordinates ([format: CSV? GeoJSON? one lat,lng per line?]) and a text prompt describing what to look for.
Fetch — for each coordinate, map-crawler requests the corresponding Mapbox satellite tile at [zoom level / tile size].
Analyze — each tile is sent to OpenAI's vision model along with your prompt.
Output — results are written to [format: JSON / CSV / console], one row per coordinate with the model's finding [and confidence / bounding info, if any].
Requirements
[Runtime — e.g. Node.js 18+ / Python 3.10+]
A Mapbox access token (get one here)
An OpenAI API key with vision-model access
Setup
bash
# clone
git clone https://github.com/bradydavis/map-crawler.git
cd map-crawler

# install dependencies
[e.g. npm install  /  pip install -r requirements.txt]

# configure credentials
cp .env.example .env
# then edit .env and add:
#   MAPBOX_TOKEN=...
#   OPENAI_API_KEY=...
Usage
bash
[example invocation — replace with the real command, e.g.]
node crawl.js --coords sites.csv --prompt "Is there a visible solar array on this rooftop?"
Example output:

[paste a few real lines of output here — this is the single most
convincing thing you can add. Seeing actual results sells it instantly.]
Configuration
Option	Description	Default
[--zoom]	[Mapbox tile zoom level]	[18]
[--prompt]	[What to look for in each tile]	—
[--out]	[Output file path]	[results.json]
[...]		
Notes & limitations
Imagery is only as current as Mapbox's satellite layer for that region.
Vision-model results are probabilistic — good for triage and prioritization, not [a system of record / legal determinations].
API usage costs money on both Mapbox and OpenAI; batch responsibly.
License
[MIT / Apache-2.0 / etc. — pick one, or delete this section]


