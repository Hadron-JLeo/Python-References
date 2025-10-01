"""Calculate the number of shards needed to upgrade from one rank to another."""

from typing import Dict

# Amount of shards needed to upgrade to the next rank
TIERS: Dict[str, int] = {
    'SSS+': 0,         # Highest Rank (no more upgrades possible)
    'SSS': 25 * 20,
    'SS': 0 * 20,
    'S': 9 * 20,
    'A': 3 * 20,
    'B': 0 * 20,
}

PER_LEVEL: int = 20  # Number of levels per tier


def get_previous_tier(tier: str) -> str:
    """
    Retrieve the previous tier for a given tier.
    
    Args:
        tier (str): The current tier name (e.g., 'A', 'S', etc.)
    
    Returns:
        str: The previous tier name.
    """
    tier_list = list(TIERS.keys())
    try:
        current_index = tier_list.index(tier)
        return tier_list[current_index + 1]
    except (ValueError, IndexError):
        raise ValueError(f"Invalid tier '{tier}' or no lower tier exists.")


def calculate_remaining_shards(next_tier: str, current_level: int, shards_inside: int = 0) -> int:
    """
    Calculate the remaining number of shards needed to reach the next rank.
    
    Args:
        next_tier (str): The target tier (e.g., 'SS', 'A').
        current_level (int): Current level within the tier (0 to 19).
        shards_inside (int, optional): Extra shards already collected in the current level. Defaults to 0.
    
    Returns:
        int: The number of shards still needed to upgrade.
    """
    if not (0 <= current_level < PER_LEVEL):
        raise ValueError(f"current_level must be between 0 and {PER_LEVEL - 1}. Got {current_level}.")

    current_tier = get_previous_tier(next_tier)
    full_shards_required = TIERS.get(current_tier)

    if full_shards_required is None:
        raise ValueError(f"Tier '{current_tier}' not found in TIERS.")

    shards_collected = int(full_shards_required / PER_LEVEL * current_level) + shards_inside
    remaining_shards = full_shards_required - shards_collected
    return max(remaining_shards, 0)  # Avoid negative results


if __name__ == "__main__":
    result = calculate_remaining_shards('SS', 5, 3)
    print(result)
