import json
import urllib.parse
import urllib.request


def fetch_json(url: str, params: dict | None = None) -> dict:
	if params:
		query = urllib.parse.urlencode(params)
		url = f"{url}?{query}"

	request = urllib.request.Request(url, headers={"Accept": "application/json"})
	with urllib.request.urlopen(request, timeout=30) as response:
		charset = response.headers.get_content_charset() or "utf-8"
		payload = response.read().decode(charset)

	return json.loads(payload)


def iter_votacoes(base_url: str, params: dict) -> list[dict]:
	url = base_url
	all_items: list[dict] = []

	while url:
		data = fetch_json(url, params)
		params = None
		items = data.get("dados", [])
		all_items.extend(items)

		next_url = None
		for link in data.get("links", []):
			if link.get("rel") == "next":
				next_url = link.get("href")
				break

		url = next_url

	return all_items


def test_votacoes_nominais(max_items: int = 200) -> dict:
	base_url = "https://dadosabertos.camara.leg.br/api/v2/votacoes"
	params = {
		"ordem": "DESC",
		"ordenarPor": "dataHoraRegistro",
		"itens": 100,
	}

	all_votacoes = iter_votacoes(base_url, params)
	all_votacoes = all_votacoes[:max_items]

	with_data = []
	without_data = []

	for item in all_votacoes:
		votacao_id = item.get("id")
		if not votacao_id:
			continue

		votos_url = f"{base_url}/{votacao_id}/votos"
		votos = fetch_json(votos_url)
		if votos.get("dados"):
			with_data.append(votacao_id)
		else:
			without_data.append(votacao_id)

	return {
		"total_checked": len(with_data) + len(without_data),
		"with_data": with_data,
		"without_data": without_data,
	}

def main():
	result = test_votacoes_nominais(max_items=20)
	print(json.dumps(result, indent=2, ensure_ascii=True))

if __name__ == "__main__":    main()