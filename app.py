from board import GoGame
from flask import Flask,render_template,jsonify,request,session
import uuid
from judger import judgeresult
from AI import predict_move
app = Flask(__name__)

app.secret_key = "your_secret_key"


games = {}
def get_game():

    if "id" not in session:
        session["id"] = str(uuid.uuid4())


    if session["id"] not in games:
        games[session["id"]] = GoGame()


    return games[session["id"]]

@app.route("/")
def index():

    return render_template(
        "show.html"
    )



@app.route("/move",methods=["POST"])
def move():

    game = get_game()


    data=request.json

    x=data["x"]+1
    y=data["y"]+1


    success=game.move(x,y)
    if not success:
        return jsonify({

            "success": False,

            "board": game.board.tolist()

        })

    ai_move = predict_move(game)

    if ai_move is not None:
        ai_x, ai_y = ai_move

        # 你的 GoGame 使用 1~19
        game.move(
            ai_x + 1,
            ai_y + 1
        )

    # =====================
    # 返回棋盘
    # =====================

    return jsonify({

        "success": True,

        "board": game.board.tolist(),

        "ai_move": ai_move

    })



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
