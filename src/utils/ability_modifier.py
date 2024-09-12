def ability_modifier(number: int) -> str:
    """Take the ability score and generate the modifier based on the table below

    Args:
        number (int): The ability score

    Returns:
        str: The modifier as a string (with + or - included)
    """
    # Ability score modifiers table
    ability_table = [
        ("1", "-5"),
        ("2-3", "-4"),
        ("4-5", "-3"),
        ("6-7", "-2"),
        ("8-9", "-1"),
        ("10-11", "+0"),
        ("12-13", "+1"),
        ("14-15", "+2"),
        ("16-17", "+3"),
        ("18-19", "+4"),
        ("20-21", "+5"),
        ("22-23", "+6"),
        ("24-25", "+7"),
        ("26-27", "+8"),
        ("28-29", "+9"),
        ("30", "+10"),
    ]

    # Iterate over the table to find the matching range or value
    for range, value in ability_table:
        if "-" in range:
            start, end = map(int, range.split("-"))
            if start <= number <= end:
                return value
        elif int(range) == number:
            return value

    # Return "0" if no match found
    return "+0"
