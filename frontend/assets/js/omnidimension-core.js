/**
 * OmniDimension Core Integration for SkillSnap
 * Main client setup and initialization
 */

class SkillSnapOmniCore {
    constructor() {
        this.client = null;
        this.assistants = {};
        this.isInitialized = false;
        this.init();
    }

    async init() {
        try {
            // Initialize OmniDimension client
            this.client = new OmniDim.Client({
                apiKey: 'demo-key-skillsnap', // Replace with actual API key
                environment: 'sandbox' // Change to 'production' when ready
            });

            this.isInitialized = true;
            console.log('🎯 SkillSnap OmniDimension Core Initialized');
            
            // Initialize all assistant modules
            this.initializeCustomerSupport();
            
        } catch (error) {
            console.error('❌ Failed to initialize OmniDimension:', error);
            this.fallbackToBasicSupport();
        }
    }

    // Customer Support Widget (Feature 2)
    initializeCustomerSupport() {
        try {
            // Create support widget container
            const widgetContainer = document.createElement('div');
            widgetContainer.id = 'omnidim-support-widget';
            document.body.appendChild(widgetContainer);

            // Initialize customer support assistant
            const supportWidget = new OmniDim.WebWidget({
                containerId: 'omnidim-support-widget',
                assistant: {
                    name: 'SkillSnap Support Assistant',
                    prompt: `You are SkillSnap's helpful voice assistant. Help users with:
                        - Microphone setup and permission issues
                        - Voice recording troubleshooting  
                        - Account registration and login problems
                        - Challenge submission difficulties
                        - Dashboard navigation help
                        
                        Always be helpful, patient, and provide step-by-step guidance.`,
                    voice: 'nova',
                    model: 'gpt-4'
                },
                ui: {
                    position: 'bottom-right',
                    theme: {
                        primaryColor: '#4f46e5',
                        accentColor: '#667eea'
                    },
                    minimized: true
                }
            });

            this.addSupportWidgetStyles();
            console.log('✅ Customer Support Assistant initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize customer support:', error);
            this.fallbackToBasicSupport();
        }
    }

    addSupportWidgetStyles() {
        const styles = `
            <style id="omnidim-custom-styles">
                #omnidim-support-widget {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 10000;
                }
                
                .omnidim-widget-bubble {
                    background: linear-gradient(135deg, #4f46e5 0%, #667eea 100%);
                    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
                    border: none;
                    transition: transform 0.2s ease;
                }
                
                .omnidim-widget-bubble:hover {
                    transform: translateY(-2px);
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    fallbackToBasicSupport() {
        const fallbackWidget = `
            <div id="fallback-support-widget" style="
                position: fixed; 
                bottom: 20px; 
                right: 20px; 
                z-index: 10000;
                background: linear-gradient(135deg, #4f46e5 0%, #667eea 100%);
                color: white;
                padding: 15px;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
                font-weight: 600;
            " onclick="window.open('mailto:support@skillsnap.com', '_blank')">
                🎧 Need Help?
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', fallbackWidget);
    }

    isReady() {
        return this.isInitialized;
    }
}

// Initialize when page loads
let skillSnapOmni = null;

document.addEventListener('DOMContentLoaded', () => {
    if (typeof OmniDim !== 'undefined') {
        skillSnapOmni = new SkillSnapOmniCore();
        window.skillSnapOmni = skillSnapOmni;
    } else {
        console.warn('⚠️ OmniDimension SDK not loaded');
        // Load SDK dynamically
        const script = document.createElement('script');
        script.src = 'https://cdn.omnidim.io/sdk/v1/omnidim.js';
        script.onload = () => {
            skillSnapOmni = new SkillSnapOmniCore();
            window.skillSnapOmni = skillSnapOmni;
        };
        document.head.appendChild(script);
    }
});

window.SkillSnapOmniCore = SkillSnapOmniCore; 