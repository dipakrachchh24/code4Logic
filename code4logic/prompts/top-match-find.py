import json
import math
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# 1. CONFIG
# =========================

TOP_K = 5

# Put likely column names here. The script will try them in order.
TEXT_COL_CANDIDATES = [
    "sentence",
    "nl",
    "natural_language",
    "natural_language_statement",
    "text",
    "input",
    "input_text",
    "question",
    "query",
]

FOL_COL_CANDIDATES = [
    "fol",
    "fopl",
    "logic",
    "formula",
    "first_order_logic",
    "target",
    "output",
]

# Weights for hybrid score
W_SEM = 0.50
W_CUE = 0.20
W_STRUCT = 0.20
W_COMPLEX = 0.10

# Diversity penalty to avoid near-duplicate final top-5
DIVERSITY_PENALTY = 0.12


# =========================
# 2. LOAD DATA
# =========================

def load_dataset(path: str) -> pd.DataFrame:
    path_obj = Path(path)

    if path_obj.suffix.lower() == ".xlsx":
        df = pd.read_excel(path_obj)
    elif path_obj.suffix.lower() == ".json":
        with open(path_obj, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    elif path_obj.suffix.lower() == ".jsonl":
        rows = []
        with open(path_obj, "r", encoding="utf-8") as f:
            for line in f:
                rows.append(json.loads(line))
        df = pd.DataFrame(rows)
    else:
        raise ValueError(f"Unsupported file type: {path_obj.suffix}")

    return df


def find_column(df: pd.DataFrame, candidates: List[str]) -> str:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    raise ValueError(
        f"Could not find any of these columns: {candidates}\n"
        f"Available columns: {list(df.columns)}"
    )


# =========================
# 3. FEATURE EXTRACTION
# =========================

LOGIC_CUE_GROUPS = {
    "universal": ["every", "all", "each", "any"],
    "existential": ["some", "a", "an", "there exists", "at least one"],
    "implication": ["if", "then", "whenever", "when"],
    "conjunction": ["and", "both"],
    "disjunction": ["or", "either"],
    "negation": ["not", "no", "never", "none"],
    "biconditional": ["iff", "if and only if"],
}

TOKEN_RE = re.compile(r"\b\w+\b")


def normalize_text(text: str) -> str:
    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(normalize_text(text))


def extract_logic_cues(text: str) -> Dict[str, int]:
    text_n = normalize_text(text)
    cues = {}
    for group, keywords in LOGIC_CUE_GROUPS.items():
        cues[group] = int(any(k in text_n for k in keywords))
    return cues


def estimate_structure_from_text(text: str) -> str:
    """
    Rule-based estimate of logic structure from NL text.
    """
    t = normalize_text(text)
    cues = extract_logic_cues(t)

    has_univ = cues["universal"]
    has_exist = cues["existential"]
    has_impl = cues["implication"]
    has_conj = cues["conjunction"]
    has_disj = cues["disjunction"]
    has_neg = cues["negation"]
    has_bi = cues["biconditional"]

    if has_bi:
        base = "biconditional"
    elif has_impl:
        base = "implication"
    elif has_disj:
        base = "disjunction"
    elif has_conj:
        base = "conjunction"
    elif has_neg:
        base = "negation"
    else:
        base = "atomic"

    if has_univ:
        quant = "forall"
    elif has_exist:
        quant = "exists"
    else:
        quant = "noquant"

    return f"{quant}_{base}"


def estimate_complexity(text: str) -> Dict[str, float]:
    tokens = tokenize(text)
    cues = extract_logic_cues(text)

    return {
        "length": len(tokens),
        "num_logic_cues": sum(cues.values()),
        "num_commas": text.count(","),
    }


def structure_similarity(s1: str, s2: str) -> float:
    return 1.0 if s1 == s2 else 0.0


def cue_similarity(c1: Dict[str, int], c2: Dict[str, int]) -> float:
    keys = sorted(c1.keys())
    inter = sum(1 for k in keys if c1[k] == 1 and c2[k] == 1)
    union = sum(1 for k in keys if c1[k] == 1 or c2[k] == 1)
    if union == 0:
        return 0.0
    return inter / union


def complexity_similarity(x: Dict[str, float], y: Dict[str, float]) -> float:
    # simple bounded similarity
    len_sim = 1.0 - min(abs(x["length"] - y["length"]) / max(x["length"], y["length"], 1), 1.0)
    cue_sim = 1.0 - min(abs(x["num_logic_cues"] - y["num_logic_cues"]) / max(x["num_logic_cues"], y["num_logic_cues"], 1), 1.0)
    comma_sim = 1.0 - min(abs(x["num_commas"] - y["num_commas"]) / max(x["num_commas"], y["num_commas"], 1), 1.0)
    return (len_sim + cue_sim + comma_sim) / 3.0


# =========================
# 4. SCORING
# =========================

def build_text_vectorizer(all_texts: List[str]) -> Tuple[TfidfVectorizer, Any]:
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=20000,
    )
    matrix = vectorizer.fit_transform(all_texts)
    return vectorizer, matrix


def greedy_diverse_topk(
    ranked_items: List[Dict[str, Any]],
    similarity_matrix: Any,
    top_k: int = 5,
    diversity_penalty: float = 0.12,
) -> List[Dict[str, Any]]:
    """
    Greedy reranking:
    select high-scoring items, but penalize near-duplicates with already selected items.
    """
    selected = []
    selected_indices = []

    remaining = ranked_items.copy()

    while remaining and len(selected) < top_k:
        best_item = None
        best_score = -1e9

        for item in remaining:
            idx = item["row_index"]
            redundancy = 0.0
            if selected_indices:
                redundancy = max(similarity_matrix[idx, sidx] for sidx in selected_indices)
            adjusted = item["score"] - diversity_penalty * redundancy
            if adjusted > best_score:
                best_score = adjusted
                best_item = item

        selected.append(best_item)
        selected_indices.append(best_item["row_index"])
        remaining = [x for x in remaining if x["row_index"] != best_item["row_index"]]

    return selected


def find_top_k_examples(
    df: pd.DataFrame,
    target_sentence: str,
    text_col: str,
    fol_col: str = None,
    top_k: int = 5,
) -> pd.DataFrame:
    texts = df[text_col].fillna("").astype(str).tolist()
    all_texts = texts + [target_sentence]

    vectorizer, matrix = build_text_vectorizer(all_texts)

    candidate_matrix = matrix[:-1]
    target_vector = matrix[-1]

    semantic_scores = cosine_similarity(candidate_matrix, target_vector).reshape(-1)

    target_cues = extract_logic_cues(target_sentence)
    target_struct = estimate_structure_from_text(target_sentence)
    target_complex = estimate_complexity(target_sentence)

    rows = []
    for i, row in df.iterrows():
        cand_text = str(row[text_col])
        cand_cues = extract_logic_cues(cand_text)
        cand_struct = estimate_structure_from_text(cand_text)
        cand_complex = estimate_complexity(cand_text)

        s_sem = float(semantic_scores[i])
        s_cue = cue_similarity(target_cues, cand_cues)
        s_struct = structure_similarity(target_struct, cand_struct)
        s_complex = complexity_similarity(target_complex, cand_complex)

        final_score = (
            W_SEM * s_sem
            + W_CUE * s_cue
            + W_STRUCT * s_struct
            + W_COMPLEX * s_complex
        )

        item = {
            "row_index": i,
            "sentence": cand_text,
            "score": final_score,
            "semantic_score": s_sem,
            "cue_score": s_cue,
            "structure_score": s_struct,
            "complexity_score": s_complex,
            "predicted_structure": cand_struct,
        }

        if fol_col is not None and fol_col in df.columns:
            item["fol"] = row[fol_col]

        rows.append(item)

    scored = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

    # Build candidate-candidate similarity matrix for diversity filtering
    cand_sim_matrix = cosine_similarity(candidate_matrix)

    # Greedy diverse reranking over top-N pool
    pool_size = min(50, len(scored))
    top_pool = scored.head(pool_size).to_dict(orient="records")
    diverse_topk = greedy_diverse_topk(
        top_pool,
        cand_sim_matrix,
        top_k=top_k,
        diversity_penalty=DIVERSITY_PENALTY,
    )

    result_df = pd.DataFrame(diverse_topk).sort_values("score", ascending=False).reset_index(drop=True)
    return result_df


def get_top_k_example_rows(
    dataset_path: str,
    target_sentence: str,
    top_k: int = 5,
) -> Tuple[List[Dict[str, Any]], str, str]:
    """
    Convenience wrapper:
    - loads dataset
    - finds NL + FOL columns
    - returns top-k rows (as dicts) plus column names
    """
    df = load_dataset(dataset_path)
    text_col = find_column(df, TEXT_COL_CANDIDATES)

    try:
        fol_col = find_column(df, FOL_COL_CANDIDATES)
    except ValueError:
        fol_col = None

    # remove exact target match if it already exists in the pool
    df = df[df[text_col].fillna("").astype(str).str.strip() != target_sentence.strip()].reset_index(drop=True)

    topk_df = find_top_k_examples(
        df=df,
        target_sentence=target_sentence,
        text_col=text_col,
        fol_col=fol_col,
        top_k=top_k,
    )

    rows: List[Dict[str, Any]] = []
    for _, row in topk_df.iterrows():
        idx = int(row["row_index"])
        src = df.iloc[idx].to_dict()
        src["_row_index"] = idx
        src["_score"] = float(row["score"])
        rows.append(src)

    return rows, text_col, fol_col


# =========================
# 5. MAIN USAGE
# =========================

if __name__ == "__main__":
    # -------------------------
    # CHANGE THESE
    # -------------------------
    DATASET_PATH = "MALLS-train.xlsx"   # or MALLS-test.xlsx / .json / .jsonl
    TARGET_SENTENCE = "A song becomes a hit if it achieves high rankings on music charts and gains widespread popularity."

    # -------------------------
    # LOAD
    # -------------------------
    df = load_dataset(DATASET_PATH)
    text_col = find_column(df, TEXT_COL_CANDIDATES)

    try:
        fol_col = find_column(df, FOL_COL_CANDIDATES)
    except ValueError:
        fol_col = None

    # Optional: remove exact target match if it already exists in the pool
    df = df[df[text_col].fillna("").astype(str).str.strip() != TARGET_SENTENCE.strip()].reset_index(drop=True)

    # -------------------------
    # FIND TOP-5
    # -------------------------
    top5 = find_top_k_examples(
        df=df,
        target_sentence=TARGET_SENTENCE,
        text_col=text_col,
        fol_col=fol_col,
        top_k=TOP_K,
    )

    print("\nTARGET SENTENCE:")
    print(TARGET_SENTENCE)
    print("\nTOP-5 MATCHING EXAMPLES:\n")

    cols = [
        "row_index",
        "sentence",
        "score",
        "semantic_score",
        "cue_score",
        "structure_score",
        "complexity_score",
        "predicted_structure",
    ]
    if "fol" in top5.columns:
        cols.append("fol")

    print(top5[cols].to_string(index=False))

    # Save results
    top5.to_csv("top5_matching_examples.csv", index=False)
    print("\nSaved to: top5_matching_examples.csv")
