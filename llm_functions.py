# general libraries
from datetime import datetime
import json

# LLM related libraries
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


def select_category():
    """Select Category based upon weekday"""
    categories = {
        0: "Python Programming",
        1: "Database Management",
        2: "Website Development",
        3: "Data Science",
        4: "Graphic Designing",
        5: "Cloud Computing",
        6: "Data Structures & Algorithms"
    }
    return categories[datetime.now().weekday()]


def generate_post(category, openai_api_key):
    """Generate post using category and openai_api_key"""

    prompt_template = """
        Context: 
            We are Orbytal Solutions (IT company) with page in Instagram. We have multiple-subcategories on category below:
            Category: {category}
        
        Task:
            Generate an Instagram post on random topic (junior to intermediate level) for one of those sub-categories. Don't include already used topic.
            
            Respond in a JSON format like this:
            {{
                "title": "Your catchy title. Maximum 1 line with 50 characters (including spaces).",
                "description": "A clear engaging explanation of the topic. 10-20 lines."
                "code": "Optional short code block of 5-10 lines or empty string. Don't include more than 60 characters per line here including spaces."
            }}
        
        Additional details:
            - Use only one paragraph and bullets if needed in description.
            - Don't use more than 5 lines for one paragraph.
            - Represent bullet by *.
            - Don't use emojis.
            - Sum of lines used by description and code should be 15-20 lines strictly.
            - Also add empty line in code after end of block of code like classes, functions or loops.
            - Don't write incomplete code like comments only.
        
        STRICTLY USE BULLETS AND PARAGRAPHS IN DIFFERENT LINES.
        Recheck and correct if errors and mistakes.
        """
    prompt = PromptTemplate(
        input_variables=["topic"],
        template=prompt_template
    )
    llm = ChatOpenAI(temperature=1.0, max_tokens=1024, model_name="gpt-4.1-mini", openai_api_key=openai_api_key)
    chain = prompt | llm
    post = chain.invoke({"category": category}).content
    start = post.find('{')
    end = post.rfind('}')
    return json.loads(post[start: end+1])


def create_caption(post, openai_api_key):
    """Create caption from post"""
    prompt_template = """
            Generate short caption for this Instagram post.
            Title: {title}
            Description: {description}

            The caption should also attract customers to contact our Instagram profile Orbytal Solutions for python programming, website development, graphic designing, data science, database management, cloud computing and many more. Customers should DM for inquiries. Help in assignments and tutoring are also available.
            The content should be placed properly in lines.
            Add at least 10 hashtags.
            """
    prompt = PromptTemplate(
        input_variables=["title", "description"],
        template=prompt_template
    )
    llm = ChatOpenAI(temperature=1.0, max_tokens=1024, model_name="gpt-4.1-mini", openai_api_key=openai_api_key)
    chain = prompt | llm
    return chain.invoke({"title": post["title"], "description": post["description"]}).content