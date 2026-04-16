import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebScanner:
    def __init__(self, target_url):
        # Ensure URL has scheme
        if not target_url.startswith('http://') and not target_url.startswith('https://'):
            target_url = 'http://' + target_url
        self.target_url = target_url
        self.session = requests.Session()
        
    def run_full_scan(self):
        print(f"Starting scan for {self.target_url}")
        results = {
            "target": self.target_url,
            "security_headers": self.check_security_headers(),
            "xss_vulnerabilities": self.check_xss(),
            "sqli_vulnerabilities": self.check_sqli(),
            "directory_exposure": self.check_directory_exposure()
        }
        return results
        
    def check_security_headers(self):
        issues = []
        try:
            response = self.session.get(self.target_url, timeout=5)
            headers = response.headers
            
            security_headers = [
                'Strict-Transport-Security',
                'X-Frame-Options',
                'X-Content-Type-Options',
                'Content-Security-Policy'
            ]
            
            for header in security_headers:
                if header not in headers:
                    issues.append(f"Missing {header}")
                    
        except requests.exceptions.RequestException as e:
            issues.append(f"Error connecting: {str(e)}")
            
        return {"status": "Complete", "issues_found": issues}
        
    def extract_forms(self):
        try:
            response = self.session.get(self.target_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.find_all("form")
        except:
            return []

    def check_xss(self):
        xss_payload = "<script>alert('XSS')</script>"
        vulnerable_forms = []
        forms = self.extract_forms()
        
        for form in forms:
            action = form.attrs.get("action", self.target_url)
            method = form.attrs.get("method", "get").lower()
            target = urljoin(self.target_url, action)
            
            # Simple check for demo purposes
            if method == "get":
                vulnerable_forms.append(f"Potential Reflected XSS at {target} (Method: GET)")
                
        return {"status": "Complete", "issues": vulnerable_forms}
        
    def check_sqli(self):
        sqli_payloads = ["'", "\"", " OR 1=1 --", "' OR '1'='1"]
        vulnerable_urls = []
        
        # Test basic URL-based SQLi if there are parameters in URL (for demo purposes)
        parsed = urlparse(self.target_url)
        if parsed.query:
            for payload in sqli_payloads:
                test_url = f"{self.target_url}{payload}"
                try:
                    res = self.session.get(test_url, timeout=5)
                    # Check for generic SQL error messages
                    if "syntax error" in res.text.lower() or "mysql" in res.text.lower():
                        vulnerable_urls.append(f"Potential SQL Injection on URL parameter with payload {payload}")
                        break
                except:
                    pass
                    
        return {"status": "Complete", "issues": vulnerable_urls}
        
    def check_directory_exposure(self):
        common_dirs = ['/admin', '/.env', '/.git', '/robots.txt']
        exposed = []
        
        for d in common_dirs:
            test_url = urljoin(self.target_url, d)
            try:
                res = self.session.get(test_url, timeout=3)
                if res.status_code == 200 and "404" not in res.text:
                    if d == '/robots.txt' and "User-agent" in res.text:
                        exposed.append(f"Exposed directory/file found: {test_url}")
                    elif d != '/robots.txt':
                        exposed.append(f"Exposed directory/file found: {test_url}")
            except:
                pass
                
        return {"status": "Complete", "issues": exposed}

# For local testing
if __name__ == "__main__":
    scanner = WebScanner("http://example.com")
    print(scanner.run_full_scan())
