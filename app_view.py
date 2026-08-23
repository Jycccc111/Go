from flask import Flask, render_template,jsonify
from data_loader import SGFLoader
from judger import judgeresult

app = Flask(__name__)

def convert_clusters(clusters):

    output=[]

    for cluster in clusters:

        stones=[]

        for x,y,c in cluster:

            stones.append({

                "x":int(x),
                "y":int(y),
                "color":int(c)

            })

        output.append(stones)

    return output
@app.route("/")
def index():

    return render_template(
        "view_board.html"
    )


@app.route("/sgf_board")
def sgf_board():

    loader = SGFLoader(
        "/Users/jiangyuncong/Downloads/games/AlphaGo/selfplay/1c.sgf"
    )

    loader.load()


    return {
        "board":
        loader.game.board.tolist(),

        "result":
        str(loader.result),

        "komi":
        str(loader.komi),

        "handicap":
        str(loader.handicap)
    }
@app.route("/judge")
def judge():

    game = judgeresult(
        "/Users/jiangyuncong/Downloads/games/AlphaGo/selfplay/1c.sgf"
    )


    result = game.cal_result()


    air=[]


    for i,cluster in enumerate(game.airclusters):


        owner = result["airtype"][i]


        for x,y in cluster:

            air.append({

                "x":int(x),

                "y":int(y),

                "owner":int(owner)

            })

    stones = []

    dead_position = set()

    # 记录死子坐标
    for cluster in result["dead"]:

        for x, y, color in cluster:
            dead_position.add(
                (int(x), int(y))
            )

    for cluster in result["clusters"]:

        for x, y, color in cluster:
            stones.append({

                "x": int(x),

                "y": int(y),

                "color": int(color),

                "dead":
                    (int(x), int(y)) in dead_position

            })

    return jsonify({

        "air": air,

        "stones": stones,

        "black_score": game.black_score,

        "white_score": game.white_score,

        "result":
            "黑胜"
            if game.black_score > game.white_score
            else "白胜"

    })

if __name__ == "__main__":
    app.run(port=5001, debug=True)