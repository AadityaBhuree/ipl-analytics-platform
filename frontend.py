import customtkinter as ctk
from tkinter import messagebox
import requests
import threading

API_URL = "http://127.0.0.1:8000"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

IPL_ORANGE = "#FF6537"
IPL_PURPLE = "#4B0082"
IPL_GOLD = "#FFD700"
DARK_BG = "#0A0E14"
CARD_BG = "#151C25"
INPUT_BG = "#1C2632"
BORDER_COLOR = "#2A3441"



class IPLPredictorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🏏 IPL Score Predictor")
        self.geometry("750x850")
        self.resizable(False, False)
        self.configure(fg_color=DARK_BG)

        self.teams = []
        self.venues = []
        self.fetch_data()

        self.create_widgets()

    def fetch_data(self):
        try:
            response = requests.get(f"{API_URL}/teams", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.teams = data.get("teams", [])
                self.venues = data.get("venues", [])
        except requests.exceptions.RequestException:
            self.teams = ["Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bangalore",
                         "Kolkata Knight Riders", "Delhi Capitals", "Punjab Kings",
                         "Sunrisers Hyderabad", "Rajasthan Royals", "Lucknow Super Giants", "Gujarat Titans"]
            self.venues = ["M Chinnaswamy Stadium", "Wankhede Stadium", "Eden Gardens", 
                          "MA Chidambaram Stadium", "Arun Jaitley Stadium", "Rajiv Gandhi International Stadium",
                          "Punjab Cricket Association IS Bindra Stadium", "Brabourne Stadium", "DY Patil Stadium"]

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=DARK_BG)
        self.main_frame.pack(fill="both", expand=True)

        self.create_header()
        self.create_team_cards()
        self.create_venue_section()
        self.create_overs_section()
        self.create_predict_button()
        self.create_result_display()

    def create_header(self):
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent", corner_radius=0)
        header.pack(fill="x")

        gradient_frame = ctk.CTkFrame(header, fg_color=IPL_ORANGE, height=80, corner_radius=0)
        gradient_frame.pack(fill="x")
        gradient_frame.pack_propagate(False)

        title_frame = ctk.CTkFrame(gradient_frame, fg_color="transparent")
        title_frame.place(relx=0.5, rely=0.5, anchor="center")

        trophy = ctk.CTkLabel(title_frame, text="🏆", font=ctk.CTkFont(size=36))
        trophy.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_box.pack(side="left")

        title = ctk.CTkLabel(title_box, text="IPL SCORE PREDICTOR", font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(title_box, text="AI-Powered Match Prediction", font=ctk.CTkFont(size=12), text_color="white")
        subtitle.pack(anchor="w")

        season = ctk.CTkLabel(gradient_frame, text="2024", font=ctk.CTkFont(size=14, weight="bold"), 
                              fg_color="white", text_color=IPL_ORANGE, corner_radius=4)
        season.pack(side="right", padx=20, pady=15)

    def create_team_cards(self):
        teams_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        teams_frame.pack(fill="x", padx=25, pady=(25, 0))

        self.batting_team_var = ctk.StringVar()
        self.bowling_team_var = ctk.StringVar()
        self.venue_var = ctk.StringVar()

        batting_card = self.create_team_card(teams_frame, "BATTING", self.batting_team_var, "🏏")
        batting_card.pack(side="left", fill="x", expand=True, padx=(0, 8))

        vs_frame = ctk.CTkFrame(teams_frame, fg_color="transparent", width=60)
        vs_frame.pack(side="left", padx=5)
        vs_frame.pack_propagate(False)

        vs_label = ctk.CTkLabel(vs_frame, text="VS", font=ctk.CTkFont(size=24, weight="bold"), 
                                text_color=IPL_GOLD, fg_color=IPL_PURPLE, corner_radius=20)
        vs_label.pack(expand=True)

        bowling_card = self.create_team_card(teams_frame, "BOWLING", self.bowling_team_var, "🎯")
        bowling_card.pack(side="right", fill="x", expand=True, padx=(8, 0))

    def create_team_card(self, parent, title, variable, icon):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        card.configure(fg_color=CARD_BG)

        title_label = ctk.CTkLabel(card, text=f"{icon} {title} TEAM", font=ctk.CTkFont(size=11, weight="bold"), 
                                    text_color="#6B7785")
        title_label.pack(pady=(12, 8))

        self.team_combo = ctk.CTkComboBox(card, variable=variable, values=self.teams,
                                          font=ctk.CTkFont(size=14, weight="bold"), height=45,
                                          button_color=IPL_ORANGE, button_hover_color="#E55A2B",
                                          dropdown_fg_color=CARD_BG, border_color=IPL_ORANGE,
                                          fg_color=INPUT_BG, text_color="white", dropdown_font=ctk.CTkFont(size=13))
        self.team_combo.pack(fill="x", padx=12, pady=(0, 12))

        if title == "BATTERING" and self.teams:
            self.team_combo.set(self.teams[0])
        elif title == "BOWLING" and len(self.teams) > 1:
            self.team_combo.set(self.teams[1])

        return card

    def create_venue_section(self):
        venue_card = ctk.CTkFrame(self.main_frame, fg_color=CARD_BG, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        venue_card.pack(fill="x", padx=25, pady=(15, 0))

        venue_title = ctk.CTkLabel(venue_card, text="📍 VENUE", font=ctk.CTkFont(size=11, weight="bold"), text_color="#6B7785")
        venue_title.pack(pady=(12, 8))

        self.venue_combo = ctk.CTkComboBox(venue_card, variable=self.venue_var, values=self.venues,
                                           font=ctk.CTkFont(size=14), height=40,
                                           button_color="#58A6FF", button_hover_color="#4090E0",
                                           dropdown_fg_color=CARD_BG, fg_color=INPUT_BG, text_color="white",
                                           dropdown_font=ctk.CTkFont(size=13))
        self.venue_combo.pack(fill="x", padx=12, pady=(0, 12))
        if self.venues:
            self.venue_combo.set(self.venues[0])

    def create_overs_section(self):
        overs_card = ctk.CTkFrame(self.main_frame, fg_color=CARD_BG, border_color=BORDER_COLOR, border_width=1, corner_radius=12)
        overs_card.pack(fill="x", padx=25, pady=(15, 0))

        overs_title = ctk.CTkLabel(overs_card, text="🎯 OVERS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#6B7785")
        overs_title.pack(pady=(12, 10))

        self.overs_var = ctk.IntVar(value=20)

        slider_frame = ctk.CTkFrame(overs_card, fg_color="transparent")
        slider_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.overs_value = ctk.CTkLabel(slider_frame, text="20", font=ctk.CTkFont(size=32, weight="bold"), 
                                        text_color=IPL_ORANGE, width=50)
        self.overs_value.pack(side="left")

        overs_label = ctk.CTkLabel(slider_frame, text="overs", font=ctk.CTkFont(size=14), text_color="#6B7785")
        overs_label.pack(side="left", padx=(5, 15))

        self.overs_slider = ctk.CTkSlider(slider_frame, from_=5, to=20, number_of_steps=15,
                                          variable=self.overs_var, button_color=IPL_ORANGE,
                                          button_hover_color="#E55A2B", progress_color=IPL_PURPLE, fg_color=INPUT_BG)
        self.overs_slider.pack(side="right", fill="x", expand=True)
        self.overs_slider.configure(command=self.update_overs_label)

    def update_overs_label(self, value):
        self.overs_value.configure(text=str(int(value)))

    def create_predict_button(self):
        self.predict_btn = ctk.CTkButton(self.main_frame, text="🔮 PREDICT SCORE",
                                         font=ctk.CTkFont(size=18, weight="bold"), height=55,
                                         fg_color=IPL_ORANGE, hover_color="#E55A2B", border_width=0,
                                         corner_radius=12, command=self.predict_score)
        self.predict_btn.pack(fill="x", padx=25, pady=(20, 0))

    def create_result_display(self):
        result_card = ctk.CTkFrame(self.main_frame, fg_color=CARD_BG, border_color=IPL_GOLD, border_width=2, corner_radius=16)
        result_card.pack(fill="x", padx=25, pady=(20, 25))

        result_header = ctk.CTkFrame(result_card, fg_color=IPL_GOLD, corner_radius=14)
        result_header.pack(fill="x", padx=2, pady=(2, 0))
        result_header.pack_propagate(False)

        header_label = ctk.CTkLabel(result_header, text="🎯 PREDICTED SCORE", 
                                   font=ctk.CTkFont(size=14, weight="bold"), text_color=DARK_BG, height=35)
        header_label.pack(pady=8)

        self.score_display = ctk.CTkLabel(result_card, text="---", font=ctk.CTkFont(size=80, weight="bold"),
                                           text_color=IPL_GOLD)
        self.score_display.pack(pady=(15, 0))

        runs_text = ctk.CTkLabel(result_card, text="TOTAL RUNS", font=ctk.CTkFont(size=12, weight="bold"),
                                  text_color="#6B7785")
        runs_text.pack(pady=(0, 15))

        separator = ctk.CTkFrame(result_card, height=1, fg_color=BORDER_COLOR)
        separator.pack(fill="x", padx=20)

        stats_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=15)

        range_box = ctk.CTkFrame(stats_frame, fg_color=INPUT_BG, corner_radius=8)
        range_box.pack(side="left", fill="x", expand=True, padx=(0, 5))

        range_label = ctk.CTkLabel(range_box, text="📊 RANGE", font=ctk.CTkFont(size=10, weight="bold"), text_color="#6B7785")
        range_label.pack(pady=(10, 5))

        self.range_text = ctk.CTkLabel(range_box, text="-- - --", font=ctk.CTkFont(size=16, weight="bold"), text_color="#58A6FF")
        self.range_text.pack(pady=(0, 10))

        conf_box = ctk.CTkFrame(stats_frame, fg_color=INPUT_BG, corner_radius=8)
        conf_box.pack(side="right", fill="x", expand=True, padx=(5, 0))

        conf_label = ctk.CTkLabel(conf_box, text="🎯 CONFIDENCE", font=ctk.CTkFont(size=10, weight="bold"), text_color="#6B7785")
        conf_label.pack(pady=(10, 5))

        self.conf_text = ctk.CTkLabel(conf_box, text="--", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3FB950")
        self.conf_text.pack(pady=(0, 10))

        self.status_text = ctk.CTkLabel(result_card, text="", font=ctk.CTkFont(size=12), text_color="#6B7785")
        self.status_text.pack(pady=(0, 12))

    def predict_score(self):
        batting = self.batting_team_var.get()
        bowling = self.bowling_team_var.get()
        venue = self.venue_var.get()
        overs = int(self.overs_slider.get())

        if not batting or not bowling or not venue:
            messagebox.showwarning("Warning", "Please select all fields!")
            return

        if batting == bowling:
            messagebox.showwarning("Warning", "Teams must be different!")
            return

        self.status_text.configure(text="🤔 Analyzing match data...")
        self.predict_btn.configure(state="disabled", text="⏳ Processing...")

        thread = threading.Thread(target=self.make_prediction, args=(batting, bowling, venue, overs))
        thread.start()

    def make_prediction(self, batting, bowling, venue, overs):
        try:
            response = requests.post(f"{API_URL}/predict", 
                                    json={"batting_team": batting, "bowling_team": bowling, "venue": venue, "overs": overs},
                                    timeout=15)

            if response.status_code == 200:
                data = response.json()
                self.after(0, self.display_result, data)
            else:
                error = response.json().get("detail", "Failed")
                self.after(0, self.show_error, error)
        except requests.exceptions.ConnectionError:
            self.after(0, self.show_error, "Cannot connect to API!\nStart main.py first.")
        except Exception as e:
            self.after(0, self.show_error, f"Error: {str(e)}")

    def display_result(self, data):
        score = data.get("predicted_score", 0)
        score_range = data.get("predicted_score_range", {})
        confidence = data.get("confidence", "N/A")

        self.score_display.configure(text=str(score))
        self.range_text.configure(text=f"{score_range.get('min', '--')} - {score_range.get('max', '--')}")

        conf_emoji = "🔥" if confidence == "high" else "⚠️" if confidence == "medium" else "❄️"
        self.conf_text.configure(text=f"{conf_emoji} {confidence.upper()}")

        self.status_text.configure(text="✅ Prediction complete!")
        self.predict_btn.configure(state="normal", text="🔮 PREDICT SCORE")

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_text.configure(text="")
        self.predict_btn.configure(state="normal", text="🔮 PREDICT SCORE")


if __name__ == "__main__":
    app = IPLPredictorApp()
    app.mainloop()
