import os
import sys

sys.path.append(os.path.dirname(__name__))

from sample_application import create_app

# create an app instance
app = create_app()

app.run(host='0.0.0.0')


from myproject import app

if __name__ == "__main__":
    app.run()
