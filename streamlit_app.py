import streamlit as st
import time
from datetime import datetime
from app.agents.cs_agents import support_agent

# Page config
st.set_page_config(
    page_title="Customer Support",
    page_icon="🛎️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS styling
st.markdown("""
<style>
/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Chat styling */
.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px 60px;
    max-width: 80%;
    float: right;
    clear: both;
    word-wrap: break-word;
}

.bot-message {
    background: #f1f3f5;
    color: #333;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 60px 8px 0;
    max-width: 80%;
    float: left;
    clear: both;
    word-wrap: break-word;
    white-space: pre-line;
}

.message-time {
    font-size: 12px;
    color: #666;
    margin-top: 4px;
    opacity: 0.7;
}

/* Button styling */
.stButton > button {
    width: 100% !important;
    padding: 16px !important;
    border-radius: 12px !important;
    border: 1px solid #e0e0e0 !important;
    background: white !important;
    color: #333 !important;
    text-align: left !important;
    margin-bottom: 12px !important;
    font-size: 16px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    border-color: #ff6b35 !important;
    box-shadow: 0 4px 8px rgba(255,107,53,0.2) !important;
    transform: translateY(-1px) !important;
}

/* Payment button styling */
.payment-button {
    background: #f8f9fa !important;
    border: 2px solid #007bff !important;
    color: #007bff !important;
    font-weight: 600 !important;
    margin: 8px 0 !important;
}

.payment-button:hover {
    background: #007bff !important;
    color: white !important;
}

/* Choice button styling */
.choice-button {
    background: #f8f9fa !important;
    border: 2px solid #ff6b35 !important;
    color: #ff6b35 !important;
    font-weight: 600 !important;
    margin: 8px 0 !important;
}

.choice-button:hover {
    background: #ff6b35 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    defaults = {
        "page": "categories",
        "session_id": None,
        "messages": [],
        "show_input": False,
        "show_chat": False,
        "show_buttons": False,
        "show_payment_buttons": False,
        "buttons": [],
        "payment_buttons": [],
        "escalated": False,
        "resolved": False,
        "next_message": None,
        "next_message_prompt": None,
        "next_message_items": None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

CATEGORIES = [
    "I did not receive this order",
    "Item(s) portion size is not adequate", 
    "Few item(s) are missing in my order",
    "Item(s) delivered are incorrect or wrong",
    "Item(s) quality is poor",
    "Item(s) has spillage issue",
    "I have coupon related query for this order",
    "Payment and billing related query"
]

def show_categories():
    """Show category selection page"""
    
    col1, col2 = st.columns([1, 8])
    with col1:
        st.markdown("← ")
    with col2:
        st.markdown("**Help & Support**")
    
    st.markdown("---")
    
    for i, category in enumerate(CATEGORIES):
        if st.button(category, key=f"cat_{i}"):
            start_chat(category)

def start_chat(category: str):
    """Start chat with selected category"""
    
    st.session_state.resolved = False
    st.session_state.escalated = False
    
    result = support_agent.start_conversation(category)
    
    if result["success"]:
        st.session_state.session_id = result["session_id"]
        st.session_state.page = "chat"
        st.session_state.show_input = result.get("show_input", False)
        st.session_state.show_chat = result.get("show_chat", False)
        st.session_state.show_payment_buttons = result.get("show_payment_buttons", False)
        st.session_state.payment_buttons = result.get("buttons", [])
        st.session_state.escalated = result.get("needs_escalation", False)
        
        st.session_state.messages = [
            {"role": "user", "content": category, "time": datetime.now().strftime("%H:%M")},
            {"role": "assistant", "content": result["message"], "time": datetime.now().strftime("%H:%M")}
        ]
        
        st.rerun()

def show_chat():
    """Show chat interface"""
    
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("←", key="back"):
            reset_chat()
    with col2:
        st.markdown("**Chat with us**")
    
    st.markdown("---")
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="text-align: right; margin-bottom: 15px;">
                <div class="user-message">
                    {msg["content"]}
                    <div class="message-time">{msg["time"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: left; margin-bottom: 15px;">
                <div class="bot-message">
                    {msg["content"]}
                    <div class="message-time">{msg["time"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.next_message:
        time.sleep(1) 
        st.session_state.messages.append({
            "role": "assistant",
            "content": st.session_state.next_message,
            "time": datetime.now().strftime("%H:%M")
        })
        st.session_state.next_message = None
        st.rerun()
    
    if st.session_state.next_message_prompt and st.session_state.next_message_items:
        from app.llm import llm
        from app.prompts.prompts import CustomerSupportPrompts
        
        time.sleep(1)
        prompt_key = st.session_state.next_message_prompt
        items = st.session_state.next_message_items
        
        prompts = CustomerSupportPrompts()
        ai_prompt = prompts.AI_PROMPTS[prompt_key].format(items=items)
        next_msg = llm.generate_response(ai_prompt)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": next_msg,
            "time": datetime.now().strftime("%H:%M")
        })
        
        st.session_state.next_message_prompt = None
        st.session_state.next_message_items = None
        st.rerun()
    
    if st.session_state.escalated:
        st.info(" Chat transferred to support agent")
    
    elif st.session_state.resolved:
        st.success(" Issue resolved. Thank you!")
    
    elif st.session_state.show_payment_buttons:
        st.markdown("**Please choose an option:**")
        
        for button_text in st.session_state.payment_buttons:
            if st.button(button_text, key=f"payment_{button_text}"):
                process_payment_button(button_text)
    
    elif st.session_state.show_buttons:
        st.markdown("**Please choose an option:**")
        
        for button_text in st.session_state.buttons:
            if st.button(button_text, key=f"choice_{button_text}"):
                process_input(button_text)
    
    elif st.session_state.show_input:
        user_input = st.text_input("chat", placeholder="Enter your response here...", key="input_box", label_visibility="collapsed")
        
        if user_input and user_input.strip():
            if st.button("Send", key="send_input"):
                process_input(user_input)
    
    elif st.session_state.show_chat:
        user_input = st.chat_input("Type your message...")
        if user_input:
            process_input(user_input)

def process_payment_button(button_text: str):
    """Process payment button click"""
    
    result = support_agent._handle_payment_button(st.session_state.session_id, button_text)
    
    if result["success"]:
        st.session_state.messages.append({
            "role": "user",
            "content": button_text,
            "time": datetime.now().strftime("%H:%M")
        })
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["message"],
            "time": datetime.now().strftime("%H:%M")
        })
        
        st.session_state.show_payment_buttons = False
        st.session_state.show_chat = result.get("show_chat", False)
        st.session_state.escalated = result.get("escalated", False)
        
        st.rerun()

def process_input(user_input: str):
    """Process user input"""
    
    result = support_agent.process_input(st.session_state.session_id, user_input)
    
    if result["success"]:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": datetime.now().strftime("%H:%M")
        })
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["message"],
            "time": datetime.now().strftime("%H:%M")
        })
        
        st.session_state.show_input = result.get("show_input", False)
        st.session_state.show_chat = result.get("show_chat", False)
        st.session_state.show_buttons = result.get("show_buttons", False)
        st.session_state.buttons = result.get("buttons", [])
        st.session_state.escalated = result.get("escalated", False)
        st.session_state.resolved = result.get("resolved", False)
        st.session_state.next_message = result.get("next_message", None)
        st.session_state.next_message_prompt = result.get("next_message_prompt", None)
        st.session_state.next_message_items = result.get("next_message_items", None)
        
        st.rerun()

def reset_chat():
    """Reset to categories page"""
    init_session_state()
    st.session_state.page = "categories"
    st.rerun()

def main():
    init_session_state()
    
    if st.session_state.page == "categories":
        show_categories()
    else:
        show_chat()

if __name__ == "__main__":
    main()
