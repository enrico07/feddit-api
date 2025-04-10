from typing import List, Optional, Tuple

from textblob import TextBlob

from app.database.postgre import PostgreClient


class CommentsHandler:
    """
    A class to handle operations related to comments.
    It includes methods to get comments, analyze their sentiment, and filter them based on sentiment polarity.
    """

    def __init__(self):
        """
        Initializes the CommentsHandler instance and establishes a database client connection
        using PostgreClient for querying data.
        """

        self.db_client = PostgreClient()

    @staticmethod
    def get_polarity(text: str) -> Tuple[str, str]:
        """
        Analyzes the sentiment of the given text using TextBlob and returns its polarity score
        and classification ('positive', 'negative', or 'neutral') based on the polarity score.

        Args:
            text (str): The text whose sentiment is to be analyzed.

        Returns:
            Tuple[str, str]: A tuple containing the polarity score (float) and the sentiment classification (str).
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        # Classifying sentiment based on the polarity score
        if polarity > 0.1:
            polarity_classification = "positive"
        elif polarity < -0.1:
            polarity_classification = "negative"
        else:
            polarity_classification = "neutral"

        return polarity, polarity_classification

    async def get_comments(
        self,
        subfeddit_name: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        polarity_sorting: str = None,
        n_comments: int = 25,
        min_polarity: str = -1,
        max_polarity: str = 1,
    ) -> List[dict]:
        """
        Fetches comments from a specific subfeddit, analyzes their sentiment, and applies filters
        such as date range, polarity range, and sorting by polarity.

        Args:
            subfeddit_name (str): The name of the subfeddit from which to fetch comments.
            from_date (Optional[str]): Start date for filtering comments (inclusive). Defaults to None.
            to_date (Optional[str]): End date for filtering comments (inclusive). Defaults to None.
            polarity_sorting (str): 'asc' or 'desc' to sort comments by polarity score. Defaults to None.
            n_comments (int): Number of comments to fetch. Defaults to 25.
            min_polarity (str): Minimum polarity value to filter comments. Defaults to -1 (allow all).
            max_polarity (str): Maximum polarity value to filter comments. Defaults to 1 (allow all).

        Returns:
            List[dict]: A list of comments with sentiment analysis results and optional filters applied.
        """
        # Retrieve the ID of the subfeddit from the database
        subfeddit_id = await self.db_client.get_subfeddit_id(
            subfeddit_name=subfeddit_name
        )

        # Retrieve the comments from the database for the given subfeddit, with optional filters
        retrieved_comments = await self.db_client.get_comments(
            subfeddit_id=subfeddit_id,
            from_date=from_date,
            to_date=to_date,
            n_comments=n_comments,
        )
        comments = []

        # Process each retrieved comment
        for comment in retrieved_comments:
            # Get the polarity score and classification for the comment text
            polarity_score, polarity_classification = self.get_polarity(comment["text"])

            # Add polarity score and classification to the comment
            comment["polarity_score"] = polarity_score
            comment["polarity_classification"] = polarity_classification

            # Filter comments based on the given polarity range (min_polarity to max_polarity)
            if polarity_score >= min_polarity and polarity_score <= max_polarity:
                comments.append(comment)

        # If polarity sorting is requested, sort comments by their polarity score
        if polarity_sorting:
            reverse = True if polarity_sorting == "desc" else False
            comments.sort(key=lambda x: x["polarity_score"], reverse=reverse)

        return comments
