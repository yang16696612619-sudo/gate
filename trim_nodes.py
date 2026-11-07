# -*- coding: utf-8 -*-
"""Trim public/nodes.txt to the best KEEP nodes using public/data.json ping.

Kept nodes are chosen by ascending ping among successful checks (residential
first, matching the pipeline's own preference), then nodes.txt is rewritten
preserving its original line order.
"""
import json
import os
import sys

PUB = 'public'
KEEP = 15


def main():
    nodes_file = os.path.join(PUB, 'nodes.txt')
    data_file = os.path.join(PUB, 'data.json')
    if not os.path.exists(nodes_file) or not os.path.exists(data_file):
        print('SKIP missing nodes.txt/data.json')
        return 0

    with open(data_file, encoding='utf-8') as fh:
        data = json.load(fh)

    candidates = []
    for country in (data.get('countries') or {}).values():
        residential = country.get('residential') or 0
        for node in country.get('nodes') or []:
            if not node.get('success'):
                continue
            ping = node.get('ping')
            if not isinstance(ping, (int, float)):
                continue
            cat = node.get('category') or ''
            is_res = cat.startswith('residential') or bool(residential and cat == '')
            candidates.append((0 if is_res else 1, ping, node.get('link')))

    candidates.sort()
    keep_links = {link for _, _, link in candidates[:KEEP] if link}

    with open(nodes_file, encoding='utf-8') as fh:
        lines = [ln.rstrip('\n') for ln in fh if ln.strip()]

    kept = []
    for ln in lines:
        link = ln.split('$', 1)[1] if '$' in ln else ''
        if link in keep_links:
            kept.append(ln)
    if len(kept) < min(KEEP, len(keep_links)):
        kept = lines[:KEEP]

    with open(nodes_file, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(kept[:KEEP]) + '\n')
    print(f'TRIM {len(lines)} -> {len(kept[:KEEP])}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
