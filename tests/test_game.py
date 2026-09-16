import unittest

from game import Character, GameState, take_turn


class FixedRng:
    def __init__(self, *values: int):
        self.values = list(values)

    def randint(self, _start: int, _end: int) -> int:
        return self.values.pop(0)


class GameTests(unittest.TestCase):
    def test_attack_can_defeat_enemy(self) -> None:
        state = GameState(
            hero=Character("Hero", hp=20, max_hp=20, attack_power=8),
            enemy=Character("Slime", hp=4, max_hp=4, attack_power=4),
        )

        messages = take_turn(state, "attack", FixedRng(4))

        self.assertEqual(state.enemy.hp, 0)
        self.assertEqual(state.hero.hp, 20)
        self.assertIn("The Slime is defeated!", messages[-1])

    def test_heal_uses_potion_and_clamps_hp(self) -> None:
        state = GameState(
            hero=Character("Hero", hp=18, max_hp=20, attack_power=8),
            enemy=Character("Slime", hp=10, max_hp=10, attack_power=4),
            potions=1,
        )

        messages = take_turn(state, "heal", FixedRng(8, 2))

        self.assertEqual(state.hero.hp, 18)
        self.assertEqual(state.potions, 0)
        self.assertIn("restore 2 HP", messages[0])
        self.assertIn("hits you for 2 damage", messages[1])

    def test_unknown_action_does_not_change_state(self) -> None:
        state = GameState(
            hero=Character("Hero", hp=20, max_hp=20, attack_power=8),
            enemy=Character("Slime", hp=10, max_hp=10, attack_power=4),
        )

        messages = take_turn(state, "dance", FixedRng())

        self.assertEqual(state.hero.hp, 20)
        self.assertEqual(state.enemy.hp, 10)
        self.assertEqual(messages, ["Unknown action. Choose attack, heal, or run."])

    def test_heal_at_full_hp_still_reports_potion_use(self) -> None:
        state = GameState(
            hero=Character("Hero", hp=20, max_hp=20, attack_power=8),
            enemy=Character("Slime", hp=10, max_hp=10, attack_power=4),
            potions=1,
        )

        messages = take_turn(state, "heal", FixedRng(7, 2))

        self.assertEqual(state.hero.hp, 18)
        self.assertEqual(state.potions, 0)
        self.assertEqual(messages[0], "You drink a potion and restore 0 HP.")
        self.assertEqual(messages[1], "The Slime hits you for 2 damage.")

    def test_weak_attacker_still_deals_damage(self) -> None:
        state = GameState(
            hero=Character("Hero", hp=20, max_hp=20, attack_power=1),
            enemy=Character("Slime", hp=10, max_hp=10, attack_power=1),
        )

        messages = take_turn(state, "attack", FixedRng(1, 1))

        self.assertEqual(state.enemy.hp, 9)
        self.assertEqual(state.hero.hp, 19)
        self.assertIn("for 1 damage", messages[0])

    def test_zero_attack_power_deals_no_damage(self) -> None:
        state = GameState(
            hero=Character("Hero", hp=20, max_hp=20, attack_power=0),
            enemy=Character("Slime", hp=10, max_hp=10, attack_power=0),
        )

        messages = take_turn(state, "attack", FixedRng())

        self.assertEqual(state.enemy.hp, 10)
        self.assertEqual(state.hero.hp, 20)
        self.assertEqual(messages[0], "You strike the Slime for 0 damage.")

    def test_run_ends_turn_without_counterattack(self) -> None:
        state = GameState(
            hero=Character("Hero", hp=20, max_hp=20, attack_power=8),
            enemy=Character("Slime", hp=10, max_hp=10, attack_power=4),
        )

        messages = take_turn(state, "run", FixedRng())

        self.assertTrue(state.fled)
        self.assertEqual(state.hero.hp, 20)
        self.assertEqual(state.enemy.hp, 10)
        self.assertEqual(messages, ["You run away and abandon the quest."])


if __name__ == "__main__":
    unittest.main()
