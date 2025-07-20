import json
import os
import boto3
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Slack client
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
slack_client = WebClient(token=SLACK_BOT_TOKEN)

def lambda_handler(event, context):
    """
    Lambda handler for Slack notifications
    
    Args:
        event: Lambda event containing notification details
        context: Lambda context
        
    Returns:
        Response with status information
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract notification details
        notification_type = event.get('type', 'info')
        message = event.get('message', 'No message provided')
        channel = event.get('channel', '#t-developer')
        blocks = event.get('blocks', [])
        thread_ts = event.get('thread_ts')
        
        # Send message to Slack
        if thread_ts:
            response = slack_client.chat_postMessage(
                channel=channel,
                text=message,
                blocks=blocks if blocks else None,
                thread_ts=thread_ts
            )
        else:
            response = slack_client.chat_postMessage(
                channel=channel,
                text=message,
                blocks=blocks if blocks else None
            )
        
        logger.info(f"Message sent successfully: {response['ts']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': 'Notification sent successfully',
                'timestamp': response['ts']
            })
        }
    
    except SlackApiError as e:
        logger.error(f"Error sending message to Slack: {e.response['error']}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f"Error sending message to Slack: {e.response['error']}"
            })
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }