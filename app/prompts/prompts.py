import random

class CustomerSupportPrompts:
    """All customer support templates and responses"""
    
    CATEGORY_TEMPLATES = {
        "I did not receive this order": "Please stay on the chat screen. The next available representative will join in to assist you shortly..",
        
        "Item(s) portion size is not adequate": "Sorry to hear that. Let us know which items were of Insufficient quantity?",
        
        "Few item(s) are missing in my order": "Sorry to hear that. Let us know which items are missing from your order?",
        
        "Item(s) delivered are incorrect or wrong": "Sorry to hear that. Can you please help us know what items were affected by this issue?",
        
        "Item(s) quality is poor": "Sorry to hear that. Let us know which items were of poor quality?",
        
        "Item(s) has spillage issue": "Sorry to hear that. What items were affected by this issue?",
        
        "I have coupon related query for this order": """I have coupon related query for this order

**1. I am unable to find my coupon:**
You can view available coupons for your order, by going to the 'APPLY COUPON' section on the cart page while placing your order.

**2. I unable to apply my coupon:**
Please check if you have adhered to all the coupon's terms and conditions. Choose your coupon in the 'APPLY COUPON' section and click '+MORE' to review all T&Cs to avail the benefits.

**3. I forgot to apply my coupon:**
It looks like you missed applying your coupon. No worries, though! Your coupon is still valid and waiting for you. Simply apply it to your next order and enjoy the savings. We appreciate your understanding and look forward to serving you again soon!""",
        
        "Payment and billing related query": "Hi there! I am the Swiggy Bot and I'm here to help you. Please choose the option which best describes your issue for me to help you better"
    }
    
    # Payment option buttons
    PAYMENT_OPTIONS = [
        "I want to know my refund status",
        "I have payment failure related issues", 
        "I want an invoice for this order",
        "I have bill-related issues",
        "My coupon did not work as expected"
    ]
    
    UI_BEHAVIOR = {
        "I did not receive this order": {
            "show_input": False,
            "show_chat": False,
            "needs_escalation": True
        },
        
        "Item(s) portion size is not adequate": {
            "show_input": True,
            "show_chat": False,
            "needs_photo": True
        },
        
        "Few item(s) are missing in my order": {
            "show_input": True,
            "show_chat": False,
            "needs_photo": True
        },
        
        "Item(s) delivered are incorrect or wrong": {
            "show_input": True,
            "show_chat": False,
            "needs_photo": True
        },
        
        "Item(s) quality is poor": {
            "show_input": True,
            "show_chat": False,
            "needs_photo": True
        },
        
        "Item(s) has spillage issue": {
            "show_input": True,
            "show_chat": False,
            "needs_photo": True
        },
        
        "I have coupon related query for this order": {
            "show_input": False,
            "show_chat": False,
            "needs_escalation": False
        },
        
        "Payment and billing related query": {
            "show_input": False,
            "show_chat": False,
            "show_payment_buttons": True
        }
    }
    
    AI_PROMPTS = {
        "photo_request": "Generate a natural customer support message asking for photo of {items} to share feedback with restaurant partner. Keep it 1-2 lines and professional.",
        
        "apology_portion": "Generate 1 line professional apology for insufficient portion size not meeting customer expectations",
        "apology_quality": "Generate 1 line professional apology for food quality not meeting customer expectations", 
        "apology_spillage": "Generate 1 line professional apology for spillage issues with the food delivery",
        
        "apology_missing_first": "Generate a professional 1-line apology for missing items '{items}' in the order, mentioning feedback will be passed to delivery partner to prevent future issues.",
        "reorder_offer_missing_second": "Generate a helpful message offering to reorder the missing '{items}' items for quick delivery. Don't mention restaurant, just focus on reordering the specific items mentioned.",
        
        "apology_wrong": "Generate a professional customer support apology for incorrect/wrong items delivered and say feedback will be passed to restaurant partner. Keep it natural and realistic.",
        
        "restaurant_policy_intro": "Generate a professional 1-line message about checking with the restaurant regarding this issue",
        "restaurant_policy_alternative": "Generate a helpful 1-2 line message about alternative ways to resolve this issue, mentioning email escalation option",
        
        "resolution_acknowledge": "Generate 1-2 line message acknowledging customer wants resolution for {items} and asking if they prefer refund or reorder. Be professional and helpful.",
        
        "report_thanks": "Generate a professional 1-2 line message thanking customer for reporting food delivery issue and confirming it will be shared with restaurant partner for improvement.",
        
        "refund_feedback_final": "Generate 1-2 line message apologizing for trouble with {items} and confirming feedback will be shared with restaurant partner to improve quality. Don't ask if they need more help.",
        "reorder_feedback_final": "Generate 1-2 line message apologizing for inconvenience with {items} and confirming delivery partner will be informed to prevent future issues. Don't ask if they need more help.",
        
        "order_query_response": "Customer asks order-related question: {query}. Respond helpfully in 1-2 lines as a professional customer support agent for food delivery app.",
        "redirect_non_order": "Customer asked: {query}. Generate a polite 1-line response redirecting them to ask only order-related questions as you're a customer support bot for food delivery.",
        
        "payment_refund_status": "Customer wants to know refund status. Generate a helpful 2-3 line response explaining how to check refund status and typical timelines, like a professional customer support agent.",
        "payment_failure": "Customer has payment failure issues. Generate a helpful 2-3 line response about payment failure troubleshooting and next steps, like a professional customer support agent.",
        "payment_invoice": "Customer wants an invoice for their order. Generate a helpful 2-3 line response about how to get invoice and where to find it, like a professional customer support agent.",
        "payment_bill_issues": "Customer has bill-related issues. Generate a helpful 2-3 line response about resolving billing concerns and next steps, like a professional customer support agent.",
        "payment_coupon_not_work": "Customer's coupon didn't work as expected. Generate a helpful 2-3 line response about coupon troubleshooting and resolution, like a professional customer support agent.",
        
        "escalation_refund_status": "Generate a professional 1-line message about connecting customer with support team for further assistance with their refund status inquiry.",
        "escalation_payment_failure": "Generate a professional 1-line message about connecting customer with support team for further assistance with their payment failure issue.",
        "escalation_invoice": "Generate a professional 1-line message about connecting customer with support team for further assistance with their invoice request.",
        "escalation_bill_issues": "Generate a professional 1-line message about connecting customer with support team for further assistance with their billing issue.",
        "escalation_coupon": "Generate a professional 1-line message about connecting customer with support team for further assistance with their coupon issue."
    }
    
    @staticmethod
    def generate_refund_details(items: str) -> str:
        """Generate random refund details"""
        refund_id = f"RF{random.randint(100000, 999999)}"
        amount = random.randint(150, 800)
        days = random.choice([3, 5, 7])
        
        return f"Refund of ₹{amount} initiated for {items}. Refund ID: {refund_id}. Amount will reflect in {days} business days."
    
    @staticmethod
    def generate_reorder_details(items: str) -> str:
        """Generate random reorder details"""
        order_id = random.randint(100000000, 999999999)
        eta = random.randint(30, 50)
        
        return f"Reorder placed for {items}! Order ID: {order_id}. Fresh items will arrive in {eta} minutes."
    
    @staticmethod
    def get_escalation_message() -> str:
        """Escalation message"""
        return "Let me connect you with our support team for further assistance. Please stay on the chat."
