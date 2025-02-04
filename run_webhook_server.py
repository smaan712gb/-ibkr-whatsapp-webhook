import asyncio
import logging
from dotenv import load_dotenv
import os
from aiohttp import web
from ibkr_trading_system.whatsapp_webhook import WhatsAppWebhook

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_app():
    """Run the web application"""
    # Load environment variables
    load_dotenv()
    
    # Get webhook configuration
    host = os.getenv('WHATSAPP_WEBHOOK_HOST', '0.0.0.0')
    port = int(os.getenv('WHATSAPP_WEBHOOK_PORT', '8080'))
    
    logger.info("Starting WhatsApp webhook server...")
    logger.info(f"Webhook URL: http://{host}:{port}/webhook")
    logger.info("Use this URL in the WhatsApp Business API configuration")
    
    # Create the application
    app = web.Application()
    
    # Create webhook handler
    async with WhatsAppWebhook() as webhook:
        # Add routes
        app.router.add_get('/webhook', webhook.handle_verification)
        app.router.add_post('/webhook', webhook.handle_update)
        
        # Start the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        
        try:
            await site.start()
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("Server shutdown requested")
        finally:
            await runner.cleanup()

async def main():
    """Main entry point with signal handling"""
    try:
        await run_app()
    except KeyboardInterrupt:
        logger.info("Shutting down webhook server...")

if __name__ == "__main__":
    asyncio.run(main())
