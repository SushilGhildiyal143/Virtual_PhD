from fastmcp import FastMCP

from tools.search_papers import search_papers
from tools.download_papers import download_papers
from tools.parse_pdf import extract_text
from tools.idea_extractor import extract_idea
from tools.gap_analysis import analyze_gaps
from tools.paper_writer import write_paper

mcp = FastMCP("ResearchAgent")

@mcp.tool()
def search(query: str):
    return search_papers(query)

@mcp.tool()
def download(pdf_url: str):
    return download_papers(pdf_url)

@mcp.tool()
def parse(pdf_path: str):
    return extract_text(pdf_path)

@mcp.tool()
def extract(text: str):
    return extract_idea(text)

@mcp.tool()
def gap_analysis(summaries: list):
    return analyze_gaps(summaries)

@mcp.tool()
def generate_paper(idea: str):
    return write_paper(idea)

if __name__ == "__main__":
    mcp.run()