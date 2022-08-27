from flask import Flask

app = Flask(__name__)
app.secret_key = b'_5#234sgwhw"F4Q8z\n\xec]/'

import routes

if __name__ == "__main__":
    app.run()