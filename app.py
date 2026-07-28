from board import GoGame
from flask import Flask,render_template,jsonify,request

app=Flask(__name__)


game=GoGame()



@app.route("/")
def index():

    return render_template(
        "棋盘展示.html"
    )



@app.route("/move",methods=["POST"])
def move():
    print("收到move请求")
    data = request.json
    print(data)
    x = data["x"]+1
    y = data["y"]+1
    success = game.move(x,y)
    return jsonify({
        "success":success,
        "board":game.board.tolist()
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )