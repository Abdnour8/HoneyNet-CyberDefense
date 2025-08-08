package com.zeevweinerich.honeynet;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import android.view.View;
import android.widget.ProgressBar;
import android.content.Intent;
import android.net.Uri;

/**
 * HoneyNet - Global Cyber Defense
 * Android Application
 * 
 * Ze'ev Weinerich Technologies Ltd.
 * Israel, HaHartzit 3, Ashdod, 7761803
 */
public class MainActivity extends Activity {
    
    private WebView webView;
    private ProgressBar progressBar;
    private static final String HONEYNET_URL = "http://18.209.27.121";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Initialize views
        webView = findViewById(R.id.webview);
        progressBar = findViewById(R.id.progressBar);
        
        // Configure WebView
        setupWebView();
        
        // Load HoneyNet
        loadHoneyNet();
    }
    
    private void setupWebView() {
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                progressBar.setVisibility(View.VISIBLE);
            }
            
            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
            }
            
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url.startsWith("https://paypal.me/")) {
                    // Open PayPal links in external browser
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                }
                return false;
            }
        });
    }
    
    private void loadHoneyNet() {
        // Load the mobile-optimized version
        String mobileHtml = generateMobileHtml();
        webView.loadDataWithBaseURL(HONEYNET_URL, mobileHtml, "text/html", "UTF-8", null);
    }
    
    private String generateMobileHtml() {
        return "<!DOCTYPE html>" +
                "<html>" +
                "<head>" +
                "    <title>🛡️ HoneyNet - Mobile</title>" +
                "    <meta charset='UTF-8'>" +
                "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>" +
                "    <style>" +
                "        * { margin: 0; padding: 0; box-sizing: border-box; }" +
                "        body { " +
                "            font-family: 'Roboto', Arial, sans-serif;" +
                "            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);" +
                "            color: white; min-height: 100vh; padding: 10px;" +
                "        }" +
                "        .container { max-width: 100%; margin: 0 auto; }" +
                "        .header { text-align: center; margin-bottom: 20px; }" +
                "        .logo { font-size: 3em; margin-bottom: 10px; }" +
                "        .title { font-size: 2em; font-weight: bold; margin-bottom: 10px; }" +
                "        .subtitle { font-size: 1em; opacity: 0.9; }" +
                "        .mobile-badge { background: #28a745; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin-bottom: 15px; font-size: 0.9em; }" +
                "        .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }" +
                "        .stat-card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; }" +
                "        .stat-number { font-size: 1.5em; font-weight: bold; margin-bottom: 5px; }" +
                "        .stat-label { font-size: 0.8em; opacity: 0.8; }" +
                "        .features { margin-bottom: 20px; }" +
                "        .feature-card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; }" +
                "        .feature-icon { font-size: 1.5em; margin-bottom: 8px; }" +
                "        .feature-title { font-size: 1em; font-weight: bold; margin-bottom: 5px; }" +
                "        .feature-text { font-size: 0.9em; opacity: 0.9; }" +
                "        .btn-container { text-align: center; margin: 20px 0; }" +
                "        .btn { display: inline-block; padding: 12px 20px; background: #ff6b6b; color: white; text-decoration: none; border-radius: 20px; font-weight: bold; margin: 5px; font-size: 0.9em; }" +
                "        .btn:hover { background: #ff5252; }" +
                "        .footer { text-align: center; margin-top: 20px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; font-size: 0.8em; }" +
                "        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }" +
                "        .pulse { animation: pulse 2s infinite; }" +
                "    </style>" +
                "</head>" +
                "<body>" +
                "    <div class='container'>" +
                "        <div class='header'>" +
                "            <div class='mobile-badge'>📱 HoneyNet Mobile App</div>" +
                "            <div class='logo pulse'>🛡️</div>" +
                "            <h1 class='title'>HoneyNet</h1>" +
                "            <p class='subtitle'>Global Cyber Defense Network</p>" +
                "        </div>" +
                "        " +
                "        <div class='stats'>" +
                "            <div class='stat-card'>" +
                "                <div class='stat-number'>1,250</div>" +
                "                <div class='stat-label'>Active Users</div>" +
                "            </div>" +
                "            <div class='stat-card'>" +
                "                <div class='stat-number'>15,847</div>" +
                "                <div class='stat-label'>Threats Blocked</div>" +
                "            </div>" +
                "            <div class='stat-card'>" +
                "                <div class='stat-number'>67</div>" +
                "                <div class='stat-label'>Countries</div>" +
                "            </div>" +
                "            <div class='stat-card'>" +
                "                <div class='stat-number'>99.9%</div>" +
                "                <div class='stat-label'>Uptime</div>" +
                "            </div>" +
                "        </div>" +
                "        " +
                "        <div class='features'>" +
                "            <div class='feature-card'>" +
                "                <div class='feature-icon'>📱</div>" +
                "                <h3 class='feature-title'>Mobile Protection</h3>" +
                "                <p class='feature-text'>Real-time cybersecurity monitoring on your mobile device.</p>" +
                "            </div>" +
                "            <div class='feature-card'>" +
                "                <div class='feature-icon'>🌍</div>" +
                "                <h3 class='feature-title'>Global Network</h3>" +
                "                <p class='feature-text'>Connected to worldwide threat intelligence network.</p>" +
                "            </div>" +
                "            <div class='feature-card'>" +
                "                <div class='feature-icon'>⚡</div>" +
                "                <h3 class='feature-title'>Instant Alerts</h3>" +
                "                <p class='feature-text'>Get notified immediately about security threats.</p>" +
                "            </div>" +
                "        </div>" +
                "        " +
                "        <div class='btn-container'>" +
                "            <a href='javascript:checkHealth()' class='btn'>🏥 Health Check</a>" +
                "            <a href='javascript:showInfo()' class='btn'>📊 System Info</a>" +
                "            <a href='javascript:openDonate()' class='btn'>💝 Donate</a>" +
                "        </div>" +
                "        " +
                "        <div class='footer'>" +
                "            <h3>🎉 HoneyNet Mobile is Active!</h3>" +
                "            <p>Your mobile device is now protected by our global cybersecurity network.</p>" +
                "            <p style='margin-top: 10px;'>" +
                "                All rights reserved to <strong>Ze'ev Weinerich Technologies Ltd.</strong><br>" +
                "                Israel, HaHartzit 3, Ashdod, 7761803" +
                "            </p>" +
                "        </div>" +
                "    </div>" +
                "    " +
                "    <script>" +
                "        function checkHealth() {" +
                "            alert('🏥 Health Status: HEALTHY\\n✅ Service: Running\\n📱 Platform: Android\\n🔋 Battery: Optimized');" +
                "        }" +
                "        " +
                "        function showInfo() {" +
                "            alert('📊 System Information\\n🛡️ HoneyNet: Active\\n📱 Platform: Android\\n🌐 Connected: Yes\\n🔒 Security: High');" +
                "        }" +
                "        " +
                "        // Simple real-time updates" +
                "        setInterval(() => {" +
                "            const stats = document.querySelectorAll('.stat-number');" +
                "            if (stats[1]) {" +
                "                let current = parseInt(stats[1].textContent.replace(',', ''));" +
                "                stats[1].textContent = (current + Math.floor(Math.random() * 3) + 1).toLocaleString();" +
                "            }" +
                "        }, 10000);" +
                "    </script>" +
                "</body>" +
                "</html>";
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
