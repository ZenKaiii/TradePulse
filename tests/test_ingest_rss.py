from tradepulse.ingest.rss import parse_rss_entries


def test_parse_rss_to_canonical_article():
    entries = [
        {
            "title": "Fed hints rate cut path",
            "link": "https://example.com/fed",
            "published": "Mon, 01 Jan 2026 00:00:00 GMT",
            "summary": "A short note",
        }
    ]

    items = parse_rss_entries("Reuters", entries)

    assert items[0].source_name == "Reuters"
    assert items[0].url == "https://example.com/fed"
    assert items[0].title == "Fed hints rate cut path"
