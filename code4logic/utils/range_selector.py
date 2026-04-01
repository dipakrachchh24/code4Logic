def parse_id_range(user_input, all_ids):
    """
    Returns a filtered list of IDs based on user input.
    """

    all_ids = sorted(all_ids)

    if not user_input.strip():
        return all_ids

    user_input = user_input.strip()

    # Single ID: start → end
    if user_input.isdigit():
        start = int(user_input)
        return [i for i in all_ids if i >= start]

    # Range A-B
    if "-" in user_input:
        parts = user_input.split("-")
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            raise ValueError("Invalid range format. Use A B")

        start, end = map(int, parts)
        return [i for i in all_ids if start <= i <= end]
    # Range A B
    if " " in user_input:
        parts = user_input.split(" ")
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            raise ValueError("Invalid range format. Use A B")

        start, end = map(int, parts)
        return [i for i in all_ids if start <= i <= end]

    raise ValueError("Invalid input. Use empty, N, or A-B or A B.")
