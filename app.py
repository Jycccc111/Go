from board import GoGame
from flask import Flask,render_template,jsonify,request,session
import uuid


app = Flask(__name__)

app.secret_key = "your_secret_key"


games = {}
def get_game():

    if "id" not in session:
        session["id"] = str(uuid.uuid4())

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


    return jsonify({

        "success":success,

        "board":game.board.tolist()

    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
