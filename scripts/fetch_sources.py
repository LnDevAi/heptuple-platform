#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch and ingest data from external JSON APIs into PostgreSQL.

WARNING: Ensure you have the rights/licence to fetch and store content.

Config file (YAML) example:

hadith_sources:
  - name: hadithapi_sahih_bukhari
    url: https://api.hadithapi.com/v1/hadiths?book=sahih-bukhari&page=1
    headers:
      Authorization: Bearer ${HADITH_API_TOKEN}
    mapping:
      numero_hadith: number
      recueil: book
      texte_arabe: arabic
      texte_francais: french
      degre_authenticite: grade
      narrateur: narrator
      livre: chapter_book
      chapitre: chapter

fiqh_sources: []
invocation_sources: []

Usage:
  python scripts/fetch_sources.py --config db/sources/hadith.yaml --hadiths
"""

import os
import sys
import time
import json
import yaml
import argparse
import requests
from typing import Dict, Any, List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import SessionLocal, Hadith, FiqhRuling, Invocation


def env_expand(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: env_expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [env_expand(v) for v in value]
    return value


def http_get_json(url: str, headers: Dict[str, str] | None = None) -> Any:
    resp = requests.get(url, headers=headers or {}, timeout=30)
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        raise ValueError(f"Response is not JSON from {url}")


def normalize_hadith(item: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    out = {}
    for dst, src in mapping.items():
        out[dst] = item.get(src)
    return out


def upsert_hadiths(items: List[Dict[str, Any]]) -> int:
    db = SessionLocal()
    count = 0
    try:
        for obj in items:
            h = Hadith(
                numero_hadith=str(obj.get("numero_hadith")),
                recueil=obj.get("recueil"),
                livre=obj.get("livre"),
                chapitre=obj.get("chapitre"),
                texte_arabe=obj.get("texte_arabe"),
                texte_francais=obj.get("texte_francais"),
                narrateur=obj.get("narrateur"),
                degre_authenticite=obj.get("degre_authenticite"),
            )
            db.add(h)
            count += 1
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def run_hadith_fetch(config: Dict[str, Any]) -> int:
    total = 0
    for src in config.get("hadith_sources", []) or []:
        url = env_expand(src.get("url"))
        headers = env_expand(src.get("headers") or {})
        mapping = src.get("mapping") or {}
        data = http_get_json(url, headers)
        # try common wrappers
        if isinstance(data, dict):
            if "data" in data:
                data = data["data"]
            elif "hadiths" in data:
                data = data["hadiths"]
        if not isinstance(data, list):
            raise ValueError("Hadith source did not return a list")
        normalized = [normalize_hadith(it, mapping) for it in data]
        total += upsert_hadiths(normalized)
        time.sleep(0.5)
    return total


def main():
    parser = argparse.ArgumentParser(description="Fetch and ingest external sources")
    parser.add_argument("--config", required=True, help="YAML config with sources and mappings")
    parser.add_argument("--hadiths", action="store_true", help="Fetch hadith sources")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    inserted = 0
    if args.hadiths:
        inserted += run_hadith_fetch(cfg)
        print(f"Inserted hadiths: {inserted}")


if __name__ == "__main__":
    main()

