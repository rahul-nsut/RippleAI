from app.core.vectorstore import get_vectorstore
from app.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an internal documentation assistant.
Respond to user in a friendly and helpful manner. 
Answer the question ONLY using the context below.
If the answer is not present, say:
"I could not find this information in the documentation."

Context:
{context}

Question:
{question}

Answer:
Be concise and to the point.
Try to build on the answer you receive from the document and return it in a concise manner.
Donot deviate or return anything at all which is not present in the document.
"""

)

def answer_question(question: str):
    logger.info(f"Received question: {question}")
    
    vectorstore = get_vectorstore()
    logger.info("Got vectorstore")

    docs = vectorstore.similarity_search(question, k=15)
    logger.info(f"Found {len(docs)} documents")

    if not docs:
        logger.warning("No documents found")
        return {
            "answer": "No relevant documentation found.",
            "sources": []
        }

    context = "\n\n".join(d.page_content for d in docs)
    logger.info(f"Context length: {len(context)} characters")

    try:
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set")

        logger.info("Calling OpenRouter LLM...")
        llm = ChatOpenAI(
            model=settings.OPENROUTER_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            temperature=0,
            max_tokens=256,
            timeout=25.0,
        )
        # LangChain will wrap the string as a user message for ChatOpenAI
        response = llm.invoke(PROMPT.format(context=context, question=question))
        answer_text = response.content if hasattr(response, 'content') else str(response)
        logger.info("Got response from OpenRouter")
    except Exception as e:
        logger.error(f"Error calling OpenRouter: {str(e)}")
        raise Exception(f"Error calling OpenRouter LLM: {str(e)}")

    sources = list({
        d.metadata.get("source")
        for d in docs
        if d.metadata.get("source")
    })

    return {
        "answer": answer_text.strip() if hasattr(answer_text, 'strip') else str(answer_text),
        "sources": sources
    }