"""
Structured FAQ knowledge base.

Kept as a plain Python data structure for now so it's trivial to read/edit.
It's intentionally isolated from the tool logic so it can later be swapped
for a database table or a vector store (RAG) without touching FAQTool's
interface -- see README > "Future Expansion".
"""

from typing import Dict, List, TypedDict


class FAQEntry(TypedDict):
    topic: str
    keywords: List[str]
    answer: str


FAQ_KNOWLEDGE_BASE: List[FAQEntry] = [
    {
        "topic": "order_cancellation",
        "keywords": ["cancel", "cancellation", "cancel order", "cancel my order"],
        "answer": (
            "You can cancel an order as long as it hasn't been shipped yet. "
            "Steps: 1) Go to 'My Orders'. 2) Select the order you want to cancel. "
            "3) Tap 'Cancel Order' and choose a reason. 4) If you already paid, "
            "the refund will be initiated automatically to your original payment method. "
            "Once an order has shipped, it can no longer be cancelled, but you can request "
            "a return after delivery."
        ),
    },
    {
        "topic": "payment_pending",
        "keywords": ["payment pending", "payment stuck", "why is my payment pending"],
        "answer": (
            "A payment usually shows as 'pending' while your bank or payment provider is "
            "still confirming the transaction, which can take a few minutes. Steps: "
            "1) Wait 10-15 minutes and refresh your order status. 2) Check if the amount "
            "was debited from your bank/UPI app. 3) If it's still pending after 24 hours, "
            "or was debited but the order didn't confirm, contact support with your order id "
            "so the payment can be manually verified."
        ),
    },
    {
        "topic": "payment_failed",
        "keywords": ["payment failed", "payment did not go through", "payment declined"],
        "answer": (
            "If a payment fails, no money should be deducted -- if it was, it's usually "
            "auto-refunded within 5-7 business days. Steps: 1) Check your bank/UPI app for "
            "the transaction status. 2) Try the payment again with a different method if needed. "
            "3) If the amount was deducted but your order wasn't placed, contact support with "
            "the transaction reference so it can be traced and refunded."
        ),
    },
    {
        "topic": "refund",
        "keywords": ["refund", "request a refund", "get my money back"],
        "answer": (
            "Refunds are issued after a cancelled or returned item is verified. Steps: "
            "1) Cancel the order or complete a return request. 2) Refunds to UPI/cards "
            "typically take 5-7 business days; refunds to store wallet are usually instant. "
            "3) You can track refund status under 'My Orders' > the specific order > "
            "'Refund Status'. If it's been longer than 7 business days, contact support "
            "with your order id."
        ),
    },
    {
        "topic": "return",
        "keywords": ["return", "return policy", "how to return", "return a product"],
        "answer": (
            "Most items can be returned within 7 days of delivery if unused and in original "
            "packaging. Steps: 1) Go to 'My Orders' and select the delivered item. "
            "2) Tap 'Return' and choose a reason. 3) A pickup will be scheduled, or you may "
            "be asked to ship it back. 4) Once the item is verified, your refund or "
            "replacement will be processed. Some categories (e.g. innerwear, perishables) "
            "may not be eligible for return -- this will be shown on the product page."
        ),
    },
    {
        "topic": "replacement",
        "keywords": ["replace", "replacement", "wrong item", "damaged item", "defective"],
        "answer": (
            "If you received a damaged, defective, or wrong item, you can request a free "
            "replacement instead of a refund. Steps: 1) Go to 'My Orders' and select the item. "
            "2) Choose 'Replace Item' and upload a photo if prompted. 3) A pickup of the "
            "original item and delivery of the replacement will be scheduled together where "
            "possible. Replacement requests must usually be raised within 7 days of delivery."
        ),
    },
    {
        "topic": "order_not_arrived",
        "keywords": ["order hasn't arrived", "order not delivered", "where is my order", "late delivery"],
        "answer": (
            "If your order is taking longer than the estimated delivery date: "
            "1) Check the live tracking status under 'My Orders'. 2) Delays of 1-2 days can "
            "happen due to logistics issues. 3) If it's significantly delayed or tracking hasn't "
            "updated in 48+ hours, contact support with your order id so they can escalate it "
            "with the courier partner."
        ),
    },
    {
        "topic": "shipping_delivery",
        "keywords": ["shipping", "delivery time", "how long does delivery take"],
        "answer": (
            "Delivery times depend on your location and the seller, and are shown on the "
            "product page and at checkout before you place the order. Once shipped, you can "
            "track real-time status under 'My Orders' using the tracking id."
        ),
    },
    {
        "topic": "coupons",
        "keywords": ["coupon", "coupon code", "discount code", "promo code"],
        "answer": (
            "Coupons can be applied at checkout in the 'Apply Coupon' section. If a coupon "
            "isn't working, check that: 1) it hasn't expired, 2) your cart meets the minimum "
            "order value, 3) it's valid for the items in your cart. Only one coupon can "
            "usually be applied per order."
        ),
    },
    {
        "topic": "account_login",
        "keywords": ["login", "log in", "sign in", "can't log in", "forgot password"],
        "answer": (
            "If you're having trouble logging in: 1) Double-check your email/phone and "
            "password. 2) Use 'Forgot Password' to reset it via OTP or email link. "
            "3) Make sure you're using the same login method (email vs phone) you signed up "
            "with. If issues persist, contact support."
        ),
    },
    {
        "topic": "account_signup",
        "keywords": ["signup", "sign up", "create account", "register"],
        "answer": (
            "You can create an account using your email or phone number from the Sign Up page. "
            "You'll be asked to verify via OTP or email confirmation before you can start "
            "shopping and saving addresses."
        ),
    },
    {
        "topic": "profile_update",
        "keywords": ["update profile", "change email", "change phone number", "edit profile"],
        "answer": (
            "You can update your profile details from 'My Account' > 'Profile'. Changing your "
            "registered email or phone number may require OTP verification for security."
        ),
    },
    {
        "topic": "customer_support",
        "keywords": ["contact support", "customer support", "talk to agent", "help desk"],
        "answer": (
            "You can reach APNA STORE support through the 'Help & Support' section of the "
            "app/website, where you can raise a ticket referencing your order id. Our team "
            "typically responds within 24 hours."
        ),
    },
    {
        "topic": "privacy",
        "keywords": ["privacy", "data privacy", "is my data safe"],
        "answer": (
            "APNA STORE only uses your account information to process orders, deliveries, and "
            "support requests, and never shares your personal details with other users. You can "
            "review what information is stored about you from 'My Account' > 'Profile'."
        ),
    },
]


def find_faq_answer(query: str) -> FAQEntry | None:
    """Very lightweight keyword matcher over the FAQ knowledge base.

    This is intentionally simple for v1. See README > "Future Expansion"
    for upgrading this to embeddings/RAG for fuzzier matching.
    """
    normalized = query.lower()
    best_match: FAQEntry | None = None
    best_score = 0

    for entry in FAQ_KNOWLEDGE_BASE:
        score = sum(1 for kw in entry["keywords"] if kw in normalized)
        if score > best_score:
            best_score = score
            best_match = entry

    return best_match if best_score > 0 else None


def all_topics() -> Dict[str, str]:
    """Return a topic -> answer map (used for admin/debug purposes)."""
    return {entry["topic"]: entry["answer"] for entry in FAQ_KNOWLEDGE_BASE}
