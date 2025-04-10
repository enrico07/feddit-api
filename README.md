# Feddit APIs

# Introduction
This repository contains the implementation of the **Feddit APIs**. The `docker-compose.yml` file sets up the following services:

- **db**: PostgreSQL database service.
- **feddit**: Base (mock) Reddit-like API service.
- **feddit-api**: implemented API service that allows retrieving comments from a specific subfeddit using various filtering parameters. It also returns the **polarity score** and **sentiment classification** (positive, neutral, or negative) for each comment.

## Sentiment Polarity

The **polarity score** is a value ranging from **-1** to **1**:

- `0.1` to `1`: **Positive polarity**
- `-1` to `-0.1`: **Negative polarity**
- `-0.1` to `0.1`: **Neutral polarity**


# FEDDIT-API Specification
You can access the interactive API documentation via:

- [Swagger UI](http://0.0.0.0:8081/docs)
- [ReDoc](http://0.0.0.0:8081/redoc)

## Retrieve Comments Endpoint

**Endpoint:** `GET /comments`  
Use this endpoint to retrieve comments with various optional filters.

### Query Parameters

| Parameter         | Type   | Description |
|------------------|--------|-------------|
| `subfeddit_name` | string | The name of the subfeddit to retrieve comments from. |
| `n_comments`     | int    | The number of comments to retrieve (default: 25). |
| `from_date`      | string | The starting date for the comments. Format: `DD-MM-YYYY`. |
| `to_date`        | string | The ending date for the comments. Format: `DD-MM-YYYY`. |
| `polarity_sorting` | string | Whether to sort comments by polarity. Accepts `"asc"` or `"desc"`. Defaults to sorting from the most recent to the oldest. |
| `min_polarity`   | float  | Minimum polarity value for comments. Range: -1 to 1. |
| `max_polarity`   | float  | Maximum polarity value for comments. Range: -1 to 1. |


# How-to-run
1. Please make sure you have docker installed.
2. To run `Feddit-api` API locally in the terminal, replace `<path-to-docker-compose.yml>` by the actual path of the given `docker-compose.yml` file in `docker compose -f <path-to-docker-compose.yml> up -d`. It should be available in [http://0.0.0.0:8081](http://0.0.0.0:8081). 
3. To stop `Feddit` API in the terminal,  replace `<path-to-docker-compose.yml>` by the actual path of the given `docker-compose.yml` file in `docker compose -f <path-to-docker-compose.yml> down`.


# Data Schemas
## Comment

+ **id**: unique identifier of the comment.
+ **username**: user who made/wrote the comment.
+ **text**: content of the comment in free text format.
+ **created_at**: timestamp in unix epoch time indicating when the comment was made/wrote.

## Subfeddit
+ **id**: unique identifier of the subfeddit
+ **username**: user who started the subfeddit.
+ **title**: topic of the subfeddit.
+ **description**: short description of the subfeddit.
+ **comments**: comments under the subfeddit.

