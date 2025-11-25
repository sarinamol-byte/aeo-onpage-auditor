from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
import textstat
import os


app = Flask(__name__)
CORS(app)

def fetch_page(url):
    """Fetch webpage content"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

def analyze_schema(soup):
    """Analyze structured data/schema markup"""
    schema_scripts = soup.find_all('script', type='application/ld+json')
    
    faq_present = False
    howto_present = False
    article_present = False
    faq_count = 0
    howto_count = 0
    
    for script in schema_scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    schema_type = item.get('@type', '').lower()
                    if 'faqpage' in schema_type:
                        faq_present = True
                        faq_count = len(item.get('mainEntity', []))
                    elif 'howto' in schema_type:
                        howto_present = True
                        howto_count = len(item.get('step', []))
                    elif 'article' in schema_type:
                        article_present = True
            else:
                schema_type = data.get('@type', '').lower()
                if 'faqpage' in schema_type:
                    faq_present = True
                    faq_count = len(data.get('mainEntity', []))
                elif 'howto' in schema_type:
                    howto_present = True
                    howto_count = len(data.get('step', []))
                elif 'article' in schema_type:
                    article_present = True
        except:
            continue
    
    return {
        'faq_present': faq_present,
        'faq_count': faq_count,
        'howto_present': howto_present,
        'howto_count': howto_count,
        'article_present': article_present
    }

def analyze_questions(soup):
    """Analyze question-based content"""
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    question_words = ['what', 'why', 'how', 'when', 'where', 'who', 'which', 'can', 'is', 'are', 'do', 'does']
    question_headings = []
    
    for heading in headings:
        text = heading.get_text().strip().lower()
        if any(text.startswith(qw) for qw in question_words) or text.endswith('?'):
            question_headings.append(heading.get_text().strip())
    
    return {
        'total_headings': len(headings),
        'question_headings': len(question_headings),
        'question_heading_examples': question_headings[:5]
    }

def analyze_snippet_optimization(soup):
    """Analyze featured snippet readiness"""
    # Find first paragraph
    paragraphs = soup.find_all('p')
    first_para_words = 0
    
    if paragraphs:
        first_para_text = paragraphs[0].get_text().strip()
        first_para_words = len(first_para_text.split())
    
    # Count lists and tables
    lists = len(soup.find_all(['ul', 'ol']))
    tables = len(soup.find_all('table'))
    
    # Check for short answer paragraphs (40-60 words)
    short_paragraphs = 0
    for p in paragraphs:
        word_count = len(p.get_text().split())
        if 40 <= word_count <= 60:
            short_paragraphs += 1
    
    # Calculate snippet score
    snippet_score = 0
    if first_para_words >= 40 and first_para_words <= 60:
        snippet_score += 30
    if lists > 0:
        snippet_score += 25
    if tables > 0:
        snippet_score += 20
    if short_paragraphs >= 3:
        snippet_score += 25
    
    return {
        'first_para_words': first_para_words,
        'lists': lists,
        'tables': tables,
        'short_paragraphs': short_paragraphs,
        'snippet_score': min(snippet_score, 100)
    }

def analyze_structure(soup):
    """Analyze content structure"""
    text = soup.get_text()
    
    # Check for TL;DR or Summary
    has_tldr = bool(re.search(r'(tl;?dr|summary|key takeaways)', text, re.IGNORECASE))
    
    # Check for Table of Contents
    has_toc = bool(soup.find(['div', 'nav'], class_=re.compile('toc|table-of-contents', re.I)))
    
    # Calculate average paragraph length
    paragraphs = soup.find_all('p')
    if paragraphs:
        total_words = sum(len(p.get_text().split()) for p in paragraphs)
        avg_para_length = total_words / len(paragraphs)
    else:
        avg_para_length = 0
    
    # Word count
    word_count = len(text.split())
    
    # Readability
    try:
        flesch_score = textstat.flesch_reading_ease(text)
    except:
        flesch_score = 0
    
    return {
        'has_tldr': has_tldr,
        'has_toc': has_toc,
        'avg_para_length': round(avg_para_length, 1),
        'word_count': word_count,
        'flesch_reading_ease': round(flesch_score, 1)
    }

def analyze_entities(soup):
    """Basic entity extraction"""
    text = soup.get_text()
    
    # Simple capitalized words as entities (basic NER)
    words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Count unique entities
    entities = list(set(words))
    entities_found = len(entities)
    
    return {
        'entities_found': entities_found,
        'entity_examples': entities[:10]
    }

def analyze_eeat(soup, url):
    """Analyze E-E-A-T signals"""
    # Check for author meta
    author_meta = soup.find('meta', attrs={'name': re.compile('author', re.I)})
    has_author_meta = bool(author_meta)
    
    # Check for publication date
    date_meta = soup.find('meta', attrs={'property': re.compile('published', re.I)})
    has_date = bool(date_meta)
    
    # Check for author bio
    has_author_bio = bool(soup.find(['div', 'section'], class_=re.compile('author|bio', re.I)))
    
    # Check for about and contact links
    links = soup.find_all('a', href=True)
    has_about_link = any('about' in link['href'].lower() for link in links)
    has_contact_link = any('contact' in link['href'].lower() for link in links)
    
    # Check for sources/references
    has_sources = bool(soup.find(['div', 'section'], class_=re.compile('reference|source|citation', re.I)))
    
    return {
        'has_author_meta': has_author_meta,
        'has_date': has_date,
        'has_author_bio': has_author_bio,
        'has_about_link': has_about_link,
        'has_contact_link': has_contact_link,
        'has_sources': has_sources
    }

def calculate_aeo_score(data):
    """Calculate overall AEO score"""
    score = 0
    
    # Schema (25 points)
    if data['schema']['faq_present']:
        score += 10
    if data['schema']['howto_present']:
        score += 10
    if data['schema']['article_present']:
        score += 5
    
    # Questions (20 points)
    if data['questions']['question_headings'] > 0:
        score += min(data['questions']['question_headings'] * 4, 20)
    
    # Snippet optimization (20 points)
    score += data['snippet']['snippet_score'] * 0.2
    
    # Structure (15 points)
    if data['structure']['has_tldr']:
        score += 5
    if data['structure']['has_toc']:
        score += 5
    if data['structure']['flesch_reading_ease'] >= 60:
        score += 5
    
    # E-E-A-T (10 points)
    eeat_score = sum([
        data['eeat']['has_author_meta'],
        data['eeat']['has_date'],
        data['eeat']['has_author_bio'],
        data['eeat']['has_sources']
    ]) * 2.5
    score += eeat_score
    
    # Entities (10 points)
    if data['entities']['entities_found'] > 10:
        score += 10
    elif data['entities']['entities_found'] > 5:
        score += 5
    
    return min(round(score), 100)

def generate_recommendations(data):
    """Generate actionable recommendations"""
    recommendations = []
    
    if not data['schema']['faq_present']:
        recommendations.append("Add FAQ schema markup to target 'People Also Ask' boxes")
    
    if not data['schema']['howto_present'] and 'how' in str(data['questions']).lower():
        recommendations.append("Add HowTo schema for step-by-step content")
    
    if data['questions']['question_headings'] < 3:
        recommendations.append("Add more question-based headings (What, Why, How)")
    
    if data['snippet']['first_para_words'] < 40 or data['snippet']['first_para_words'] > 60:
        recommendations.append("Optimize first paragraph to 40-60 words for featured snippets")
    
    if data['snippet']['lists'] == 0:
        recommendations.append("Add bulleted or numbered lists for better snippet visibility")
    
    if not data['structure']['has_tldr']:
        recommendations.append("Add a TL;DR or summary section at the beginning")
    
    if data['structure']['avg_para_length'] > 100:
        recommendations.append("Break down paragraphs into shorter chunks (2-3 sentences)")
    
    if not data['eeat']['has_author_meta']:
        recommendations.append("Add author information and credentials")
    
    if data['entities']['entities_found'] < 10:
        recommendations.append("Include more relevant entities and topics for semantic richness")
    
    return recommendations

@app.route('/api/aeo-analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Fetch page
        html = fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Run all analyses
        schema_data = analyze_schema(soup)
        question_data = analyze_questions(soup)
        snippet_data = analyze_snippet_optimization(soup)
        structure_data = analyze_structure(soup)
        entity_data = analyze_entities(soup)
        eeat_data = analyze_eeat(soup, url)
        
        # Combine results
        result = {
            'url': url,
            'schema': schema_data,
            'questions': question_data,
            'snippet': snippet_data,
            'structure': structure_data,
            'entities': entity_data,
            'eeat': eeat_data
        }
        
        # Calculate score
        aeo_score = calculate_aeo_score(result)
        recommendations = generate_recommendations(result)
        
        result['aeo_score'] = aeo_score
        result['recommendations'] = recommendations
        result['tool_name'] = 'AEO On-Page Auditor'
        result['version'] = '1.0.0'
        
        # Flatten for frontend compatibility
        flattened = {
            'url': url,
            'aeo_score': aeo_score,
            'faq_schema_present': schema_data['faq_present'],
            'faq_count': schema_data['faq_count'],
            'howto_schema_present': schema_data['howto_present'],
            'howto_count': schema_data['howto_count'],
            'article_schema_present': schema_data['article_present'],
            'total_headings': question_data['total_headings'],
            'question_headings': question_data['question_headings'],
            'question_heading_examples': question_data['question_heading_examples'],
            'first_para_words': snippet_data['first_para_words'],
            'lists': snippet_data['lists'],
            'tables': snippet_data['tables'],
            'short_paragraphs': snippet_data['short_paragraphs'],
            'snippet_score': snippet_data['snippet_score'],
            'has_tldr': structure_data['has_tldr'],
            'has_toc': structure_data['has_toc'],
            'word_count': structure_data['word_count'],
            'flesch_reading_ease': structure_data['flesch_reading_ease'],
            'entities_found': entity_data['entities_found'],
            'entity_examples': entity_data['entity_examples'],
            'has_author_meta': eeat_data['has_author_meta'],
            'has_date': eeat_data['has_date'],
            'has_author_bio': eeat_data['has_author_bio'],
            'has_about_link': eeat_data['has_about_link'],
            'has_contact_link': eeat_data['has_contact_link'],
            'has_sources': eeat_data['has_sources'],
            'recommendations': recommendations,
            'aeo_checks': {
                'FAQ Schema': schema_data['faq_present'],
                'HowTo Schema': schema_data['howto_present'],
                'Question Headings': question_data['question_headings'] >= 3,
                'Snippet Ready': snippet_data['snippet_score'] >= 50,
                'Has TL;DR': structure_data['has_tldr'],
                'Good Readability': structure_data['flesch_reading_ease'] >= 60,
                'Author Info': eeat_data['has_author_meta']
            }
        }
        
        return jsonify(flattened)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'tool': 'AEO On-Page Auditor'})


if __name__ == '__main__':
   # Railway provides PORT - MUST use it
    port = int(os.environ.get('PORT', 8080))
    print(f"=== Starting Flask on port {port} ===")
    app.run(host='0.0.0.0', port=port, debug=False)