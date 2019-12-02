# Tally AI Lambda Labs19 Starter Files 

These files are based on the collaborative efforts of Alfredo Quintana, Andrew Allen, Anthony Piazza, Arvin Agas, Enrique Collado, Kevona Webb, Kemberly Eliscar, Lily Su, Melissa Kemp, Obaida Albaroudi and Richany Nguon with guidance from Crawford Collins as a Project Manager from Better Business by Review buildweek. The front-end was never hooked up with the backend, so the finalized version only has login authentification and a homepage: https://business-recommendation.netlify.com/index.html

Here is the Labs 19 Project Pitch:
https://www.youtube.com/watch?v=YA5EYLWVp7Y&

Here is a walkthrough of the two Flask apps that are here in the repo:
https://www.youtube.com/watch?v=FpM6yXa6rGI&

## Getting Started 

### DS
### Running Flask locally
The following files:

### basic-flaskapp
![alt text](https://i.ibb.co/YjDjP6s/01.png)
![alt text](https://i.ibb.co/t2LHj43/02.png)
### flaskbootstrap
![alt text](https://i.ibb.co/gMyQZPs/03.png)
![alt text](https://i.ibb.co/5YrhxKF/04.png)
are individual pipenv environments to run two identically functional versions of the app. The only difference is that the flaskbootstrap version has bootstrap formatting applied, and instead of json, it returns a string formatted with bootstrap line items. 

### Please note that running the myproject.py will be running at http://127.0.0.1:5000/ instead of http://0.0.0.0:5000/
### notebooks
scraper-to-df-for-app.ipynb is the comprehensive IPython notebook that one can run on Jupyter Labs or Jupyter Notebooks. 
sampleNLP-projectCoffeeShopDataset is a folder containing open data from data.world of coffee shops in the Austin area where the scattertext library is used to explore the dataset.
explorations is a folder that contains lda topic modeling explorations on yelp reviews from the scraper-to-df-for-app.ipynb file. 
### webscraper
The webscraper is a .py file created by Kevona Webb. The same code is run in all other instances of the notebooks that may contain a web scraper. 
### usingAPIs
Contains explorations of accessing the YelpAPI

### UX
### visualideasforUI
Contains storyboard ideas for an explainer video for the TallyAI brand. Please feel free to use as little or as much for inspiration and guidance.

Some fundamental Questions: 
What do you think a business owner needs to see for them to trust the app enough to make a decision? 
How can we work on visually representing the importance and rank of words?

### Web
There are no assets in this repo at this time that will help you with your work. However, you are welcome to work with UX students on front-end ideas for the dashboard. 
This app will involve a Django API from the Django Rest Framework pulling from a PostgreSQL database. 
Feel free to look through and run the Flask app to see what you can come up with to problem solve UI challenges. 



#### To run the flask app locally
```
pipenv shell
```
```
python <pythonfile>.py
```

##### Common Pipenv Troubleshooting

To update the lock file

```
pipenv lock
```

Be sure to install all missing modules/packages using

```
pipenv install <package>
```

