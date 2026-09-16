from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Character:
    name: str
    hp: int
    max_hp: int
    attack_power: int

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        damage = max(0, amount)
        self.hp = max(0, self.hp - damage)
        return damage

    def heal(self, amount: int) -> int:
        restored = max(0, min(amount, self.max_hp - self.hp))
        self.hp += restored
        return restored


@dataclass
class GameState:
    hero: Character
    enemy: Character
    potions: int = 3


def attack(attacker: Character, defender: Character, rng: random.Random) -> int:
    low = min(2, attacker.attack_power)
    high = max(2, attacker.attack_power)
    return defender.take_damage(rng.randint(low, high))


def heal_hero(state: GameState, rng: random.Random) -> int:
    if state.potions <= 0:
        return 0
    state.potions -= 1
    return state.hero.heal(rng.randint(4, 8))


def take_turn(state: GameState, action: str, rng: random.Random) -> list[str]:
    action = action.strip().lower()
    messages: list[str] = []

    if action == "attack":
        damage = attack(state.hero, state.enemy, rng)
        messages.append(f"You strike the {state.enemy.name} for {damage} damage.")
    elif action == "heal":
        if state.potions <= 0:
            messages.append("Your potion bag is empty.")
        else:
            healed = heal_hero(state, rng)
            messages.append(f"You drink a potion and restore {healed} HP.")
    elif action == "run":
        state.hero.hp = 0
        messages.append("You run away and abandon the quest.")
        return messages
    else:
        messages.append("Unknown action. Choose attack, heal, or run.")
        return messages

    if state.enemy.is_alive():
        counter = attack(state.enemy, state.hero, rng)
        messages.append(f"The {state.enemy.name} hits you for {counter} damage.")
    else:
        messages.append(f"The {state.enemy.name} is defeated!")

    return messages


def main() -> None:
    rng = random.Random()
    state = GameState(
        hero=Character(name="Hero", hp=30, max_hp=30, attack_power=8),
        enemy=Character(name="Slime King", hp=20, max_hp=20, attack_power=6),
    )

    print("Welcome, Hero. Defeat the Slime King to win.")

    while state.hero.is_alive() and state.enemy.is_alive():
        print(
            f"\nHero HP: {state.hero.hp}/{state.hero.max_hp} | "
            f"{state.enemy.name} HP: {state.enemy.hp}/{state.enemy.max_hp} | "
            f"Potions: {state.potions}"
        )
        try:
            choice = input("Choose your action (attack/heal/run): ")
        except EOFError:
            print("\nNo more input. Ending the adventure early.")
            break
        for message in take_turn(state, choice, rng):
            print(message)

    if state.enemy.is_alive() and not state.hero.is_alive():
        print("Game over.")
    elif not state.enemy.is_alive():
        print("Victory! The village is safe.")


if __name__ == "__main__":
    main()
