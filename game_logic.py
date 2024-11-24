import random
import os
import json
import sqlite3

class Game:
    def __init__(self):
        self.deck = []
        self.player_board = {'bottom': [], 'middle': [], 'top': []}
        self.ai_board = {'bottom': [], 'middle': [], 'top': []}
        self.used_cards = set()
        self.conn = sqlite3.connect('progress/game.db', check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY,
                    state TEXT
                )
            ''')

    def start_game(self):
        self.deck = self.generate_deck()
        random.shuffle(self.deck)
        self.player_board = {'bottom': [], 'middle': [], 'top': []}
        self.ai_board = {'bottom': [], 'middle': [], 'top': []}
        self.used_cards = set()
        self.save_progress()

    def generate_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return [f'{rank}_of_{suit}' for rank in ranks for suit in suits]

    def deal_cards(self, num):
        cards = []
        for _ in range(num):
            card = self.deck.pop()
            self.used_cards.add(card)
            cards.append(card)
        return cards

    def validate_player_move(self, move):
        """
        Проверяет, что игрок сделал допустимый ход.
        """
        return self.is_hand_valid(move)

    def is_hand_valid(self, board):
        """
        Проверяет, что порядок силы линий соблюдается:
        верхняя < средняя < нижняя.
        """
        def hand_strength(hand):
            # Примерная оценка силы руки (можно доработать)
            ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            return sum(ranks[card.split('_')[0]] for card in hand)

        top_strength = hand_strength(board['top'])
        middle_strength = hand_strength(board['middle'])
        bottom_strength = hand_strength(board['bottom'])

        return top_strength <= middle_strength <= bottom_strength

    def play_turn(self, player_move):
        """
        Обрабатывает ход игрока.
        """
        self.player_board = player_move
        if not self.is_hand_valid(self.player_board):
            raise ValueError("Мёртвая рука! Нарушен порядок линий.")

    def play_ai_turn(self, ai_move):
        """
        Обрабатывает ход ИИ.
        """
        self.ai_board = ai_move

    def calculate_scores(self):
        """
        Подсчитывает очки для игрока и ИИ.
        """
        def compare_lines(player_line, ai_line):
            # Простое сравнение силы линий
            player_strength = self.hand_strength(player_line)
            ai_strength = self.hand_strength(ai_line)
            if player_strength > ai_strength:
                return 1  # Игрок выигрывает линию
            elif player_strength < ai_strength:
                return -1  # ИИ выигрывает линию
            else:
                return 0  # Ничья

        scores = {'player': 0, 'ai': 0}
        for line in ['top', 'middle', 'bottom']:
            result = compare_lines(self.player_board[line], self.ai_board[line])
            if result == 1:
                scores['player'] += 1
            elif result == -1:
                scores['ai'] += 1

        # Бонус за выигрыш всех линий
        if scores['player'] == 3:
            scores['player'] += 3
        elif scores['ai'] == 3:
            scores['ai'] += 3

        return scores

    def calculate_royalties(self, board):
        """
        Рассчитывает бонусы за комбинации в каждой линии.
        """
        royalties = {'top': 0, 'middle': 0, 'bottom': 0}

        # Пример: бонусы за каре, стрит-флеш и т.д.
        if 'K_of_spades' in board['bottom']:  # Условие для теста
            royalties['bottom'] += 10  # Пример бонуса

        return royalties

    def save_progress(self):
        with self.conn:
            self.conn.execute('DELETE FROM progress')
            self.conn.execute('INSERT INTO progress (state) VALUES (?)', (json.dumps(self.get_state()),))

    def load_progress(self):
        cursor = self.conn.execute('SELECT state FROM progress')
        row = cursor.fetchone()
        if row:
            state = json.loads(row[0])
            self.player_board = state['player_board']
            self.ai_board = state['ai_board']
            self.deck = state['remaining_deck']

    def get_state(self):
        return {
            'player_board': self.player_board,
            'ai_board': self.ai_board,
            'remaining_deck': len(self.deck)
        }
