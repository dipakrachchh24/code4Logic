# -------------------------------------------------------------------
# infer.py
# End-to-end NL → FOL translation for the CODE4LOGIC-style pipeline.
#
# Pipeline:
#   1. Build in-context prompt (basis functions + demos + query)
#   2. Send prompt to LLM (code generation)
#   3. Execute generated code in a restricted environment
#   4. Return final FOL string
# -------------------------------------------------------------------

from prompts.build_prompt import build_prompt
from inference.llm_api import LLMClient
from inference.execute_code import execute_generated_code


# -------------------------------------------------------------------
# Core API
# -------------------------------------------------------------------

def translate_nl_to_fol(
    nl_sentence: str,
    k: int = 5,
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
) -> str:
    """
    Translate a natural language sentence into a First-Order Logic (FOL) formula
    using the CODE4LOGIC-style pipeline.

    Args:
        nl_sentence: Natural language statement to be translated.
        k: Number of few-shot demonstration examples to include in the prompt.
        model: Name of the LLM model (e.g., "gpt-4o-mini", "gpt-4.1-mini", etc.).
        temperature: Sampling temperature for the LLM.

    Returns:
        A string representing the final FOL formula, or None if something failed.
    """

    # 1. Build the full prompt
    prompt = build_prompt(nl_sentence, k=k)

    # 2. Call the LLM to get generated code
    llm = LLMClient(model=model, temperature=temperature)
    generated_code = llm.generate_code(prompt)

    # Optional: you might want to log/inspect this
    print("----- GENERATED CODE -----")
    print(generated_code)
    print("--------------------------")

    if not generated_code or not isinstance(generated_code, str):
        print("[ERROR] LLM did not return a valid code string.")
        return None

    # 3. Execute the generated code to obtain the FOL formula
    fol_formula = execute_generated_code(generated_code)

    return fol_formula


# -------------------------------------------------------------------
# Convenience CLI entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        sentence = " ".join(sys.argv[1:])
    else:
        sentence = input("Enter a natural language sentence: ")

    print("\n[NL] :", sentence)
    print("[INFO] Translating to FOL...\n")

    result = translate_nl_to_fol(sentence, k=5, model="gpt-4o-mini")

    print("[FOL]:", result)
