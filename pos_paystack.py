import tkinter as tk
from tkinter import messagebox
import urllib.request
import urllib.error
import json
import random
import string
import threading

# ── Paystack API Keys ──
PAYSTACK_SECRET_KEY = "sk_test_edb69695124f80c05d856a9a980f082dd02387c8"
PAYSTACK_BASE_URL   = "https://api.paystack.co"


def generate_reference():
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"POS-{suffix}"


def paystack_request(method, endpoint, data=None):
    """Make a real HTTP request to Paystack API."""
    url = PAYSTACK_BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req  = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            return json.loads(error_body)
        except Exception:
            return {"status": False, "message": str(e)}
    except Exception as e:
        return {"status": False, "message": str(e)}


class PaystackPaymentWindow:
    """
    Real Paystack Mobile Money / Card payment window.
    - Initiates a charge via Paystack API
    - Polls for payment confirmation
    - Calls on_success(amount, reference) or on_cancel() accordingly
    """

    def __init__(self, parent, amount, on_success, on_cancel):
        self.parent      = parent
        self.amount      = amount
        self.on_success  = on_success
        self.on_cancel   = on_cancel
        self.reference   = generate_reference()
        self.polling     = False
        self.poll_count  = 0
        self.MAX_POLLS   = 24          # 24 × 5s = 2 minutes max wait

        self.win = tk.Toplevel(parent)
        self.win.title("Mobile Money / Card Payment")
        self.win.geometry("430x520")
        self.win.resizable(False, False)
        self.win.configure(bg="#1e1e2e")
        self.win.protocol("WM_DELETE_WINDOW", self.cancel)
        self.build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def build_ui(self):
        tk.Label(self.win, text="Paystack Payment",
                 font=("Helvetica", 16, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(pady=(20, 4))
        tk.Label(self.win, text=f"Amount: GHS {self.amount:.2f}",
                 font=("Helvetica", 13, "bold"), bg="#1e1e2e", fg="#a6e3a1").pack()
        tk.Label(self.win, text=f"Ref: {self.reference}",
                 font=("Helvetica", 9), bg="#1e1e2e", fg="#6c7086").pack()

        tk.Frame(self.win, bg="#313244", height=1).pack(fill="x", padx=20, pady=12)

        form = tk.Frame(self.win, bg="#1e1e2e", padx=30)
        form.pack(fill="both", expand=True)

        # Email
        tk.Label(form, text="Customer Email:", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#bac2de", anchor="w").pack(fill="x", pady=(0, 3))
        self.email_var = tk.StringVar(value="customer@example.com")
        tk.Entry(form, textvariable=self.email_var, font=("Helvetica", 11),
                 bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                 relief="flat", bd=6).pack(fill="x", ipady=5)

        # Phone
        tk.Label(form, text="Phone Number (MoMo):", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#bac2de", anchor="w").pack(fill="x", pady=(12, 3))
        self.phone_var = tk.StringVar(value="0241234567")
        tk.Entry(form, textvariable=self.phone_var, font=("Helvetica", 11),
                 bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                 relief="flat", bd=6).pack(fill="x", ipady=5)

        # Network (for MoMo)
        tk.Label(form, text="Mobile Network:", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#bac2de", anchor="w").pack(fill="x", pady=(12, 3))
        self.network_var = tk.StringVar(value="mtn")
        networks = [("MTN", "mtn"), ("Vodafone", "vod"), ("AirtelTigo", "tgo")]
        net_row = tk.Frame(form, bg="#1e1e2e")
        net_row.pack(fill="x")
        for label, val in networks:
            tk.Radiobutton(net_row, text=label, variable=self.network_var, value=val,
                           bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                           activebackground="#1e1e2e",
                           font=("Helvetica", 11)).pack(side="left", padx=(0, 12))

        # Payment channel
        tk.Label(form, text="Payment Channel:", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#bac2de", anchor="w").pack(fill="x", pady=(12, 3))
        self.channel_var = tk.StringVar(value="mobile_money")
        ch_row = tk.Frame(form, bg="#1e1e2e")
        ch_row.pack(fill="x")
        for label, val in [("Mobile Money", "mobile_money"), ("Card", "card")]:
            tk.Radiobutton(ch_row, text=label, variable=self.channel_var, value=val,
                           bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                           activebackground="#1e1e2e",
                           font=("Helvetica", 11)).pack(side="left", padx=(0, 12))

        # Status
        self.status_var = tk.StringVar(value="")
        tk.Label(form, textvariable=self.status_var, font=("Helvetica", 10),
                 bg="#1e1e2e", fg="#f9e2af", wraplength=360,
                 justify="center").pack(pady=(10, 0))

        # Buttons
        self.pay_btn = tk.Button(form, text="Pay Now",
                                 font=("Helvetica", 13, "bold"),
                                 bg="#a6e3a1", fg="#1e1e2e", relief="flat",
                                 cursor="hand2", command=self.start_payment)
        self.pay_btn.pack(fill="x", ipady=8, pady=(14, 5))

        tk.Button(form, text="Cancel", font=("Helvetica", 11),
                  bg="#f38ba8", fg="#1e1e2e", relief="flat",
                  cursor="hand2", command=self.cancel).pack(fill="x", ipady=6)

    # ── Payment Flow ──────────────────────────────────────────────────────────

    def start_payment(self):
        email   = self.email_var.get().strip()
        phone   = self.phone_var.get().strip()
        channel = self.channel_var.get()

        if not email:
            self.status_var.set("⚠ Please enter a customer email.")
            return
        if channel == "mobile_money" and not phone:
            self.status_var.set("⚠ Please enter a phone number for Mobile Money.")
            return

        self.pay_btn.config(state="disabled")
        self.status_var.set("Connecting to Paystack...")
        self.win.update()

        # Run API call in a background thread so UI doesn't freeze
        threading.Thread(target=self._initiate_charge,
                         args=(email, phone, channel), daemon=True).start()

    def _initiate_charge(self, email, phone, channel):
        """Called in background thread — initiates a Paystack charge."""
        amount_kobo = int(self.amount * 100)   # Paystack uses kobo (pesewas × 100)

        payload = {
            "email":     email,
            "amount":    amount_kobo,
            "currency":  "GHS",
            "reference": self.reference,
        }

        if channel == "mobile_money":
            payload["mobile_money"] = {
                "phone":    phone,
                "provider": self.network_var.get(),
            }

        response = paystack_request("POST", "/charge", payload)

        # Back to main thread for UI updates
        self.win.after(0, self._handle_charge_response, response, channel)

    def _handle_charge_response(self, response, channel):
        """Handles the response from the initial charge call."""
        if not response.get("status"):
            msg = response.get("message", "Unknown error from Paystack.")
            self.status_var.set(f"❌ Error: {msg}")
            self.pay_btn.config(state="normal")
            return

        data   = response.get("data", {})
        status = data.get("status", "")

        if status == "send_otp":
            self.status_var.set("📲 OTP sent to customer. Waiting for approval...")
            self._start_polling()

        elif status == "pay_offline":
            self.status_var.set(
                f"📱 Prompt sent to {self.phone_var.get()}.\n"
                "Please approve the payment on your phone.\n"
                "Waiting for confirmation..."
            )
            self._start_polling()

        elif status == "pending":
            self.status_var.set("⏳ Payment pending. Waiting for confirmation...")
            self._start_polling()

        elif status == "success":
            self._payment_confirmed()

        elif status == "failed":
            reason = data.get("gateway_response", "Payment failed.")
            self.status_var.set(f"❌ Payment failed: {reason}")
            self.pay_btn.config(state="normal")

        else:
            # Unexpected status — still poll in case it completes
            self.status_var.set(f"Status: {status}. Waiting for confirmation...")
            self._start_polling()

    # ── Polling ───────────────────────────────────────────────────────────────

    def _start_polling(self):
        self.polling    = True
        self.poll_count = 0
        self._poll()

    def _poll(self):
        if not self.polling:
            return
        if self.poll_count >= self.MAX_POLLS:
            self.status_var.set("⏰ Payment timed out. Please try again.")
            self.pay_btn.config(state="normal")
            self.polling = False
            return

        self.poll_count += 1
        threading.Thread(target=self._check_status, daemon=True).start()

    def _check_status(self):
        """Verify transaction status from Paystack."""
        response = paystack_request("GET", f"/transaction/verify/{self.reference}")
        self.win.after(0, self._handle_verify_response, response)

    def _handle_verify_response(self, response):
        if not self.polling:
            return

        data   = response.get("data", {})
        status = data.get("status", "")

        if status == "success":
            self.polling = False
            self._payment_confirmed()

        elif status in ("failed", "reversed"):
            self.polling = False
            reason = data.get("gateway_response", "Payment failed.")
            self.status_var.set(f"❌ Payment failed: {reason}")
            self.pay_btn.config(state="normal")

        else:
            # Still pending — poll again in 5 seconds
            dots = "." * (self.poll_count % 4 + 1)
            self.status_var.set(
                f"⏳ Waiting for customer approval{dots}\n"
                f"({self.poll_count * 5}s elapsed)"
            )
            self.win.after(5000, self._poll)

    # ── Success / Cancel ──────────────────────────────────────────────────────

    def _payment_confirmed(self):
        self.status_var.set(
            f"✅ Payment of GHS {self.amount:.2f} confirmed!\n"
            f"Reference: {self.reference}"
        )
        self.win.update()
        self.win.after(1800, self._finish)

    def _finish(self):
        if self.win.winfo_exists():
            self.win.destroy()
        self.on_success(self.amount, self.reference)

    def cancel(self):
        self.polling = False
        if self.win.winfo_exists():
            self.win.destroy()
        self.on_cancel()


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    PaystackPaymentWindow(
        root, 1.00,
        on_success=lambda amt, ref: print(f"✅ Paid GHS {amt:.2f} | Ref: {ref}"),
        on_cancel=lambda: print("❌ Cancelled"),
    )
    root.mainloop()
