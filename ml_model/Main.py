from .Scraping import scrape_comments
from .ModelImpoter import analyze_social_media_sentiments,single_prediction
from dotenv import load_dotenv
import os


def analyser(topic,api=""):
    result = scrape_comments(topic,api)
    sentiment_results = analyze_social_media_sentiments(result)
    return sentiment_results

'''
result = scrape_comments("Us Iran War", youtube_api_key=api)
sentiment_results = analyze_social_media_sentiments(result)

for platform, comments in sentiment_results.items():
    for com in comments:
        print(com,"\n")
'''
'''
# result is a dict: { "Reddit": [...], "HackerNews": [...], "Dev.to": [...], "YouTube": [...] }
for platform, comments in result.items():
    print(f"{platform}: {len(comments)} comments")
    for com in comments:
        print(com)
        print()
'''
#print(analyser('Elon Musk'))

#print(single_prediction("Good you done a very nice work"))
#print(single_prediction('Fuck you bitch'))