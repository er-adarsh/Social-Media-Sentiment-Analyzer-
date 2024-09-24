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

nltk.download('vader_lexicon')
nltk.download('stopwords')

# Predefined YouTube API key
YOUTUBE_API_KEY = ''

# Function to get comments from YouTube video
def get_youtube_comments(video_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    comments = []
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100
    )
    response = request.execute()

    while request is not None:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100
            )
            response = request.execute()
        else:
            break
    return comments

# Function to get comments from Instagram post
def get_instagram_comments(post_url):
    L = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(L.context, post_url.split('/')[-2])
    comments = [comment.text for comment in post.get_comments()]
    return comments

# Function to perform sentiment analysis and extract top words
def analyze_sentiments(comments):
    stop_words = set(stopwords.words('english'))
    sid = SentimentIntensityAnalyzer()
    sentiments = {'positive': [], 'negative': [], 'neutral': []}
    positive_words = []
    negative_words = []

    for comment in comments:
        words = [word for word in comment.split() if word.lower() not in stop_words]
        score = sid.polarity_scores(comment)
        if score['compound'] >= 0.05:
            sentiments['positive'].append(comment)
            positive_words.extend(words)
        elif score['compound'] <= -0.05:
            sentiments['negative'].append(comment)
            negative_words.extend(words)
        else:
            sentiments['neutral'].append(comment)

    top_positive_words = Counter(positive_words).most_common(10)
    top_negative_words = Counter(negative_words).most_common(10)

    return sentiments, top_positive_words, top_negative_words

# Chatbot responses

# Dash app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

home_page = html.Div([
    html.Header([
        html.Img(src='https://cdn-icons-png.flaticon.com/512/12373/12373911.png', style={'width': '100px', 'height': '100px', 'margin': '10px'}),
        html.H1('Redil', style={'font-family': 'Arial, sans-serif', 'color': '#ffffff', 'fontSize': '3em', 'margin': '0'}),
        html.H2('Your go-to platform for social media sentiment analysis', style={'font-family': 'Arial, sans-serif', 'color': '#ffffff', 'fontSize': '1.5em', 'margin': '0'})
    ], style={'text-align': 'center', 'background-color': '#343a40', 'padding': '20px', 'borderBottom': '2px solid #ffffff'}),
    
    html.Div(style={
        'backgroundImage': 'url(https://img.freepik.com/free-vector/dark-wavy-colors-background_23-2148403785.jpg?w=900&t=st=1724293011~exp=1724293611~hmac=9e15fae3d6e70356d18cadb36743fd7069b7cb855a0e6c19193e9a12415e7def)', 
        'height': '400px',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'flexDirection': 'column'
    }, children=[
        dbc.Nav([
            dbc.NavItem(dbc.NavLink('YouTube Analysis', href='/youtube', style={'color': '#ffffff', 'fontSize': '1.2em', 'padding': '10px 20px'})),
            dbc.NavItem(dbc.NavLink('Instagram Analysis', href='/instagram', style={'color': '#ffffff', 'fontSize': '1.2em', 'padding': '10px 20px'})),
            dbc.NavItem(dbc.NavLink('Chatbot', href='/chatbot', style={'color': '#ffffff', 'fontSize': '1.2em', 'padding': '10px 20px'})),
            dbc.NavItem(dbc.NavLink('Feedback', href='/feedback', style={'color': '#ffffff', 'fontSize': '1.2em', 'padding': '10px 20px'})),
            dbc.NavItem(dbc.NavLink('About Us', href='/about', style={'color': '#ffffff', 'fontSize': '1.2em', 'padding': '10px 20px'}))
        ], pills=True, style={'backgroundColor': 'rgba(0, 0, 0, 0.7)', 'padding': '10px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)'})
    ])
])

# 
youtube_page = html.Div([
    html.H1('YouTube Comment Sentiment Analysis', style={'textAlign': 'center', 'color': '#ffffff', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Input(
            id='youtube-video-url', 
            type='text', 
            placeholder='Enter YouTube video URL', 
            style={'width': '100%', 'padding': '15px', 'borderRadius': '10px', 'border': '1px solid #ccc', 'marginBottom': '20px', 'backgroundColor': '#2c3e50', 'color': '#ffffff'}
        ),
        
        html.Button(
            'Analyze YouTube', 
            id='analyze-youtube-button', 
            n_clicks=0, 
            style={'width': '100%', 'padding': '15px', 'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'borderRadius': '10px', 'cursor': 'pointer', 'marginBottom': '10px'}
        ),
        
        html.Button(
            'Show All Sorted Comments', 
            id='show-all-comments-button', 
            n_clicks=0, 
            style={'width': '100%', 'padding': '15px', 'backgroundColor': '#2ecc71', 'color': 'white', 'border': 'none', 'borderRadius': '10px', 'cursor': 'pointer'}
        ),
        
        html.Div(
            id='youtube-output-div', 
            style={'border': '1px solid #ccc', 'padding': '15px', 'height': '300px', 'overflowY': 'scroll', 'marginTop': '20px', 'borderRadius': '10px', 'backgroundColor': '#2c3e50', 'color': '#ffffff'}
        )
    ], style={
        'width': '50%', 
        'margin': '0 auto', 
        'padding': '20px', 
        'boxShadow': '0 0 20px rgba(0, 0, 0, 0.2)', 
        'borderRadius': '20px', 
        'backgroundColor': '#ecf0f1',
        'backgroundImage': 'url("https://img.freepik.com/free-vector/dark-wavy-colors-background_23-2148403785.jpg?w=900&t=st=1724293011~exp=1724293611~hmac=9e15fae3d6e70356d18cadb36743fd7069b7cb855a0e6c19193e9a12415e7def")',
        'backgroundSize': 'cover'
    })
])

instagram_page = html.Div([
    html.Header([
        html.H1('Instagram Comment Sentiment Analysis', style={'font-family': 'Arial, sans-serif', 'color': '#ffffff'}),
    ], style={'text-align': 'center', 'background-color': '#343a40', 'padding': '20px'}),
    
    html.Div([
        dcc.Input(
            id='instagram-post-url', 
            type='text', 
            placeholder='Enter Instagram post URL', 
            style={
                'width': '60%', 
                'padding': '10px', 
                'border-radius': '5px', 
                'border': '1px solid #ccc', 
                'margin-bottom': '20px'
            }
        ),
        html.Button(
            'Analyze Instagram', 
            id='analyze-instagram-button', 
            n_clicks=0, 
            style={
                'background-color': '#007bff', 
                'color': '#ffffff', 
                'border': 'none', 
                'padding': '10px 20px', 
                'border-radius': '5px', 
                'cursor': 'pointer'
            }
        ),
        html.Div(id='instagram-output-div', style={'margin-top': '20px'})
    ], style={
        'display': 'flex', 
        'flex-direction': 'column', 
        'align-items': 'center', 
        'justify-content': 'center', 
        'height': '80vh'
    })
])

chatbot_page = html.Div([
    html.H1('Chatbot - Redil', style={'textAlign': 'center', 'color': '#ffffff', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Input(
            id='user-input', 
            type='text', 
            placeholder='Ask me anything...', 
            style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #ccc', 'marginBottom': '10px', 'backgroundColor': '#2c3e50', 'color': '#ffffff'}
        ),
        
        html.Button(
            'Send', 
            id='send-button', 
            n_clicks=0, 
            style={'width': '100%', 'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}
        ),
        
        html.Div(
            id='chat-output', 
            style={'border': '1px solid #ccc', 'padding': '10px', 'height': '300px', 'overflowY': 'scroll', 'marginTop': '20px', 'borderRadius': '5px', 'backgroundColor': '#2c3e50', 'color': '#ffffff'}
        )
    ], style={
        'width': '50%', 
        'margin': '0 auto', 
        'padding': '20px', 
        'boxShadow': '0 0 10px rgba(0, 0, 0, 0.1)', 
        'borderRadius': '10px', 
        'backgroundColor': '#ecf0f1',
        'backgroundImage': 'url("https://img.freepik.com/free-vector/dark-wavy-colors-background_23-2148403785.jpg?w=900&t=st=1724293011~exp=1724293611~hmac=9e15fae3d6e70356d18cadb36743fd7069b7cb855a0e6c19193e9a12415e7def")',
        'backgroundSize': 'cover'
    })
])


# chatbot_page = html.Div([
#     html.H1('Chatbot - Redil'),
#     dcc.Input(id='user-input', type='text', placeholder='Ask me anything...', style={'width': '50%'}),
#     html.Button('Send', id='send-button', n_clicks=0),
#     html.Div(id='chat-output', style={'border': '1px solid #ccc', 'padding': '10px', 'height': '300px', 'overflowY': 'scroll'})
# ])

# feedback_page = html.Div([
#     html.H1('Feedback'),
#     dcc.Input(id='feedback-rating', type='number', min=1, max=5, placeholder='Rate out of 5'),
#     dcc.Textarea(id='feedback-review', placeholder='Write your review here...', style={'width': '50%', 'height': '150px'}),
#     html.Button('Submit Feedback', id='submit-feedback-button', n_clicks=0),
#     html.Div(id='feedback-output-div')
# ])

feedback_page = html.Div([
    html.H1('Feedback', style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Input(
            id='feedback-rating', 
            type='number', 
            min=1, 
            max=5, 
            placeholder='Rate out of 5', 
            style={'width': '100%', 'padding': '10px', 'marginBottom': '20px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
        ),
        
        dcc.Textarea(
            id='feedback-review', 
            placeholder='Write your review here...', 
            style={'width': '100%', 'height': '150px', 'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #ccc'}
        ),
        
        html.Button(
            'Submit Feedback', 
            id='submit-feedback-button', 
            n_clicks=0, 
            style={'width': '100%', 'padding': '10px', 'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'marginTop': '20px'}
        ),
        
        html.Div(id='feedback-output-div', style={'marginTop': '20px', 'textAlign': 'center'})
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '20px', 'boxShadow': '0 0 10px rgba(0, 0, 0, 0.1)', 'borderRadius': '10px', 'backgroundColor': '#f9f9f9'})
])

about_page = html.Div([
    html.H1('About Us', style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
    
    html.Div([
        html.H3('Our Story', style={'textAlign': 'center', 'color': '#34495e', 'marginBottom': '20px'}),
        
        html.P(
            'Developed through the dedicated efforts of Raghuvendra and Adarsh, Redil is a cutting-edge sentiment analysis app designed to understand and interpret human emotions in text. Our app leverages advanced algorithms and machine learning techniques to provide accurate sentiment analysis, making it an invaluable tool for businesses, researchers, and individuals alike.',
            style={'textAlign': 'justify', 'color': '#7f8c8d', 'lineHeight': '1.6', 'marginBottom': '20px'}
        ),
        
        html.H2('Contact Us', style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '40px', 'marginBottom': '20px'}),
        
        html.P(
            'For any inquiries, feedback, or support, please reach out to us at:',
            style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '10px'}
        ),
        
        html.P(
            'Email: support@redilapp.com',
            style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '5px'}
        ),
        
        html.P(
            'Phone: +91-9631085870',
            style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '5px'}
        ),
        
        html.P(
            'Address: Noida, Uttar Pradesh, India',
            style={'textAlign': 'center', 'color': '#7f8c8d'}
        )
    ], style={'width': '60%', 'margin': '0 auto', 'padding': '20px', 'boxShadow': '0 0 10px rgba(0, 0, 0, 0.1)', 'borderRadius': '10px', 'backgroundColor': '#ecf0f1'})
])

# Define the app layout with a location component
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Update the page content based on the URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/youtube':
        return youtube_page
    elif pathname == '/instagram':
        return instagram_page
    elif pathname == '/chatbot':
        return chatbot_page
    elif pathname == '/feedback':
        return feedback_page
    elif pathname == '/about':
        return about_page
    else:
        return home_page

# Callbacks for YouTube and Instagram analysis
@app.callback(
    Output('youtube-output-div', 'children'),
    [Input('analyze-youtube-button', 'n_clicks')],
    [State('youtube-video-url', 'value')]
)
def update_youtube_output(n_clicks, video_url):
    if n_clicks > 0 and video_url:
        video_id = video_url.split('v=')[1]
        comments = get_youtube_comments(video_id)
        sentiments, top_positive_words, top_negative_words = analyze_sentiments(comments)

        fig_pie = px.pie(values=[len(sentiments['positive']), len(sentiments['negative']), len(sentiments['neutral'])],
                         names=['Positive', 'Negative', 'Neutral'],
                         title='Sentiment Distribution')

        fig_bar = go.Figure(data=[
            go.Bar(name='Positive', x=['Positive'], y=[len(sentiments['positive'])], marker_color='green'),
            go.Bar(name='Negative', x=['Negative'], y=[len(sentiments['negative'])], marker_color='red'),
            go.Bar(name='Neutral', x=['Neutral'], y=[len(sentiments['neutral'])], marker_color='blue')
        ])
        fig_bar.update_layout(barmode='group', title='Sentiment Analysis Bar Graph')

        return html.Div([
            html.H3(f'Total comments extracted: {len(comments)}'),
            html.H3(f'Positive comments: {len(sentiments["positive"])}'),
            html.H3(f'Negative comments: {len(sentiments["negative"])}'),
            html.H3(f'Neutral comments: {len(sentiments["neutral"])}'),
            html.H4('Top 10 Positive Words'),
            html.Ul([html.Li(f'{word}: {count}') for word, count in top_positive_words]),
            html.H4('Top 10 Negative Words'),
            html.Ul([html.Li(f'{word}: {count}') for word, count in top_negative_words]),
            html.H4('Sentiment Distribution'),
            dcc.Graph(figure=fig_pie),
            html.H4('Sentiment Analysis Bar Graph'),
            dcc.Graph(figure=fig_bar),
            html.Div(id='youtube-comments-div'),
            html.Div(id='youtube-comments-div'),
            html.Div(id='youtube-comments-div'),
            html.Div(id='youtube-comments-div')
            
        ])

@app.callback(
    Output('youtube-comments-div', 'children'),
    [Input('show-all-comments-button', 'n_clicks')],
    [State('youtube-video-url', 'value')]
)
def show_all_youtube_comments(n_clicks, video_url):
    if n_clicks > 0 and video_url:
        video_id = video_url.split('v=')[1]
        comments = get_youtube_comments(video_id)
        
        # Analyze sentiments and get sorted comments
        sentiments, _, _ = analyze_sentiments(comments)
        
        # Flatten the lists of comments and sort them
        sorted_comments = (
            sentiments['positive'] +
            sentiments['neutral'] +
            sentiments['negative']
        )
        
        return html.Div([
            html.H4('All Comments Sorted by Sentiment:'),
            html.Ul([html.Li(comment) for comment in sorted_comments])
        ])
    return html.Div()


@app.callback(
    Output('chat-output', 'children'),
    [Input('send-button', 'n_clicks')],
    [State('user-input', 'value')]
)
def update_chat_output(n_clicks, user_input):
    if n_clicks > 0 and user_input:
        sid = SentimentIntensityAnalyzer()
        score = sid.polarity_scores(user_input)
        sentiment = 'positive' if score['compound'] >= 0.05 else 'negative' if score['compound'] <= -0.05 else 'neutral'

        response = ""
        if any(word in user_input.lower() for word in ['who' and 'you']):
            response = "I am Redil AI developed by sir Adarsh to help you with various sentiment analysis tasks."
        elif any(word in user_input.lower() for word in ['how', 'you']):
            response = "I am fine. Let's hear about you!"
        elif any(word in user_input.lower() for word in ['joke', 'jokes', 'yes', 'yup', 'ya']):
            response = random.choice(jokes)
        elif any(word in user_input.lower() for word in ['hello', 'hi', 'namaste', 'heyy', 'hey']):
            response = random.choice(greetings)
        else:
            if sentiment == 'positive':
                response = random.choice(positive_responses)
            elif sentiment == 'negative':
                response = random.choice(negative_responses) + " Would you like to hear a joke? (yes/no)"
            else:
                response = "I'm here to assist you with your queries!"

        return html.Div([
            html.Div(f'User: {user_input}', style={'color': 'blue'}),
            html.Div(f'Chatbot: {response}', style={'color': 'green'})
        ], style={'padding': '10px'})

@app.callback(
    Output('feedback-output-div', 'children'),
    [Input('submit-feedback-button', 'n_clicks')],
    [State('feedback-rating', 'value'),
     State('feedback-review', 'value')]
)
def update_feedback_output(n_clicks, review):
    if n_clicks > 0 and review:
        sid = SentimentIntensityAnalyzer()
        #rating_score = sid.polarity_scores(str(rating))['compound']
        review_score = sid.polarity_scores(review)['compound']

        #rating_sentiment = 'positive' if rating_score > 3 else 'negative' if rating_score < 3 else 'neutral'
        review_sentiment = 'positive' if review_score > 0.05 else 'negative' if review_score < -0.05 else 'neutral'

        def feedback_response(rating, review):
            if rating and review:
                if (rating in ['1', '2'] and review_sentiment == 'positive') or (rating in ['3', '4', '5'] and review_sentiment == 'negative'):
                    return html.Div("Thank you for your feedback!")
                else:
                    return html.Div("Thank you for the feedback!!")
            else:
                return html.Div("Please provide both rating and review.")


if __name__ == '__main__':
    app.run_server(debug=True)
