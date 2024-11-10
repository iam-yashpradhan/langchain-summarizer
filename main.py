from crewai_tools import ScrapeWebsiteTool
import ollama
import re
import streamlit as st

def clean_text(text):
    # Remove hyperlinks
    text = re.sub(r'http\S+', '', text)
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    # Remove citations (assuming they are in square brackets)
    text = re.sub(r'\[\d+\]', '', text)
    return text

url = 'https://medium.com/feedzaitech/building-trust-in-a-digital-world-the-role-of-machine-learning-in-behavioral-biometrics-bb0da913d95a'

def scraperAgent(url):
    tool = ScrapeWebsiteTool(website_url= url)
    text = tool.run()
    text = clean_text(text)
    return text


def summaryAgent(data):
    response = ollama.chat(
        model='llama3.2:latest',
        messages=[{
            'role': 'system',
            'content': 'Act as an article summarizer, the user will give you clean text and you should be able to summarize it accurately. While writing the summary, directly start the response with the summary and no fillers'
        },{
            'role': 'user',
            'content': f'''Summarize the following {data} in a concise manner, highlighting the main points and key details'''
        }]
    ) ['message']['content']
    return (response)

def chatAgent(summary, question):
    response = ollama.chat(
        model='llama3.2:latest',
        messages=[{
            'role': 'system',
            'content': f'You are a helpful assistant. The user has read a summary of an article and will ask questions about it. The summary is: "{summary}". Answer any questions based on this summary and the article.'
        }, {
            'role': 'user',
            'content': question
        }]
    )['message']['content']
    return response

def main():
    st.title("Article Summarizer")
    
    url = st.text_input("Enter a URL", "")
    process = st.button("Scrape and Summarize")
    tab1, tab2 = st.tabs(['Summary', 'Chat'])

    if "summary" not in st.session_state:
        st.session_state.summary = ""
        
    with tab1:
        if process:
            if url:
                result = scraperAgent(url)
                st.session_state.summary = summaryAgent(result)
                st.write(st.session_state.summary)

            else:
                st.warning("Please enter a valid URL.")

    with tab2:
        st.header('Chat')
        if st.session_state.summary:
            # Initialize chat history if not already done
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Display previous chat messages from history on app rerun
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Accept user input via chat interface (st.chat_input)
            if user_input := st.chat_input("Ask a question about the article"):
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Get LLM response based on the user's question and the article summary
                response = chatAgent( st.session_state.summary, user_input)

                # Display LLM (assistant) response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response)

                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.info("No summary available yet. Please generate a summary in the Summary tab.")


if __name__ == "__main__":
    main()
