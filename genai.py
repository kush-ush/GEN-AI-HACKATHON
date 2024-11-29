from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex , SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core import Settings
import pandas as pd
from llama_index.core import StorageContext
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from typing import List, NamedTuple
import json
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import KnowledgeGraphIndex
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from llama_index.core.prompts.guidance_utils import convert_to_handlebars
import markdown
class Meeting_assist:
    def __init__(self):
        self.llm = Ollama(model = 'llama3.2:3b-instruct-q8_0')
        self.threshold = 20
        self.checkllm = Ollama(model='llama3.2:3b-instruct-q8_0')
    def initialize(self):
        self.documents = SimpleDirectoryReader("Documents", exclude_hidden=False).load_data()
        embed_model = resolve_embed_model("local:BAAI/bge-m3")
        graph_store = SimpleGraphStore()
        storage_context = StorageContext.from_defaults(graph_store=graph_store)
        index = KnowledgeGraphIndex.from_documents(documents=self.documents,
                                                   max_triplets_per_chunk=3,
                                                   storage_context=storage_context,
                                                   embed_model=embed_model,
                                                   include_embeddings=True,
                                                   llm=self.llm)
        self.query_engine = index.as_query_engine(include_text=True,
                                                  response_mode="tree_summarize",
                                                  embedding_mode="hybrid",
                                                  similarity_top_k=5,
                                                  llm=self.llm)
        self.generated_text = ""
        for doc in self.documents:
            self.generated_text = self.generated_text + doc.text + "\n"
 
    def summerise(self , chunk_size =800 , context_size = 50):
        string = self.generated_text    
        total_chars = len(string)
        summerise_string = " "
        print("Started summerisizng")
        for i in range(0, total_chars, chunk_size):
            start_index = max(i - context_size, 0)
            end_index = min(i + chunk_size + context_size, total_chars)
            chunk = string[start_index:end_index]
            summerise_string = summerise_string + " " + str(self.llm.complete(chunk + "This is a part extracted text from the meeting give a breif summary and dont start with here is the summary like a bot"))
        print(summerise_string)
        with open("summary.txt", "w") as file:
         file.write(summerise_string)
        return summerise_string
    def answer_from_documents(self, query):
        self.query = query 
        print("Answering doubt...")
        try:
            self.answer = self.query_engine.query(query + " elaborately")
            self.ansr = str(self.answer)
            if self.similarity() > self.threshold:
                return f'{self.answer}'
            else:
                return f'The relaiblity is low please also refer to other sources like your uploaded document and sites like wiki. Answer: {self.answer}'
        except Exception as e:
            print(f"Error answering query: {e}")
            return "Unable to retrieve answer from documents."
    def similarity(self):
        text1 = str(self.checkllm.complete(self.query))
        text2 = self.ansr
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        print(f"Reliablity %: {similarity[0][0]*100}")            
        return similarity[0][0]*100
    