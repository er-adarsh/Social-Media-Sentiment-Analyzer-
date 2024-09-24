# Social-Media-Sentiment-Analyzer-

## Project Overview

The **Social Media Sentiment Analyzer** is a web-based tool that fetches, analyzes, and visualizes the sentiment of comments from social media posts. Using a **lexicon-based sentiment analysis approach**, the application organizes comments based on sentiment scores and generates graphs to display sentiment trends. The tool also includes a **feedback page** and a sentiment-aware chatbot that interacts with users based on their emotional tone.

## Features

- **Lexicon-Based Sentiment Analysis**: Uses the VADER sentiment analysis tool for accurate sentiment scoring.
- **API Integration**: Fetches comments from social media platforms using various APIs (Google YouTube, Instagram, etc.).
- **Sentiment-Based Comment Arrangement**: Comments are organized into positive, neutral, and negative categories.
- **Data Visualization**: Creates interactive graphs and visualizations using Plotly.
- **Chatbot Interaction**: Provides dynamic responses based on user sentiment.
- **Feedback Page**: Users can submit feedback, which is analyzed to further improve the application.

## Technologies Used

- **Dash**: For building interactive web applications.
- **Dash Bootstrap Components**: For responsive and modern UI.
- **Pandas**: For data manipulation and analysis.
- **NLTK**: For natural language processing and sentiment analysis (VADER).
- **Google API Client**: To fetch comments from YouTube.
- **Instaloader**: To fetch Instagram data.
- **Plotly**: For creating interactive visualizations and graphs.
- **Random**: For generating random responses for the chatbot.

## Python Libraries

Here’s a list of the Python libraries used in the project:

```bash
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from collections import Counter
from googleapiclient.discovery import build
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import plotly.express as px
import plotly.graph_objects as go
import instaloader
import random
from nltk.corpus import stopwords

# Ensure necessary NLTK resources are downloaded
nltk.download('vader_lexicon')
nltk.download('stopwords')
```
## Installation and Setup

Make sure you have the following installed:
- Python 3.x
- API keys for social media platforms (e.g., Google, Instagram)
- Internet connection for fetching data from APIs

## Usage
1. Fetch Comments: Enter the social media post URL (YouTube or Instagram), and the app fetches comments using the relevant API.
2. Analyze Sentiment: The system uses the VADER sentiment analysis tool to score each comment.
3. Visualize Data: View dynamic graphs and sentiment trends using Plotly visualizations.
4. Chatbot: Interact with a chatbot that responds based on the sentiment of your feedback.
5. Provide Feedback: Submit your feedback through the feedback page and let the system analyze your sentiment.

## Example graph visulaizations


