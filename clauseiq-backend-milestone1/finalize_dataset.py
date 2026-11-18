#!/usr/bin/env python3
"""
Mix real clauses (LexGLUE UNFAIR-ToS + LEDGAR) into clauses_60k.csv.
Run LOCALLY (needs internet):   pip install datasets pandas
    python mix_real_datasets.py --syn clauses_60k.csv --out clauses_final.csv

Input  columns: id, text, label, label_id, split           (keyword_label already removed)
Output columns: id, text, label, label_id, split, source   (use --drop-source for the first five only)
"""
import argparse, re
import pandas as pd

LABELS = ["Privacy", "Financial", "Cancellation", "Data", "Intellectual Property",
          "Contractual", "Account", "Changes"]
LABEL_ID = {l: i for i, l in enumerate(LABELS)}

# ---- edit these maps if you disagree with a mapping (keys compared case-insensitively) ----
UNFAIR = {  # UNFAIR-ToS tag -> your category
    "limitation of liability": "Contractual",
    "unilateral termination": "Cancellation",
    "unilateral change": "Changes",
    "content removal": "Account",
    "contract by using": "Contractual",
    "choice of law": "Contractual",
    "jurisdiction": "Contractual",
    "arbitration": "Contractual",
}
LEDGAR = {  # LEDGAR label -> your category (only clear matches)
    "governing laws": "Contractual", "arbitration": "Contractual",
    "indemnifications": "Contractual", "jurisdictions": "Contractual",
    "venues": "Contractual", "waiver of jury trials": "Contractual",
    "terminations": "Cancellation", "fees": "Financial", "payments": "Financial",
    "expenses": "Financial", "intellectual property": "Intellectual Property",
    "amendments": "Changes", "modifications": "Changes",
}


def detok(t):
    """Undo PTB-style tokenization so real text looks like the synthetic text."""
    t = str(t).replace("``", '"').replace("''", '"')
    t = re.sub(r"\s+([,.;:!?)\]])", r"\1", t)
    t = re.sub(r"([(\[])\s+", r"\1", t)
    t = re.sub(r"\s*/\s*", "/", t)
    t = re.sub(r"\s+'\s*s\b", "'s", t)
    t = re.sub(r"(\w)s\s+'(\s|$)", r"\1s'\2", t)
    t = re.sub(r'"\s+([^"]*?)\s+"', r'"\1"', t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:1].upper() + t[1:] if t else t


def load_real():
    from datasets import load_dataset
    rows = []

    u = load_dataset("coastalcph/lex_glue", "unfair_tos")
    names = u["train"].features["labels"].feature.names
    print("UNFAIR-ToS tags:", names)
    missing = set(UNFAIR) - {n.lower() for n in names}
    if missing: print("!! UNFAIR keys not found, fix the map:", missing)
    for split in u:
        for ex in u[split]:
            cats = {UNFAIR[names[i].lower()] for i in ex["labels"] if names[i].lower() in UNFAIR}
            if len(cats) == 1:                      # skip unlabeled / cross-category rows
                rows.append({"text": ex["text"], "label": cats.pop(), "source": "unfair_tos"})

    l = load_dataset("coastalcph/lex_glue", "ledgar")
    lnames = l["train"].features["label"].names
    missing = set(LEDGAR) - {n.lower() for n in lnames}
    if missing: print("!! LEDGAR keys not found, fix the map:", missing)
    for split in l:
        for ex in l[split]:
            n = lnames[ex["label"]].lower()
            if n in LEDGAR:
                rows.append({"text": ex["text"], "label": LEDGAR[n], "source": "ledgar"})
    return pd.DataFrame(rows)


def build(syn, real, max_real_per_class=3000, seed=42):
    syn = syn.drop(columns=[c for c in ("keyword_label",) if c in syn.columns]).copy()
    syn["source"] = "synthetic"

    real = real.copy()
    real["text"] = real["text"].map(detok)
    real = real[real["text"].str.len().between(20, 1500)]
    real = real.drop_duplicates("text")
    real = real[~real["text"].isin(set(syn["text"]))]
    if max_real_per_class:                          # limit Contractual-style skew
        real = pd.concat([g.sample(min(len(g), max_real_per_class), random_state=seed)
                          for _, g in real.groupby("label")])
    real = real.reset_index(drop=True)
    real["label_id"] = real["label"].map(LABEL_ID).astype(int)

    # stratified 80/10/10 split for the real rows (synthetic rows keep theirs)
    real["split"] = None
    for lab, idx in real.groupby("label").groups.items():
        idx = list(pd.Series(list(idx)).sample(frac=1, random_state=seed))
        n = len(idx)
        for j, i in enumerate(idx):
            real.at[i, "split"] = "train" if j < 0.8 * n else "val" if j < 0.9 * n else "test"

    df = pd.concat([syn[["text", "label", "label_id", "split", "source"]],
                    real[["text", "label", "label_id", "split", "source"]]], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df.insert(0, "id", range(len(df)))
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--syn", default="clauses_60k.csv")
    ap.add_argument("--out", default="clauses_final.csv")
    ap.add_argument("--max-real-per-class", type=int, default=3000, help="0 = no cap")
    ap.add_argument("--drop-source", action="store_true")
    a = ap.parse_args()

    syn = pd.read_csv(a.syn)
    real = load_real()
    print("\nreal rows before cleanup:\n", real.groupby(["source", "label"]).size())
    df = build(syn, real, a.max_real_per_class or None)
    if a.drop_source: df = df.drop(columns=["source"])
    assert df.isna().sum().sum() == 0
    df.to_csv(a.out, index=False)
    print("\nfinal:", df.shape)
    print(df.groupby("label").size().to_dict())
    print(df["split"].value_counts().to_dict())