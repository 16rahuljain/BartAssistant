#!/usr/bin/env python
from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
  return 'Hello world'


if __name__ == "__main__":
  port = int(os.getenv('PORT', 5000))

   

    app.run(debug=False, port=port, host='0.0.0.0')


