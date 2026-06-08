import urllib.request, json
url = 'https://api.crossref.org/works?query=reinforcement+learning+intrusion+detection+cyber+security&select=title,author,issued,DOI,container-title&rows=20'
req = urllib.request.Request(url, headers={'User-Agent': 'mailto:test@example.com'})
res = urllib.request.urlopen(req)
data = json.loads(res.read())
out = []
for item in data['message']['items']:
    try:
        authors = ', '.join([a.get('family', '') for a in item.get('author', [])])
        title = item.get('title', [''])[0]
        journal = item.get('container-title', [''])[0]
        doi = item.get('DOI', '')
        year = item.get('issued', {}).get('date-parts', [[2021]])[0][0]
        if authors and title and journal:
            out.append(f"{authors}. \"{title}\", {journal} ({year}). DOI: {doi}")
    except Exception:
        pass
with open('new_refs.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
