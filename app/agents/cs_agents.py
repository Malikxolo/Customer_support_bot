import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.prompts.prompts import CustomerSupportPrompts
from app.llm import llm

class ConversationContext:
    def __init__(self, session_id: str, category: str):
        self.session_id = session_id
        self.selected_category = category
        self.stage = "initial"
        self.collected_items = ""
        self.conversation_history = []
        self.payment_option = "" 

class CustomerSupportAgent:
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
        self.prompts = CustomerSupportPrompts()
    
    def start_conversation(self, category: str) -> Dict[str, Any]:
        """Start new conversation with category"""
        session_id = str(uuid.uuid4())
        
        context = ConversationContext(session_id, category)
        self.sessions[session_id] = context
        
        template = self.prompts.CATEGORY_TEMPLATES[category]
        behavior = self.prompts.UI_BEHAVIOR[category]
        
        context.conversation_history.extend([
            {"role": "user", "content": category, "timestamp": datetime.now()},
            {"role": "assistant", "content": template, "timestamp": datetime.now()}
        ])
        
        result = {
            "success": True,
            "session_id": session_id,
            "message": template,
            **behavior
        }
        
        if category == "Payment and billing related query":
            result["buttons"] = self.prompts.PAYMENT_OPTIONS
        
        return result
    
    def process_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """Process user input based on conversation stage"""
        
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}
        
        context = self.sessions[session_id]
        
        context.conversation_history.append({
            "role": "user", 
            "content": user_input, 
            "timestamp": datetime.now()
        })
        
        if context.stage == "initial":
            return self._handle_items_input(context, user_input)
        elif context.stage == "photo_requested":
            return self._handle_photo_response(context, user_input)
        elif context.stage == "additional_info":
            return self._handle_additional_info(context, user_input)
        elif context.stage == "resolution_choice":
            return self._handle_resolution_choice(context, user_input)
        elif context.stage == "final_resolution":
            return self._handle_final_resolution(context, user_input)
        elif context.stage == "general_chat":
            return self._handle_general_chat(context, user_input)
        elif context.stage == "payment_response":
            return self._handle_payment_followup(context, user_input)
        else:
            return {"success": True, "message": "I'm here to help with your order issues.", "show_chat": True}
    
    def _handle_payment_button(self, session_id: str, button_text: str) -> Dict[str, Any]:
        """Handle payment option button clicks"""
        
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}
        
        context = self.sessions[session_id]
        context.stage = "payment_response"
        context.payment_option = button_text 
        
        context.conversation_history.append({
            "role": "user",
            "content": button_text,
            "timestamp": datetime.now()
        })
        
        if "refund status" in button_text.lower():
            prompt_key = "payment_refund_status"
        elif "payment failure" in button_text.lower():
            prompt_key = "payment_failure"
        elif "invoice" in button_text.lower():
            prompt_key = "payment_invoice"
        elif "bill-related" in button_text.lower():
            prompt_key = "payment_bill_issues"
        elif "coupon did not work" in button_text.lower():
            prompt_key = "payment_coupon_not_work"
        else:
            prompt_key = "payment_refund_status"
        
        ai_prompt = self.prompts.AI_PROMPTS[prompt_key]
        response = llm.generate_response(ai_prompt)
        
        context.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
        return {
            "success": True,
            "message": response,
            "show_chat": True  
        }
    
    def _handle_payment_followup(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Handle any input after payment response - escalate with specific message"""
        
        payment_option = context.payment_option
        
        if "refund status" in payment_option.lower():
            escalation_prompt = self.prompts.AI_PROMPTS["escalation_refund_status"]
        elif "payment failure" in payment_option.lower():
            escalation_prompt = self.prompts.AI_PROMPTS["escalation_payment_failure"]
        elif "invoice" in payment_option.lower():
            escalation_prompt = self.prompts.AI_PROMPTS["escalation_invoice"]
        elif "bill-related" in payment_option.lower():
            escalation_prompt = self.prompts.AI_PROMPTS["escalation_bill_issues"]
        elif "coupon did not work" in payment_option.lower():
            escalation_prompt = self.prompts.AI_PROMPTS["escalation_coupon"]
        else:
            escalation_prompt = self.prompts.AI_PROMPTS["escalation_refund_status"]
        
        response = llm.generate_response(escalation_prompt)
        
        context.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
        return {
            "success": True,
            "message": response,
            "show_chat": False,
            "escalated": True
        }
    
    def _handle_items_input(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Handle initial items input"""
        
        context.collected_items = user_input
        context.stage = "photo_requested"
        
        ai_prompt = self.prompts.AI_PROMPTS["photo_request"].format(items=user_input)
        response = llm.generate_response(ai_prompt)
        
        context.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
        return {
            "success": True,
            "message": response,
            "show_input": False,
            "show_chat": True
        }
    
    def _handle_photo_response(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Handle photo response - Send separate thank you messages"""
        
        context.stage = "additional_info"
        
        thank_you = "Thank you for providing the details."
        
        context.conversation_history.append({
            "role": "assistant",
            "content": thank_you,
            "timestamp": datetime.now()
        })
        
        return {
            "success": True,
            "message": thank_you,
            "show_chat": True,
            "next_message": "Please provide additional information so that we can assist you better"
        }
    
    def _handle_additional_info(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Handle additional info based on category"""
        
        category = context.selected_category
        items = context.collected_items 
        
        # Category 3
        if category == "Few item(s) are missing in my order":
            context.stage = "final_resolution"
            
            apology_prompt = self.prompts.AI_PROMPTS["apology_missing_first"].format(items=items)
            apology = llm.generate_response(apology_prompt)
            
            context.conversation_history.append({
                "role": "assistant",
                "content": apology,
                "timestamp": datetime.now()
            })
            
            return {
                "success": True,
                "message": apology,
                "show_chat": True,
                "next_message_prompt": "reorder_offer_missing_second",
                "next_message_items": items
            }
        
        # Category 4
        elif category == "Item(s) delivered are incorrect or wrong":
            context.stage = "final_resolution"
            
            apology_prompt = self.prompts.AI_PROMPTS["apology_wrong"]
            apology = llm.generate_response(apology_prompt)
            
            resolution_offer = "Would you prefer a refund or reorder for the affected items?"
            
            context.conversation_history.append({
                "role": "assistant",
                "content": apology,
                "timestamp": datetime.now()
            })
            
            context.conversation_history.append({
                "role": "assistant",
                "content": resolution_offer,
                "timestamp": datetime.now()
            })
            
            return {
                "success": True,
                "message": f"{apology}\n\n{resolution_offer}",
                "show_chat": True
            }
        
        # Categories 2, 5, 6
        context.stage = "resolution_choice"
        
        if "portion" in category.lower():
            apology_prompt = self.prompts.AI_PROMPTS["apology_portion"]
        elif "quality" in category.lower():
            apology_prompt = self.prompts.AI_PROMPTS["apology_quality"]
        elif "spillage" in category.lower():
            apology_prompt = self.prompts.AI_PROMPTS["apology_spillage"]
        else:
            apology_prompt = self.prompts.AI_PROMPTS["apology_quality"]
        
        apology = llm.generate_response(apology_prompt)
        
        context.conversation_history.append({
            "role": "assistant",
            "content": apology,
            "timestamp": datetime.now()
        })
        
        return {
            "success": True,
            "message": apology,
            "show_chat": False,
            "multiple_messages": [
                {"content": "We just checked with the restaurant regarding this matter.", "delay": 1000},
                {"content": "However, we're here to help. If you need further assistance, do drop an email for us to escalate this issue further.\n\nPlease let us know how you would like to proceed", "delay": 2000}
            ],
            "show_buttons": True,
            "buttons": [
                "I only want to report this issue",
                "I would still like a resolution for this issue"
            ]
        }
    
    def _handle_resolution_choice(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Handle resolution choice buttons"""
        
        if "only want to report" in user_input.lower() or "report this issue" in user_input.lower():
            report_prompt = self.prompts.AI_PROMPTS["report_thanks"]
            response = llm.generate_response(report_prompt)
            
            context.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            return {
                "success": True,
                "message": response,
                "show_chat": False,
                "resolved": True
            }
        
        elif "still like a resolution" in user_input.lower() or "resolution for this issue" in user_input.lower():
            context.stage = "final_resolution"
            
            items = context.collected_items
            acknowledge_prompt = self.prompts.AI_PROMPTS["resolution_acknowledge"].format(items=items)
            response = llm.generate_response(acknowledge_prompt)
            
            context.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            return {
                "success": True,
                "message": response,
                "show_chat": True
            }
        
        else:
            return {
                "success": True,
                "message": "Please let me know if you want to report the issue or need a resolution.",
                "show_chat": True
            }
    
    def _handle_final_resolution(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Handle final refund/reorder choice"""
        
        user_choice = user_input.lower()
        items = context.collected_items 
        category = context.selected_category
        
        # Category 3
        if category == "Few item(s) are missing in my order":
            if "reorder" in user_choice or "re-order" in user_choice or "order" in user_choice or "yes" in user_choice or "ok" in user_choice:
                response = self.prompts.generate_reorder_details(items)
                
                context.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
                closing_prompt = self.prompts.AI_PROMPTS["reorder_feedback_final"].format(items=items)
                closing_msg = llm.generate_response(closing_prompt)
                
                context.conversation_history.append({
                    "role": "assistant",
                    "content": closing_msg,
                    "timestamp": datetime.now()
                })
                
                return {
                    "success": True,
                    "message": f"{response}\n\n{closing_msg}",
                    "show_chat": False,
                    "resolved": True  
                }
            else:
                reorder_prompt = self.prompts.AI_PROMPTS["reorder_offer_missing_second"].format(items=items)
                response = llm.generate_response(reorder_prompt)
                
                context.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
                return {
                    "success": True,
                    "message": response,
                    "show_chat": True
                }
        
        # Categories 2, 4, 5, 6
        else:
            if "refund" in user_choice:
                response = self.prompts.generate_refund_details(items)
                feedback_prompt = self.prompts.AI_PROMPTS["refund_feedback_final"].format(items=items)
            elif "reorder" in user_choice or "re-order" in user_choice or "order" in user_choice:
                response = self.prompts.generate_reorder_details(items)
                feedback_prompt = self.prompts.AI_PROMPTS["reorder_feedback_final"].format(items=items)
            else:
                response = f"Would you prefer a refund or reorder for {items}?"
                
                context.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
                return {
                    "success": True,
                    "message": response,
                    "show_chat": True
                }
            
            context.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            closing_msg = llm.generate_response(feedback_prompt)
            
            context.conversation_history.append({
                "role": "assistant",
                "content": closing_msg,
                "timestamp": datetime.now()
            })
            
            return {
                "success": True,
                "message": f"{response}\n\n{closing_msg}",
                "show_chat": False,
                "resolved": True
            }
    
    def _handle_general_chat(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Handle general chat - order-related only"""
        
        relevance_prompt = f"""Is this query related to food delivery, order issues, refunds, delivery status, payment issues, or customer support for food delivery apps?
        Query: "{user_input}"
        
        Answer only: YES or NO"""
        
        is_relevant = llm.generate_response(relevance_prompt)
        
        if "NO" in is_relevant.upper():
            redirect_prompt = self.prompts.AI_PROMPTS["redirect_non_order"].format(query=user_input)
            response = llm.generate_response(redirect_prompt)
        else:
            order_prompt = self.prompts.AI_PROMPTS["order_query_response"].format(query=user_input)
            response = llm.generate_response(order_prompt)
        
        context.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
        return {
            "success": True,
            "message": response,
            "show_chat": True
        }

support_agent = CustomerSupportAgent()
