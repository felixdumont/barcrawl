## Getting Started

### Running the app locally

First create a virtual environment with conda or venv inside a temp folder, then activate it.

```
virtualenv venv

# Windows
venv\Scripts\activate
# Or Linux
source venv/bin/activate

pip install -r requirements.txt

```

Then, download the dataset https://www.yelp.com/dataset. Extract its content, then extract once again in the data folder
 to get all of the data. 
 
Open the .gitignore file (assuming the code has been cloned from the repository) and add "data/" to the list of excluded
 folders.
 
Run the app

```

python app.py

```

## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots

