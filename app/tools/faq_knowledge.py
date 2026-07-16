"""
Structured FAQ knowledge base.

Kept as a plain Python data structure for now so it's trivial to read/edit.
It's intentionally isolated from the tool logic so it can later be swapped
for a database table or a vector store (RAG) without touching FAQTool's
interface -- see README > "Future Expansion".
"""
from typing import Dict, List, TypedDict, NotRequired


class FAQEntry(TypedDict):
    category: str
    topic: str
    priority: int
    keywords: List[str]
    answer: str
    next_actions: NotRequired[List[str]]


FAQ_KNOWLEDGE_BASE: List[FAQEntry] = [
    {
        "category": "Orders",
        "topic": "track_order",
        "priority": 10,
        "keywords": [
            "track order",
            "where is my order",
            "track my order",
            "order status",
            "tracking",
            "delivery status",
        ],
        "answer": (
            "Customers can track their orders from My Orders. "
            "The latest delivery status, tracking ID and estimated delivery date are available there."
        ),
        "next_actions": [
            "View Latest Order",
            "Delivery Delay",
            "Contact Support",
        ],
    },
    {
        "category": "Orders",
        "topic": "order_cancellation",
        "priority": 10,
        "keywords": [
            "cancel",
            "cancel order",
            "cancel my order",
            "order cancellation",
            "stop my order",
            "don't want order",
        ],
        "answer": (
            "Orders can be cancelled before they are shipped. "
            "If the order has already been shipped, cancellation is no longer available, but an eligible return can be requested after delivery."
        ),
        "next_actions": [
            "Track My Order",
            "Return an Item",
            "Refund Status",
        ],
    },
    {
        "category": "Orders",
        "topic": "latest_order",
        "priority": 9,
        "keywords": [
            "latest order",
            "last order",
            "recent order",
            "my newest order",
        ],
        "answer": (
            "Customers can view their latest order from the My Orders section, including its status, payment details and delivery information."
        ),
        "next_actions": [
            "Track My Order",
            "Cancel Order",
        ],
    },
    {
        "category": "Orders",
        "topic": "order_not_found",
        "priority": 9,
        "keywords": [
            "can't find order",
            "order missing",
            "order not showing",
            "where is my purchase",
        ],
        "answer": (
            "If an order is not visible, refresh My Orders or check that you are logged into the correct account. "
            "If it still doesn't appear, contact customer support."
        ),
        "next_actions": [
            "Latest Order",
            "Contact Support",
        ],
    },
    {
        "category": "Delivery",
        "topic": "delivery_delay",
        "priority": 10,
        "keywords": [
            "late delivery",
            "delivery delayed",
            "order delayed",
            "delivery taking long",
        ],
        "answer": (
            "Occasional delivery delays may happen because of weather, logistics or courier issues. "
            "Customers can check the latest delivery updates from My Orders."
        ),
        "next_actions": [
            "Track My Order",
            "Contact Support",
        ],
    },
    {
        "category": "Delivery",
        "topic": "estimated_delivery",
        "priority": 9,
        "keywords": [
            "delivery date",
            "estimated delivery",
            "when will it arrive",
            "delivery time",
        ],
        "answer": (
            "Estimated delivery dates are shown on the product page, during checkout and inside My Orders after purchase."
        ),
        "next_actions": [
            "Track My Order",
        ],
    },
    {
        "category": "Delivery",
        "topic": "delivery_attempt_failed",
        "priority": 9,
        "keywords": [
            "delivery failed",
            "missed delivery",
            "delivery attempt",
            "courier missed",
        ],
        "answer": (
            "If delivery could not be completed, another attempt may be scheduled automatically. "
            "Please check the latest tracking updates for more information."
        ),
        "next_actions": [
            "Track My Order",
            "Contact Support",
        ],
    },
    {
        "category": "Delivery",
        "topic": "change_delivery_address",
        "priority": 9,
        "keywords": [
            "change address",
            "delivery address",
            "update delivery address",
            "edit shipping address",
        ],
        "answer": (
            "Delivery addresses can usually be changed before the order is shipped. "
            "After shipment, address changes may no longer be possible."
        ),
        "next_actions": [
            "Track My Order",
            "Saved Addresses",
        ],
    },
    {
        "category": "Delivery",
        "topic": "shipping_charges",
        "priority": 8,
        "keywords": [
            "shipping charges",
            "delivery charges",
            "shipping fee",
            "delivery fee",
        ],
        "answer": (
            "Shipping charges depend on the seller, product and delivery location. "
            "Any applicable delivery charges are shown during checkout."
        ),
        "next_actions": [
            "Offers",
        ],
    },
    {
        "category": "Delivery",
        "topic": "out_for_delivery",
        "priority": 10,
        "keywords": [
            "out for delivery",
            "when will courier arrive",
            "courier coming",
        ],
        "answer": (
            "When an order is marked 'Out for Delivery', it is with the delivery partner and is expected to arrive the same day whenever possible."
        ),
        "next_actions": [
            "Track My Order",
            "Contact Support",
        ],
    },
        {
        "category": "Payments",
        "topic": "payment_pending",
        "priority": 10,
        "keywords": [
            "payment pending",
            "pending payment",
            "money deducted",
            "payment stuck",
            "payment processing",
            "payment taking time"
        ],
        "answer": (
            "Payments may remain pending while your bank or payment provider confirms the transaction. "
            "Most payments are updated automatically within a few minutes."
        ),
        "next_actions": [
            "Payment Failed",
            "Refund Status",
            "Contact Support"
        ],
    },

    {
        "category": "Payments",
        "topic": "payment_failed",
        "priority": 10,
        "keywords": [
            "payment failed",
            "payment declined",
            "payment unsuccessful",
            "transaction failed",
            "unable to pay"
        ],
        "answer": (
            "If a payment fails, you can try again using another payment method. "
            "If money was deducted but the order wasn't placed, the amount is usually refunded automatically."
        ),
        "next_actions": [
            "Refund Status",
            "Retry Payment",
            "Contact Support"
        ],
    },

    {
        "category": "Payments",
        "topic": "refund_status",
        "priority": 10,
        "keywords": [
            "refund",
            "refund status",
            "where is my refund",
            "refund pending",
            "money back"
        ],
        "answer": (
            "Refunds are processed after cancellation or return verification. "
            "Customers can check the latest refund status from My Orders."
        ),
        "next_actions": [
            "Return Item",
            "Payment Failed",
            "Contact Support"
        ],
    },

    {
        "category": "Payments",
        "topic": "refund_delay",
        "priority": 9,
        "keywords": [
            "refund delayed",
            "refund not received",
            "late refund",
            "refund taking time"
        ],
        "answer": (
            "Refunds usually take 5–7 business days depending on the payment method. "
            "If it takes longer, customer support can verify the refund."
        ),
        "next_actions": [
            "Refund Status",
            "Contact Support"
        ],
    },

    {
        "category": "Payments",
        "topic": "cash_on_delivery",
        "priority": 8,
        "keywords": [
            "cash on delivery",
            "cod",
            "pay on delivery",
            "cash payment"
        ],
        "answer": (
            "Cash on Delivery may be available for eligible products and locations. "
            "Availability is shown during checkout."
        ),
        "next_actions": [
            "Payment Methods",
            "Shipping Charges"
        ],
    },

    {
        "category": "Payments",
        "topic": "upi_payment",
        "priority": 8,
        "keywords": [
            "upi",
            "google pay",
            "phonepe",
            "paytm",
            "bhim"
        ],
        "answer": (
            "Customers can pay securely using supported UPI apps during checkout."
        ),
        "next_actions": [
            "Payment Failed",
            "Refund Status"
        ],
    },

    {
        "category": "Payments",
        "topic": "credit_debit_card",
        "priority": 8,
        "keywords": [
            "credit card",
            "debit card",
            "visa",
            "mastercard",
            "rupay"
        ],
        "answer": (
            "Major credit and debit cards are supported. "
            "Cards must support online transactions."
        ),
        "next_actions": [
            "Payment Failed",
            "EMI"
        ],
    },

    {
        "category": "Payments",
        "topic": "emi",
        "priority": 8,
        "keywords": [
            "emi",
            "installment",
            "monthly payment",
            "no cost emi"
        ],
        "answer": (
            "Eligible products may offer EMI options through supported banks or payment partners. "
            "Available plans are shown during checkout."
        ),
        "next_actions": [
            "Credit Card",
            "Payment Methods"
        ],
    },

    {
        "category": "Payments",
        "topic": "invoice",
        "priority": 8,
        "keywords": [
            "invoice",
            "bill",
            "tax invoice",
            "gst invoice"
        ],
        "answer": (
            "Invoices can be downloaded from My Orders after the order has been confirmed or delivered."
        ),
        "next_actions": [
            "Latest Order"
        ],
    },

    {
        "category": "Payments",
        "topic": "payment_security",
        "priority": 9,
        "keywords": [
            "payment safe",
            "secure payment",
            "payment security",
            "is payment safe"
        ],
        "answer": (
            "All supported payment methods use secure payment processing to help protect customer information."
        ),
        "next_actions": [
            "Privacy",
            "Contact Support"
        ],
    },
        {
        "category": "Returns",
        "topic": "return_item",
        "priority": 10,
        "keywords": [
            "return item",
            "return order",
            "return product",
            "how to return",
            "return request"
        ],
        "answer": (
            "Eligible products can be returned within the return window from My Orders. "
            "Select the item, choose a return reason and confirm your request."
        ),
        "next_actions": [
            "Return Status",
            "Refund Status",
            "Replacement"
        ],
    },

    {
        "category": "Returns",
        "topic": "return_window",
        "priority": 10,
        "keywords": [
            "return period",
            "return window",
            "how many days",
            "return policy",
            "return deadline"
        ],
        "answer": (
            "Return eligibility depends on the product category. "
            "The available return window is shown on the product page and inside My Orders."
        ),
        "next_actions": [
            "Return Item",
            "Replacement"
        ],
    },

    {
        "category": "Returns",
        "topic": "replacement",
        "priority": 10,
        "keywords": [
            "replacement",
            "replace product",
            "replace item",
            "exchange damaged"
        ],
        "answer": (
            "Eligible products can be replaced if they are damaged, defective or incorrect. "
            "Replacement availability depends on the product and seller."
        ),
        "next_actions": [
            "Return Item",
            "Wrong Item",
            "Damaged Product"
        ],
    },

    {
        "category": "Returns",
        "topic": "exchange",
        "priority": 9,
        "keywords": [
            "exchange",
            "exchange product",
            "exchange item",
            "size exchange"
        ],
        "answer": (
            "Exchange is available only for selected products. "
            "Availability is shown on the product page and in My Orders."
        ),
        "next_actions": [
            "Replacement",
            "Return Item"
        ],
    },

    {
        "category": "Returns",
        "topic": "damaged_product",
        "priority": 10,
        "keywords": [
            "damaged",
            "broken",
            "product damaged",
            "received damaged",
            "cracked"
        ],
        "answer": (
            "If you receive a damaged product, request a replacement or return from My Orders. "
            "You may be asked to upload photos for verification."
        ),
        "next_actions": [
            "Replacement",
            "Return Item",
            "Contact Support"
        ],
    },

    {
        "category": "Returns",
        "topic": "wrong_item",
        "priority": 10,
        "keywords": [
            "wrong item",
            "wrong product",
            "different item",
            "incorrect item"
        ],
        "answer": (
            "If you received the wrong product, request a replacement or return from My Orders."
        ),
        "next_actions": [
            "Replacement",
            "Return Item",
            "Contact Support"
        ],
    },

    {
        "category": "Returns",
        "topic": "missing_item",
        "priority": 10,
        "keywords": [
            "missing item",
            "item missing",
            "missing product",
            "missing package"
        ],
        "answer": (
            "If part of your order is missing, please report it from My Orders so the issue can be verified."
        ),
        "next_actions": [
            "Contact Support",
            "Latest Order"
        ],
    },

    {
        "category": "Returns",
        "topic": "pickup_failed",
        "priority": 9,
        "keywords": [
            "pickup failed",
            "pickup cancelled",
            "return pickup",
            "pickup not happened"
        ],
        "answer": (
            "If a return pickup was unsuccessful, another pickup attempt may be scheduled automatically. "
            "You can also contact support for assistance."
        ),
        "next_actions": [
            "Return Status",
            "Contact Support"
        ],
    },

    {
        "category": "Returns",
        "topic": "return_rejected",
        "priority": 9,
        "keywords": [
            "return rejected",
            "return declined",
            "return denied",
            "return failed"
        ],
        "answer": (
            "Return requests may be rejected if the product is not eligible or doesn't meet the return policy."
        ),
        "next_actions": [
            "Return Policy",
            "Contact Support"
        ],
    },

    {
        "category": "Returns",
        "topic": "replacement_unavailable",
        "priority": 8,
        "keywords": [
            "replacement unavailable",
            "replacement not available",
            "cannot replace",
            "no replacement"
        ],
        "answer": (
            "If a replacement is unavailable, an eligible refund or return option may be offered instead."
        ),
        "next_actions": [
            "Refund Status",
            "Return Item"
        ],
    },
        {
        "category": "Account",
        "topic": "login",
        "priority": 10,
        "keywords": [
            "login",
            "log in",
            "sign in",
            "can't login",
            "unable to login",
            "login problem"
        ],
        "answer": (
            "Make sure you're using the correct email or phone number and password. "
            "If you're still unable to sign in, use the 'Forgot Password' option to reset your password."
        ),
        "next_actions": [
            "Forgot Password",
            "Contact Support"
        ],
    },

    {
        "category": "Account",
        "topic": "signup",
        "priority": 9,
        "keywords": [
            "signup",
            "sign up",
            "register",
            "create account",
            "new account"
        ],
        "answer": (
            "Create an account using your email address or mobile number. "
            "Complete OTP verification to start shopping."
        ),
        "next_actions": [
            "Login"
        ],
    },

    {
        "category": "Account",
        "topic": "forgot_password",
        "priority": 10,
        "keywords": [
            "forgot password",
            "reset password",
            "password reset",
            "can't remember password"
        ],
        "answer": (
            "Use the 'Forgot Password' option on the login screen. "
            "A password reset link or OTP will be sent to your registered email or phone number."
        ),
        "next_actions": [
            "Login"
        ],
    },

    {
        "category": "Account",
        "topic": "otp_issue",
        "priority": 9,
        "keywords": [
            "otp",
            "otp not received",
            "verification code",
            "didn't receive otp"
        ],
        "answer": (
            "Wait a few minutes and request a new OTP. "
            "Make sure your mobile network is available and your registered phone number is correct."
        ),
        "next_actions": [
            "Login",
            "Contact Support"
        ],
    },

    {
        "category": "Account",
        "topic": "change_email",
        "priority": 9,
        "keywords": [
            "change email",
            "update email",
            "new email",
            "edit email"
        ],
        "answer": (
            "You can update your registered email from My Account > Profile. "
            "Email verification may be required for security."
        ),
        "next_actions": [
            "Update Profile"
        ],
    },

    {
        "category": "Account",
        "topic": "change_phone",
        "priority": 9,
        "keywords": [
            "change phone",
            "update phone",
            "mobile number",
            "change mobile"
        ],
        "answer": (
            "Update your registered phone number from My Account > Profile. "
            "OTP verification may be required."
        ),
        "next_actions": [
            "Update Profile"
        ],
    },

    {
        "category": "Account",
        "topic": "update_profile",
        "priority": 8,
        "keywords": [
            "profile",
            "edit profile",
            "update profile",
            "change profile"
        ],
        "answer": (
            "You can update your name, phone number and email from My Account > Profile."
        ),
        "next_actions": [
            "Change Email",
            "Change Phone"
        ],
    },

    {
        "category": "Account",
        "topic": "delete_account",
        "priority": 8,
        "keywords": [
            "delete account",
            "remove account",
            "close account",
            "permanently delete"
        ],
        "answer": (
            "If you wish to permanently delete your account, please contact customer support. "
            "Account deletion cannot be undone."
        ),
        "next_actions": [
            "Contact Support"
        ],
    },

    {
        "category": "Security",
        "topic": "privacy",
        "priority": 8,
        "keywords": [
            "privacy",
            "data privacy",
            "is my data safe",
            "personal information"
        ],
        "answer": (
            "Your personal information is used only for shopping, delivery and customer support. "
            "Your information is never shared with other customers."
        ),
        "next_actions": [
            "Contact Support"
        ],
    },

    {
        "category": "Security",
        "topic": "account_locked",
        "priority": 9,
        "keywords": [
            "account locked",
            "blocked account",
            "disabled account",
            "can't access account"
        ],
        "answer": (
            "Accounts may be temporarily locked after multiple unsuccessful login attempts. "
            "Try again later or contact customer support if the problem continues."
        ),
        "next_actions": [
            "Forgot Password",
            "Contact Support"
        ],
    },
        {
        "category": "Shopping",
        "topic": "search_products",
        "priority": 10,
        "keywords": [
            "find product",
            "search product",
            "looking for",
            "show products",
            "find item"
        ],
        "answer": (
            "You can search products using the search bar at the top of the app. "
            "Use product names, brands or categories to find what you're looking for."
        ),
        "next_actions": [
            "Compare Products",
            "Best Offers"
        ],
    },

    {
        "category": "Shopping",
        "topic": "compare_products",
        "priority": 9,
        "keywords": [
            "compare",
            "compare products",
            "difference between",
            "which is better"
        ],
        "answer": (
            "You can compare products based on price, ratings, features and customer reviews before making a purchase."
        ),
        "next_actions": [
            "Search Products",
            "Product Reviews"
        ],
    },

    {
        "category": "Shopping",
        "topic": "wishlist",
        "priority": 8,
        "keywords": [
            "wishlist",
            "save product",
            "save for later",
            "favorite"
        ],
        "answer": (
            "Products can be saved to your Wishlist for future purchases. "
            "You can access your Wishlist anytime from your account."
        ),
        "next_actions": [
            "Search Products"
        ],
    },

    {
        "category": "Shopping",
        "topic": "out_of_stock",
        "priority": 9,
        "keywords": [
            "out of stock",
            "not available",
            "sold out",
            "stock unavailable"
        ],
        "answer": (
            "If a product is out of stock, it may become available again later. "
            "Please check back periodically for updates."
        ),
        "next_actions": [
            "Search Products"
        ],
    },

    {
        "category": "Shopping",
        "topic": "product_reviews",
        "priority": 8,
        "keywords": [
            "reviews",
            "ratings",
            "customer reviews",
            "product rating"
        ],
        "answer": (
            "Customer ratings and reviews help you understand product quality and buying experience before purchasing."
        ),
        "next_actions": [
            "Compare Products"
        ],
    },

    {
        "category": "Offers",
        "topic": "coupons",
        "priority": 10,
        "keywords": [
            "coupon",
            "promo code",
            "discount code",
            "offer code"
        ],
        "answer": (
            "Coupons can be applied during checkout. "
            "Only eligible coupons will be accepted based on the order value and applicable products."
        ),
        "next_actions": [
            "Best Offers"
        ],
    },

    {
        "category": "Offers",
        "topic": "best_offers",
        "priority": 9,
        "keywords": [
            "offers",
            "discount",
            "today deals",
            "best deals",
            "sale"
        ],
        "answer": (
            "Current offers, discounts and promotional deals are displayed on the homepage and eligible product pages."
        ),
        "next_actions": [
            "Coupons",
            "Gift Cards"
        ],
    },

    {
        "category": "Shopping",
        "topic": "gift_cards",
        "priority": 8,
        "keywords": [
            "gift card",
            "gift voucher",
            "gift coupon"
        ],
        "answer": (
            "Gift Cards can be used to purchase eligible products. "
            "The available balance is applied during checkout."
        ),
        "next_actions": [
            "Payment Methods"
        ],
    },

    {
        "category": "Shopping",
        "topic": "product_availability",
        "priority": 8,
        "keywords": [
            "available",
            "availability",
            "is product available",
            "stock"
        ],
        "answer": (
            "Product availability depends on the seller and your delivery location. "
            "Availability is shown on each product page."
        ),
        "next_actions": [
            "Search Products"
        ],
    },

    {
        "category": "Support",
        "topic": "contact_support",
        "priority": 10,
        "keywords": [
            "contact support",
            "customer support",
            "help",
            "talk to agent",
            "raise ticket",
            "customer care"
        ],
        "answer": (
            "If you need additional assistance, you can contact APNA STORE Customer Support or raise a support ticket from the Help & Support section."
        ),
        "next_actions": [
            "Raise Ticket"
        ],
    },
]


def find_faq_answer(query: str) -> FAQEntry | None:
    """
    Lightweight keyword matcher for FAQ knowledge.

    Returns the FAQ with the highest keyword match.
    If multiple FAQs have the same score, the one with the
    higher priority is selected.
    """

    normalized = query.lower().strip()

    best_match: FAQEntry | None = None
    best_score = 0

    for entry in FAQ_KNOWLEDGE_BASE:
        score = sum(
            1
            for kw in entry["keywords"]
            if kw.lower() in normalized
        )

        if (
            score > best_score
            or (
                score == best_score
                and best_match is not None
                and entry["priority"] > best_match["priority"]
            )
        ):
            best_score = score
            best_match = entry

    # Require at least one keyword match
    if best_score == 0:
        return None

    return best_match

def all_topics() -> Dict[str, FAQEntry]:
    """
    Return all FAQ topics mapped to their complete FAQ entry.
    Useful for admin panels, debugging and future APIs.
    """
    return {
        entry["topic"]: entry
        for entry in FAQ_KNOWLEDGE_BASE
    }
    
def get_faq_by_category(category: str) -> List[FAQEntry]:
    """
    Return all FAQs belonging to a category.
    """

    return [
        entry
        for entry in FAQ_KNOWLEDGE_BASE
        if entry["category"].lower() == category.lower()
    ]

def get_faq_by_topic(topic: str) -> FAQEntry | None:
    """
    Return a FAQ by its topic.
    """

    for entry in FAQ_KNOWLEDGE_BASE:
        if entry["topic"] == topic:
            return entry

    return None

def all_categories() -> List[str]:
    """
    Return all unique FAQ categories.
    """

    return sorted({
        entry["category"]
        for entry in FAQ_KNOWLEDGE_BASE
    })