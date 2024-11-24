import random
import numpy as np
from game_logic import Game

class MCCFRAgent:
    def __init__(self):
        self.regret_table = {}  # Таблица сожалений
        self.strategy_table = {}  # Таблица стратегий
        self.num_simulations = 1000  # Количество симуляций для обучения

    def train(self, game_state):
        """
        Тренирует агента с использованием MCCFR.
        """
        for _ in range(self.num_simulations):
            self.simulate(game_state, 1)

    def simulate(self, game_state, player):
        """
        Одна итерация MCCFR. Возвращает utility (выгоду) для текущего состояния игры.
        """
        if self.is_terminal(game_state):
            return self.evaluate(game_state)

        actions = self.get_available_moves(game_state)
        if not actions:
            return 0

        strategy = self.get_strategy(game_state, actions)
        utilities = {}
        node_utility = 0

        for action in actions:
            next_state = self.apply_action(game_state, action, player)
            utilities[action] = -self.simulate(next_state, -player)
            node_utility += strategy[action] * utilities[action]

        for action in actions:
            regret = utilities[action] - node_utility
            self.regret_table.setdefault(game_state, {}).setdefault(action, 0)
            self.regret_table[game_state][action] += regret

        return node_utility

    def get_strategy(self, game_state, actions):
        """
        Возвращает стратегию для текущего состояния игры.
        """
        regrets = self.regret_table.get(game_state, {})
        positive_regrets = {a: max(0, regrets.get(a, 0)) for a in actions}
        total_positive_regret = sum(positive_regrets.values())
        if total_positive_regret > 0:
            strategy = {a: positive_regrets[a] / total_positive_regret for a in actions}
        else:
            strategy = {a: 1 / len(actions) for a in actions}
        self.strategy_table[game_state] = strategy
        return strategy

    def make_move(self, game_state):
        """
        Выбирает действие на основе текущей стратегии.
        """
        actions = self.get_available_moves(game_state)
        if not actions:
            return None
        strategy = self.get_strategy(game_state, actions)
        return random.choices(list(strategy.keys()), weights=strategy.values())[0]

    def get_available_moves(self, game_state):
        """
        Возвращает список доступных ходов, которые не нарушают правила.
        """
        moves = self.generate_possible_moves(game_state)
        valid_moves = [move for move in moves if Game().is_hand_valid(move)]
        return valid_moves

    def generate_possible_moves(self, game_state):
        """
        Генерирует все возможные ходы для текущего состояния игры.
        """
        # Для упрощения: возвращаем случайные карты из оставшейся колоды
        deck = game_state['remaining_deck']
        return [deck[i:i+3] for i in range(0, len(deck), 3)]

    def apply_action(self, game_state, action, player):
        """
        Применяет действие и возвращает новое состояние игры.
        """
        new_state = game_state.copy()
        for card in action:
            new_state['remaining_deck'].remove(card)
        if player == 1:
            new_state['player_board']['bottom'].extend(action)  # Пример обновления
        else:
            new_state['ai_board']['bottom'].extend(action)
        return new_state

    def is_terminal(self, game_state):
        """
        Проверяет, закончена ли игра.
        """
        return len(game_state['remaining_deck']) == 0

    def evaluate(self, game_state):
        """
        Оценивает состояние игры с учётом комбинаций.
        """
        def hand_value(hand):
            # Учитываем комбинации (например, пары, тройки, стриты)
            if len(hand) == 3:  # Верхняя линия
                return self.evaluate_top_line(hand)
            elif len(hand) == 5:  # Средняя и нижняя линии
                return self.evaluate_five_card_hand(hand)
            return 0

        player_score = sum(hand_value(game_state['player_board'][line]) for line in ['top', 'middle', 'bottom'])
        ai_score = sum(hand_value(game_state['ai_board'][line]) for line in ['top', 'middle', 'bottom'])
        return player_score - ai_score

    def evaluate_top_line(self, hand):
        # Пример: оцениваем верхнюю линию (только пары, тройки)
        ranks = [card.split('_')[0] for card in hand]
        if len(set(ranks)) == 1:  # Тройка
            return 10
        elif len(set(ranks)) == 2:  # Пара
            return 5
        return 0

    def evaluate_five_card_hand(self, hand):
        # Пример: оцениваем пятёрки (стриты, флеши и т.д.)
        # Можно использовать готовую библиотеку для оценки покерных комбинаций
        return random.randint(1, 10)  # Упрощённо, нужно доработать
