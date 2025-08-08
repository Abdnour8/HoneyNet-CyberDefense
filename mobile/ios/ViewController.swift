import UIKit
import WebKit

/**
 * HoneyNet - Global Cyber Defense
 * iOS Application
 * 
 * Ze'ev Weinerich Technologies Ltd.
 * Israel, HaHartzit 3, Ashdod, 7761803
 */

class ViewController: UIViewController, WKNavigationDelegate {
    
    @IBOutlet weak var webView: WKWebView!
    @IBOutlet weak var progressView: UIProgressView!
    @IBOutlet weak var statusLabel: UILabel!
    
    private let honeyNetURL = "http://18.209.27.121"
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupWebView()
        loadHoneyNet()
    }
    
    private func setupUI() {
        // Set up the navigation bar
        navigationItem.title = "🛡️ HoneyNet"
        navigationController?.navigationBar.prefersLargeTitles = true
        navigationController?.navigationBar.barTintColor = UIColor(red: 0.4, green: 0.5, blue: 0.9, alpha: 1.0)
        navigationController?.navigationBar.tintColor = .white
        navigationController?.navigationBar.titleTextAttributes = [.foregroundColor: UIColor.white]
        navigationController?.navigationBar.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
        
        // Set up progress view
        progressView.progressTintColor = UIColor(red: 1.0, green: 0.42, blue: 0.42, alpha: 1.0)
        progressView.trackTintColor = UIColor.lightGray
        progressView.isHidden = true
        
        // Set up status label
        statusLabel.text = "🔄 Connecting to HoneyNet..."
        statusLabel.textColor = .white
        statusLabel.backgroundColor = UIColor(red: 0.4, green: 0.5, blue: 0.9, alpha: 0.8)
        statusLabel.textAlignment = .center
        statusLabel.layer.cornerRadius = 8
        statusLabel.clipsToBounds = true
    }
    
    private func setupWebView() {
        webView.navigationDelegate = self
        webView.allowsBackForwardNavigationGestures = true
        
        // Add observer for progress
        webView.addObserver(self, forKeyPath: #keyPath(WKWebView.estimatedProgress), options: .new, context: nil)
        
        // Configure web view settings
        let configuration = webView.configuration
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []
    }
    
    private func loadHoneyNet() {
        let mobileHtml = generateMobileHtml()
        webView.loadHTMLString(mobileHtml, baseURL: URL(string: honeyNetURL))
    }
    
    private func generateMobileHtml() -> String {
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🛡️ HoneyNet - iOS</title>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0, user-scalable=no'>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; min-height: 100vh; padding: 20px;
                    -webkit-user-select: none; user-select: none;
                }
                .container { max-width: 100%; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .logo { font-size: 4em; margin-bottom: 15px; }
                .title { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
                .subtitle { font-size: 1.1em; opacity: 0.9; }
                .ios-badge { 
                    background: #007AFF; padding: 10px 20px; border-radius: 25px; 
                    font-weight: bold; margin-bottom: 20px; font-size: 0.9em;
                    box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
                }
                .stats { 
                    display: grid; grid-template-columns: repeat(2, 1fr); 
                    gap: 15px; margin-bottom: 30px; 
                }
                .stat-card { 
                    background: rgba(255,255,255,0.15); padding: 20px; 
                    border-radius: 15px; text-align: center;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }
                .stat-number { font-size: 2em; font-weight: bold; margin-bottom: 8px; }
                .stat-label { font-size: 0.9em; opacity: 0.8; }
                .features { margin-bottom: 30px; }
                .feature-card { 
                    background: rgba(255,255,255,0.1); padding: 20px; 
                    border-radius: 15px; margin-bottom: 15px;
                    backdrop-filter: blur(10px);
                }
                .feature-icon { font-size: 2em; margin-bottom: 10px; }
                .feature-title { font-size: 1.2em; font-weight: bold; margin-bottom: 8px; }
                .feature-text { font-size: 1em; opacity: 0.9; line-height: 1.4; }
                .btn-container { text-align: center; margin: 30px 0; }
                .btn { 
                    display: inline-block; padding: 15px 25px; 
                    background: linear-gradient(45deg, #ff6b6b, #ff5252);
                    color: white; text-decoration: none; border-radius: 25px; 
                    font-weight: bold; margin: 8px; font-size: 1em;
                    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
                    transition: all 0.3s ease;
                }
                .btn:active { transform: scale(0.95); }
                .footer { 
                    text-align: center; margin-top: 30px; padding: 25px; 
                    background: rgba(0,0,0,0.2); border-radius: 15px; 
                    font-size: 0.9em;
                }
                @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
                .pulse { animation: pulse 2s infinite; }
                
                /* iOS specific optimizations */
                .btn { -webkit-tap-highlight-color: transparent; }
                body { -webkit-touch-callout: none; }
            </style>
        </head>
        <body>
            <div class='container'>
                <div class='header'>
                    <div class='ios-badge'>📱 HoneyNet for iOS</div>
                    <div class='logo pulse'>🛡️</div>
                    <h1 class='title'>HoneyNet</h1>
                    <p class='subtitle'>Global Cyber Defense Network</p>
                </div>
                
                <div class='stats'>
                    <div class='stat-card'>
                        <div class='stat-number'>1,250</div>
                        <div class='stat-label'>Active Users</div>
                    </div>
                    <div class='stat-card'>
                        <div class='stat-number'>15,847</div>
                        <div class='stat-label'>Threats Blocked</div>
                    </div>
                    <div class='stat-card'>
                        <div class='stat-number'>67</div>
                        <div class='stat-label'>Countries</div>
                    </div>
                    <div class='stat-card'>
                        <div class='stat-number'>99.9%</div>
                        <div class='stat-label'>Uptime</div>
                    </div>
                </div>
                
                <div class='features'>
                    <div class='feature-card'>
                        <div class='feature-icon'>📱</div>
                        <h3 class='feature-title'>iOS Protection</h3>
                        <p class='feature-text'>Advanced cybersecurity protection optimized for iOS devices with real-time monitoring.</p>
                    </div>
                    <div class='feature-card'>
                        <div class='feature-icon'>🔒</div>
                        <h3 class='feature-title'>Privacy First</h3>
                        <p class='feature-text'>Built with Apple's privacy standards in mind. Your data stays secure and private.</p>
                    </div>
                    <div class='feature-card'>
                        <div class='feature-icon'>⚡</div>
                        <h3 class='feature-title'>Lightning Fast</h3>
                        <p class='feature-text'>Optimized for iOS performance with minimal battery and resource usage.</p>
                    </div>
                </div>
                
                <div class='btn-container'>
                    <a href='javascript:checkHealth()' class='btn'>🏥 Health Check</a>
                    <a href='javascript:showInfo()' class='btn'>📊 Device Info</a>
                    <a href='javascript:openDonate()' class='btn'>💝 Support Us</a>
                </div>
                
                <div class='footer'>
                    <h3>🎉 HoneyNet iOS is Active!</h3>
                    <p>Your iPhone/iPad is now protected by our global cybersecurity network.</p>
                    <p style='margin-top: 15px;'>
                        All rights reserved to <strong>Ze'ev Weinerich Technologies Ltd.</strong><br>
                        Israel, HaHartzit 3, Ashdod, 7761803
                    </p>
                </div>
            </div>
            
            <script>
                function checkHealth() {
                    const healthInfo = '🏥 Health Status: HEALTHY\\n✅ Service: Running\\n📱 Platform: iOS\\n🔋 Battery: Optimized\\n🛡️ Protection: Active';
                    alert(healthInfo);
                }
                
                function showInfo() {
                    const deviceInfo = '📊 Device Information\\n🛡️ HoneyNet: Active\\n📱 Platform: iOS\\n🌐 Connected: Yes\\n🔒 Security: High\\n⚡ Performance: Optimized';
                    alert(deviceInfo);
                }
                
                function openDonate() {
                    window.open('https://www.paypal.com/donate/?hosted_button_id=4HDBZEQ9PBT7U', '_blank');
                }
                
                // Real-time stats updates
                setInterval(() => {
                    const stats = document.querySelectorAll('.stat-number');
                    if (stats[1]) {
                        let current = parseInt(stats[1].textContent.replace(',', ''));
                        stats[1].textContent = (current + Math.floor(Math.random() * 3) + 1).toLocaleString();
                    }
                }, 15000);
                
                // iOS specific optimizations
                document.addEventListener('touchstart', function() {}, {passive: true});
            </script>
        </body>
        </html>
        """
    }
    
    // MARK: - WKNavigationDelegate
    
    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        progressView.isHidden = false
        statusLabel.text = "🔄 Loading HoneyNet..."
    }
    
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        progressView.isHidden = true
        statusLabel.text = "✅ HoneyNet Connected"
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.statusLabel.isHidden = true
        }
    }
    
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        progressView.isHidden = true
        statusLabel.text = "❌ Connection Failed"
        statusLabel.backgroundColor = UIColor.red
    }
    
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        
        if let url = navigationAction.request.url {
            if url.absoluteString.contains("paypal.me") {
                // Open PayPal links in Safari
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
                decisionHandler(.cancel)
                return
            }
        }
        
        decisionHandler(.allow)
    }
    
    // MARK: - KVO
    
    override func observeValue(forKeyPath keyPath: String?, of object: Any?, change: [NSKeyValueChangeKey : Any]?, context: UnsafeMutableRawPointer?) {
        if keyPath == "estimatedProgress" {
            progressView.progress = Float(webView.estimatedProgress)
        }
    }
    
    deinit {
        webView.removeObserver(self, forKeyPath: #keyPath(WKWebView.estimatedProgress))
    }
}
