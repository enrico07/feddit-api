from typing import List, Optional, Tuple

from textblob import TextBlob

from app.database.postgre import PostgreClient


class CommentsHandler:

    def __init__(self):
        self.db_client = PostgreClient()

    @staticmethod
    def get_polarity(text: str) -> Tuple[str, str]:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            polarity_classification = "positive"
        elif polarity < -0.1:
            polarity_classification = "negative"
        else:
            polarity_classification = "neutral"

        return polarity, polarity_classification

    def get_comments(
        self,
        subfeddit_name: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        polarity_sorting: str = None,
        n_comments: int = 25,
        min_polarity: str = -1,
        max_polarity: str = 1,
    ) -> List[dict]:
        subfeddit_id = self.db_client.get_subfeddit_id(subfeddit_name=subfeddit_name)
        retrieved_comments = self.db_client.get_comments(
            subfeddit_id=subfeddit_id,
            from_date=from_date,
            to_date=to_date,
            n_comments=n_comments,
        )
        comments = []

        for comment in retrieved_comments:
            polarity_score, polarity_classification = self.get_polarity(comment["text"])

            comment["polarity_score"] = polarity_score
            comment["polarity_classification"] = polarity_classification

            if polarity_score >= min_polarity and polarity_score <= max_polarity:
                comments.append(comment)

        if polarity_sorting:
            reverse = True if polarity_sorting == "desc" else False
            comments.sort(key=lambda x: x["polarity_score"], reverse=reverse)

        return comments
