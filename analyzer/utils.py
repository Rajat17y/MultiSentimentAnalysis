def calculate_statistics(results):

    total_comments = 0

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for platform_comments in results.values():

        for comment_data in platform_comments:

            comment = comment_data[0]
            sentiment = comment_data[1]
            confidence = comment_data[2]

            total_comments += 1

            if sentiment == "positive":
                positive_count += 1

            elif sentiment == "negative":
                negative_count += 1

            elif sentiment == "neutral":
                neutral_count += 1

    if total_comments > 0:

        positive_rate = (
            positive_count / total_comments
        ) * 100

        negative_rate = (
            negative_count / total_comments
        ) * 100

        neutral_rate = (
            neutral_count / total_comments
        ) * 100

    else:

        positive_rate = 0
        negative_rate = 0
        neutral_rate = 0

    # Sentiment gap
    sentiment_gap = positive_rate - negative_rate

    # Overall sentiment
    if positive_count > negative_count and positive_count > neutral_count:
        overall_sentiment = "Positive"

    elif negative_count > positive_count and negative_count > neutral_count:
        overall_sentiment = "Negative"

    else:
        overall_sentiment = "Neutral"

    return {
        "total_comments": total_comments,

        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,

        "positive_rate": round(positive_rate, 2),
        "negative_rate": round(negative_rate, 2),
        "neutral_rate": round(neutral_rate, 2),

        "sentiment_gap": round(sentiment_gap, 2),

        "overall_sentiment": overall_sentiment,
    }