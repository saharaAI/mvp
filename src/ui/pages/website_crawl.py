# --- src/ui/pages/website_crawl.py ---
import streamlit as st
import requests
from bs4 import BeautifulSoup

def display_website_crawl():
    """Renders the Website Crawl page."""
    st.markdown("# Website Crawl 🕸️")

    # Input URL from user
    url = st.text_input("Enter the URL to crawl:")

    if st.button("Crawl Website"):
        if url:
            with st.spinner("Crawling the website..."):
                # Perform web crawling
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an HTTPError for bad responses
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract and display page title
                    page_title = soup.title.string if soup.title else "No Title Found"
                    st.write(f"**Page Title:** {page_title}")

                    # Extract and display all links
                    links = [a['href'] for a in soup.find_all('a', href=True)]
                    if links:
                        st.write("**Links found on the page:**")
                        for link in links:
                            st.write(link)
                    else:
                        st.write("No links found on the page.")

                    # Display a snippet of the content
                    content_snippet = soup.get_text()[:1000]  # Limit the content length to avoid overload
                    st.subheader("Content Snippet")
                    st.text_area("", content_snippet, height=300)

                except requests.RequestException as e:
                    st.error(f"Error while crawling the website: {e}")
        else:
            st.warning("Please enter a URL.")
