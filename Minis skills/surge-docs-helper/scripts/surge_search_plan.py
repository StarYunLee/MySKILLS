#!/usr/bin/env python3
import json
import sys
import urllib.parse

SITES = {
    'manual': 'site:manual.nssurge.com',
    'kb': 'site:kb.nssurge.com',
    'community': 'site:community.nssurge.com',
    'official': '(site:manual.nssurge.com OR site:kb.nssurge.com OR site:community.nssurge.com)'
}


def build(query, scope='official'):
    scope_expr = SITES.get(scope, SITES['official'])
    q = f'{scope_expr} {query}'.strip()
    return {
        'scope': scope,
        'query': query,
        'search_query': q,
        'google': 'https://www.google.com/search?q=' + urllib.parse.quote(q),
        'bing': 'https://www.bing.com/search?q=' + urllib.parse.quote(q),
        'brave': 'https://search.brave.com/search?q=' + urllib.parse.quote(q),
    }


def main():
    if len(sys.argv) < 2:
        print('usage: surge_search_plan.py <query> [official|manual|kb|community]')
        sys.exit(1)
    query = sys.argv[1]
    scope = sys.argv[2] if len(sys.argv) >= 3 else 'official'
    print(json.dumps(build(query, scope), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
