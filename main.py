from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import os
from game_logic import Game
from ai_agent import MCCFRAgent
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('AI_PROGRESS_TOKEN', 'default_secret')
socketio = SocketIO(app, cors_allowed_origins="*")

# Инициализация игры и агента
game = Game()
ai_agent = MCCFRAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    game.start_game()
    return jsonify({'status': 'ok', 'state': game.get_state()})

@app.route('/play', methods=['POST'])
def play_turn():
    data = request.json
    try:
        # Ход игрока
        game.play_turn(data['player_move'])
        # Ход ИИ
        ai_move = ai_agent.make_move(game.get_state())
        game.play_ai_turn(ai_move)
        return jsonify({'status': 'ok', 'state': game.get_state()})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/end', methods=['POST'])
def end_game():
    scores = game.calculate_scores()
    royalties_player = game.calculate_royalties(game.player_board)
    royalties_ai = game.calculate_royalties(game.ai_board)
    return jsonify({
        'status': 'ok',
        'scores': scores,
        'royalties': {
            'player': royalties_player,
            'ai': royalties_ai
        }
    })

@app.route('/state', methods=['GET'])
def get_game_state():
    return jsonify(game.get_state())

if __name__ == '__main__':
    # Получаем порт из переменной окружения или используем 5000 по умолчанию
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
