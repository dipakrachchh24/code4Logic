# -------------------------------------------------------------------
# main.py
#
# Top-level runner for the full CODE4LOGIC-style NL → FOL pipeline.
#
# Usage:
#   python main.py
# -------------------------------------------------------------------

import sys
from inference.infer import translate_nl_to_fol


def run_interactive():
    """
    Runs an interactive NL → FOL translation loop.
    """
    print("\n=============================================")
    print("      NL → FOL Translator (CODE4LOGIC)       ")
    print("=============================================\n")

    while True:
        nl_sentence = input("Enter an English sentence (or type 'exit'): ")

        if nl_sentence.lower().strip() in ["exit", "quit", "q"]:
            print("\nExiting translator. Goodbye!\n")
            break

        print("\nTranslating...")
        fol = translate_nl_to_fol(
            nl_sentence,
            k=5,                # number of few-shot examples
            model="gpt-4o-mini" # change if needed
        )

        print("\n---------------------------------------------")
        print("Natural Language : ", nl_sentence)
        print("FOL Output       : ", fol)
        print("---------------------------------------------\n")


def run_single_from_cli():
    """
    If the user runs: python main.py "Every boy likes some girl"
    This function takes that argument and translates it.
    """
    nl_sentence = " ".join(sys.argv[1:])
    print("\nTranslating NL → FOL...\n")
    fol = translate_nl_to_fol(
        nl_sentence,
        k=5,
        model="gpt-4o-mini"
    )
    print("Input :", nl_sentence)
    print("FOL   :", fol)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_single_from_cli()
    else:
        run_interactive()
