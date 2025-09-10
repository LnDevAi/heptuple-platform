#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest JSON datasets (hadiths, fiqh rulings, invocations) into PostgreSQL using
existing SQLAlchemy models from backend.database.

Usage examples:

  # Use DATABASE_URL or DB_* env vars
  python scripts/ingest_json.py \
    --hadiths db/json_templates/hadiths.json \
    --fiqh db/json_templates/fiqh_rulings.json \
    --invocations db/json_templates/invocations.json

Environment:
  - DATABASE_URL or DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database import (
    SessionLocal, Base, engine,
    Hadith, FiqhRuling, Invocation
)


def load_json_array(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if not isinstance(data, list):
            raise ValueError(f"JSON at {file_path} must be an array of objects")
        return data


def coerce_list(value):
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        # Split CSV-like strings
        parts = [v.strip() for v in value.split(",") if v.strip()]
        return parts or None
    return None


def ingest_hadiths(items: List[Dict[str, Any]]) -> int:
    db = SessionLocal()
    count = 0
    try:
        for obj in items:
            hadith = Hadith(
                numero_hadith=str(obj.get("numero_hadith")),
                recueil=obj.get("recueil"),
                livre=obj.get("livre"),
                chapitre=obj.get("chapitre"),
                texte_arabe=obj.get("texte_arabe"),
                texte_francais=obj.get("texte_francais"),
                texte_anglais=obj.get("texte_anglais"),
                narrateur=obj.get("narrateur"),
                degre_authenticite=obj.get("degre_authenticite"),
                dimension_heptuple=obj.get("dimension_heptuple"),
                mots_cles=coerce_list(obj.get("mots_cles")),
                themes=coerce_list(obj.get("themes")),
                contexte_historique=obj.get("contexte_historique"),
            )
            db.add(hadith)
            count += 1
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def ingest_fiqh(items: List[Dict[str, Any]]) -> int:
    db = SessionLocal()
    count = 0
    try:
        for obj in items:
            ruling = FiqhRuling(
                rite=obj.get("rite"),
                topic=obj.get("topic"),
                question=obj.get("question"),
                ruling_text=obj.get("ruling_text"),
                evidences=coerce_list(obj.get("evidences")),
                sources=coerce_list(obj.get("sources")),
                keywords=coerce_list(obj.get("keywords")),
            )
            db.add(ruling)
            count += 1
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def ingest_invocations(items: List[Dict[str, Any]]) -> int:
    db = SessionLocal()
    count = 0
    try:
        for obj in items:
            inv = Invocation(
                titre=obj.get("titre"),
                texte_arabe=obj.get("texte_arabe"),
                texte_traduit=obj.get("texte_traduit"),
                source=obj.get("source"),
                categories=coerce_list(obj.get("categories")),
                tags=coerce_list(obj.get("tags")),
                temps_recommande=coerce_list(obj.get("temps_recommande")),
            )
            db.add(inv)
            count += 1
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Ingest JSON datasets into PostgreSQL")
    parser.add_argument("--hadiths", help="Path to hadiths JSON array file")
    parser.add_argument("--fiqh", help="Path to fiqh rulings JSON array file")
    parser.add_argument("--invocations", help="Path to invocations JSON array file")
    parser.add_argument("--create-tables", action="store_true", help="Create tables before ingest")
    args = parser.parse_args()

    if args.create_tables:
        Base.metadata.create_all(bind=engine)

    total = 0
    if args.hadiths:
        items = load_json_array(args.hadiths)
        n = ingest_hadiths(items)
        print(f"Inserted hadiths: {n}")
        total += n
    if args.fiqh:
        items = load_json_array(args.fiqh)
        n = ingest_fiqh(items)
        print(f"Inserted fiqh rulings: {n}")
        total += n
    if args.invocations:
        items = load_json_array(args.invocations)
        n = ingest_invocations(items)
        print(f"Inserted invocations: {n}")
        total += n

    if total == 0:
        parser.print_help()


if __name__ == "__main__":
    main()

