import os
import sys
from sample_application import create_app
sys.path.append(os.path.dirname(__name__))


app = create_app()

if __name__ == "__main__":
    app.run()
