import streamlit as st
import altair as alt
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import pandas as pd


def main():
    # Grab media data
    df = get_data()
    """
    # Pictionary Generator

    Given it a whirl to find a book, TV programme, or film to use in pictionary.
    """
    clicked = st.button('Click to refresh data')
    if clicked:
        st.write(df.sample(1, weights='weight'))
    """

    The code for this app is available at:

    [https://github.com/aeturrell/millennium-app]
    (https://github.com/aeturrell/millennium-app)
    """


@st.cache
def get_data():
    # Download IMDB's Top 250 data
    user_agent_desktop = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 "
        "Safari/537.36"
    )
    headers = {"User-Agent": user_agent_desktop, "Accept-Language": "en-US,en;q=0.8"}
    url = "http://www.imdb.com/chart/top"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    movies = soup.select("td.titleColumn")
    m_strings = [x.get_text().split("\n")[2].lstrip() for x in movies]
    # Trunate films a bit to first 100
    m_strings = m_strings[:100]
    # Get books
    b_url = "https://www.listchallenges.com/the-greatest-novels-of-all-time"
    b_response = requests.get(b_url, headers=headers)
    b_soup = BeautifulSoup(b_response.text, "lxml")
    mydivs = b_soup.findAll("div", {"class": "item-name"})
    books = [x.text.strip() for x in mydivs]
    # Get TV shows
    t_url = "https://www.ign.com/lists/top-100-tv-shows/20"
    t_response = requests.get(t_url, headers=headers)
    t_soup = BeautifulSoup(t_response.text, "lxml")
    t_divs = t_soup.findAll("div", {"class": "item-heading"})
    tv_shows = [x.text.split(">")[-1].replace("</a>", "").strip() for x in t_divs]
    col_list = ["Title", "Type"]
    df = pd.concat(
        [
            pd.DataFrame(
                np.array([m_strings, ["Film"] * len(m_strings)]).T, columns=col_list
            ),
            pd.DataFrame(
                np.array([tv_shows, ["TV"] * len(tv_shows)]).T, columns=col_list
            ),
            pd.DataFrame(np.array([books, ["Book"] * len(books)]).T, columns=col_list),
        ],
        axis=0,
    )
    df["weight"] = 1 / 3
    df["weight"] = df.groupby("Type")["weight"].transform(lambda x: x / x.count())
    return df


if __name__ == "__main__":
    main()
