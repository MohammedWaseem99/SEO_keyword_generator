import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
from rake_nltk import Rake
from textblob import TextBlob
from collections import Counter
import nltk
from nltk.corpus import stopwords
from urllib.parse import urlparse
import re
import math
import webbrowser
from PIL import Image, ImageTk
import io

# Initialize NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

class SEOAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional SEO Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f2f5')
        self.style.configure('TLabel', background='#f0f2f5', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
        self.style.configure('Score.TLabel', font=('Segoe UI', 24, 'bold'))
        self.style.configure('Good.TLabel', foreground='#2ecc71')
        self.style.configure('Warning.TLabel', foreground='#f39c12')
        self.style.configure('Error.TLabel', foreground='#e74c3c')
        self.style.configure('TNotebook', background='#f0f2f5')
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'))
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.logo_image = self.create_logo()
        self.logo_label = ttk.Label(self.header_frame, image=self.logo_image)
        self.logo_label.pack(side=tk.LEFT)
        
        self.title_label = ttk.Label(self.header_frame, text="Professional SEO Analyzer", 
                                   style='Header.TLabel')
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # URL Input
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.url_label = ttk.Label(self.input_frame, text="Website URL:")
        self.url_label.pack(side=tk.LEFT)
        
        self.url_entry = ttk.Entry(self.input_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        self.analyze_button = ttk.Button(self.input_frame, text="Analyze", 
                                       command=self.analyze_website)
        self.analyze_button.pack(side=tk.LEFT)
        
        # Results Notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview Tab
        self.overview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_tab, text="Overview")
        
        # Scores Frame
        self.scores_frame = ttk.Frame(self.overview_tab)
        self.scores_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.seo_score_frame = ttk.Frame(self.scores_frame)
        self.seo_score_frame.pack(side=tk.LEFT, expand=True)
        
        self.seo_score_label = ttk.Label(self.seo_score_frame, text="SEO Score", 
                                       style='Header.TLabel')
        self.seo_score_label.pack()
        
        self.seo_score_value = ttk.Label(self.seo_score_frame, text="--", 
                                       style='Score.TLabel')
        self.seo_score_value.pack()
        
        self.seo_score_status = ttk.Label(self.seo_score_frame, text="Not analyzed yet")
        self.seo_score_status.pack()
        
        self.performance_score_frame = ttk.Frame(self.scores_frame)
        self.performance_score_frame.pack(side=tk.LEFT, expand=True)
        
        self.performance_score_label = ttk.Label(self.performance_score_frame, 
                                              text="Performance Score", 
                                              style='Header.TLabel')
        self.performance_score_label.pack()
        
        self.performance_score_value = ttk.Label(self.performance_score_frame, 
                                              text="--", 
                                              style='Score.TLabel')
        self.performance_score_value.pack()
        
        self.performance_score_status = ttk.Label(self.performance_score_frame, 
                                                text="Not analyzed yet")
        self.performance_score_status.pack()
        
        self.mobile_score_frame = ttk.Frame(self.scores_frame)
        self.mobile_score_frame.pack(side=tk.LEFT, expand=True)
        
        self.mobile_score_label = ttk.Label(self.mobile_score_frame, 
                                          text="Mobile Score", 
                                          style='Header.TLabel')
        self.mobile_score_label.pack()
        
        self.mobile_score_value = ttk.Label(self.mobile_score_frame, 
                                          text="--", 
                                          style='Score.TLabel')
        self.mobile_score_value.pack()
        
        self.mobile_score_status = ttk.Label(self.mobile_score_frame, 
                                           text="Not analyzed yet")
        self.mobile_score_status.pack()
        
        # Keywords Frame
        self.keywords_frame = ttk.LabelFrame(self.overview_tab, text="Top Keywords")
        self.keywords_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.keywords_text = scrolledtext.ScrolledText(self.keywords_frame, 
                                                     height=8, 
                                                     wrap=tk.WORD)
        self.keywords_text.pack(fill=tk.BOTH, expand=True)
        
        # Suggestions Frame
        self.suggestions_frame = ttk.LabelFrame(self.overview_tab, 
                                              text="SEO Suggestions")
        self.suggestions_frame.pack(fill=tk.BOTH, expand=True)
        
        self.suggestions_text = scrolledtext.ScrolledText(self.suggestions_frame, 
                                                        height=8, 
                                                        wrap=tk.WORD)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
        
        # Details Tab
        self.details_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.details_tab, text="Details")
        
        # Meta Tags Frame
        self.meta_frame = ttk.LabelFrame(self.details_tab, text="Meta Tags")
        self.meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(self.meta_frame, text="Title:")
        self.title_label.pack(anchor=tk.W)
        
        self.title_value = ttk.Label(self.meta_frame, text="", wraplength=800)
        self.title_value.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        self.desc_label = ttk.Label(self.meta_frame, text="Description:")
        self.desc_label.pack(anchor=tk.W)
        
        self.desc_value = ttk.Label(self.meta_frame, text="", wraplength=800)
        self.desc_value.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # Content Frame
        self.content_frame = ttk.LabelFrame(self.details_tab, text="Content Analysis")
        self.content_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.headings_label = ttk.Label(self.content_frame, text="Headings Structure:")
        self.headings_label.pack(anchor=tk.W)
        
        self.headings_value = scrolledtext.ScrolledText(self.content_frame, 
                                                      height=6, 
                                                      wrap=tk.WORD)
        self.headings_value.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # Technical Tab
        self.technical_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.technical_tab, text="Technical")
        
        # Technical Data Frame
        self.tech_data_frame = ttk.LabelFrame(self.technical_tab, 
                                            text="Technical Data")
        self.tech_data_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tech_data_text = scrolledtext.ScrolledText(self.tech_data_frame, 
                                                      height=15, 
                                                      wrap=tk.WORD)
        self.tech_data_text.pack(fill=tk.BOTH, expand=True)
        
        # Developer Tab
        self.developer_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.developer_tab, text="Developer")
        
        # Developer Recommendations Frame
        self.dev_frame = ttk.LabelFrame(self.developer_tab, 
                                      text="Developer Recommendations")
        self.dev_frame.pack(fill=tk.BOTH, expand=True)
        
        self.dev_text = scrolledtext.ScrolledText(self.dev_frame, 
                                                height=15, 
                                                wrap=tk.WORD)
        self.dev_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Bind Enter key to analyze button
        self.root.bind('<Return>', lambda event: self.analyze_website())
        
    def create_logo(self):
        # Create a simple logo image
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (40, 40), color='#3498db')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "SEO", fill='white')
        return ImageTk.PhotoImage(img)
    
    def analyze_website(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a website URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.status_bar.config(text=f"Analyzing {url}...")
        self.root.update_idletasks()
        
        try:
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_page(url)
            self.display_results(results)
            self.status_bar.config(text=f"Analysis complete for {url}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze website: {str(e)}")
            self.status_bar.config(text="Ready")
    
    def display_results(self, data):
        if "error" in data:
            messagebox.showerror("Error", data['error'])
            return
        
        # Update scores
        self.update_score_display(self.seo_score_value, self.seo_score_status, 
                                data['seo_score'], "SEO")
        self.update_score_display(self.performance_score_value, 
                                self.performance_score_status, 
                                data['performance_score'], "Performance")
        self.update_score_display(self.mobile_score_value, self.mobile_score_status, 
                                data['mobile_score'], "Mobile")
        
        # Update keywords
        self.keywords_text.config(state=tk.NORMAL)
        self.keywords_text.delete(1.0, tk.END)
        for i, kw in enumerate(data['keywords'], 1):
            self.keywords_text.insert(tk.END, f"{i}. {kw}\n")
        self.keywords_text.config(state=tk.DISABLED)
        
        # Update suggestions
        self.suggestions_text.config(state=tk.NORMAL)
        self.suggestions_text.delete(1.0, tk.END)
        for i, suggestion in enumerate(data['suggestions'], 1):
            self.suggestions_text.insert(tk.END, f"{i}. {suggestion}\n")
        self.suggestions_text.config(state=tk.DISABLED)
        
        # Update meta tags
        self.title_value.config(text=data['meta']['title'])
        self.desc_value.config(text=data['meta']['description'])
        
        # Update headings
        self.headings_value.config(state=tk.NORMAL)
        self.headings_value.delete(1.0, tk.END)
        for i in range(1, 7):
            if data['headings'][f'h{i}']:
                self.headings_value.insert(tk.END, f"H{i}:\n")
                for heading in data['headings'][f'h{i}']:
                    self.headings_value.insert(tk.END, f"- {heading}\n")
                self.headings_value.insert(tk.END, "\n")
        self.headings_value.config(state=tk.DISABLED)
        
        # Update technical data
        self.tech_data_text.config(state=tk.NORMAL)
        self.tech_data_text.delete(1.0, tk.END)
        self.tech_data_text.insert(tk.END, f"Page Load Time: {data['load_time']:.2f} seconds\n\n")
        self.tech_data_text.insert(tk.END, f"Images: {data['images']['count']} total\n")
        self.tech_data_text.insert(tk.END, f" - With alt text: {data['images']['with_alt']}\n")
        self.tech_data_text.insert(tk.END, f" - Without alt text: {data['images']['without_alt']}\n\n")
        self.tech_data_text.insert(tk.END, f"Links: {data['links']['internal']} internal, {data['links']['external']} external\n\n")
        self.tech_data_text.insert(tk.END, f"Viewport: {'Present' if data['meta']['viewport'] else 'Missing'}\n")
        self.tech_data_text.config(state=tk.DISABLED)
        
        # Update developer recommendations
        self.dev_text.config(state=tk.NORMAL)
        self.dev_text.delete(1.0, tk.END)
        for i, rec in enumerate(data['developer_recommendations'], 1):
            self.dev_text.insert(tk.END, f"{i}. {rec}\n")
        self.dev_text.config(state=tk.DISABLED)
    
    def update_score_display(self, value_label, status_label, score, score_type):
        value_label.config(text=f"{score}/100")
        
        if score >= 80:
            value_label.config(style='Good.TLabel')
            status_label.config(text="Excellent", style='Good.TLabel')
        elif score >= 60:
            value_label.config(style='Warning.TLabel')
            status_label.config(text="Good", style='Warning.TLabel')
        else:
            value_label.config(style='Error.TLabel')
            status_label.config(text="Needs Improvement", style='Error.TLabel')

class SEOAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.stop_words = set(stopwords.words('english'))
    
    def fetch_website_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Check for mobile responsiveness
            mobile_friendly = self.check_mobile_responsiveness(response.text)
            
            return {
                'html': response.text,
                'load_time': response.elapsed.total_seconds(),
                'status': response.status_code,
                'mobile_friendly': mobile_friendly
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None
    
    def check_mobile_responsiveness(self, html):
        """Simple check for mobile responsiveness"""
        soup = BeautifulSoup(html, 'html.parser')
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            return False
        
        # Check for responsive design indicators
        responsive_indicators = [
            'width=device-width',
            'initial-scale=1',
            'maximum-scale=1',
            'user-scalable=no'
        ]
        
        content = viewport.get('content', '').lower()
        return any(indicator in content for indicator in responsive_indicators)
    
    def analyze_page(self, url):
        print(f"\n🔍 Analyzing: {url}")
        
        # Fetch website data
        website_data = self.fetch_website_content(url)
        if not website_data:
            return {"error": "Could not fetch website content"}
        
        html = website_data['html']
        load_time = website_data['load_time']
        mobile_friendly = website_data['mobile_friendly']
        
        # Extract SEO elements
        seo_data = {
            'meta': self.extract_meta_data(html),
            'headings': self.extract_headings(html),
            'keywords': self.extract_keywords(html),
            'links': self.extract_links(html),
            'images': self.extract_images(html),
            'load_time': load_time,
            'mobile_friendly': mobile_friendly
        }
        
        # Calculate scores
        seo_data['seo_score'] = self.calculate_seo_score(seo_data)
        seo_data['performance_score'] = self.calculate_performance_score(seo_data)
        seo_data['mobile_score'] = self.calculate_mobile_score(seo_data)
        
        # Generate suggestions
        seo_data['suggestions'] = self.generate_suggestions(seo_data)
        seo_data['developer_recommendations'] = self.generate_dev_recommendations(seo_data)
        
        return seo_data
    
    def extract_meta_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return {
            'title': soup.find('title').text if soup.find('title') else "",
            'description': soup.find('meta', attrs={'name': 'description'}).get('content', '') if soup.find('meta', attrs={'name': 'description'}) else "",
            'keywords': soup.find('meta', attrs={'name': 'keywords'}).get('content', '').split(',') if soup.find('meta', attrs={'name': 'keywords'}) else [],
            'viewport': bool(soup.find('meta', attrs={'name': 'viewport'}))
        }
    
    def extract_headings(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        headings = {f'h{i}': [] for i in range(1, 7)}
        for i in range(1, 7):
            headings[f'h{i}'] = [h.text.strip() for h in soup.find_all(f'h{i}')]
        return headings
    
    def extract_keywords(self, html):
        text = self.extract_text_from_html(html)
        
        # RAKE keywords
        r = Rake(stopwords=self.stop_words)
        r.extract_keywords_from_text(text)
        rake_keywords = r.get_ranked_phrases()[:20]
        
        # TextBlob keywords
        blob = TextBlob(text)
        tb_keywords = [np for np in blob.noun_phrases if len(np.split()) < 4]
        
        # Combine and rank
        all_keywords = rake_keywords + tb_keywords
        return [kw for kw, _ in Counter(all_keywords).most_common(15)]
    
    def extract_text_from_html(self, html):
        if not html:
            return ""
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return ""
    
    def extract_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        return {
            'count': len(links),
            'internal': sum(1 for link in links if not link['href'].startswith('http')),
            'external': sum(1 for link in links if link['href'].startswith('http'))
        }
    
    def extract_images(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        images = soup.find_all('img')
        return {
            'count': len(images),
            'with_alt': sum(1 for img in images if img.get('alt', '').strip()),
            'without_alt': sum(1 for img in images if not img.get('alt', '').strip())
        }
    
    def calculate_seo_score(self, data):
        score = 0
        
        # Title (10 points)
        title = data['meta']['title']
        if title:
            score += 5
            if 50 <= len(title) <= 60:
                score += 5
        
        # Description (10 points)
        description = data['meta']['description']
        if description:
            score += 5
            if 120 <= len(description) <= 160:
                score += 5
        
        # Keywords (5 points)
        if data['meta']['keywords']:
            score += 5
        
        # Headings (15 points)
        if data['headings']['h1']:
            score += 5
            if len(data['headings']['h1']) == 1:
                score += 5
        if any(data['headings'][f'h{i}'] for i in range(2, 7)):
            score += 5
        
        # Images (10 points)
        if data['images']['count'] > 0:
            score += 5
            if data['images']['with_alt'] / data['images']['count'] > 0.8:
                score += 5
        
        # Links (10 points)
        if data['links']['internal'] > 5:
            score += 5
        if data['links']['external'] > 2:
            score += 5
        
        # Viewport (5 points)
        if data['meta']['viewport']:
            score += 5
        
        # Content (15 points)
        if len(data['keywords']) >= 5:
            score += 15
        
        # Load time (15 points)
        if data['load_time'] < 2:
            score += 15
        elif data['load_time'] < 4:
            score += 10
        
        return min(100, math.ceil(score))
    
    def calculate_performance_score(self, data):
        # Simplified performance score based on load time
        if data['load_time'] < 1:
            return 95
        elif data['load_time'] < 2:
            return 85
        elif data['load_time'] < 3:
            return 70
        elif data['load_time'] < 4:
            return 50
        else:
            return 30
    
    def calculate_mobile_score(self, data):
        # Score based on mobile responsiveness
        score = 0
        
        # Viewport (30 points)
        if data['meta']['viewport']:
            score += 30
        
        # Mobile friendly (70 points)
        if data['mobile_friendly']:
            score += 70
        
        return score
    
    def generate_suggestions(self, data):
        suggestions = []
        
        # Title suggestions
        if not data['meta']['title']:
            suggestions.append("Add a title tag with primary keywords (50-60 characters)")
        elif len(data['meta']['title']) > 60:
            suggestions.append("Shorten your title tag (currently too long)")
        
        # Description suggestions
        if not data['meta']['description']:
            suggestions.append("Add a meta description (120-160 characters)")
        elif len(data['meta']['description']) > 160:
            suggestions.append("Shorten your meta description (currently too long)")
        
        # Heading suggestions
        if not data['headings']['h1']:
            suggestions.append("Add exactly one H1 heading with your main keyword")
        elif len(data['headings']['h1']) > 1:
            suggestions.append("Reduce to one H1 heading per page")
        
        # Image suggestions
        if data['images']['without_alt'] > 0:
            suggestions.append(f"Add alt text to {data['images']['without_alt']} images")
        
        # Keyword suggestions
        if len(data['keywords']) < 5:
            suggestions.append("Add more content with relevant keywords")
        
        # Performance suggestions
        if data['load_time'] > 2:
            suggestions.append("Optimize page speed by compressing images and minimizing resources")
        
        # Mobile suggestions
        if not data['mobile_friendly']:
            suggestions.append("Improve mobile responsiveness with proper viewport settings")
        
        return suggestions
    
    def generate_dev_recommendations(self, data):
        recs = []
        
        # Technical SEO
        recs.append("Ensure proper use of semantic HTML5 elements")
        
        # Performance
        if data['load_time'] > 2:
            recs.append("Implement lazy loading for images")
            recs.append("Minify CSS and JavaScript files")
            recs.append("Enable browser caching")
            recs.append("Consider using a CDN for static assets")
        
        # Mobile
        if not data['meta']['viewport']:
            recs.append("Add responsive viewport meta tag: <meta name='viewport' content='width=device-width, initial-scale=1'>")
        
        if not data['mobile_friendly']:
            recs.append("Test mobile responsiveness using Google's Mobile-Friendly Test")
        
        # Accessibility
        if data['images']['without_alt'] > 0:
            recs.append("Add alt attributes to all images for accessibility")
        
        # Security
        recs.append("Ensure site uses HTTPS for all pages")
        recs.append("Implement security headers (CSP, X-Frame-Options, etc.)")
        
        return recs

if __name__ == "__main__":
    root = tk.Tk()
    app = SEOAnalyzerApp(root)
    root.mainloop()